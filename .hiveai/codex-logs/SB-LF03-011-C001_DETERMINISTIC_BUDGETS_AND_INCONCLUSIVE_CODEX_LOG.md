# SB-LF03-011-C001 - Deterministic Budgets / UNSOLVED vs INCONCLUSIVE

Document role: CODEX BUILDER LOG

## Start and authority

- Starting timestamp: `2026-09-22T21:01:48.5827589+03:00`.
- Repository root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repository `Sekiph82/ScrubBots-Level-Factory`; branch `main`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Starting local/origin HEAD: `9754c0942a5375aa003add40566690e631ed6ac2`; divergence `0 0`.
- Synchronization: `git fetch origin main` followed by `git merge --ff-only origin/main`; already up to date.
- Initial status: only pre-existing untracked `level_factory/**/*.gd.uid` files; no tracked changes.
- Canonical gameplay authority remains `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`; LF03-001..010 contracts are retained.
- Root `TASKS.md`, LF03 batch index, LF03-011 prompt/criteria, and existing LF03 search/evidence/reproduction contracts were read. `TASKS.md` is protected and will not be modified.

## Scope decision

Define a versioned deterministic budget policy and explicit solver outcome mapping. Budget/depth/state/solution exhaustion and provider `UNKNOWN_BOUND` must be `INCONCLUSIVE`, never `PROVEN_UNSOLVABLE`; optional operational timeout is telemetry/kill-switch evidence that also maps to `INCONCLUSIVE`.

## Implementation record

- Added `src/scrubbots_pixel_factory/solver_budget.py` with versioned `SolverBudgetPolicy`, explicit `SolverOutcomeDisposition`, budget-exhaustion reasons, operational timeout policy identity, and classification helpers for baseline search and solution-count evidence.
- Integrated budget policy/outcome evidence into `SolverEvidenceReport.canonical_dict()` and `EvidenceSearchEngine`; timing telemetry remains non-canonical while deterministic budgets are included in canonical evidence.
- Integrated reproduction manifests with `SolverBudgetPolicy` while normalizing existing `SolutionAnalysisBounds` inputs to the versioned policy.
- Preserved child inconclusive reasons in `BaselineSearchEngine` so parent branches do not obscure deterministic depth exhaustion.
- Added `docs/SB_LF03_011_DETERMINISTIC_BUDGETS_AND_INCONCLUSIVE_V1.md` and `tests/unit/test_sb_lf03_011_solver_budget.py`.
- No gameplay move generation, placement, clearing, routing, canonical key, solver difficulty, or WFC semantics were added.

## Failed command and correction

- Initial focused `python -m pytest -q tests/unit/test_sb_lf03_011_solver_budget.py`: `1 failed, 5 passed, 2 warnings`. The failure showed `BaselineSearchEngine` returned a generic parent-branch inconclusive reason, hiding child depth exhaustion from the budget classifier.
- Correction: preserved the first child `INCONCLUSIVE` reason when unwinding provider-driven DFS. Retest: `6 passed, 1 warning`.

## Verification

- Focused `python -m pytest -q tests/unit/test_sb_lf03_011_solver_budget.py`: `6 passed, 1 warning`.
- Neighbor regression `python -m pytest -q tests/unit/test_sb_lf03_004_baseline_search.py tests/unit/test_sb_lf03_006_solver_evidence.py tests/unit/test_sb_lf03_010_reproduction.py`: `16 passed, 1 warning`.
- Retained LF03/M01/M02 regression using explicit `rg --files tests | rg 'test_(m01|m02)|test_sb_lf03'`: `139 passed, 2 skipped, 1 warning`; skips are the absent canonical checkout/runner fixture and the pre-existing compact-state canonical-checkout fixture.
- Full `python -m pytest -q`: `832 passed, 2 skipped, 1 warning` in `151.49s`; skips are the same two capability-gated fixtures. Pytest emitted only the existing Windows cache-permission warning.
- `python -m compileall -q src tests`: passed.
- `godot_console.exe --headless --editor --path . --quit`: passed; Godot `4.7.2.stable.official.ed1daf0bf` booted and exited successfully.
- `git diff --check`: passed; only normal LF-to-CRLF working-copy notices were emitted. `git diff --exit-code -- TASKS.md`: passed.
- Offline/safety review: no runtime network, source regeneration, gameplay semantic, WFC, dependency, or license changes.

## Files changed

- `.hiveai/codex-logs/SB-LF03-011-C001_DETERMINISTIC_BUDGETS_AND_INCONCLUSIVE_CODEX_LOG.md`
- `docs/SB_LF03_011_DETERMINISTIC_BUDGETS_AND_INCONCLUSIVE_V1.md`
- `src/scrubbots_pixel_factory/__init__.py`
- `src/scrubbots_pixel_factory/baseline_search.py`
- `src/scrubbots_pixel_factory/reproduction.py`
- `src/scrubbots_pixel_factory/solver_budget.py`
- `src/scrubbots_pixel_factory/solver_evidence.py`
- `tests/unit/test_sb_lf03_011_solver_budget.py`

The pre-existing untracked `level_factory/**/*.gd.uid` files remain unstaged and untouched.

## Publication

- Implementation commit and push are pending; exact commit SHA, push result, final status, and local/origin equality will be appended after publication.
