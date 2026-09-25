# SB-LF07-002-C001 — Safe Hardening Mutations / Canonical Mechanics
Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Scope: `SB-LF07-002-C001`, immediately after published SB-LF07-001.
- Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting HEAD and `origin/main`: `d7367ffb87d893fbd7247a00c35973229796ee32`.
- Initial status: equal to origin; pre-existing untracked LF04 worktree directories and Godot UID files preserved and not staged.

## Required records and contracts read before edits

- Live root `TASKS.md`, M07 batch master prompt, M07 implementation/audit index, this task prompt and strict criteria.
- `AGENTS.md`, `GOVERNANCE.md`, and the accepted SB-LF07-001 mutation interface/immutable-lineage implementation and builder log.
- Read-only current-main ScrubBots authority at exact accepted SHA `edf672f61989d28fd1931917ab49b2d64cc416d6`:
  `scripts/gameplay/supply/batch_supply_engine.gd`, especially M23 `preview_depth` bounds and FIFO preview contract.

This log was created before SB-LF07-002 product implementation and tests.

## Planned implementation boundary

- Add only the authority-bound hardening operator and adversarial tests on the accepted M07-001 substrate.
- Bind exact repository/SHA/source path/contract version; do not use board size, colors, art complexity or difficulty labels.
- Keep parent, source and canonical checkout immutable; output remains a candidate and is not accepted content.

## Chronological implementation and verification

- The accepted M07-001 substrate already contains the closed canonical operator registry and its current-main authority records. SB-LF07-002 exercises the M23 `CANONICAL_PREVIEW_DEPTH_HARDEN_V1` entry end-to-end and adds `tests/unit/test_sb_lf07_002_hardening.py` for real authority binding, bound/inapplicable state, source identity preservation, and forbidden board/color shortcut regression.
- Exact authority used: repository `https://github.com/Sekiph82/Scrubbots`, commit `edf672f61989d28fd1931917ab49b2d64cc416d6`, source `scripts/gameplay/supply/batch_supply_engine.gd`, contract `M23_V02_FIFO_PREVIEW_DEPTH`.
- Focused command: `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_001_mutation_interface.py tests/unit/test_sb_lf07_002_hardening.py` -> `7 passed`.
- Required focused-and-prior-M07 command repeated before publication -> `7 passed`.
- Full command: `python -m pytest -q -p no:cacheprovider` -> `992 passed, 2 skipped` in `312.54s`. Skips remain the pre-existing explicitly capability-gated canonical ScrubBots checkout/bridge skips.
- `python -m compileall -q src tests` -> exit code 0.
- `godot_console.exe --headless --editor --path level_factory --quit` (Godot 4.7.2) -> exit code 0.
- `git diff --check` -> exit code 0. `git diff --exit-code -- TASKS.md` -> exit code 0.
- No dimensions, color count, visual complexity or descriptive difficulty label is consulted by the hardening transform. It changes only the canonical M23 `preview_depth` field from 3 to 4, keeps the exact parent/source/art identities, and returns a candidate rather than acceptance.

## Publication checkpoints

The operator implementation is retained from the already-published immutable M07 substrate commit; this task’s implementation evidence/test commit and terminal log-only publication checkpoint are recorded below. Root `TASKS.md`, prompts, audits, prior logs, and owner-local untracked files remain unchanged.

- Implementation/evidence commit: `6d7040b1a1c191b0ffa70c006c13bfbc63e84159` (`Add M07-002 canonical hardening evidence`).
- Implementation push succeeded; local `HEAD` and `origin/main` were both `6d7040b1a1c191b0ffa70c006c13bfbc63e84159` immediately afterward.
- Terminal log-only publication commit is the final SB-LF07-002 checkpoint.
