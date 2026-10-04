# SB-CP00-004-C001 - Separate Staging and Production

Document role: CODEX BUILDER LOG

## Chronological Record

### 2026-10-04 13:18:31 +03:00 — Child start

- Active authority: the live M11 master prompt authorizes this child second, continuing in the single master execution worktree after SB-CP00-003 passed and published.
- Execution root: %TEMP%\ScrubBots-Level-Factory\M11-CP00-003-009-MASTER; current base SHA 57d63a8cd30470b11297da60aae8c4f0bdcdf776, equal to origin/main at the end of child 003.
- Persistent Desktop checkout remains owner-dirty and untouched under the master preflight disposition.
- Read the SB-CP00-004 implementation prompt and audit criteria. Scope is a versioned local target identity model, collision/mismatch/promotion guards, deterministic config/report evidence, and tests. No provider or network mutation.
- Read current config.py, alidation.py, cli.py, provider protocol, pipeline config schema/example, current CP001 boundary tests, and prior child-003 payload validator/log from execution HEAD.

### 2026-10-04 13:39:48 +03:00 — Target implementation and regression gates

- Implementation changes: config.py now defines a versioned EnvironmentTarget, canonical staging/production target identities, deterministic serialization, fail-closed target-pair/binding/use results, and explicit promotion-intent checks. alidation.py includes target identity in every dry-run report and refuses unknown/mismatched configuration. Updated the config schema/example and README; extended CP001 compatibility tests; added CP004 target tests.
- Staging/production identities have distinct logical IDs, state namespaces, and content namespaces. Production has direct publication disabled and promotion required. Target pair validation detects state/content/logical identity collisions; binding rejects unknown/mismatched environment; staging-to-production use rejects absent promotion intent.
- A first focused run failed 1 of 90 tests because the test searched source comments for the word ndpoint instead of checking serialized configuration. The assertion was corrected to inspect serialized configuration; rerun passed. Failure retained here.
- Focused + prior-child + governance command: python -m pytest tests/unit/test_sb_cp00_004_environment_targets.py tests/unit/test_sb_cp00_003_payload_validation.py tests/unit/test_sb_cp00_002_content_boundary.py tests/unit/test_sb_cp00_002_r01_contract_binding.py tests/unit/test_sb_cp00_001_content_pipeline_boundary.py tests/unit/test_sb_lf00_007_governance_authority.py -q — **90 passed**.
- Full regression: python -m pytest -q — **1252 passed, 3 skipped, 0 failed** in 1002.61s. Skips: 	ests/integration/test_maint_supply_pipeline_v01.py:232 (SCRUBBOTS_SLOW=1), 	ests/unit/test_sb_lf03_002_compact_solver_state.py:274 (canonical ScrubBots checkout capability not supplied), and 	ests/unit/test_sb_lf04_012_regression.py:222 (canonical ScrubBots checkout capability not supplied; no bridge exercised).
- Full-suite existing tests performed a read-only shallow clone of Sekiph82/Scrubbots and headless Godot integration checks. No provider/network mutation or runtime/game file modification was performed by this implementation.
- python -m compileall -q content_pipeline/src — PASS. git diff --check — PASS. No endpoints, credentials, dependencies, or license changes were introduced.
- Implementation diff: 8 paths, 390 insertions, 9 deletions; content-pipeline target/config/report/schema/docs and focused regression tests only.
- Base SHA: 57d63a8cd30470b11297da60aae8c4f0bdcdf776. Implementation commit: 9e29084d4a8490b95b972ec645e09d1b77abaade.
- git fetch --prune origin immediately before implementation push showed 1 ahead / 0 behind. Normal non-force git push origin HEAD:main succeeded; post-push fetch verified local = origin/main at 9e29084d4a8490b95b972ec645e09d1b77abaade, 0/0.
- Builder-log commit/publication and its final parity will be recorded in the master log after completion.
