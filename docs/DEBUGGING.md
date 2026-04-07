# Debugging Guide

This guide teaches you how to debug the Task Assistant API using VS Code. It assumes you've never debugged Python before.

---

## What Is Debugging?

When your code doesn't work as expected, you have two options:

1. **Print statements** — Sprinkle `print()` calls everywhere, read the terminal output, then delete them all. Slow, messy, easy to forget one.
2. **A debugger** — Pause your running code at any line, inspect every variable, and step through the code one line at a time. Fast, clean, and far more powerful.

This guide covers option 2.

---

## Prerequisites

Before you start, make sure you have:

1. **VS Code** installed
2. **Python extension** installed — search "Python" in the Extensions sidebar (`Ctrl+Shift+X`) and install the one by Microsoft (`ms-python.python`)
3. **uv installed** — this is a global system tool (not a Python package). If `uv --version` doesn't work in your terminal, see [DEVELOPMENT.md](DEVELOPMENT.md#install-uv-one-time-setup) for install instructions.
4. **Dependencies installed** — run `uv sync` in the terminal
5. **Python interpreter selected** — VS Code should auto-detect the `.venv` folder. If it doesn't:
   - Press `Ctrl+Shift+P` to open the Command Palette
   - Type "Python: Select Interpreter"
   - Choose the interpreter inside `.venv` (it will look something like `.venv\Scripts\python.exe`)

---

## Quick Start (5-Minute Version)

If you just want to get debugging working right now:

1. Open `app/routers/tasks.py`
2. Click in the gutter (the space to the left of line number 106) on the line `tasks.append(new_task)` — a red dot appears (this is a **breakpoint**)
3. Press `F5` to start debugging (choose "Debug: FastAPI Server" if prompted)
4. The terminal shows the server starting on `http://localhost:8000`
5. Open your browser and go to `http://localhost:8000/docs`
6. Use the Swagger UI to send a POST request to create a task
7. VS Code pauses on your breakpoint — you can now see every variable in the left panel

That's it! Read on for the full explanation.

---

## Understanding the Launch Profiles

The project includes three pre-configured launch profiles in `.vscode/launch.json`. Each one is a different way to start the app with the debugger.

### Profile 1: "Debug: FastAPI Server" (recommended)

This is the one you'll use 99% of the time. It starts the API server with `--reload` enabled, so the server automatically restarts when you save a file.

- **When to use:** Normal development and debugging
- **How to start:** Press `F5` (or `Run > Start Debugging`)
- **Keyboard shortcut:** `F5`

### Profile 2: "Debug: FastAPI (no reload)"

Same as Profile 1, but without `--reload`. Use this if you run into issues where breakpoints don't get hit or the debugger disconnects unexpectedly — the `--reload` flag spawns a child process that can sometimes confuse the debugger.

- **When to use:** When breakpoints aren't working with Profile 1
- **How to start:** Click the dropdown next to the green play button in the Run and Debug sidebar and select this profile, then press `F5`

### Profile 3: "Debug: Current File"

Runs whatever Python file you currently have open in the editor. Useful for standalone scripts or quick experiments.

- **When to use:** Testing a single file in isolation (not the API server)
- **How to start:** Open the file you want to run, select this profile, then press `F5`

### Switching Between Profiles

1. Open the **Run and Debug** sidebar: `Ctrl+Shift+D`
2. At the top, there's a dropdown menu showing the current profile name
3. Click it and select the profile you want
4. Press `F5` to start

---

## How to Use Breakpoints

Breakpoints are markers that tell the debugger "pause here." When the code reaches a breakpoint, it stops so you can inspect what's happening.

### Setting a Breakpoint

- **Click** in the gutter (the narrow space to the left of line numbers) — a red dot appears
- **Keyboard:** Place your cursor on the line and press `F9`
- **Remove:** Click the red dot again, or press `F9` again

### Where to Put Breakpoints

Here are good places to set breakpoints in this project:

| File | Line | Why |
|------|------|-----|
| `app/routers/tasks.py` | `new_task = TaskResponse(...)` (line 99) | See the data that comes in when a task is created |
| `app/routers/tasks.py` | `update_data = updated_task.model_dump(...)` (line 231) | See what fields the client sent in an update request |
| `app/routers/tasks.py` | `raise HTTPException(...)` (line 136) | Catch 404 errors to see which ID was requested |
| `app/routers/tasks.py` | `results = [...]` (line 191) | See the search results before they're returned |

### Conditional Breakpoints

Sometimes you only want to pause when a specific condition is true. For example, pause only when someone creates a task with the title "test":

1. Right-click a breakpoint (the red dot)
2. Select "Edit Breakpoint..."
3. Choose "Expression" and type: `task.title == "test"`
4. The breakpoint turns yellow — it will only trigger when that condition is true

### Logpoints (Non-Stopping Breakpoints)

A logpoint logs a message to the Debug Console without pausing execution. Think of it as a `print()` statement that you don't have to add to your code.

1. Right-click in the gutter
2. Select "Add Logpoint..."
3. Type a message like: `Creating task: {task.title}`
4. The text inside `{}` gets evaluated as Python — use it to print variable values
5. A diamond shape appears instead of a circle — the code won't stop, but you'll see the message in the Debug Console

---

## Debugger Controls

Once the code pauses on a breakpoint, use these controls (they appear in the floating toolbar at the top of the editor):

| Button | Shortcut | Name | What It Does |
|--------|----------|------|-------------|
| ▶ | `F5` | **Continue** | Resume execution until the next breakpoint |
| ⤵ | `F10` | **Step Over** | Run the current line and move to the next line (doesn't go inside function calls) |
| ↓ | `F11` | **Step Into** | If the current line calls a function, jump inside that function |
| ↑ | `Shift+F11` | **Step Out** | Finish the current function and return to the caller |
| ⟲ | `Ctrl+Shift+F5` | **Restart** | Stop and restart the debugger |
| ⬛ | `Shift+F5` | **Stop** | Stop debugging |

### When to Use Each

- **Step Over (`F10`)**: Use this most of the time. It runs one line and moves to the next.
- **Step Into (`F11`)**: Use this when the current line calls a function you wrote and you want to see what happens inside it. For example, if the line calls `find_task_by_id()`, Step Into takes you inside that function.
- **Step Out (`Shift+F11`)**: Use this when you accidentally stepped into a function and want to get back to where you were.
- **Continue (`F5`)**: Use this when you've seen what you need and want to let the code run to the next breakpoint (or finish executing).

---

## Inspecting Variables

When paused on a breakpoint, you have several ways to see what's in your variables:

### 1. Variables Panel (left sidebar)

The **Variables** panel in the Run and Debug sidebar shows all variables in the current scope:

- **Locals** — Variables in the current function
- **Globals** — Module-level variables (like `tasks` and `next_id`)

Click the arrow next to a variable to expand it and see its contents (useful for objects and lists).

### 2. Hover

Hover your mouse over any variable name in the code — a tooltip shows its current value.

### 3. Watch Expressions

The **Watch** panel lets you monitor specific expressions that update every time the code pauses:

1. In the Run and Debug sidebar, find the "Watch" section
2. Click the `+` button
3. Type any Python expression, such as:
   - `len(tasks)` — How many tasks are stored
   - `task.title` — The title of the current task variable
   - `task_id` — The ID from the URL path
   - `[t.title for t in tasks]` — A list of all task titles

### 4. Debug Console

The **Debug Console** (at the bottom of VS Code, next to the Terminal) lets you type and run Python expressions live while paused:

```
>>> task.title
'Buy groceries'
>>> len(tasks)
3
>>> tasks[0].model_dump()
{'title': 'First task', 'description': '', 'completed': False, 'id': 1}
```

This is extremely powerful — you can call functions, modify variables, and test ideas without changing your code.

---

## Debugging Common Scenarios

### "My endpoint returns 404 but the task should exist"

1. Set a breakpoint at the top of `find_task_by_id` (line 131 in `tasks.py`)
2. Send the request that triggers the 404
3. When it pauses, check:
   - **`task_id`**: Is it the ID you expected?
   - **`tasks`**: Does the list actually contain a task with that ID? Expand it in the Variables panel.
   - Hover over each `task.id` in the loop to see what IDs exist

### "My task data looks wrong after creation"

1. Set a breakpoint on `new_task = TaskResponse(...)` (line 99)
2. Create a task via the Swagger UI or curl
3. When it pauses, inspect:
   - **`task`**: The raw input from the client — is it what you expected?
   - **`task.title`**, **`task.description`**: Were they stripped/validated correctly?
4. Press `F10` (Step Over) to execute the line
5. Now inspect **`new_task`** — it should have the `id` field added

### "My search isn't returning results"

1. Set a breakpoint on `query = q.lower()` (line 186)
2. Send a search request
3. Inspect **`q`** — is the query what you expected?
4. Step Over to line 191 and then Step Over again past the list comprehension
5. Inspect **`results`** — what matched? If empty, check:
   - In the Debug Console, type: `[t.title.lower() for t in tasks]`
   - Does your query actually appear in any of those titles?

---

## Debugging from the Terminal (Without VS Code)

If you prefer the terminal, Python has a built-in debugger called `pdb`. You can add this line anywhere in your code:

```python
breakpoint()  # Python pauses here when this line is reached
```

Then run the server normally:

```bash
uv run uvicorn main:app --port 8000
```

When the code hits `breakpoint()`, the terminal becomes interactive. Useful commands:

| Command | What It Does |
|---------|-------------|
| `n` | Next line (same as Step Over) |
| `s` | Step into a function |
| `c` | Continue running |
| `p variable_name` | Print a variable's value |
| `pp variable_name` | Pretty-print (better for dicts/lists) |
| `l` | Show surrounding code |
| `q` | Quit the debugger |

**Important:** Remove `breakpoint()` lines before committing your code!

---

## Debugging with Print Statements

Sometimes a quick `print()` is the fastest way to check something. With `--reload` enabled, just add the print, save, and watch the terminal. Here's a useful pattern:

```python
# Instead of just: print(task)
# Use an f-string with a label so you know WHAT you're printing:
print(f"DEBUG create_task | title={task.title!r} completed={task.completed}")
```

The `!r` adds quotes around strings so you can see whitespace issues (e.g., `' hello '` vs `'hello'`).

**Important:** Remove print statements before committing your code! They clutter the production logs.

---

## VS Code Keyboard Shortcut Cheat Sheet

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+D` | Open the Run and Debug sidebar |
| `F5` | Start debugging / Continue |
| `Shift+F5` | Stop debugging |
| `Ctrl+Shift+F5` | Restart debugging |
| `F9` | Toggle breakpoint on current line |
| `F10` | Step Over |
| `F11` | Step Into |
| `Shift+F11` | Step Out |
| `Ctrl+Shift+Y` | Open Debug Console |
| `Ctrl+\`` | Open/focus the Terminal |

---

## Troubleshooting

### "Breakpoints aren't being hit"

This is the most common issue. Try these fixes in order:

1. **Switch to the "no reload" profile** — The `--reload` flag creates a child process, and sometimes the debugger attaches to the parent instead. Use "Debug: FastAPI (no reload)" from the launch dropdown.
2. **Check that `justMyCode` is `true`** — Already set in our launch.json. This tells the debugger to only stop in YOUR code, not inside library code.
3. **Make sure the right interpreter is selected** — `Ctrl+Shift+P` > "Python: Select Interpreter" > choose the `.venv` one.
4. **Restart VS Code** — Sometimes the Python extension gets confused. Close and reopen VS Code.

### "ModuleNotFoundError when debugging"

The debugger can't find your packages. Fix:

1. Make sure you ran `uv sync` in the terminal
2. Check that VS Code is using the `.venv` interpreter (`Ctrl+Shift+P` > "Python: Select Interpreter")
3. The status bar at the bottom of VS Code should show something like `Python 3.11.x ('.venv': venv)`

### "Address already in use" when starting the debugger

Another process is using port 8000. Either:

- Stop the other process (check your terminal tabs — do you have a server running already?)
- Or change the port in the launch profile: edit `.vscode/launch.json` and change `"8000"` to `"8001"`

### The Debug Console shows an error but the server keeps running

FastAPI catches exceptions and turns them into HTTP error responses (like 404 or 422). The server doesn't crash — it returns the error to the client and keeps going. This is normal and expected.

---

## Recommended Workflow

1. **Reproduce the bug** — First, figure out exactly what request causes the problem (which endpoint, what data)
2. **Set a breakpoint** — Put it at the start of the endpoint function that handles that request
3. **Start debugging** — Press `F5`
4. **Trigger the bug** — Send the same request again (via Swagger UI, curl, or your browser)
5. **Step through** — Use `F10` to go line by line, watching variables change in the sidebar
6. **Find the mismatch** — At some point, a variable won't contain what you expect. That's your bug.
7. **Fix and verify** — Make the fix, save (the server reloads automatically), and test again
