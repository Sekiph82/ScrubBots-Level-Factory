# SB-LFX-012-C001-R03 — True Restart + Surface-Path Revision Remediation

Document role: CODEX BUILDER LOG

## Chronology

- 2026-09-21 Europe/Istanbul: Continued on canonical `main` after SB-LFX-011 R03 publication and cleanup; local and `origin/main` are equal at `8b5ba3b16d87fa0abadac64422f81ba9987c7097`; repository identity, branch, origin, and protected `TASKS.md` boundary verified.
- Read the R03 master prompt and index, R02 summary, SB-LFX-012 R02 strict audit, exact R03 prompt, `AGENTS.md`, `GOVERNANCE.md`, root `TASKS.md`, revision/editor surfaces, owner-review contracts, and retained R02 integration.
- This log was created before SB-LFX-012 R03 product or integration edits.

## Scope and implementation

Close only the remaining restart/operator-path matrix: execute revision Compare, Select/Undo, branch R3, Restore Source, owner-review separation, and fail-closed corruption through the real revision surface, then destroy/reinstantiate Studio and reconstruct the same durable immutable history. Production/promotion/export remains unavailable where the canonical authority is not connected.

## Verification ledger

- Extended the retained real Godot revision integration to create owner-review evidence, snapshot its bytes, save R0/R1/R2 through `FactoryStudioRevisions`, invoke surface Compare, invoke surface Select/Undo, branch R3 without overwriting R2, and invoke surface Restore Source.
- Added a true Studio teardown/reinstantiate boundary. The fresh surface reloads the durable revision lineage, compares the reconstructed branch, preserves owner-review PASS and export NOT AVAILABLE truth, then rejects a corrupted revision lineage fail-closed before the fixture is restored for cleanup.
- Focused gates passed: `godot_console.exe --headless --path level_factory --script res://tests/factory_studio_revisions_r01_integration_suite.gd` — `SB-LFX-012-C001 REVISION lineage integration PASS`; `python -m pytest -q tests/unit/test_sb_lfx_012_revisions.py` — `1 passed, 1 warning`.
- Retained revision semantics remain green: source artwork bytes are unchanged, R2 remains immutable after branch R3, manual revisions never claim validation PASS, and promotion/export remains unavailable.
- `python -m pytest -q` passed `760 passed, 1 warning` in `355.60s`; `python -m compileall -q src` passed; headless Godot editor boot passed with `BOOT_EXIT=0`; `git diff --check` passed; `TASKS.md` diff length was zero.
- Files changed: this R03 builder log and the retained `level_factory/tests/factory_studio_revisions_r01_integration_suite.gd`. `TASKS.md` was not modified.
- Implementation publication SHA: `f0186eb5b65b0b066761df924d4179436aec0623`; pushed to `main`, with local HEAD equal to `origin/main` at that SHA.
- The required terminal log-only commit and SHA are recorded after this log is finalized and pushed.
