# MAINT-GIT-HYGIENE-C002 — Canonical Local Main Reconciliation

Document role: CODEX BUILDER LOG

## Session start and authority

- Starting timestamp: 2026-10-01 (Europe/Istanbul; exact command evidence is recorded below).
- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Repository identity: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical branch: `main`.
- Authoritative prompt: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/MAINT-GIT-HYGIENE-C002_CANONICAL_LOCAL_MAIN_RECONCILIATION_PROMPT.md`.
- Prompt-published `origin/main`: `7beb9976d3b2660fdea217c7f63401773d26ae87`.
- No new branch, Desktop clone, Desktop worktree, temporary Desktop repository, or `Scrubbots - Pixel Art Generator-*` folder was created by this session.

## Exact starting inspection

- `git rev-parse --show-toplevel` => `C:/Users/sekip/Desktop/Scrubbots - Pixel Art Generator`.
- `git remote -v` => `origin https://github.com/Sekiph82/ScrubBots-Level-Factory.git` for fetch and push.
- `git branch --show-current` => `main`.
- Starting local HEAD => `a6ac0141dc1c816f6820bacae76849cf2c9c7611`.
- Starting `origin/main` => `7beb9976d3b2660fdea217c7f63401773d26ae87`.
- Starting divergence => `0 67` from `git rev-list --left-right --count HEAD...origin/main` (local-only, remote-only).
- Starting tracked modifications: `TASKS.md`; `src/scrubbots_pixel_factory/__init__.py`.
- Starting staged modifications: none.
- Starting stashes: 18 pre-existing stashes; none created or modified by this session.
- Starting registered worktrees: canonical `main`; six existing temporary detached worktrees under `%LOCALAPPDATA%\Temp\ScrubBots-Level-Factory`; four pre-existing prunable Desktop worktree registrations. None was created or removed by this session.

## Dirty-state classification

### Preserve in one normal local preservation commit

- Tracked local project/process changes: `TASKS.md` and `src/scrubbots_pixel_factory/__init__.py`. These are preserved in the local commit history before current GitHub history is integrated; the current `origin/main` tracker remains authoritative after reconciliation.
- Durable `.hiveai` evidence and process records: all 35 untracked files under `.hiveai/audit-criteria`, `.hiveai/audits`, `.hiveai/codex-logs`, and `.hiveai/prompts`, including the prior blocked `SB-LF09-004` builder log. Most are byte-identical to `origin/main`; differing historical records remain recoverable in the preservation commit and current GitHub versions take precedence in the reconciled tree.
- Project code/test candidates: `src/scrubbots_pixel_factory/m08_batch.py` and `tests/unit/test_m08_batch.py`. Both are legitimate prior-cycle local project files but differ from the fetched GitHub versions; they are preserved in the local commit and the current `origin/main` versions are authoritative during merge resolution.

### Leave uncommitted and do not delete

- 51 generated Godot `.uid` files under `level_factory/scripts` and `level_factory/tests`; they are generated/cache-like outputs and are not included in the preservation commit.
- Three pre-existing nested Desktop worktree directories: `Scrubbots - Pixel Art Generator-SB-LF04-001`, `Scrubbots - Pixel Art Generator-SB-LF04-001-R01`, and `Scrubbots - Pixel Art Generator-SB-LF04-001-R01-VERIFY`. They contain `.git` link files into the canonical repository’s worktree administration and are retained because the prompt forbids automatic deletion.

No ambiguous file was guessed into deletion. No legacy tracker/control-plane file was created or restored.

## Planned reconciliation

The dirty tracked changes and durable project/evidence files will be committed once with message:
`chore: preserve canonical local changes before main reconciliation`

After that preservation commit, `origin/main` will be fetched with prune and integrated through a normal non-destructive merge. Any conflict will be resolved in favor of current GitHub governance/current root `TASKS.md` and current GitHub versions, while the preservation commit retains the pre-existing local bytes. Generated `.uid` files and nested worktree residue will remain outside the commit.

## Verification to complete

- Re-run `git diff --check`.
- Run focused governance/import smoke and available Python compile/test checks.
- Push `main` normally only after reconciliation is clean.
- Fetch again and prove local HEAD equals `origin/main`, ahead/behind is `0/0`, branch is `main`, only remote branch is `main`, and no new Desktop folder/worktree was created.
- Confirm the M09-004 policy, criteria, prompt, and authorized root `TASKS.md` are present on synchronized local `main`.
- Do not implement SB-LF09-004 during this maintenance task.

## Verification results and tracker readiness

- `git diff --check` after the merge produced no working-tree errors.
- `python -m compileall -q src tests` passed.
- Full `python -m pytest -q -p no:cacheprovider` completed with `1101 passed, 2 skipped, 1 failed` in `365.56s`.
- The single failure was `tests/unit/test_sb_lf00_007_governance_authority.py::test_project_status_and_active_task_contract_are_exact`: the current GitHub `TASKS.md` declares `Current Sprint: MAINT-GIT-HYGIENE-C002` while its current task is `SB-LF09-004`, so the governance test correctly rejected the sprint/task mismatch.
- The two skips were the existing unavailable canonical-ScrubBots bridge capabilities; no provider or network workaround was used.
- `TASKS.md` task-state fields were not edited to hide or bypass this failure.
- Because the authoritative tracker currently reflects the maintenance sprint rather than an M09-004 sprint, `SB-LF09-004` is **NOT_READY** to resume from this maintenance run.
- `godot --headless --path level_factory --editor --quit` passed with Godot `4.7.2.stable.official.ed1daf0bf` and exit code 0.
- Readiness files were present: the M09-004 policy, audit criteria, prompt, and root `TASKS.md`.
- The remote branch listing contains only `origin/main` (plus the symbolic `origin/HEAD`); no new branch was created.

## Merge and publication records

- Preservation commit: `e38cdedb9d5c371eef788016c86ea82b08857a48`.
- Refreshed remote before merge: `origin/main=9faedf08c53e8d54298ddffc97f08e1b3754b7a4`.
- Normal merge commit: `2cac282aff8343e6105a35dc6dabe71a03867baf`.
- Merge conflicts: 12; all were resolved by selecting current GitHub (`origin/main`) content. Local versions remain recoverable from the preservation commit.
- The merge staged one pre-existing remote whitespace warning in `.hiveai/codex-logs/SB-LF08-C001_MASTER_BATCH_CODEX_LOG.md`; the immutable remote record was not edited. Post-merge working-tree `git diff --check` was clean.
- Verification-log append commit: pending before publication.
- Push and final equality proof: pending before publication.
