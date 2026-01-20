# GitHub Basics

This document gives a **minimal, practical introduction** to using GitHub for collaboration.

## What GitHub Is (in one sentence)

GitHub hosts Git repositories so multiple people can work on the same codebase safely.


## Repository Basics

* **Repository (repo)**: The project (code + history)
* **Working tree**: Your local files
* **Remote**: The copy on GitHub (usually called `origin`)


## `.gitignore`

`.gitignore` tells Git which files **should NOT be tracked**.

Typical examples:

* Build output (`dist/`, `build/`)
* Virtual environments (`venv/`, `.env`)
* IDE files (`.idea/`, `.vscode/`)
* Secrets (`.env`, `config.local.json`)

Example:

```gitignore
__pycache__/
venv/
.env
.idea/
*.log
```

**Rule:** If it can be regenerated or contains secrets → ignore it.


## Basic Workflow (Most Important Part)

### 1. Pull (before you start)

Always get the latest changes first:

```bash
git pull
```

Do this:

* When you start working
* Before committing


### 2. Make Changes

Edit code, add files, fix bugs, etc.

Check status:

```bash
git status
```

### 3. Commit (save a snapshot)

A **commit** is a logical, named checkpoint.

Steps:

```bash
git add .
git commit -m "Short, clear description"
```

**When to commit:**

* One logical change
* Code compiles / tests pass
* Before switching tasks

**Good commit messages:**

* `Fix login validation`
* `Add user profile endpoint`

**Bad:**

* `stuff`
* `updates`


### 4. Push (share your work)

Upload commits to GitHub:

```bash
git push
```

Do this:

* When your work is ready to share
* Before stopping for the day


## Pulling vs Pushing (Common Mistake)

* **Pull** → Get others' changes
* **Push** → Send your changes

If push fails:

```bash
git pull --rebase
git push
```


## Branches (Light Intro)

* `main` / `master` = stable code
* Feature work should use branches

Create a branch:

```bash
git checkout -b feature-name
```

Merge via GitHub Pull Request.


## Golden Rules

* Pull before you code
* Commit often, but meaningfully
* Never commit secrets
* Read `git status` when unsure


## Help Commands

```bash
git status
git log
git diff
git branch
```

