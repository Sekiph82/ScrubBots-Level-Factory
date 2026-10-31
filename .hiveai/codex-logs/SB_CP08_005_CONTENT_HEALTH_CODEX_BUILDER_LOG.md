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
