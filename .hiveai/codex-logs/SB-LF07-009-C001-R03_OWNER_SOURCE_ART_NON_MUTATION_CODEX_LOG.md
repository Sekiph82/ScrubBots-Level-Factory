# SB-LF07-009-C001-R03 — Remediation Prompt

Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-26 Europe/Istanbul.
- Scope: SB-LF07-009-C001-R03 M05 owner-source preservation lifecycle and duplicate-authority removal.
- Canonical repository verified as `Sekiph82/ScrubBots-Level-Factory`.
- Local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting HEAD and `origin/main`: `2e20cf9dffac048f15e19955ba6ef9e9e750fc73`; tracked tree clean before this log; owner-untracked files preserved.
- Frozen SB-LF07-002/003 behavior and tests remain unchanged except compatibility wiring.

## Contracts read before edits

- R03 master/index, original SB-LF07-009 criteria/C001 audit, R01/R02 prompts/logs and strict re-audits.
- `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, accepted M05 `qa.source_preservation` contracts, M07 authentic runner, and retained M03/M04/M05/M06/Palette V3 tests.

## Frozen finding and R03 boundary

- R02 left a duplicate M07 owner-source record/report/verifier and required a pre-built after-PASS context before mutation.
- R03 must make accepted M05 own the source identity and verification, perform pre-check before mutation and post-check after the actual operation/authentic revalidation before TARGET_MATCH, and reject missing/stale/corrupt/aliased/changed source state.

## Chronological implementation and verification

- Removed the duplicate M07 owner-source implementation authority. `m07_services` now exposes only compatibility aliases to accepted M05 `qa.source_preservation.OwnerSourceRecord`, `SourcePreservationReport`, and `verify_owner_source_preservation`; no parallel byte/path verifier remains.
- Hardened `SourceLinkedMutationContext`: `establish` performs and requires the real M05 pre-check; `verify_after` requires the pre-check and performs the real M05 post-check. A pre-built after-PASS context is no longer required before mutation.
- Integrated source-linked orchestration into the authentic bounded runner. With source-linked parent identity, the runner requires an accepted M05 pre-PASS, executes the mutation and authentic M03/M04/M05 validation, runs the M05 post-check, and only then permits target selection/TARGET_MATCH. Post-check failure returns terminal ERROR with the authentic attempt/provenance retained.
- The runner now requires the actual `SourceLinkedMutationContext` type for source-linked parent identity; shape-compatible or prebuilt fake contexts cannot bypass the M05 lifecycle.
- Added accepted M05 compatibility construction for legacy `from_m05_owner_upload` mappings without creating a second source identity type.
- Added real temporary-file tests for byte preservation, source corruption, alias path, missing source, and an integrated hardening runner that proves post-operation byte mutation is rejected before success.
- Focused result: `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_009_owner_source.py tests/unit/test_sb_lf07_004_revalidation.py tests/unit/test_sb_lf07_005_provenance.py tests/unit/test_sb_lf07_007_attempts.py` — 29 passed.
- Affected M07 run: 71 passed; two retained SB-LF07-010 R02 regression tests still use the removed legacy owner-source constructor and caller-created accounting/config path, reserved for the ordered SB-LF07-010 remediation.
- Offline/network boundary: source checks read only the real local M05 source path and derived artifact paths; no network or telemetry dependency added.
- Dependency/license/security: no dependency or license changes; missing, stale, aliased, corrupt, dimension-changing, or post-operation-mutated source state fails closed.
- Changed files: `src/scrubbots_pixel_factory/qa/source_preservation.py`, `src/scrubbots_pixel_factory/m07_services.py`, `src/scrubbots_pixel_factory/mutation_source.py`, `src/scrubbots_pixel_factory/mutation_attempts.py`, `tests/unit/test_sb_lf07_004_revalidation.py`, `tests/unit/test_sb_lf07_005_provenance.py`, `tests/unit/test_sb_lf07_007_attempts.py`, `tests/unit/test_sb_lf07_009_owner_source.py`, and this builder log.

## Publication checkpoints

- Implementation commit: `8a25a2a9920ce2a45854a4c61bf3a8a4f197ae44` (`Remediate SB-LF07-009 source preservation lifecycle`), pushed to `origin/main`.
- Terminal log-only commit: pending after this chronological entry is committed.
- Final local HEAD and `origin/main` equality: implementation push completed; final equality is recorded after the log-only push.
