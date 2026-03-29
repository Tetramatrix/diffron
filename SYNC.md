# Diffron - Sync Scripts

Scripts for synchronizing between Private and Public repositories.

---

## Repository Structure

```
Private Repo (D:\...\diffron\)          Public Repo (D:\Benutzer\github\diffron\)
├── sync-to-public.bat                  ├── commit-push.bat
├── sync-from-public.bat                └── (public files only)
├── diffron/
├── docs/
│   ├── SETUP.md         (public)
│   ├── HOOKS.md         (public)
│   ├── USAGE.md         (public)
│   ├── PLAN.md          (PRIVATE)
│   └── PYPI_RELEASE.md  (PRIVATE)
└── internal/            (PRIVATE)
```

---

## Workflow

### 1. Work in Private Repo

```bash
# Edit files in Private Repo
D:\Benutzer\Dokumente\__ [ Projects ] __\diffron\
```

### 2. Sync to Public

**Run in Private Repo:**
```
sync-to-public.bat
```

This copies all public files to `D:\Benutzer\github\diffron\`
(Excludes: `.git/`, `internal/`, `PLAN.md`, `PYPI_RELEASE.md`)

### 3. Commit and Push to GitHub

**Run in Public Repo:**
```
commit-push.bat
```

Or manually:
```bash
cd "D:\Benutzer\github\diffron"
git status
git add .
git commit -m "your message"
git push origin master
```

### 4. Get Updates from GitHub

If you made changes on GitHub or want to sync latest:

**Step 1:** Pull in Public Repo
```bash
cd "D:\Benutzer\github\diffron"
git pull origin master
```

**Step 2:** Sync to Private Repo
```
sync-from-public.bat
```

---

## Scripts

### `sync-to-public.bat`

**Location:** Private Repo (`D:\...\diffron\`)

**Purpose:** Copy changes from Private to Public repo

**Excludes:**
- `.git/`
- `internal/`
- `docs/PLAN.md`
- `docs/PYPI_RELEASE.md`
- `__pycache__/`
- `*.pyc`
- `.egg-info/`

### `sync-from-public.bat`

**Location:** Private Repo (`D:\...\diffron\`)

**Purpose:** Copy updates from Public to Private repo

**Preserves:**
- `internal/` folder
- `docs/PLAN.md`
- `docs/PYPI_RELEASE.md`

### `commit-push.bat`

**Location:** Public Repo (`D:\Benutzer\github\diffron\`)

**Purpose:** Interactive commit and push to GitHub

**Features:**
- Shows current branch
- Shows pending changes
- Prompts for commit message
- Adds, commits, and pushes

---

## Quick Reference

| Task | Command |
|------|---------|
| Sync Private → Public | Run `sync-to-public.bat` in Private |
| Sync Public → Private | Run `sync-from-public.bat` in Private |
| Commit & Push | Run `commit-push.bat` in Public |
| Manual Push | `cd Public && git add . && git commit -m "msg" && git push` |

---

## Important Rules

✅ **DO:**
- Always work in Private Repo
- Run `sync-to-public.bat` before pushing to GitHub
- Keep internal docs only in Private Repo

❌ **DON'T:**
- Never commit internal files to Public Repo
- Never push directly from Private Repo to GitHub
- Don't edit files in Public Repo (always work in Private)

---

## Troubleshooting

### "File in use" Error

Close any open files in the target directory before syncing.

### Sync Fails

1. Check that both directories exist
2. Make sure no files are open in either repo
3. Try running as Administrator

### Git Conflicts

If you get conflicts when pulling from GitHub:

```bash
cd "D:\Benutzer\github\diffron"
git pull origin master
# Resolve conflicts if any
git push origin master
# Then run sync-from-public.bat in Private
```

---

*Last updated: 2026-03-28*
