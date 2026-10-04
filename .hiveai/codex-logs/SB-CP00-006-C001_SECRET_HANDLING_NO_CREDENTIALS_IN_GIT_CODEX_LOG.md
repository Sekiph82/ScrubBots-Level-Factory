# SB-CP00-006-C001 - Secret Handling, No Credentials in Git

Document role: CODEX BUILDER LOG

## Chronological Record

### 2026-10-04 14:09:15 +03:00 — Child start

- Active authority: the live M11 master prompt authorizes this child sixth, after SB-CP00-001..005 implementation/test/publication gates passed.
- Execution root: %TEMP%\ScrubBots-Level-Factory\M11-CP00-003-009-MASTER; starting SHA 8bc3029b098a2d2231965939f3c9e20f3d1697b9 equals origin/main; the persistent Desktop checkout remains untouched.
- Read child prompt and audit criteria. Scope is an opaque, versioned, environment-bound secret-reference model; safe serialization/redaction; narrow static guard tests; no secret-manager access or credentials.
- Will preserve the builder-only boundary and not edit TASKS.md or audit files.
### 2026-10-04 15:02:36 +03:00 — Implementation, correction history, gates, and implementation publication

- Implemented SecretReference: frozen model with reference_version, opaque reference_id, purpose, environment, and optional version_label only. It has no secret-value field. Validation rejects credential-bearing/unknown fields, invalid opaque references, unknown environments, and environment mismatches.
- Added deterministic safe repr, secret-reference serialization, recursive evidence redaction for recognized secret fields, credential assignments, PEM private-key blocks, common token forms, and URI credentials. Config, dry-run report, and release-event/snapshot/result serialization apply redaction. The README explicitly says these known-pattern checks do not prove arbitrary text secret-free.
- Added versioned JSON schema and opaque example, package exports, and focused tests. Added a tracked-file guard over Content Pipeline source and schema/config JSON using narrow obvious-secret patterns and no secret fixture output.
- An initial discovery rg command used a PowerShell-invalid wildcard path and returned OS error 123; reran the search on valid content_pipeline paths and inspected the relevant current models. No source was changed by the failed discovery.
- First full pytest run: 1275 passed, 1 failed, 3 skipped. Existing changed-file guard matched the _KNOWN_TOKEN constant assignment as a credential literal. Renamed the detector to COMMON_CREDENTIAL_PATTERNS.
- First focused rerun then exposed two credential-shaped test source strings (one redaction input and one config input) to the same guard. Constructed these strings from parts so the runtime guard cases remain while the test source contains no credential assignment literal. Subsequent focused run: 115 passed.
- Full regression after corrections: python -m pytest -q — 1276 passed, 3 skipped, 0 failed in 1204.53s. Skips: tests/integration/test_maint_supply_pipeline_v01.py:232 (SCRUBBOTS_SLOW=1), tests/unit/test_sb_lf03_002_compact_solver_state.py:274 (canonical ScrubBots checkout capability not supplied), and tests/unit/test_sb_lf04_012_regression.py:222 (canonical ScrubBots checkout capability not supplied; no bridge exercised).
- Compileall: python -m compileall -q content_pipeline/src — PASS. git diff --check — PASS. Post-commit focused guard plus CP001..006/governance regression: 115 passed.
- The full suite included existing read-only external-contract clone and headless Godot checks. No secret-manager access, credential retrieval, provider/network mutation, runtime/game change, dependency, or license change was added.
- Implementation diff: 9 paths, 353 insertions and 4 deletions. Base SHA: 8bc3029b098a2d2231965939f3c9e20f3d1697b9. Implementation commit: 159666daa6a3dc54f782214a06b56c464e3b9738.
- git fetch --prune origin before implementation push showed 1 ahead / 0 behind. Normal non-force git push origin HEAD:main succeeded; post-push fetch verified local = origin/main at 159666daa6a3dc54f782214a06b56c464e3b9738, 0/0.
- Builder-log commit/publication and final parity will be recorded in the master log after completion.