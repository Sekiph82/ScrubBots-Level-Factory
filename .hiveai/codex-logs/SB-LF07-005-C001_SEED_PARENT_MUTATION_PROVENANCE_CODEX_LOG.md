# SB-LF07-005-C001 — Seed / Parent / Mutation Provenance
Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Scope: `SB-LF07-005-C001`, immediately after published SB-LF07-004.
- Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting HEAD and `origin/main`: `3e927fb15277bfee12fc8ecdc36257423815ccd0`.
- Initial status: equal to origin; pre-existing untracked LF04 worktree directories and Godot UID files preserved and not staged.

## Required records and contracts read before edits

- Live `TASKS.md`, M07 master prompt/index, this task prompt and strict criteria.
- `AGENTS.md`, `GOVERNANCE.md`, and accepted SB-LF07-001..004 implementation/log evidence.
- M03/M04/M05 evidence identity and immutable owner-source contracts.

This log was created before SB-LF07-005 product implementation and tests.

## Planned implementation boundary

- Add a closed canonical provenance record that reconstructs request, seed derivation, root/parent/child identities, operator/authority, attempt ordinal, pre/post digests, evidence digests and disposition.
- Derived digests are computed, not caller-overridable; cycles, self-parenting, mixed roots, seed/operator/authority drift and conflicting duplicate children fail closed.
- Exclude paths, timestamps and wall-clock telemetry from canonical identity.

## Chronological implementation and verification

- Added `MutationProvenance` and `ProvenanceLedger` to `src/scrubbots_pixel_factory/mutation.py`. Provenance binds request digest, seed/derivation version, lineage root and immediate parent, exact LevelData/source/art identities through candidate identities, operator id/version/intent/authority, attempt ordinal, pre/post state digests, disposition/reason and evidence digests.
- Derived pre/post/lineage fields are verified against exact parent/child identities. The ledger is idempotent for identical records and rejects conflicting duplicate child provenance. Mixed roots, self-parenting, seed drift and authority/request drift fail closed.
- Added `tests/unit/test_sb_lf07_005_provenance.py` for round-trip determinism, derived-field tamper, seed/root drift and duplicate conflict.
- Focused command for M07-001..005: `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_001_mutation_interface.py tests/unit/test_sb_lf07_002_hardening.py tests/unit/test_sb_lf07_003_easing.py tests/unit/test_sb_lf07_004_revalidation.py tests/unit/test_sb_lf07_005_provenance.py` -> `17 passed`.
- Full command: `python -m pytest -q -p no:cacheprovider` -> `1002 passed, 2 skipped` in `313.95s`. Skips remain the pre-existing explicitly capability-gated canonical ScrubBots checkout/bridge skips.
- `python -m compileall -q src tests` -> exit code 0.
- `godot_console.exe --headless --editor --path level_factory --quit` (Godot 4.7.2) -> exit code 0.
- `git diff --check` -> exit code 0. `git diff --exit-code -- TASKS.md` -> exit code 0.
- Canonical provenance excludes filesystem paths, timestamps and wall-clock values. No owner-source or canonical ScrubBots checkout mutation occurred.

## Publication checkpoints

Implementation and terminal log-only publication checkpoints are recorded below. Root `TASKS.md`, prompts, audits, prior logs, and owner-local untracked files remain unchanged.

- Implementation/evidence commit: `93d89dd1d0a40b991a8331499a23c8149bda1dcc` (`Add M07-005 mutation provenance`).
- Implementation push succeeded; local `HEAD` and `origin/main` were both `93d89dd1d0a40b991a8331499a23c8149bda1dcc` immediately afterward.
- Terminal log-only publication commit is the final SB-LF07-005 checkpoint.
