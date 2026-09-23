# SB-LF03-012-C001-R04 — Historical Regression Fidelity Closure

Document role: CODEX BUILDER LOG

## Chronology

- Start: 2026-09-23 Europe/Istanbul.
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`; branch: `main`.
- Starting HEAD: `03ca313`; origin/main matched the starting HEAD after the required fast-forward synchronization.
- Initial status contained only preserved pre-existing untracked `level_factory/**/*.uid` files; no owner work was discarded and `TASKS.md` was unchanged.
- Read the active R04 prompt, R04 remediation index, root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, the preceding R03 strict audit, the LF03 prompt index, the existing LF03 contracts, and the prior builder logs required by the prompt.

## Work log

- R04 scope is limited to the four historical regression-fidelity corrections: baseline transition authority drift, solution-count binding/foreign-child failure, attached-timeout canonical invariance, and stale LevelData source-hash rejection in the declarative canonical-bridge corpus.
- This log was created before product, fixture, test, or governance edits.
- Inspected `baseline_search.py`, `solution_analysis.py`, `solver_budget.py`, `canonical_bridge.py`, the existing LF03-012 fixture loader/tests, and the R04 verification/publication requirements.
- Added a declarative `LF03_TRANSITION_AUTHORITY_DRIFT_V1` payload whose fake transition provider returns a validly shaped child under a distinct authority. The real `BaselineSearchEngine` now proves `ERROR`, no foreign terminal traversal, and no derived verdict.
- Replaced the old move-order-only `LF03_ENUMERATION_BINDING_V1` case with the same accepted-interface foreign-child regression through `SolutionCountEngine`; it proves `ERROR`, never `EXACT`, `LOWER_BOUND`, or `INCONCLUSIVE`, and does not recurse into the foreign state.
- Extended `LF03_TIMEOUT_NONCANONICAL_V1` with an attached-timeout scenario. The deterministic classified result is compared with and without operational telemetry for canonical bytes and digest equality; timeout-before-result remains `INCONCLUSIVE` with no canonical result.
- Added declarative `LF03_LEVELDATA_STALE_HASH_TAMPER_V1`, mutating exactly one LevelData cell while retaining the original source SHA-256. The real canonical bridge regression rejects the request in `CanonicalBridgeRequest` before gameplay invocation; the valid source continues through legal_moves/apply_placement/solve.
- Recomputed canonical payload SHA-256 values for every modified negative fixture. The independent fixture loader checksum test passes and no placeholder hashes remain.

## Verification

- Focused command: `python -m pytest tests/unit/test_sb_lf03_012_regression_fixtures.py -q` -> `11 passed, 1 warning`.
- Focused dependency command: `python -m pytest tests/unit/test_sb_lf03_004_baseline_search.py tests/unit/test_sb_lf03_008_solution_analysis.py tests/unit/test_sb_lf03_009_canonical_bridge.py tests/unit/test_sb_lf03_011_solver_budget.py tests/unit/test_sb_lf03_012_regression_fixtures.py -q` -> `41 passed, 1 warning`.
- Retained LF00/LF06 command over all matching tests -> `94 passed, 1 warning`.
- Full command: `python -m pytest -q` -> `856 passed, 1 skipped, 1 warning in 167.77s`. The single legitimate skip is the retained canonical capability test when external canonical checkout configuration is not supplied; no failure was hidden with skip/xfail.
- `python -m compileall -q src tests` passed.
- `godot_console.exe --headless --path level_factory --editor --quit` exited 0 with Godot `4.7.2.stable.official`.
- `git diff --check` passed. `git diff --exit-code -- TASKS.md` passed; `TASKS.md` is unchanged.
- Real canonical bridge regression executed against a temporary clean exact-SHA canonical clone and verified repeated `legal_moves`, `apply_placement`, and `solve`; stale LevelData hash rejection occurred before gameplay execution and the canonical checkout remained unchanged.

## Scope and safety

- Changed files: `tests/fixtures/lf03_solver_regression_v1.json`, `tests/unit/test_sb_lf03_012_regression_fixtures.py`, and this builder log.
- No canonical gameplay implementation, WFC solver, dependency, license, runtime network, credential, telemetry, or task-tracker change was made.
- Existing untracked `level_factory/**/*.uid` files remain preserved and unstaged.

## Evidence

Implementation and publication SHAs are recorded after the commits below.
