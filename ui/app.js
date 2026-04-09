// Task Assistant UI — plain vanilla JS, no build step.
//
// This file does three things:
//   1. Wraps the FastAPI endpoints in a tiny `api` client.
//   2. Keeps an in-memory cache of tasks and assignees so we can re-render
//      filters client-side without re-fetching on every keystroke.
//   3. Wires up form submits, delete/toggle buttons, and the search box.

const API_BASE = "http://localhost:8000";

// -----------------------------------------------------------------------------
// API client
// -----------------------------------------------------------------------------

async function request(path, options = {}) {
  const res = await fetch(API_BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    // Try to surface FastAPI's {"detail": "..."} error message.
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch (_) { /* ignore — body wasn't JSON */ }
    throw new Error(detail);
  }
  // DELETE endpoints return JSON too, but 204-style empty bodies are possible.
  if (res.status === 204) return null;
  return res.json();
}

const api = {
  health:            ()        => request("/health"),
  listTasks:         ()        => request("/tasks"),
  createTask:        (body)    => request("/tasks", { method: "POST", body: JSON.stringify(body) }),
  updateTask:        (id, b)   => request(`/tasks/${id}`, { method: "PUT", body: JSON.stringify(b) }),
  deleteTask:        (id)      => request(`/tasks/${id}`, { method: "DELETE" }),
  listAssignees:     ()        => request("/assignees"),
  createAssignee:    (body)    => request("/assignees", { method: "POST", body: JSON.stringify(body) }),
  deleteAssignee:    (id)      => request(`/assignees/${id}`, { method: "DELETE" }),
};

// -----------------------------------------------------------------------------
// State — cached responses plus the current search/filter controls.
// -----------------------------------------------------------------------------

const state = {
  tasks: [],
  assignees: [],
  search: "",
  filterAssigneeId: "",
};

// -----------------------------------------------------------------------------
// Tiny helpers
// -----------------------------------------------------------------------------

const $ = (id) => document.getElementById(id);

function showToast(msg, isError = false) {
  const el = $("toast");
  el.textContent = msg;
  el.classList.toggle("error", isError);
  el.hidden = false;
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => { el.hidden = true; }, 2600);
}

// Escape text before injecting into innerHTML, so a task titled
// "<img onerror=...>" renders as text instead of executing.
function esc(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function assigneeName(id) {
  if (id == null) return null;
  const a = state.assignees.find((x) => x.id === id);
  return a ? a.name : `#${id}`;
}

// -----------------------------------------------------------------------------
// Rendering
// -----------------------------------------------------------------------------

function renderAssignees() {
  const list = $("assignee-list");
  $("assignee-count").textContent = state.assignees.length;

  if (state.assignees.length === 0) {
    list.innerHTML = `<li class="empty">No people yet. Add one above.</li>`;
  } else {
    list.innerHTML = state.assignees.map((a) => `
      <li data-id="${a.id}">
        <div class="body">
          <div class="title">${esc(a.name)}</div>
          <div class="desc">${esc(a.email)}</div>
        </div>
        <div class="actions">
          <button class="ghost danger" data-action="delete-assignee" data-id="${a.id}" title="Delete">✕</button>
        </div>
      </li>
    `).join("");
  }

  // Refresh the two assignee dropdowns (create-task form + filter).
  const options = ['<option value="">— Unassigned —</option>']
    .concat(state.assignees.map((a) => `<option value="${a.id}">${esc(a.name)}</option>`))
    .join("");
  $("task-assignee").innerHTML = options;

  const filter = $("task-filter-assignee");
  const prevFilter = state.filterAssigneeId;
  filter.innerHTML = '<option value="">All people</option>' +
    state.assignees.map((a) => `<option value="${a.id}">${esc(a.name)}</option>`).join("");
  filter.value = prevFilter;
}

function renderTasks() {
  const list = $("task-list");
  const search = state.search.trim().toLowerCase();
  const filterId = state.filterAssigneeId ? Number(state.filterAssigneeId) : null;

  const visible = state.tasks.filter((t) => {
    if (filterId !== null && t.assignee_id !== filterId) return false;
    if (!search) return true;
    return (
      t.title.toLowerCase().includes(search) ||
      (t.description && t.description.toLowerCase().includes(search))
    );
  });

  $("task-count").textContent = state.tasks.length;

  if (visible.length === 0) {
    list.innerHTML = `<li class="empty">${
      state.tasks.length === 0 ? "No tasks yet. Create one above." : "No tasks match your filters."
    }</li>`;
    return;
  }

  list.innerHTML = visible.map((t) => {
    const name = assigneeName(t.assignee_id);
    const badge = name
      ? `<span class="badge">${esc(name)}</span>`
      : `<span class="badge unassigned">Unassigned</span>`;
    return `
      <li class="${t.completed ? "completed" : ""}" data-id="${t.id}">
        <input type="checkbox" ${t.completed ? "checked" : ""} data-action="toggle" data-id="${t.id}" />
        <div class="body">
          <div class="title">${esc(t.title)}</div>
          ${t.description ? `<div class="desc">${esc(t.description)}</div>` : ""}
          <div class="meta">${badge}</div>
        </div>
        <div class="actions">
          <button class="ghost danger" data-action="delete-task" data-id="${t.id}" title="Delete">✕</button>
        </div>
      </li>
    `;
  }).join("");
}

// -----------------------------------------------------------------------------
// Data loading
// -----------------------------------------------------------------------------

async function refreshAll() {
  try {
    const [tasks, assignees] = await Promise.all([api.listTasks(), api.listAssignees()]);
    state.tasks = tasks;
    state.assignees = assignees;
    renderAssignees();
    renderTasks();
  } catch (err) {
    showToast(`Failed to load: ${err.message}`, true);
  }
}

async function checkHealth() {
  const dot = $("status-dot");
  const text = $("status-text");
  try {
    await api.health();
    dot.className = "dot ok";
    text.textContent = "API connected";
  } catch (err) {
    dot.className = "dot err";
    text.textContent = `API unreachable (${API_BASE})`;
  }
}

// -----------------------------------------------------------------------------
// Event wiring
// -----------------------------------------------------------------------------

$("assignee-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = $("assignee-name").value.trim();
  const email = $("assignee-email").value.trim();
  if (!name || !email) return;

  try {
    const created = await api.createAssignee({ name, email });
    state.assignees.push(created);
    renderAssignees();
    e.target.reset();
    showToast(`Added ${created.name}`);
  } catch (err) {
    showToast(err.message, true);
  }
});

$("task-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = $("task-title").value.trim();
  const description = $("task-description").value.trim();
  const assigneeRaw = $("task-assignee").value;

  // Build the payload — only include assignee_id if the user actually picked one.
  // The API treats omission as "unassigned".
  const payload = { title, description };
  if (assigneeRaw !== "") payload.assignee_id = Number(assigneeRaw);

  try {
    const created = await api.createTask(payload);
    state.tasks.push(created);
    renderTasks();
    e.target.reset();
    showToast(`Created "${created.title}"`);
  } catch (err) {
    showToast(err.message, true);
  }
});

// Single delegated click handler for everything inside the two lists.
document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-action]");
  if (!btn) return;
  const action = btn.dataset.action;
  const id = Number(btn.dataset.id);

  try {
    if (action === "delete-task") {
      await api.deleteTask(id);
      state.tasks = state.tasks.filter((t) => t.id !== id);
      renderTasks();
      showToast("Task deleted");
    } else if (action === "delete-assignee") {
      await api.deleteAssignee(id);
      state.assignees = state.assignees.filter((a) => a.id !== id);
      // Any tasks assigned to this person were unassigned server-side — mirror that locally.
      state.tasks = state.tasks.map((t) => (t.assignee_id === id ? { ...t, assignee_id: null } : t));
      renderAssignees();
      renderTasks();
      showToast("Person removed");
    } else if (action === "toggle") {
      const completed = btn.checked;
      const updated = await api.updateTask(id, { completed });
      state.tasks = state.tasks.map((t) => (t.id === id ? updated : t));
      renderTasks();
    }
  } catch (err) {
    showToast(err.message, true);
    // Re-sync with server in case local state drifted.
    refreshAll();
  }
});

$("task-search").addEventListener("input", (e) => {
  state.search = e.target.value;
  renderTasks();
});

$("task-filter-assignee").addEventListener("change", (e) => {
  state.filterAssigneeId = e.target.value;
  renderTasks();
});

// -----------------------------------------------------------------------------
// Boot
// -----------------------------------------------------------------------------

checkHealth();
refreshAll();
