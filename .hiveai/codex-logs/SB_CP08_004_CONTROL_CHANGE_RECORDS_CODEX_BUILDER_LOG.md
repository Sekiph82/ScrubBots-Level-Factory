# SB-CP08-004 — Disabled, Scheduled and Rollback Change Records

Document role: CODEX BUILDER LOG

## Start and authority

- Started: 2026-10-31 UTC.
- Canonical Desktop root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repo `Sekiph82/ScrubBots-Level-Factory`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; branch `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`.
- Starting `HEAD == origin/main == 1a8e48f5ed6ce628e9273ddd0c8c4ddf0aa21902`, 0 ahead / 0 behind; queue guard selected `SB-CP08-004`.
- Active owner prompt `.hiveai/prompts/SB_LFX_OWNER_GOAL_AUTONOMOUS_OPEN_BACKLOG_20261031.md`, blob `3cafdbd2168ff4cbdea1d7ceed2b91f11d08a648`; read the CP08 row, M19 scope, `operations.py`, M17 control receipt/schedule contracts and their local tests.
- M17 `ControlReceipt` carries hash-bound action/version evidence for DISABLE, REENABLE, ROLLBACK, SCHEDULE and CANCEL_SCHEDULE. The receipt lacks an authoritative remote environment field; this adapter will therefore record only a local prepared/intent event. It must not claim remote activation or final provider state. It will serialize/verify the canonical receipt before mapping and reject unsupported operation/outcome combinations.
- Planned tests use synthetic in-memory receipts; no temp directories, provider calls, R2, Production, activation, owner data, CI, Release Apply, GUI or game repo operations.

## Implementation and verification

- `operation_record_from_control_receipt` accepts only an M17 `ControlReceipt`, reconstructs and verifies its canonical receipt digest/fields, and maps only explicit DISABLE, REENABLE, ROLLBACK, SCHEDULE and CANCEL_SCHEDULE receipt outcomes. Unsupported publish operations and unknown outcomes fail closed.
- Records carry the canonical target, next content version, and candidate manifest digest. They are explicitly `LOCAL`; active control intents map to `PREPARED`, and cancellation maps to `COMPLETED` only for the canonical `INTENT_CANCELLED` receipt. No mapping claims remote activation or final provider state.
- Added optional `target_id` to operation records and incremented operation-record JSON schema version to 2 so the additive serialized field is versioned. Updated the fixed-field schema assertion. Control receipt actor/approval details remain excluded from these records.
- Focused command with process-local `PYTHONPATH=content_pipeline/src` restored afterward: `python -B -m pytest -p no:cacheprovider -p no:tmpdir -q tests/unit/test_sb_cp08_operations_evidence.py tests/unit/test_m17_release_controls.py::test_receipts_are_deterministic_and_weekly_batches_keep_distinct_lineage` — **10 passed in 0.23s**. All newly added cases use in-memory receipts; no tmp directory or filesystem write.
- `git diff --check` passed. Files changed: `operations.py` and `test_sb_cp08_operations_evidence.py`. No external provider, R2, Production activation, filesystem export, owner data, original art, CI, Release Apply, GUI or game repository was touched.
- Status is partial: the local record conversion is covered; M17 receipts alone do not prove live activation, provider final state, or a durable remote event read. Those gates remain NOT_RUN / EXTERNAL_PERMISSION_REQUIRED.

## Publication and next-task selection

- Implementation/test commit and publication receipt will be recorded after normal push and fetch parity verification.
- Next candidate is existing `SB-CP08-005` content-health check; it can be examined using explicit in-memory manifest/object bytes while leaving any live provider read external-gated.
