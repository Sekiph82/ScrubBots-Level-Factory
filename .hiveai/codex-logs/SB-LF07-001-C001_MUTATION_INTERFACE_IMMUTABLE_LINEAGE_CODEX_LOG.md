# SB-LF07-001-C001 — Mutation Interface / Immutable Lineage
Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Scope: `SB-LF07-001-C001` as the first task in the authorized sequential M07 batch.
- Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting HEAD after non-destructive synchronization: `829ca9298ac82b0a27e59f4329cc58b36ab14420`.
- `origin/main` at start: `829ca9298ac82b0a27e59f4329cc58b36ab14420`; local branch equal to origin.
- Initial status: pre-existing untracked owner-local Godot UID files and three pre-existing LF04 worktree directories; preserved and not staged.
- Repository identity, branch, origin, status, stashes and worktrees were checked. No sibling repository was used.

## Required records and contracts read before edits

- Root `TASKS.md`, with M07 active and the instruction not to edit the tracker.
- `AGENTS.md` and `GOVERNANCE.md`.
- Authoritative master prompt URL: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF07-001-010-C001_MASTER_BATCH_IMPLEMENTATION_PROMPT.md`.
- `.hiveai/prompts/SB-LF07-001-010-C001_IMPLEMENTATION_AND_AUDIT_INDEX.md`.
- `.hiveai/prompts/SB-LF07-001-C001_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_PROMPT.md`.
- `.hiveai/audit-criteria/SB-LF07-001-C001_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_AUDIT_CRITERIA.md`.
- Accepted M03/M04/M05/M06 contracts and the Palette V3 strict-audit boundary named by the M07 criteria.

This log was created before product implementation, tests, documentation, or governance edits.

## Planned implementation boundary

- Add only the versioned immutable mutation request/result and parent-to-child lineage substrate plus adversarial tests.
- Keep hardening/easing policy, revalidation, targeting, attempt budgets, efficiency comparison, owner-source gate, and regression suite for their ordered tasks.
- Preserve canonical gameplay authority as an external exact-source boundary; do not clone gameplay mechanics into Python.
- Keep identity digests deterministic and free of timestamps, paths, and wall-clock data.

## Chronological implementation and verification

- Added `src/scrubbots_pixel_factory/mutation.py` with the closed versioned mutation request/result model, immutable candidate payloads, exact parent/LevelData/source/art identity binding, deterministic request/state/lineage digests, closed dispositions, read-only operator registry, and fail-closed `MutationEngine`.
- Added `tests/unit/test_sb_lf07_001_mutation_interface.py` covering unknown operators, deep aliasing/parent non-mutation, deterministic replay, stale identity, authority/intent drift, and identity metadata exclusion.
- Exported the M07 substrate through `src/scrubbots_pixel_factory/__init__.py`.
- Used the exact accepted current-main ScrubBots authority SHA `edf672f61989d28fd1931917ab49b2d64cc416d6` only as a read-only external contract identity. No local main-game checkout was selected or mutated, and no gameplay mechanics were cloned into Python.
- First focused command: `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_001_mutation_interface.py` -> `4 passed`.
- First required full gate: `python -m pytest -q -p no:cacheprovider` -> `988 passed, 2 skipped, 1 failed`. The failure was the pre-existing governance assertion for superseded `MAINT-PALETTE-V3-001`; live `TASKS.md` authorizes `SB-LF07-001` and contains one active `~` row. No test was skipped or hidden.
- Corrected only `tests/unit/test_sb_lf00_007_governance_authority.py` to assert the live M07 task/status/active row. Root `TASKS.md` was not edited.
- Focused correction command: `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_001_mutation_interface.py tests/unit/test_sb_lf00_007_governance_authority.py` -> `11 passed`.
- Final required full gate: `python -m pytest -q -p no:cacheprovider` -> `989 passed, 2 skipped` in `309.16s`. The two skips are the pre-existing explicitly capability-gated canonical ScrubBots checkout/bridge skips; no new skip/xfail was added.
- `python -m compileall -q src tests` -> exit code 0.
- `godot_console.exe --headless --editor --path level_factory --quit` (Godot 4.7.2) -> exit code 0.
- `git diff --check` -> exit code 0. `git diff --exit-code -- TASKS.md` -> exit code 0.
- No dependency, license, provider, network, credential, API-key, telemetry, owner-source, or main-game files changed.
- The mutation identity canonical forms contain no timestamps, filesystem paths or wall-clock duration. Candidate payloads are deep-frozen and applied mutations create a distinct child with an immutable parent-to-child edge; caller acceptance is not represented.

## Publication checkpoints

- Implementation commit: `b1978ead08adf572625c476be71aad30bcdb0f99` (`Implement M07 mutation interface and immutable lineage`).
- Implementation push: `git push origin HEAD:main` succeeded; immediately after push local `HEAD` and `origin/main` were both `b1978ead08adf572625c476be71aad30bcdb0f99`.
- Terminal log-only publication commit and its push remain the final M07-001 publication checkpoint. Root `TASKS.md`, prompts, audits, prior logs, and owner-local untracked files remain unchanged.
