# SB-CP08-003 — Record Hashes and Verification

Document role: CODEX BUILDER LOG

## Start and authority

- Started: 2026-10-31 UTC.
- Canonical Desktop root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repo `Sekiph82/ScrubBots-Level-Factory`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; branch `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`.
- Starting `HEAD == origin/main == f5f7d5bc7a73f297b61c3c026a30bacba9822621`, 0 ahead / 0 behind; queue guard selected `SB-CP08-003`.
- Active owner prompt `.hiveai/prompts/SB_LFX_OWNER_GOAL_AUTONOMOUS_OPEN_BACKLOG_20261031.md`, blob `3cafdbd2168ff4cbdea1d7ceed2b91f11d08a648`; read existing task row, operations evidence implementation and provider verification contract.
- Existing `verify_content_health` computes expected and observed digests only when bytes are explicitly supplied, but no operation-record adapter converts an expected digest plus explicitly observed bytes into the declared `OBJECT_VERIFY` event. Add a pure offline helper that hashes exact bytes and records MATCH/MISMATCH; missing bytes will fail closed rather than fabricate remote evidence. No provider call or filesystem output.
- Exact target tests will use in-memory bytes only. Live R2/staging/production reads remain unauthorized and will stay NOT_RUN.

## Implementation and verification

- `OperationRecord(kind="OBJECT_VERIFY")` now requires a digest-comparison outcome (`MATCH` or `MISMATCH`) and exact expected/observed digests; an unrelated outcome can no longer be presented as verification.
- Added `operation_record_from_object_observation`: accepts only a valid expected SHA-256 and explicitly supplied bytes, hashes those exact bytes, and emits truthful MATCH/MISMATCH with both digests. Missing bytes fail closed and remain UNKNOWN/unrecorded; this helper performs no provider call and cannot claim a remote read by itself.
- Added in-memory tests for exact match, mismatch, summary count, missing observation refusal and invalid verification outcome. Existing exact content-health test continues to prove no-read state is UNKNOWN and observed mismatched bytes FAIL.
- Focused command (process-local `PYTHONPATH=content_pipeline/src`, restored afterward): `python -B -m pytest -p no:cacheprovider -p no:tmpdir -q tests/unit/test_sb_cp08_operations_evidence.py tests/unit/test_sb_cp08_publication_plan_adapter.py::test_publication_plan_maps_to_secret-free-preflight-record-in-memory` — **9 passed in 0.22s**. All data was in memory; pytest cache/tmpdir plugins were disabled.
- `git diff --check` passed. Files changed: `content_pipeline/src/scrubbots_content_pipeline/operations.py` and `tests/unit/test_sb_cp08_operations_evidence.py`; no dependency, schema, owner data, 140 PNG, Release, game repository, R2, Production, CI or external deployment changes.
- Current result is partial: builder code can faithfully record a comparison only after bytes are supplied, but no live provider read or caller proving remote observation was authorized/performed. Do not interpret this offline test as remote verification.

## Publication and next-task selection

- Source/test commit and normal push receipt will be recorded after parity verification.
- Next eligible existing row is `SB-CP08-004` disabled/scheduled/rollback change records; inspect only offline state/event contracts and do not run activation or mutate remote state.
- Builder evidence commit `e80b5366cabc427051ace573844a131d1eb37328` was pushed normally; fetch verified `HEAD == origin/main`, 0 ahead / 0 behind. No remote provider read occurred. TASKS will mark offline support partial and select CP08-004.
- Tracker transition administrative command note: the first CP08-003 progress-update script expected an unchecked `[ ]` row although CP08-003 was already correctly `[~]`. Its guard aborted before writing TASKS.md; no repository file changed. The selection script is corrected to match the actual partial row.
