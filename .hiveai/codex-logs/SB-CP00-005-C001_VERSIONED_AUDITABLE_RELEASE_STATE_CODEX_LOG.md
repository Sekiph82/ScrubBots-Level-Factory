# SB-CP00-005-C001 - Versioned Auditable Publish/Promotion/Rollback State

Document role: CODEX BUILDER LOG

## Chronological Record

### 2026-10-04 14:06:52 +03:00 — Child start

- Active authority: the live M11 master prompt authorizes this child third, after the passing/published SB-CP00-003 and SB-CP00-004 children.
- Execution root: %TEMP%\ScrubBots-Level-Factory\M11-CP00-003-009-MASTER; start SHA 31450bd89524b7392e36ab117ba5bfc159538b13, equal to origin/main; persistent Desktop checkout remains untouched under the original preservation disposition.
- Read child prompt/criteria and current content-pipeline package, CP001..004 implementation/regression tests, configuration and target model.

### 2026-10-04 14:06:52 +03:00 — Implementation, evidence, and test outcomes

- Added release_state.py: explicit release states (DRAFT, VALIDATED, STAGED, PROMOTION_PENDING, PRODUCTION_PROMOTED, ROLLED_BACK, SUPERSEDED, FAILED, ABORTED), versioned frozen events/snapshots/results, caller-supplied IDs and sequence numbers, exact content digest/environment binding, deterministic serialization, and an event SHA-256 chain.
- Replay checks contiguous ordering, hash-chain and content tampering, duplicate event/transition IDs, expected-state freshness, allowed transitions and environment consistency. Promotion creates a new production record linked to a staged source; the staging record remains staged. Rollback appends a production event linked to a previously promoted record and keeps all earlier events.
- No clock, randomness, storage/database, provider, network, credential, or runtime/game dependency was introduced. Updated package exports and README; added focused legal/illegal/replay/tamper/rollback/determinism tests.
- First focused run had 1 assertion failure (98 passed): snapshots are sorted by record ID, not lifecycle order. The test now selects the named staging-a record; rerun passed. Failure retained here.
- Focused + prior-child + governance command: python -m pytest tests/unit/test_sb_cp00_005_release_state.py tests/unit/test_sb_cp00_004_environment_targets.py tests/unit/test_sb_cp00_003_payload_validation.py tests/unit/test_sb_cp00_002_content_boundary.py tests/unit/test_sb_cp00_002_r01_contract_binding.py tests/unit/test_sb_cp00_001_content_pipeline_boundary.py tests/unit/test_sb_lf00_007_governance_authority.py -q — 99 passed.
- Full regression: python -m pytest -q — 1261 passed, 3 skipped, 0 failed in 1020.75s. Skips: tests/integration/test_maint_supply_pipeline_v01.py:232 (SCRUBBOTS_SLOW=1), tests/unit/test_sb_lf03_002_compact_solver_state.py:274 (canonical ScrubBots checkout capability not supplied), and tests/unit/test_sb_lf04_012_regression.py:222 (canonical ScrubBots checkout capability not supplied; no bridge exercised).
- Full suite included read-only external-contract clone and headless Godot checks; this task made no provider/content mutation and changed no runtime/game files.
- python -m compileall -q content_pipeline/src — PASS. git diff --check — PASS.
- Implementation diff: 4 paths, 538 insertions; release ledger/API/docs/focused tests only. No dependency/license/secret changes.
- Base SHA: 31450bd89524b7392e36ab117ba5bfc159538b13. Implementation commit: 1c3679391782458508e918a5abb27b7d8ed949ca.
- git fetch --prune origin before implementation push showed 1 ahead / 0 behind. Normal non-force git push origin HEAD:main succeeded; post-push fetch verified local = origin/main at 1c3679391782458508e918a5abb27b7d8ed949ca, 0/0.
- While writing this builder log, an initial diff check caught control whitespace from PowerShell escape processing; the uncommitted log was rewritten with literal content and rechecked before commit.
- Builder-log commit/publication and final parity will be recorded in the master log after completion.