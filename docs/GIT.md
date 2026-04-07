# Git Guide

Git tracks changes to your code over time. Think of it as an unlimited undo system that also lets multiple people work on the same project without overwriting each other's work.

---

## Key Concepts

| Concept | What It Means |
|---------|---------------|
| **Repository (repo)** | Your project folder, tracked by Git. The `.git` folder inside it stores all history. |
| **Commit** | A snapshot of your code at a point in time, with a message describing what changed. |
| **Branch** | A separate line of development. You work on a branch, then merge it back into `main` when done. |
| **Staging area** | A holding area for changes you want to include in your next commit. You "stage" files before committing. |
| **Remote** | The copy of your repo on GitHub (or another server). Your local copy and the remote stay in sync via push/pull. |
| **Pull Request (PR)** | A request to merge your branch into `main`. Your team reviews the changes before merging. |

---

## First-Time Setup

```bash
# Tell Git who you are (one-time setup, run once per machine)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Daily Workflow

This is the workflow you'll follow for every change you make:

```
  main branch          your feature branch
  ──────────┐
            │  1. git checkout -b feature/add-priority
            ├──────────────────────┐
            │                      │  2. Make code changes
            │                      │  3. git add + git commit
            │                      │  4. git push
            │                      │  5. Open a Pull Request on GitHub
            │  6. PR is reviewed   │
            │  7. PR is merged ◄───┘
            │
  ──────────▼
```

### Step by Step

```bash
# 1. Make sure you're on the main branch and up to date
git checkout main
git pull origin main

# 2. Create a new branch for your work
#    Name it something descriptive: feature/add-priority, fix/search-bug, etc.
git checkout -b feature/add-priority

# 3. Make your code changes in VS Code (edit files, save them)

# 4. See what you changed
git status                    # Shows which files were modified
git diff                      # Shows the actual line-by-line changes

# 5. Stage the files you want to commit
git add app/models.py         # Stage a specific file
git add app/routers/tasks.py  # Stage another specific file
# Or stage everything at once: git add .
# (Use with caution — run git status first to make sure you're not adding junk files)

# 6. Commit with a descriptive message
git commit -m "Add priority field to task model"

# 7. Push your branch to GitHub
git push origin feature/add-priority
#   The first time, Git may suggest:
#   git push --set-upstream origin feature/add-priority
#   That's fine — run that command instead. After that, "git push" is enough.

# 8. Go to GitHub and create a Pull Request
#    GitHub usually shows a banner:
#    "feature/add-priority had recent pushes — Compare & pull request"
#    Click it, write a description, and submit the PR.
```

---

## Common Git Commands Reference

### Checking Status

```bash
git status                    # What files have changed?
git log --oneline -10         # Last 10 commits in short format
git diff                      # What changed (in files you haven't staged yet)?
git diff --staged             # What's about to be committed?
```

### Branching

```bash
git branch                    # List all local branches (* marks the current one)
git checkout main             # Switch to the main branch
git checkout -b new-branch    # Create AND switch to a new branch
git branch -d old-branch      # Delete a branch you're done with
```

### Syncing with GitHub

```bash
git pull origin main          # Download and apply changes from GitHub
git push origin branch-name   # Upload your branch to GitHub
```

### Undoing Things

```bash
git checkout -- filename      # Discard changes to a file (revert to last commit)
git reset HEAD filename       # Unstage a file (undo "git add", keep the changes)
git commit --amend            # Edit your last commit message (only before pushing!)
```

---

## Resolving Merge Conflicts

Sometimes Git can't automatically combine your changes with someone else's. This happens when two people edit the same lines in the same file.

When you see a merge conflict, the file will contain markers like this:

```
<<<<<<< HEAD
your version of the code
=======
their version of the code
>>>>>>> main
```

### How to Fix It

1. **Open the file in VS Code** — it highlights the conflicts and shows buttons: "Accept Current Change", "Accept Incoming Change", "Accept Both Changes"
2. **Choose the correct version** — or manually edit to combine both
3. **Remove the marker lines** — delete the `<<<<<<<`, `=======`, and `>>>>>>>` lines
4. **Save the file**
5. **Stage and commit:**

```bash
git add the-conflicted-file.py
git commit -m "Resolve merge conflict in the-conflicted-file.py"
```

---

## Tips for Beginners

- **Commit often, commit small.** One commit per logical change. "Add priority field" and "Fix search bug" should be separate commits, not one big one.
- **Write meaningful commit messages.** Bad: `"fix bug"`. Good: `"Fix search returning results for deleted tasks"`.
- **Pull before you push.** Always `git pull origin main` before starting new work to avoid conflicts.
- **Never commit secrets.** API keys, passwords, `.env` files — these should be in `.gitignore`.
- **Don't panic.** Git almost never truly loses data. If something goes wrong, ask for help before running destructive commands like `git reset --hard`.
- **Use `git status` constantly.** It's your best friend. Run it before staging, before committing, and before pushing.

---

## Cheat Sheet

```
git checkout main             →  Go to the main branch
git pull origin main          →  Get the latest changes
git checkout -b my-branch     →  Start a new branch
(make your changes)
git status                    →  See what changed
git add file.py               →  Stage a file
git commit -m "message"       →  Save a snapshot
git push origin my-branch     →  Upload to GitHub
(open a Pull Request on GitHub)
```
