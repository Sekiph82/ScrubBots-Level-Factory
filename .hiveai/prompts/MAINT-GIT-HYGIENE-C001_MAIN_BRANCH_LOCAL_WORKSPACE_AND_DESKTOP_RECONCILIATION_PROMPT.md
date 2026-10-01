# MAINT-GIT-HYGIENE-C001 — Main Branch, Local Workspace & Desktop Reconciliation

Document role: CHATGPT AUTHORIZED MAINTENANCE PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Canonical branch:
`main`

Canonical local project root:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Desktop sibling to inspect, but **not delete automatically**:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator-SB-LF07-R04`

## Owner directive

The Desktop must contain only the canonical project directory for this repository.

Do not create permanent sibling clones, worktrees, remediation directories, milestone directories, or temporary repositories on the Desktop.

Examples that are forbidden:
- `Scrubbots - Pixel Art Generator-SB-*`
- `Scrubbots - Pixel Art Generator-R*`
- `Scrubbots - Pixel Art Generator-M*`
- `Scrubbots - Pixel Art Generator-Codex*`
- any other sibling copy/worktree of this repository.

If temporary Git isolation is genuinely required in future, use only:
`%TEMP%\ScrubBots-Level-Factory\...`
and remove the temporary worktree when the operation is complete.

Do not use the Desktop for generated prompts, logs, audits, patch files, temporary clones, scratch files or evidence. Durable project evidence belongs inside the canonical repository.

## Branch-creation policy

Do not create a Git branch unless:
1. the owner explicitly asks for one, or
2. an owner-approved authoritative prompt explicitly authorizes a named temporary branch.

Normal Codex work for this repository is directly on `main`.

Before any future branch/worktree creation, the builder log must record:
- branch/worktree name;
- exact reason;
- source SHA;
- intended lifetime;
- cleanup condition.

No silent branch creation.

## Initial GitHub evidence to independently re-check

At prompt authoring time:

- `main`: `a6ac0141dc1c816f6820bacae76849cf2c9c7611` before this maintenance prompt publication.
- `hiveai-control-plane-v1-rebased`: tip `182c166d16723ef1278af8d9c6b88e5fbbf5edf5`; already an ancestor of main, ahead 0.
- `__no_use__`: tip `19242be7f42a6e743965a00369263b80471cad2e`; already an ancestor of main, ahead 0.
- `hiveai-control-plane-v1`: tip `3c41508cdbdc5338f805735b33d49b7e0065d63a`; one unique historical commit relative to main.

The unique historical commit is:
`chore: standardize H!veAI project control plane`
dated 2026-09-08T15:19:55Z.

The rebased control-plane tip is:
`chore: adopt H!veAI control plane without overriding governance`
dated 2026-09-08T15:48:13Z.

The `__no_use__` tip is:
`docs: add LF CP requirement mapping ledger`
dated 2026-09-14T16:48:53Z.

Re-fetch current remote refs before acting because main may have advanced.

## Critical governance rule

Current `AGENTS.md`, `GOVERNANCE.md` and root `TASKS.md` are authoritative.

Do **not** revive the obsolete control-plane model from `hiveai-control-plane-v1`.

In particular, the final main tree must **not** reintroduce these legacy live-state files merely because they existed on the historical branch:

- `.hiveai/EVENTS.jsonl`
- `.hiveai/PROJECT.json`
- `.hiveai/RULES.md`
- `.hiveai/STATE.json`
- `.hiveai/HANDOFF.md`
- `.hiveai/PROJECT_DASHBOARD.md`
- lowercase root `tasks.md`

Root `TASKS.md` remains the sole live tracker.

Any useful non-obsolete instruction from the historical branch may be manually ported only when compatible with current governance.

## Task A — inspect the extra Desktop folder

Without modifying or deleting it, inspect:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator-SB-LF07-R04`

Determine exactly what it is:
- registered Git worktree, clone, ordinary folder or stale copy;
- current branch/detached HEAD;
- HEAD SHA and origin;
- tracked modifications;
- untracked files;
- ignored files that may contain project evidence;
- commits reachable from it but not from current `origin/main`;
- files/content not present in the canonical project root or GitHub main.

Use:
- `git worktree list --porcelain` from the canonical repository;
- `git status --short --branch`;
- `git rev-parse --show-toplevel`;
- `git rev-parse HEAD`;
- `git remote -v`;
- `git log origin/main..HEAD`;
- `git diff origin/main...HEAD`;
- `git ls-files --others --exclude-standard`;
plus safe read-only inspection as needed.

Do not delete, move, overwrite or merge files from this folder merely because it exists.

Classify it at the end as exactly one of:
- `SAFE_TO_DELETE`
- `NOT_SAFE_TO_DELETE`

`SAFE_TO_DELETE` requires proof that it contains no unique required commit, tracked change, untracked evidence or owner file not already preserved in canonical main/canonical local root.

If it is a registered worktree, report the exact cleanup command the owner can use after deleting/approving removal, but do not execute destructive removal in this task.

## Task B — reconcile canonical local root with GitHub main

Perform all repository work only inside:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Never create another Desktop project copy.

1. Verify this exact folder is the canonical repository and origin is `Sekiph82/ScrubBots-Level-Factory`.
2. Fetch all refs and prune stale remote-tracking refs safely.
3. Inspect branch, HEAD, status, ahead/behind, stashes and registered worktrees.
4. Preserve all legitimate owner work. Never reset, rebase, force checkout, discard, auto-stash or overwrite owner changes.
5. If local main is behind origin/main and otherwise safe, fast-forward it.
6. If local main contains legitimate commits not on origin/main, inspect them and integrate them into main rather than abandoning them.
7. If local main and origin/main diverged, reconcile using a normal non-destructive merge on `main`; never rebase or reset.
8. Never stage generated/temp/cache/secrets merely to make the tree clean.
9. At completion, canonical local `main` and `origin/main` must point to the same final commit, except explicitly preserved uncommitted owner files which must be reported.

## Task C — reconcile all remote branches into main history

Remote branches currently expected:
- `main`
- `hiveai-control-plane-v1-rebased`
- `hiveai-control-plane-v1`
- `__no_use__`

Re-list them first.

### C1. hiveai-control-plane-v1-rebased

It was already fully behind/contained in main at prompt authoring time.

Verify:
`git merge-base --is-ancestor origin/hiveai-control-plane-v1-rebased origin/main`

If true, do not create a meaningless merge commit.

Mark it in the log as:
`SAFE_TO_DELETE_REMOTE_BRANCH`.

### C2. __no_use__

It was already fully behind/contained in main at prompt authoring time.

Verify:
`git merge-base --is-ancestor origin/__no_use__ origin/main`

If true, do not create a meaningless merge commit.

Mark it:
`SAFE_TO_DELETE_REMOTE_BRANCH`.

### C3. hiveai-control-plane-v1

This branch has one historical unique commit and must be reconciled carefully.

Do **not** cherry-pick it blindly.

Required procedure:

1. Inspect its unique commit and compare every changed path to current main.
2. Identify whether any useful rule/content is genuinely absent from current main.
3. Port only non-obsolete compatible content if needed.
4. Merge the branch history into `main` with a normal merge commit so its tip becomes an ancestor of main.
5. During merge resolution, preserve current main governance.
6. Explicitly remove/reject legacy control-plane files listed above if the merge tries to add them.
7. Preserve current `AGENTS.md`, `GOVERNANCE.md`, `TASKS.md` semantics.
8. Never restore lowercase `tasks.md`.
9. Run `git merge-base --is-ancestor origin/hiveai-control-plane-v1 HEAD` after the merge.

The final main tree must contain all still-valid project content while the obsolete control-plane architecture remains retired.

Do not delete the remote branch in this task. Once ancestry is proven, mark:
`SAFE_TO_DELETE_REMOTE_BRANCH`.

## Task D — make Desktop/branch hygiene permanent

Update current governance/instructions on main so future Codex runs cannot repeat this problem.

At minimum update `AGENTS.md` and `GOVERNANCE.md` with explicit rules:

- the only persistent local root is
  `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`;
- never create sibling Desktop clones/worktrees/copies;
- temporary worktrees, if explicitly authorized, live only under
  `%TEMP%\ScrubBots-Level-Factory\...`;
- normal work occurs on `main`;
- no branch may be created without explicit owner/prompt authorization;
- any authorized temporary branch/worktree must be logged and removed after integration;
- durable project artifacts are committed inside the canonical repository, never left on Desktop outside the project root.

Do not edit `TASKS.md` task state for this maintenance operation.

## Task E — verification

After reconciliation:

1. `git status --short --branch`
2. `git fetch origin --prune`
3. prove local HEAD == `origin/main`;
4. prove ahead/behind main = 0/0;
5. prove all three non-main remote branch tips are ancestors of final main;
6. list remote branches and their tips;
7. prove no additional Desktop sibling clone/worktree was created by this task;
8. run `git diff --check`;
9. run targeted governance tests if any;
10. run full repository `python -m pytest -q -p no:cacheprovider` if repository state permits;
11. `python -m compileall -q src tests`;
12. relevant Godot headless boot/smoke;
13. verify root `TASKS.md` task state was not changed.

## Builder log

Create before making repository changes:

`.hiveai/codex-logs/MAINT-GIT-HYGIENE-C001_MAIN_BRANCH_LOCAL_WORKSPACE_AND_DESKTOP_RECONCILIATION_CODEX_LOG.md`

The log must include:

- exact starting local and remote SHAs;
- branch creation/history findings;
- what each extra remote branch was for;
- complete unique-commit assessment for `hiveai-control-plane-v1`;
- exact merge/reconciliation steps;
- whether legacy control-plane files were rejected from final main;
- canonical local/main synchronization evidence;
- extra Desktop folder classification and proof;
- whether it is safe for the owner to delete that folder;
- remote branch safe-to-delete status;
- AGENTS/GOVERNANCE hygiene changes;
- tests and verification;
- implementation and log commit SHAs;
- final local HEAD == origin/main proof.

## Final response

Do not dump a long report in chat.

Return only:
1. the full GitHub URL of the completed builder log;
2. one line:
   `DESKTOP_COPY: SAFE_TO_DELETE`
   or
   `DESKTOP_COPY: NOT_SAFE_TO_DELETE`;
3. one line listing remote branches safe to delete, for example:
   `REMOTE_BRANCHES_SAFE_TO_DELETE: hiveai-control-plane-v1-rebased, hiveai-control-plane-v1, __no_use__`

Do not delete the Desktop copy or remote branches automatically.
