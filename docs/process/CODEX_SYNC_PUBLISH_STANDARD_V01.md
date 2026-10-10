# Codex Sync + Publish Standard V01

Status: OWNER-LOCKED STANDING BUILDER RULE
Date: 2026-10-08
Latest explicit owner workspace ruling: 2026-10-10, **DESKTOP ONLY / NO TEMP WORKTREES**
Repository: `Sekiph82/ScrubBots-Level-Factory`

## Purpose

Preserve the established GitHub implementation and audit workflow without expanding owner laptop disk use. No new process file or parallel tracking system.

## Canonical locations

- GitHub source of truth: `https://github.com/Sekiph82/ScrubBots-Level-Factory`, branch `main`.
- **ONLY permitted Codex development working directory:** `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- **No new or reused implementation worktree, clone, copied project, archive/extraction, pytest basetemp or Godot project copy under `%TEMP%` or `%LOCALAPPDATA%\Temp`.** Do not create Desktop sibling clones either.
- Existing TEMP-created historical R05/M17 worktrees are **read-only recovery sources only**, when needed to retrieve previously committed code. Do not run new builds/tests/changes there and do not delete them by circumventing an OS denial. After relevant commits are safely on GitHub main, report any retained historical footprint accurately.

## Mandatory start, established sync

1. Run only in the Desktop directory; verify exact canonical LF origin, current branch, HEAD, `git status --porcelain`, local branch/stash/worktree inventory and pending changes.
2. `git fetch --prune origin`; compare exact `main` and `origin/main`.
3. When Desktop clean and only behind, `git merge --ff-only origin/main`. When Desktop contains local changes, **do not overwrite, discard or silently reset them**. Inspect the exact paths and preserve all owner-authored bytes; do only demonstrably safe non-overlapping work in this same Desktop checkout. If required source conflicts, stop with exact path/SHA and obtain the owner's direction rather than creating another worktree.
4. For two already committed, independently scoped task commits stored only in a historical linked TEMP worktree, use that worktree **solely to read existing Git commit objects**. After verifying Desktop is safe and synchronized, apply the *exact* existing source+log commits to the Desktop checkout by targeted `git cherry-pick <implementation-SHA> <log-SHA>` in order, with no product reimplementation, no copy of entire worktree, no large duplication. An existing dirty Desktop checkout must be made safe without discarding any owner changes first; otherwise stop. If cherry-pick conflicts, `git cherry-pick --abort` only when it would not remove owner data and report exact conflict; never override owner changes. Publishing a safe commit through Desktop is required; historical TEMP remains recovery-only.
5. Use `git revert` to restore a bad **committed** change via history-preserving new Git commit, when rollback is required. If the owner instead wants an earlier GitHub commit restored, identify the precise accepted SHA and revert only the intended changes. **Never silently run `git reset --hard`, `git clean`, destructive checkout, forced push or blanket delete of uncommitted work.** This delivers the owner's GitHub recovery intention without losing unrelated changes.

## During every Codex task

- Implement/test and keep small working evidence inside the existing Desktop LF repo. Avoid writing multi-GB temporary files, extra game clones, tar archives or extracted duplicates. Run tests in bounded serial form; use a project-owned disposable test directory only if needed and only with normal, demonstrably permitted cleanup. If cleanup is denied, stop generating additional large scratch instead of bypassing policy.
- Maintain the single matching builder log, but **Codex never modifies root `TASKS.md` or `.hiveai/audits/**`**; ChatGPT is their sole writer. No second tracker.
- Protect source/palette/solver/VOID/current-game authority and other owner data. No secrets in repo, logs, APK or any remote content.

## Mandatory finish / GitHub publication

1. Test each actual product-code change once and record its exact commands/results in the builder log. **When a later task merely moves/publishes the same unchanged, previously tested commits, REUSE that original test evidence; do not repeat the test suite.** Read-only Git tree/object/diff verification is sufficient to establish code identity. Re-run only tests affected by a demonstrable product-code change, missing/corrupt evidence or an independently identified defect, and state the precise reason. Identify genuinely NOT RUN gates without falsely claiming PASS.
2. Commit implementation/tests first, builder log/evidence separately.
3. `git fetch --prune origin` and require an actual safe fast-forward ancestor relationship before publish. If remote changed, reconcile safely in the Desktop checkout by inspection; do not manufacture a clean state, recreate worktrees, rewrite accepted commits or force push.
4. Publish using normal `git push origin HEAD:main`.
5. Fetch and verify `HEAD == origin/main`, 0 ahead / 0 behind and no task-created unstaged changes.
6. Return the REAL published GitHub builder-log URL. **An implementation is not handed off as complete if it exists only on the laptop.** If a genuine safety/permission blocker prevents publication, preserve all source and report its exact cause and source SHAs.

## Independent audit

ChatGPT reads actual published LF GitHub source/tests/logs, writes strict audit criteria/verdict and updates only LF root `TASKS.md`. Implementation publication does not itself equal audit PASS or an R2 production release.

The owner-facing durable Factory Studio release remains in its existing approved Desktop Release directory, never in a disposable worktree.
