# SB-CP08-005 — Content-Health Check

Document role: CODEX BUILDER LOG

## Start and authority

- Started: 2026-10-31 UTC.
- Canonical Desktop root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repo `Sekiph82/ScrubBots-Level-Factory`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; branch `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`.
- Starting `HEAD == origin/main == d74c3983879efb24e4c17ee79f0df92fa8835e49`, 0 ahead / 0 behind; queue guard selected `SB-CP08-005`.
- Active prompt `.hiveai/prompts/SB_LFX_OWNER_GOAL_AUTONOMOUS_OPEN_BACKLOG_20261031.md`, blob `3cafdbd2168ff4cbdea1d7ceed2b91f11d08a648`; read the existing task row, M19 content-health scope, `verify_content_health` and current offline test.
- Concrete gap found: the health verifier checked only a caller-provided manifest digest and separately supplied expected object mapping; it did not strict-parse the manifest or ensure its declared pack keys/digests exactly matched that mapping. Arbitrary bytes with a matching expected SHA plus matching caller map could therefore yield `HEALTHY`.
- Narrow repair: strict-parse exact observed Content Manifest V1 bytes and bind the expected object set to manifest-declared pack object keys/digests before any object health disposition. Missing manifest/object reads remain UNKNOWN. No live provider access or filesystem writes.

## Implementation and verification

- `verify_content_health` now strict-parses hash-matching observed bytes with the canonical Content Manifest V1 parser. A malformed manifest returns `FAIL / INVALID_MANIFEST`; a caller-supplied expected object map that differs from the manifest's declared pack object keys/digests returns `FAIL / MANIFEST_OBJECT_SET_MISMATCH`. Only the exact manifest-declared set proceeds to object-byte comparison.
- Missing manifest bytes still return `UNKNOWN / MANIFEST_BYTES_NOT_OBSERVED`; missing object reads still return `UNKNOWN / OBJECT_BYTES_NOT_OBSERVED`. Exact observed bytes with matching hashes may report HEALTHY; mismatches remain FAIL. No provider read was added.
- Updated the in-memory test to use a valid manifest declaring one pack and cover missing reads, healthy exact bytes, object mismatch, manifest digest mismatch, malformed manifest and manifest/object-set divergence.
- Focused command with process-local `PYTHONPATH=content_pipeline/src`, restored afterward: `python -B -m pytest -p no:cacheprovider -p no:tmpdir -q tests/unit/test_sb_cp08_operations_evidence.py` — **9 passed in 0.22s**. No temporary directories, provider calls, local output writes or owner data.
- `git diff --check` passed. Files changed: `operations.py` and the focused operations evidence test. No dependencies, schemas, owner files, 140 PNGs, R2, Production, CI, Release Apply, GUI or game repo changed.
- This is builder verification on explicit in-memory inputs only; live Staging/Production health observation remains NOT_RUN / EXTERNAL_PERMISSION_REQUIRED.

## Publication and next-task selection

- Source/test commit and normal push receipt will be recorded after fetch/ancestry/parity verification.
- Next eligible existing row is `SB-CP08-006` safe operational errors/alerts without unnecessary player data; inspect the fixed-field reporting boundaries and offline tests at the clean task boundary.
- Source/test evidence commit `e4f830332fc30b0320c91a525c7c2d97895d550b` was pushed normally; fetch confirmed `HEAD == origin/main`, 0 ahead / 0 behind. No provider or remote object read was made. TASKS will record this offline builder evidence as partial and select CP08-006.

## 2026-11-06 continuation — publisher report health-check bridge

- Continuation start: 2026-11-06 01:27:24 UTC. Canonical Desktop root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; branch `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`; `HEAD == origin/main == 278304f680338f4ee873f762f8f424b0ed35e222`, ahead/behind 0/0; queue guard selected existing `SB-CP08-005`; current stable goal prompt blob `3cafdbd2168ff4cbdea1d7ceed2b91f11d08a648`.
- Read the current TASKS row, this builder log, sync/publish standard and queue output. Inspected `verify_content_health`, its exact-manifest/object-set tests, CP03 publisher result and the already implemented staging read-back bridge. The verifier accepts exact in-memory receipts but no publisher-report caller reuses its canonical staging manifest bytes and retained downloaded object bytes.
- Planned bounded change: expose a pure report adapter that validates the accepted staging receipt, derives expected objects only from its exact manifest, and supplies only retained `DownloadedPackBytes.content_bytes` to the existing health verifier. No provider access, R2, Production, filesystem output, or health inference from digest metadata alone.
- Implemented `PublisherRunReport.observed_content_health`. Missing/unverified staging manifest returns UNKNOWN; malformed receipt/identity fails closed; expected keys/digests come from the receipt and the existing strict verifier cross-checks them against the exact manifest bytes. The adapter forwards only retained exact bytes and therefore reports HEALTHY/FAIL/UNKNOWN from actual in-memory observations, not digest fields alone.
- Added assertions for exact-byte HEALTHY, no-object-bytes UNKNOWN, and changed-byte FAIL; extended the actual in-memory CP03 publisher integration regression. The first test run had 2 failures because the test manifest declared an empty pack set while its receipt declared a pack. The next fixture correction exposed the canonical pack-key path format; it was corrected to `packs/pack-01/main.scrubpack`. Final focused run with process-local `PYTHONPATH=content_pipeline/src`, `PYTHONDONTWRITEBYTECODE=1`, `python -B -m pytest -p no:cacheprovider -p no:tmpdir -q tests/unit/test_sb_cp08_operations_evidence.py tests/unit/test_sb_cp03_011_one_command_publisher.py` — **23 passed in 0.46s**. Test bytes are in-memory; no temp/cache/bytecode output.
- `git diff --check` and AST parsing passed for the implementation and both changed test modules. Source/test commit `3e6b4d5e240e3fe3a9a2039c81abf09217533314` was pushed by normal `git push origin HEAD:main`; fetch verified local `HEAD == origin/main == 3e6b4d5e240e3fe3a9a2039c81abf09217533314`, 0 ahead / 0 behind. This is still offline publisher-report integration only; live Staging/Production content health remains NOT_RUN / EXTERNAL_PERMISSION_REQUIRED.
