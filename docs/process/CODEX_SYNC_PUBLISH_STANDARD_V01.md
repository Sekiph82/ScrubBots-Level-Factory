# Codex Sync + Publish Standard V01

Status: OWNER-LOCKED STANDING BUILDER RULE  
Date: 2026-10-08  
Repository: `Sekiph82/ScrubBots-Level-Factory`

## Purpose

Remove repeated manual synchronization work while preserving owner-local Desktop work.

GitHub `origin/main` is the implementation authority. The persistent Desktop checkout is an owner workspace and does not need to be made clean/current before every builder task.

## Canonical locations

- GitHub authority: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
- Persistent owner checkout: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
- Authorized task execution worktrees when the persistent checkout is unsafe: `%TEMP%\ScrubBots-Level-Factory\<TASK-ID>`

Never create a sibling Desktop clone/worktree/copy.

## Mandatory task start

Every Codex implementation/remediation/continuation/maintenance task begins with:

1. Verify the persistent root points to the canonical repository and canonical origin.
2. `git fetch --prune origin`.
3. Inspect branch, HEAD, status, ahead/behind, stashes, and worktrees.
4. If the persistent checkout is clean and only behind, fast-forward with `git merge --ff-only origin/main`.
5. If it is dirty, divergent, stale with owner work, or otherwise unsafe, do not attempt to reconcile it. Preserve it byte-for-byte and immediately create/reuse a task-specific clean detached worktree under `%TEMP%\ScrubBots-Level-Factory\<TASK-ID>` from exact current `origin/main`.
6. Require the execution worktree to be clean and exact-current before product edits.

No reset, rebase, auto-stash, clean, force checkout, restore/discard, or force push.

The owner does not need to manually synchronize the persistent Desktop checkout for builder work.

## During the task

- Work only in the selected execution authority.
- Create the matching builder log before implementation edits.
- Keep implementation commits separate from builder-log/evidence commits where practical.
- Never edit root `TASKS.md` or `.hiveai/audits/**`.
- Never record secrets.

## Mandatory task finish and automatic publication

A builder task is not handed back while its completed local commits exist only locally.

After implementation/tests:

1. Commit the authorized implementation/test changes.
2. Commit the builder log/evidence separately.
3. `git fetch --prune origin`.
4. Require current `origin/main` to remain an ancestor of the local task HEAD. If not, STOP. Do not rebase/reset/force/cherry-pick automatically.
5. Push with normal fast-forward only:
   `git push origin HEAD:main`
6. `git fetch --prune origin`.
7. Require:
   - `HEAD == origin/main`;
   - 0 ahead / 0 behind;
   - clean execution worktree.
8. Return the GitHub builder-log URL.

If GitHub returns a transient server-side error such as HTTP/Internal Server Error, preserve the existing commits and retry the same normal push up to three times. Before every retry, fetch/prune and recheck fast-forward ancestry. Never regenerate or rewrite good commits merely because the remote returned a transient error.

If publication remains blocked, report exact local HEAD, exact `origin/main`, ahead/behind, exact error and request ID if present. Preserve the task worktree and commits.

## Persistent Desktop checkout

Successful task publication does not authorize rewriting the dirty persistent Desktop checkout.

The persistent checkout may remain behind GitHub while owner-local work exists. Future builder tasks continue from exact `origin/main` in clean TEMP authority when necessary.

Owner-facing durable application runtime is a separate deployment concern and must never point at a disposable task TEMP worktree.
