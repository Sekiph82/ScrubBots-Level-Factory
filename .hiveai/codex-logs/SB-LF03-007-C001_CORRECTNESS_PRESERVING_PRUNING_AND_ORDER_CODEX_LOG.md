# SB-LF03-007-C001 - Correctness-Preserving Pruning and Order

Document role: CODEX BUILDER LOG

## Start and authority

- Starting timestamp: `2026-09-22T13:13:30.8243357+03:00`.
- Repository root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repository `Sekiph82/ScrubBots-Level-Factory`; branch `main`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Starting local/origin HEAD: `8c55d6fb7928a73b7f8e45db5f29b6fd8229a117`; divergence `0 0`.
- Initial status: only pre-existing untracked `level_factory/**/*.gd.uid` files; no tracked changes.
- Canonical gameplay authority remains `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`; accepted LF03-001..006 contracts are retained.
- Root `TASKS.md`, LF03 batch index, LF03-007 prompt/criteria, accepted predecessor contracts, and prior audits/logs were read. `TASKS.md` is protected and will not be modified.

## Scope decision

Add explicit deterministic, versioned, opt-in ordering and pruning policy objects around the provider-defined baseline search. Preserve a selectable baseline control; use only provider-order/reverse-order traversal and proof-safe canonical-key duplicate suppression when an explicit key provider is available. Do not add gameplay semantics, difficulty heuristics, WFC logic, or fabricated bounded verdicts.

## Implementation record

To be appended chronologically: implementation decisions, changed files, focused/retained/full tests, failed commands and corrections, offline/safety checks, final diff/status, implementation commit/push, terminal log-only commit/push, and final SHA equality.

## Implementation record

- Added immutable `MoveOrderingPolicy`, `PruningPolicy`, and `SearchPolicy` contracts. `PROVIDER_ORDER_V1` preserves the baseline control; `REVERSE_PROVIDER_ORDER_V1` is a deterministic opt-in traversal. Pruning is explicitly `NONE_V1` because no additional proof-safe pruning protocol is justified at this boundary.
- Extended baseline search to consume only the selected policy over provider-produced moves. Extended solver evidence to record the selected ordering/pruning policy canonically. No gameplay semantics, WFC logic, difficulty heuristic, or canonical-key reimplementation was added.
- Added paired solved, exhaustive unsolved, bounded, repeated-state, immutability, and policy-recording fixtures plus durable documentation.

## Verification so far

- Focused `python -m pytest -q tests/unit/test_sb_lf03_007_search_policy.py`: `6 passed, 1 warning`.
- First retained command `python -m pytest -q tests/unit/test_sb_lf03_*.py tests/unit/test_sb_lf02_*.py tests/unit/test_sb_lf01_*.py` failed because PowerShell passed the literal wildcard path to pytest. Correction used `rg --files` to enumerate `test_sb_lf0[123]_*.py`; corrected run: `94 passed, 1 skipped, 1 warning`.
- Corrected LF03/M01/M02 retained regression using explicit `rg --files tests | rg 'test_(m01|m02)|test_sb_lf03'`: `116 passed, 1 skipped, 1 warning`; the skip is the existing capability-gated canonical-checkout test because `SCRUBBOTS_CANONICAL_CHECKOUT` was not supplied.
- Full `python -m pytest -q`: `809 passed, 1 skipped, 1 warning` in `229.98s`; the skip is the same capability-gated canonical-checkout test. Pytest emitted only the existing Windows cache-permission warning.
- `python -m compileall -q src tests`: passed.
- `godot_console.exe --headless --editor --path . --quit`: passed; Godot `4.7.2.stable.official.ed1daf0bf` booted and exited successfully.
- `git diff --check`: passed; only normal LF-to-CRLF working-copy notices were emitted. `git diff --exit-code -- TASKS.md`: passed.
- Offline/safety review: no runtime network, provider, gameplay semantic, WFC, or dependency/license changes; canonical gameplay bridge remains unavailable and no fabricated gameplay verdicts are produced.

## Files changed

- `.hiveai/codex-logs/SB-LF03-007-C001_CORRECTNESS_PRESERVING_PRUNING_AND_ORDER_CODEX_LOG.md`
- `docs/SB_LF03_007_CORRECTNESS_PRESERVING_PRUNING_AND_ORDER_V1.md`
- `src/scrubbots_pixel_factory/__init__.py`
- `src/scrubbots_pixel_factory/baseline_search.py`
- `src/scrubbots_pixel_factory/search_policy.py`
- `src/scrubbots_pixel_factory/solver_evidence.py`
- `tests/unit/test_sb_lf03_007_search_policy.py`

The pre-existing untracked `level_factory/**/*.gd.uid` files remain unstaged and untouched.

## Publication

- Implementation commit and push are pending; exact commit SHA, push result, final status, and local/origin equality will be appended after publication.
