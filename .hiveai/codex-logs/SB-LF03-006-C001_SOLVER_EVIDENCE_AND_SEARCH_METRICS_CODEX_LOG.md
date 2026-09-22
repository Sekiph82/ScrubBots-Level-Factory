# SB-LF03-006-C001 - Solver Evidence and Search Metrics

Document role: CODEX BUILDER LOG

## Start and authority

- Starting timestamp: `2026-09-22T13:01:54.9981845+03:00`.
- Repository root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repository `Sekiph82/ScrubBots-Level-Factory`; branch `main`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Starting local/origin HEAD: `17d005940ab6fdedb09e36920a7e6802ab2a398f`; divergence `0 0`.
- Initial status: only pre-existing untracked `level_factory/**/*.gd.uid` files; no tracked changes.
- Canonical gameplay authority remains `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`; accepted LF03-001..005 contracts are retained.
- Root `TASKS.md`, LF03 batch index, LF03-006 prompt/criteria, accepted predecessor contracts, and prior audits/logs were read. `TASKS.md` is protected and will not be modified.

## Scope decision

Extend the accepted deterministic search with bounded, immutable evidence of the executed fixture/provider traversal: ordered canonical move path, state references, visited nodes, memo hits when an explicit memo observer is supplied, dead ends, depth, branch counts, and frontier peak. Record monotonic elapsed time only as non-canonical telemetry and exclude it from canonical identity. Production unavailable runs will carry no fabricated zero metrics. No heuristics, pruning, solution counting, difficulty, gameplay semantics, WFC, or runtime network behavior will be added.

## Implementation record

To be appended chronologically: implementation decisions, changed files, focused/retained/full tests, failed commands and corrections, offline/safety checks, final diff/status, implementation commit/push, terminal log-only commit/push, and final SHA equality.

## Implementation record

- Extended `baseline_search.py` with an optional observation hook without changing its provider-only search semantics.
- Added `solver_evidence.py` with bounded deterministic metrics, ordered path/state references, optional opaque-key memo-hit observation, separate unavailable evidence behavior, and monotonic non-canonical telemetry excluded from canonical bytes/digest.
- Added fixture tests and durable documentation; exported the evidence boundary through the package root.
- Initial focused test run found one metrics expectation failure (`dead_end_count` did not include a provider-reported `PROVEN_UNSOLVABLE` terminal). The collector was corrected to count that observed terminal, and the corrected focused suite passed `4 passed`.

## Verification so far

- Corrected focused `python -m pytest -q tests/unit/test_sb_lf03_006_solver_evidence.py`: `4 passed, 1 warning`.

- Retained LF03 plus M01/M02 regression `python -m pytest -q tests/unit/test_sb_lf03_*.py tests/unit/test_sb_lf02_*.py tests/unit/test_sb_lf01_*.py`: `184 passed, 1 skipped, 1 warning`; the skip is the existing capability-gated canonical-checkout test because `SCRUBBOTS_CANONICAL_CHECKOUT` was not supplied.
- Full `python -m pytest -q`: `803 passed, 1 skipped, 1 warning` in `248.39s`; the skip is the same capability-gated canonical-checkout test. Pytest emitted only the existing Windows cache-permission warning.
- `python -m compileall -q src tests`: passed.
- `godot_console.exe --headless --editor --path . --quit`: passed; Godot `4.7.2.stable.official.ed1daf0bf` booted and exited successfully.
- `git diff --check`: passed; only normal LF-to-CRLF working-copy notices were emitted. `git diff --exit-code -- TASKS.md`: passed.
- Offline/safety review: no runtime network, provider, gameplay semantic, WFC, or dependency/license changes; canonical gameplay bridge remains unavailable and no fabricated simulation metrics are emitted.

## Files changed

- `.hiveai/codex-logs/SB-LF03-006-C001_SOLVER_EVIDENCE_AND_SEARCH_METRICS_CODEX_LOG.md`
- `docs/SB_LF03_006_SOLVER_EVIDENCE_AND_SEARCH_METRICS_V1.md`
- `src/scrubbots_pixel_factory/__init__.py`
- `src/scrubbots_pixel_factory/baseline_search.py`
- `src/scrubbots_pixel_factory/solver_evidence.py`
- `tests/unit/test_sb_lf03_006_solver_evidence.py`

The pre-existing untracked `level_factory/**/*.gd.uid` files remain unstaged and untouched.

## Publication

- Implementation commit and push are pending; the exact commit SHA, push result, final status, and local/origin equality will be appended after publication.
