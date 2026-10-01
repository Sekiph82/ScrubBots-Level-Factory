# MAINT-GIT-HYGIENE-C002 — Canonical Local Main Reconciliation

Document role: CHATGPT AUTHORIZED MAINTENANCE PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Canonical branch:
`main`

Canonical local project root:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Current GitHub main at prompt publication:
`7beb9976d3b2660fdea217c7f63401773d26ae87`

## Owner directive

Reconcile the canonical local repository with `origin/main` without losing any legitimate local work.

Do not create:
- any new Git branch;
- any sibling Desktop clone;
- any Desktop worktree;
- any `Scrubbots - Pixel Art Generator-*` folder;
- any temporary repository on Desktop.

Do not use:
- git reset;
- git rebase;
- git stash;
- force checkout;
- force push;
- clean;
- destructive file overwrite;
- sibling worktrees.

All work must happen only inside:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

If temporary scratch files are absolutely necessary, use only:
`%TEMP%\ScrubBots-Level-Factory\...`
and remove them before finishing.

## Step 1 — inspect before mutation

From the canonical local root, record:

- `git rev-parse --show-toplevel`
- `git remote -v`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse origin/main`
- `git status --short --branch`
- `git diff --name-status`
- `git diff --cached --name-status`
- `git ls-files --others --exclude-standard`
- `git stash list`
- `git worktree list --porcelain`
- `git rev-list --left-right --count HEAD...origin/main`

Verify:
- repository identity = `Sekiph82/ScrubBots-Level-Factory`;
- current branch = `main`;
- local root is exactly the canonical path above.

If not, STOP without modifying files.

## Step 2 — classify dirty local state

Inspect every tracked/untracked local difference.

Classify each as one of:
- legitimate owner/project work to preserve;
- generated/cache/temp output that should remain uncommitted;
- builder log/evidence that belongs inside the repository;
- accidental external/sibling-worktree residue.

Do not delete anything automatically.

If a tracked local modification contains legitimate project work:
- preserve it in-place;
- create one normal local preservation commit on `main` before integrating remote history;
- use a clear message such as:
  `chore: preserve canonical local changes before main reconciliation`.

Do not commit generated/cache/temp files merely to make status clean.

If a local untracked file is legitimate durable project evidence:
- move it only within the canonical repository to its correct tracked path;
- never move it outside the canonical project root;
- commit it in the same preservation commit if appropriate.

If a local change is ambiguous, STOP and report it rather than guessing.

## Step 3 — reconcile with origin/main

Run `git fetch origin --prune`.

Recompute ahead/behind.

### Case A — local main has no unique commits

If local `main` is only behind and dirty changes have been safely preserved or are non-conflicting untracked/generated files:

- fast-forward with:
  `git merge --ff-only origin/main`

### Case B — local main has legitimate preservation commit(s)

If local main and origin/main diverge after the preservation commit:

- perform a normal non-destructive merge:
  `git merge --no-ff origin/main`

Resolve conflicts by preserving:
- current GitHub governance;
- current root `TASKS.md`;
- current owner-approved M09-004 policy;
- legitimate local owner/project work.

Do not restore obsolete H!veAI control-plane files.
Do not create a second tracker.
Do not edit task-state fields in `TASKS.md`.

Never rebase/reset to solve divergence.

## Step 4 — publish reconciliation

After a clean successful merge/reconciliation:

- run `git diff --check`;
- run focused governance/import smoke if affected;
- run `python -m compileall -q src tests` when available;
- run full `python -m pytest -q -p no:cacheprovider` if repository state permits;
- run relevant Godot headless smoke if available.

Commit only if reconciliation produced an actual merge or preservation commit.

Push `main` normally.

Then fetch again and prove:
- local HEAD == `origin/main`;
- ahead/behind = 0/0;
- current branch = main;
- only one remote branch exists: main;
- no new Desktop sibling project folder/worktree was created.

## Step 5 — M09-004 readiness check

After local/main reconciliation, verify these exist on the synchronized local main:

- `docs/policies/SB_LF09_004_ANALYTICS_DATA_POLICY_V01.md`
- `.hiveai/audit-criteria/SB-LF09-004-C001_TELEMETRY_CALIBRATION_POLICY_AUDIT_CRITERIA.md`
- `.hiveai/prompts/SB-LF09-004-C001_TELEMETRY_CALIBRATION_POLICY_PROMPT.md`
- root `TASKS.md` showing SB-LF09-004 as CODEX authorized.

Do **not** implement SB-LF09-004 in this maintenance task.

## Builder log

Create inside the canonical repository before making reconciliation changes:

`.hiveai/codex-logs/MAINT-GIT-HYGIENE-C002_CANONICAL_LOCAL_MAIN_RECONCILIATION_CODEX_LOG.md`

The log must include:
- exact starting local HEAD;
- exact origin/main;
- dirty file list and classification;
- whether a preservation commit was required;
- merge/fast-forward details;
- every conflict and resolution if any;
- verification commands/results;
- final local HEAD;
- final origin/main;
- 0/0 ahead/behind proof;
- proof no new Desktop sibling clone/worktree was created;
- explicit statement whether SB-LF09-004 is now ready to resume.

## Final response

Return only:

1. full GitHub URL of the completed maintenance log;
2. `LOCAL_MAIN: SYNCHRONIZED` or `LOCAL_MAIN: BLOCKED`;
3. `SB-LF09-004: READY_TO_RESUME` or `SB-LF09-004: NOT_READY`.

Do not start SB-LF09-004 implementation in the same run.
