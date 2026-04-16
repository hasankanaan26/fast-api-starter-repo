// Task Assistant UI — plain vanilla JS, no build step.
//
// This file does three things:
//   1. Wraps the FastAPI endpoints in a tiny `api` client.
//   2. Keeps an in-memory cache of tasks and assignees so we can re-render
//      filters client-side without re-fetching on every keystroke.
//   3. Wires up form submits, delete/toggle buttons, and the search box.
//   4. Provides a Document Analysis UI for the LLM pipeline endpoints.

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
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch (_) { /* ignore */ }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

const api = {
  // Existing task/assignee endpoints
  health:            ()        => request("/health"),
  listTasks:         ()        => request("/tasks"),
  createTask:        (body)    => request("/tasks", { method: "POST", body: JSON.stringify(body) }),
  updateTask:        (id, b)   => request(`/tasks/${id}`, { method: "PUT", body: JSON.stringify(b) }),
  deleteTask:        (id)      => request(`/tasks/${id}`, { method: "DELETE" }),
  listAssignees:     ()        => request("/assignees"),
  createAssignee:    (body)    => request("/assignees", { method: "POST", body: JSON.stringify(body) }),
  deleteAssignee:    (id)      => request(`/assignees/${id}`, { method: "DELETE" }),

  // Document analysis endpoints (Checkpoint 2 + 3)
  analyzePipeline:   (text)    => request("/pipeline/analyze", { method: "POST", body: JSON.stringify({ text }) }),
  analyzeSentiment:  (text)    => request("/analyze/sentiment", { method: "POST", body: JSON.stringify({ text }) }),
  analyzeSummarize:  (text, n) => request("/analyze/summarize", { method: "POST", body: JSON.stringify({ text, max_sentences: n }) }),
  analyzeClassify:   (text)    => request("/analyze/classify", { method: "POST", body: JSON.stringify({ text }) }),
};

// -----------------------------------------------------------------------------
// State
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
// Tab switching
// -----------------------------------------------------------------------------

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
    tab.classList.add("active");
    const target = document.getElementById("tab-" + tab.dataset.tab);
    if (target) target.classList.add("active");
  });
});

// -----------------------------------------------------------------------------
// Rendering — Tasks & Assignees
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
          <button class="ghost danger" data-action="delete-assignee" data-id="${a.id}" title="Delete">&#10005;</button>
        </div>
      </li>
    `).join("");
  }

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
          <button class="ghost danger" data-action="delete-task" data-id="${t.id}" title="Delete">&#10005;</button>
        </div>
      </li>
    `;
  }).join("");
}

// -----------------------------------------------------------------------------
// Rendering — Document Analysis Results
// -----------------------------------------------------------------------------

function confidenceHtml(value) {
  const pct = Math.round(value * 100);
  return `
    <span class="confidence-bar">
      <span class="bar"><span class="bar-fill" style="width:${pct}%"></span></span>
      ${pct}%
    </span>
  `;
}

function renderPipelineResult(data) {
  const area = $("analysis-results");
  let html = "";

  // Step 1: Classification
  const step1Class = data.steps_completed >= 1 ? "done" : "fail";
  html += `<div class="result-section">
    <div class="result-section-header">
      <span class="step-badge ${step1Class}">1</span> Classification
    </div>
    <div class="result-section-body">`;

  if (data.classification) {
    html += `<table class="field-table">
      <tr><th>Category</th><td><span class="badge">${esc(data.classification.category)}</span></td></tr>
      <tr><th>Confidence</th><td>${confidenceHtml(data.classification.confidence)}</td></tr>
      <tr><th>Reasoning</th><td>${esc(data.classification.reasoning)}</td></tr>
    </table>`;
  } else {
    html += `<div class="error-text">Classification did not complete.</div>`;
  }
  html += `</div></div>`;

  // Step 2: Extraction
  const step2Class = data.steps_completed >= 2 ? "done" : (data.steps_completed >= 1 ? "fail" : "fail");
  html += `<div class="result-section">
    <div class="result-section-header">
      <span class="step-badge ${step2Class}">2</span> Extracted Fields
    </div>
    <div class="result-section-body">`;

  if (data.extraction && data.extraction.fields && data.extraction.fields.length > 0) {
    html += `<table class="field-table">`;
    for (const f of data.extraction.fields) {
      html += `<tr><th>${esc(f.key)}</th><td>${esc(f.value)}</td></tr>`;
    }
    html += `</table>`;
  } else if (data.steps_completed < 2) {
    html += `<div class="error-text">Extraction did not complete.</div>`;
  } else {
    html += `<p>No fields extracted.</p>`;
  }
  html += `</div></div>`;

  // Step 3: Summary
  const step3Class = data.steps_completed >= 3 ? "done" : "fail";
  html += `<div class="result-section">
    <div class="result-section-header">
      <span class="step-badge ${step3Class}">3</span> Summary
    </div>
    <div class="result-section-body">`;

  if (data.summary) {
    html += `<div class="summary-text">${esc(data.summary)}</div>`;
  } else {
    html += `<div class="error-text">Summary was not generated.</div>`;
  }
  html += `</div></div>`;

  // Error (if any)
  if (data.error) {
    html += `<div class="result-section">
      <div class="result-section-header" style="color:var(--danger)">Error</div>
      <div class="result-section-body"><div class="error-text">${esc(data.error)}</div></div>
    </div>`;
  }

  area.innerHTML = html;
  $("analysis-status").textContent = `${data.steps_completed}/3 steps`;
}

function renderSentimentResult(data) {
  const area = $("analysis-results");
  area.innerHTML = `<div class="result-section">
    <div class="result-section-header">Sentiment Analysis</div>
    <div class="result-section-body">
      <table class="field-table">
        <tr><th>Sentiment</th><td><span class="badge">${esc(data.sentiment)}</span></td></tr>
        <tr><th>Confidence</th><td>${confidenceHtml(data.confidence)}</td></tr>
        <tr><th>Reasoning</th><td>${esc(data.reasoning)}</td></tr>
      </table>
    </div>
  </div>`;
  $("analysis-status").textContent = "Done";
}

function renderSummaryResult(data) {
  const area = $("analysis-results");
  area.innerHTML = `<div class="result-section">
    <div class="result-section-header">Summary (${data.sentence_count} sentence${data.sentence_count !== 1 ? "s" : ""})</div>
    <div class="result-section-body">
      <div class="summary-text">${esc(data.summary)}</div>
    </div>
  </div>`;
  $("analysis-status").textContent = "Done";
}

function renderClassifyResult(data) {
  const area = $("analysis-results");
  area.innerHTML = `<div class="result-section">
    <div class="result-section-header">Ticket Classification</div>
    <div class="result-section-body">
      <table class="field-table">
        <tr><th>Category</th><td><span class="badge">${esc(data.category)}</span></td></tr>
        <tr><th>Confidence</th><td>${confidenceHtml(data.confidence)}</td></tr>
        <tr><th>Reasoning</th><td>${esc(data.reasoning)}</td></tr>
      </table>
    </div>
  </div>`;
  $("analysis-status").textContent = "Done";
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
// Example texts for the Document Analysis tab
// -----------------------------------------------------------------------------

const EXAMPLES = {
  bug: `The export button throws a 500 error every time I click it. Started happening yesterday after the latest deployment. I've tried refreshing the page and clearing my cache, but the issue persists. This is blocking our end-of-month reporting.`,
  feature: `It would be amazing if we could schedule reports to be generated automatically every Monday morning. Right now I have to manually run them, which takes about 30 minutes of my time each week. This would save our entire team hours per month.`,
  billing: `I was charged $49.99 twice on March 15th for my Pro subscription. I only have one account and should only be billed once. I'd like a refund for the duplicate charge as soon as possible.`,
  praise: `I just wanted to say that Sarah from your support team was absolutely fantastic. She helped me migrate my entire workspace in under an hour and even stayed late to make sure everything was working perfectly. Best support experience I've ever had!`,
};

// -----------------------------------------------------------------------------
// Event wiring — Tasks & Assignees
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
// Event wiring — Document Analysis
// -----------------------------------------------------------------------------

// Show/hide the "max sentences" option based on analysis type
$("analysis-type").addEventListener("change", () => {
  const isSummarize = $("analysis-type").value === "summarize";
  $("summarize-options").hidden = !isSummarize;
});

// Fill textarea with example text
document.querySelectorAll(".example-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const key = btn.dataset.example;
    if (EXAMPLES[key]) {
      $("analysis-text").value = EXAMPLES[key];
    }
  });
});

// Submit analysis
$("analysis-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = $("analysis-text").value.trim();
  if (!text) return;

  const type = $("analysis-type").value;
  const btn = $("analyze-btn");
  const area = $("analysis-results");

  // Show loading state
  btn.disabled = true;
  btn.textContent = "Analyzing…";
  area.innerHTML = `<div class="empty"><span class="spinner"></span> Running analysis…</div>`;
  $("analysis-status").textContent = "Working…";

  try {
    if (type === "pipeline") {
      const result = await api.analyzePipeline(text);
      renderPipelineResult(result);
    } else if (type === "sentiment") {
      const result = await api.analyzeSentiment(text);
      renderSentimentResult(result);
    } else if (type === "summarize") {
      const maxSentences = parseInt($("analysis-max-sentences").value, 10) || 3;
      const result = await api.analyzeSummarize(text, maxSentences);
      renderSummaryResult(result);
    } else if (type === "classify") {
      const result = await api.analyzeClassify(text);
      renderClassifyResult(result);
    }
    showToast("Analysis complete");
  } catch (err) {
    area.innerHTML = `<div class="error-text">Analysis failed: ${esc(err.message)}</div>`;
    $("analysis-status").textContent = "Error";
    showToast(err.message, true);
  } finally {
    btn.disabled = false;
    btn.textContent = "Analyze";
  }
});

// -----------------------------------------------------------------------------
// Boot
// -----------------------------------------------------------------------------

checkHealth();
refreshAll();
