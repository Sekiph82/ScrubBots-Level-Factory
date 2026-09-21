# SB-LFX-014-C001-R02 — Batch Identity + FileDialog + Reload Remediation

Document role: CODEX BUILDER LOG

## Chronology

- 2026-09-21 Europe/Istanbul: Continued on canonical `main` after SB-LFX-013 publication; branch/origin equality and protected tracker state remain verified.
- Read the R02 index, SB-LFX-014 R01 strict audit, exact R02 prompt, batch backend, Studio surface, and retained unit/integration contracts. `TASKS.md` remains unchanged.
- This log was created before SB-LFX-014 edits.

## Scope and implementation

Give each batch execution a unique immutable run identity, add persisted batch reload validation, and make a real multi-file FileDialog the primary Studio selection path. The bounded programmatic setter remains for headless tests. Runtime evidence covers duplicate bytes, same display names in different directories, corrupt items, repeated runs, external-byte immutability, and reload.

## Verification ledger

Pending: implementation, focused Python/Godot gates, retained regressions, full suite, compile/boot/diff checks, implementation publication, and terminal log-only publication.
- Focused Python batch test passed: `1 passed` (one environment cache warning).
- Focused Godot command passed: `godot_console.exe --headless --path level_factory --script res://tests/factory_studio_batch_import_r01_integration_suite.gd` — `SB-LFX-014-C001 BATCH import integration PASS`.
- The run uses same-name files in different directories, duplicate bytes, a corrupt file, two intentional unique run IDs, persisted reload, external byte snapshots, and a real `FileDialog.FILE_MODE_OPEN_FILES`; no validation/promotion was added.
- Batch closure gates: `python -m pytest -q` completed `759 passed, 1 failed, 2 warnings`; the sole failure is the pre-existing protected `TASKS.md` current-task contract and was not changed. `python -m compileall -q src` passed; headless Godot editor boot passed with `BOOT_EXIT=0`; `git diff --check` passed; no `TASKS.md` diff was present.
- Implementation publication SHA: `13461c453a6a94a962c249a57722c15fb043f092`. `origin/main` matched local HEAD after every push.
- Task-final log-only publication is the next single commit; its SHA is recorded in the final master remediation log.
