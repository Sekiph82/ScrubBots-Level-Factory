# SB-LF07-007-C001 — Bounded Mutation Attempts
Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Scope: `SB-LF07-007-C001`, immediately after published SB-LF07-006.
- Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting HEAD and `origin/main`: `0757c2d97f8b8e87b30450de3a4a0339eb65fe85`.
- Initial status: equal to origin; pre-existing untracked LF04 worktree directories and Godot UID files preserved and not staged.

## Required records and contracts read before edits

- Live `TASKS.md`, M07 master prompt/index, this task prompt and strict criteria.
- `AGENTS.md`, `GOVERNANCE.md`, and accepted SB-LF07-001..006 implementation/log evidence.
- M03 deterministic budget/UNKNOWN_BOUND semantics and M07-005 provenance contract.

This log was created before SB-LF07-007 product implementation and tests.

## Planned implementation boundary

- Make attempt budgets positive, finite, versioned and deterministic, with no calls after the declared limit.
- Bind ordinals/effective seeds to provenance; report explicit EXHAUSTED outcome distinct from UNSOLVABLE and success.
- Keep wall-clock timeout out of canonical budget identity and require the M07-004 evidence chain per applied attempt.

## Chronological implementation and verification

- Extended `AttemptRecord`/`run_bounded_mutations()` so every applied attempt carries a canonical `MutationProvenance` with its deterministic ordinal and evidence digest.
- Added `tests/unit/test_sb_lf07_007_attempts.py` for success-before-limit, exact-limit exhaustion, one/invalid budgets, deterministic seed derivation, ordinal/provenance recording and no post-limit calls.
- Focused command for M07-001..007 -> `24 passed`.
- Full command: `python -m pytest -q -p no:cacheprovider` -> `1009 passed, 2 skipped` in `306.99s`. Skips remain the pre-existing explicitly capability-gated canonical ScrubBots checkout/bridge skips.
- `python -m compileall -q src tests` -> exit code 0.
- `godot_console.exe --headless --editor --path level_factory --quit` (Godot 4.7.2) -> exit code 0.
- `git diff --check` -> exit code 0. `git diff --exit-code -- TASKS.md` -> exit code 0.
- Attempt budgets are finite canonical contracts (`1..10000`), effective seeds are pure `(base_seed, ordinal)` derivations, and wall-clock timing is absent from budget/provenance identity.

## Publication checkpoints

Implementation and terminal log-only publication checkpoints are recorded below. Root `TASKS.md`, prompts, audits, prior logs, and owner-local untracked files remain unchanged.

- Implementation/evidence commit: `88b630ff2cbb260c58fc998ddd9a0b249502e021` (`Add M07-007 bounded mutation attempts`).
- Implementation push succeeded; local `HEAD` and `origin/main` were both `88b630ff2cbb260c58fc998ddd9a0b249502e021` immediately afterward.
- Terminal log-only publication commit is the final SB-LF07-007 checkpoint.
