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

## 2026-11-06 — offline publisher read-back record bridge

- Continuation start: 2026-11-06 01:12:05 UTC. Canonical Desktop root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; branch `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`; starting `HEAD == origin/main == 5b9397d4c3fbb2a96c8ac234ac449742d266f307`, ahead/behind 0/0; tracked worktree clean; pre-existing unrelated untracked owner files preserved.
- Queue guard passed with `SB-CP08-002`, Required Actor CODEX, current stable autonomous-backlog prompt blob `3cafdbd2168ff4cbdea1d7ceed2b91f11d08a648`; tracker selection commit `5b9397d4`.
- Read the current task row, active owner prompt, `C001_R03_NO_TEMP_IN_MEMORY_WORK_AND_CLOSURE_MASTER_PROMPT.md`, existing CP08-002 log, `operations.py`, the CP03 one-command publisher, staging read-back verification receipt, production activation receipt, and focused CP08/CP03 tests.
- Source inspection confirms `operation_record_from_manifest_observation` validates exact bytes, but repository references currently stop at its unit tests; `PublisherRunReport` already retains the verified staging download and production activation reports. The selected bounded source change will expose operation records only from accepted/verified canonical publisher read-back receipts, bind version and digest back to exact receipt bytes, and stay pure/in-memory. No network/R2 read/write, timestamp inference, or claim that an external observation occurred.
- The focused CP08 evidence test and relevant publisher/read-back tests contain no `tmp_path`, `tmpdir`, `tempfile`, or output-directory fixture markers. They will be run only with Python bytecode and pytest caches disabled. If transitive test setup violates the no-TEMP boundary, stop that test and retain source/static evidence truthfully.
- No source/test edits or provider operations had occurred at this log checkpoint.

### Continuation implementation, verification, and publication

- Implemented the pure `PublisherRunReport.observed_version_operation_records` adapter in `content_pipeline/src/scrubbots_content_pipeline/one_command_publisher.py`. It converts only accepted staging VERIFIED/read-back receipts and accepted production ACTIVATED receipts into CP08 records, then rechecks version, SHA-256 and byte length against the exact receipt bytes. `ALREADY_CURRENT` without returned bytes produces no production version event. No provider access or inferred timestamp was introduced.
- Added in-memory coverage in `tests/unit/test_sb_cp08_operations_evidence.py` for both environments, exact digest/version binding, weekly summary inclusion, failed read omission, receipt drift rejection and ALREADY_CURRENT without receipt. Extended two existing publisher integration tests in `tests/unit/test_sb_cp03_011_one_command_publisher.py` to verify records emitted from actual accepted in-memory staging and production reports.
- The first combined run exposed that canonical staging environment is lowercase `staging`; the comparison/fixtures were corrected to use `Environment.STAGING.value`. A later focused run passed: `PYTHONPATH=content_pipeline/src`, `PYTHONDONTWRITEBYTECODE=1`, `python -B -m pytest -p no:cacheprovider -p no:tmpdir -q tests/unit/test_sb_cp08_operations_evidence.py tests/unit/test_sb_cp03_011_one_command_publisher.py -k 'not unrelated'` — **21 passed in 0.46s**. The earlier initial mismatch run had 2 failures; the corrected rerun passed. Tests used in-memory data and disabled pytest cache/tmpdir plugins.
- `git diff --check` passed. Python AST parsing passed for the changed implementation and both changed test modules. The read-only task queue guard was attempted while tracked implementation edits were present and refused to start, as designed; it will be rerun at the clean source/log publication boundary. No CI/Actions, live provider read, R2 write, Production activation, paid generation, GUI action or owner-data mutation occurred.
- Source/test commit `74383be3b424d8924d2b95df333a8548ca1deb4d` was pushed by normal `git push origin HEAD:main`. Fetch verified local `HEAD == origin/main == 74383be3b424d8924d2b95df333a8548ca1deb4d`, 0 ahead / 0 behind, with no tracked source/test changes. The first PowerShell parity assertion itself returned an error because its literal-tab comparison was malformed despite equal printed SHAs and `0 0`; a separate normalized comparison then passed. This was a verification-script formatting error, not a repository or push failure.
- CP08-002 remains partial: offline publisher-to-record integration is builder-verified, while actual remote observation/live provider reads remain NOT_RUN and externally permission-gated. Continue with existing CP08 backlog only after queue revalidation.
