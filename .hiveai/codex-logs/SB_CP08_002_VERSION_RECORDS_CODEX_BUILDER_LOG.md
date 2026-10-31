# SB-CP08-002 — Record Staging and Production Versions

Document role: CODEX BUILDER LOG

## Start and authority

- Started: 2026-10-31 UTC.
- Canonical Desktop root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repo `Sekiph82/ScrubBots-Level-Factory`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; branch `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`.
- Starting `HEAD == origin/main == 2c1d94e2d16502185f19ffde898bf8120751db89`, 0 ahead / 0 behind; queue guard selected `SB-CP08-002`.
- Active prompt `.hiveai/prompts/SB_LFX_OWNER_GOAL_AUTONOMOUS_OPEN_BACKLOG_20261031.md`, blob `3cafdbd2168ff4cbdea1d7ceed2b91f11d08a648`; read task row, M19 CP08 scope, operation-record source, strict Content Manifest V1 parser and focused tests.
- Source currently declares `STAGING_VERSION` and `PRODUCTION_VERSION` event kinds and an optional `content_version`, but has no invariant binding event kind to matching environment or requiring an observed manifest version/digest. The publication-plan adapter also does not capture observed manifests. A narrow helper will derive these fields only from explicitly supplied strict-parsed manifest bytes; it will make no provider calls and will fail closed on absent, malformed or mismatched observation. Add focused in-memory tests only.
- No owner data, live provider/R2, Production action, CI, filesystem export, 140 PNGs, Release Apply, GUI or game repo is in scope.

## Implementation and verification

- Concrete gap: version event kinds were declared but `OperationRecord` did not bind `STAGING_VERSION` to STAGING or `PRODUCTION_VERSION` to PRODUCTION and allowed a version event with no version/digest. No safe helper derived version evidence from actual manifest bytes.
- `content_pipeline/src/scrubbots_content_pipeline/operations.py` now enforces matching environment and requires content_version plus manifest_sha256 for version events. New `operation_record_from_manifest_observation` accepts only explicit bytes and exact STAGING/PRODUCTION labels, strict-parses Content Manifest V1, and derives the version and SHA-256 from those same observed bytes. Missing, wrong-type, wrong-environment, or malformed observations fail closed. It does not access a provider or infer a version.
- Added a focused in-memory regression in `tests/unit/test_sb_cp08_operations_evidence.py` covering staging and production records, summary inclusion, matching exact-byte digest, missing/malformed bytes, mismatched event/environment and missing version proof.
- Command: temporarily set process `PYTHONPATH` to canonical `content_pipeline/src`, restore it afterward; `python -B -m pytest -p no:cacheprovider -p no:tmpdir -q tests/unit/test_sb_cp08_operations_evidence.py tests/unit/test_sb_cp08_publication_plan_adapter.py::test_publication_plan_maps_to_secret_free_preflight_record_in_memory` — **8 passed in 0.21s**. This suite uses in-memory data and a read-only runbook assertion; it does not allocate temporary filesystem directories.
- `git diff --check` passed. No test failure occurred. Files changed: operations.py and the focused operations evidence tests; no dependency, schema, owner data, original art, GUI, Release, game repo, R2, Production, CI, or external deployment changes.
- This builder evidence proves offline version records from explicit manifest bytes. Actual staging/production provider reads and live version observations remain NOT_RUN / EXTERNAL_PERMISSION_REQUIRED.

## Publication and next-task selection

- Source/test commit and publication receipt will be recorded after normal push/fetch/parity verification.
- Next candidate is existing `SB-CP08-003` record hashes/remote verification; inspect at the clean boundary and keep real provider reads external-gated.
- Source/test evidence commit `d79037f2b7f26a947a42d4fd285bb28f69c61cd2` was pushed normally; fetch verified `HEAD == origin/main`, 0 ahead / 0 behind. No provider reads were performed. Task progress and next selection remain to be recorded separately in TASKS.md.
