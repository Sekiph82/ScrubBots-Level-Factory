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
