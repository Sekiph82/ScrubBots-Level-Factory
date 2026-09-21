# SB-LFX-013-C001-R03 — Canonical-Only Failure Truth + Retry Evidence Remediation

Document role: CODEX BUILDER LOG

## Chronology

- 2026-09-21 Europe/Istanbul: Continued on canonical `main` after SB-LFX-012 R03 publication; local and `origin/main` are equal at `4e97b1054dca46230fd40c442b8b347d53611c02`; repository identity, branch, origin, and protected `TASKS.md` boundary verified.
- Read the R03 master prompt and index, R02 summary, SB-LFX-013 R02 strict audit, exact R03 prompt, `AGENTS.md`, `GOVERNANCE.md`, root `TASKS.md`, canonical failure scanner/retry implementation, launcher, Studio Failure Inbox, and retained R02 integration.
- This log was created before SB-LFX-013 R03 product or integration edits.

## Scope and implementation

Remove the product launcher path for caller-created `record-failure` evidence and remove retry fallback to free-form failure JSON. Retain the canonical scanner-only Failure Inbox, evidence binding, selective retry, append-only attempts, successful-stage reuse, and unavailable-stage non-retryability.

## Verification ledger

- Removed the `record-failure` dispatch from the product `studio-extension` launcher. The retained helper is test-only evidence that is ignored by the canonical scanner, so caller-created JSON cannot enter Failure Inbox truth.
- Removed `retry_failure()` fallback loading from `extensions/failures/<failure_id>.json`; retry now accepts only scanner-derived canonical validation/pipeline/batch evidence and fails closed otherwise.
- Extended canonical retry evidence with originating evidence bytes/hash before and after retry, append-only attempt identity, and the successful pipeline-stage evidence identities reported for reuse. The real Godot suite generates a rejected source and successful controls, selects canonical pipeline failure truth, snapshots evidence, retries, verifies byte/hash preservation, confirms successful control work is not retryable, and keeps SOLVE/DIFFICULTY unavailable/non-retryable.
- Focused gates passed: `2 passed, 1 warning` for `tests/unit/test_sb_lfx_013_failures.py`; `godot_console.exe --headless --path level_factory --script res://tests/factory_studio_failures_r01_integration_suite.gd` — `SB-LFX-013-C001 FAILURE retry integration PASS`.
- An initial Godot focused run exposed a pre-existing undeclared `_fixture_root` in the retained suite; the fixture root is now explicit and bounded. This was test-harness hygiene only.
- `python -m pytest -q` passed `761 passed, 1 warning` in `376.02s`; `python -m compileall -q src` passed; headless Godot editor boot passed with `BOOT_EXIT=0`; `git diff --check` passed; `TASKS.md` diff length was zero.
- Files changed: this R03 builder log, `level_factory/scripts/factory_core_launcher.py`, `src/scrubbots_pixel_factory/studio_extensions.py`, the retained failure integration suite, and `tests/unit/test_sb_lfx_013_failures.py`. `TASKS.md` was not modified.
- Implementation publication SHA: `2903c3246d100e8a17d3a5236fc6a06fb251b546`; pushed to `main`, with local HEAD equal to `origin/main` at that SHA.
- The required terminal log-only commit and SHA are recorded after this log is finalized and pushed.
