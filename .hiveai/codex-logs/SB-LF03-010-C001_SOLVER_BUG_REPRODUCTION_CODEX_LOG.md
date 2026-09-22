# SB-LF03-010-C001 - Solver Bug Reproduction by Candidate/Seed/Config/Version

Document role: CODEX BUILDER LOG

## Start and authority

- Starting timestamp: `2026-09-22T13:42:27.6390059+03:00`.
- Repository root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repository `Sekiph82/ScrubBots-Level-Factory`; branch `main`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Starting local/origin HEAD: `17eb5e05fd3000871b3b64bf3992d7b4efaf4eda`; divergence `0 0`.
- Initial status: only pre-existing untracked `level_factory/**/*.gd.uid` files; no tracked changes.
- Canonical gameplay authority remains `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`; accepted LF03-001..009 contracts are retained.
- Root `TASKS.md`, LF03 batch index, LF03-010 prompt/criteria, accepted predecessor contracts, and prior audits/logs were read. `TASKS.md` is protected and will not be modified.

## Scope decision

Add a closed, versioned deterministic reproduction manifest/bundle binding candidate and LevelData hashes, seed/config/generator identity, canonical authority/source identity, provider/bridge/search/memo/order/pruning versions, deterministic budgets, operation/goal, observed disposition, and evidence/path identity. Replay compares observations from existing provider/search/bridge layers and returns MATCH, DIVERGED, UNAVAILABLE, or ERROR without regenerating source artifacts or persisting paths/secrets.

## Implementation record

To be appended chronologically: implementation decisions, focused/retained/full tests, failed commands and corrections, offline/safety checks, final diff/status, implementation commit/push, terminal log-only commit/push, and final SHA equality.

## Implementation record

- Added closed-schema `ReproductionManifest` and `ReproductionBundle` contracts binding candidate/LevelData hashes, seed, normalized secret/path-safe config, generator version, exact canonical authority/source contract, provider/bridge/search/memo/order/pruning versions, deterministic solution-analysis budgets, operation/goal, expected disposition, evidence digest, and path.
- Added `ReproductionReplay` with explicit `MATCH`, `DIVERGED`, `UNAVAILABLE`, and `ERROR` outcomes. Replay accepts observations from existing provider/search/bridge layers only; it never regenerates source artifacts or reimplements gameplay.
- Added deterministic manifest-byte, replay-match, seed/config/version divergence, tamper, authority drift, unavailable, secret/path rejection, and no-gameplay-implementation tests plus durable documentation.
- Added `docs/SB_LF03_010_SOLVER_BUG_REPRODUCTION_V1.md` to make the replay/bundle identity, drift-failure, unavailable, and no-gameplay-reimplementation boundaries explicit.

## Verification so far

- Focused `python -m pytest -q tests/unit/test_sb_lf03_010_reproduction.py`: `6 passed, 1 warning`.
- Retained LF03/M01/M02 regression using explicit `rg --files tests | rg 'test_(m01|m02)|test_sb_lf03'`: `133 passed, 2 skipped, 1 warning`; skips are the absent canonical checkout/runner fixture and the pre-existing compact-state canonical-checkout fixture.
- Full `python -m pytest -q`: `826 passed, 2 skipped, 1 warning` in `167.35s`; skips are the same two capability-gated fixtures. Pytest emitted only the existing Windows cache-permission warning.
- `python -m compileall -q src tests`: passed.
- `godot_console.exe --headless --editor --path . --quit`: passed; Godot `4.7.2.stable.official.ed1daf0bf` booted and exited successfully.
- `git diff --check`: passed; only a normal LF-to-CRLF working-copy notice was emitted. `git diff --exit-code -- TASKS.md`: passed.
- Final focused retest after adding documentation: `python -m pytest -q tests/unit/test_sb_lf03_010_reproduction.py`: `6 passed, 1 warning`.
- Offline/safety review: no runtime network, source regeneration, gameplay semantic, WFC, or dependency/license changes; no secrets or absolute machine paths are persisted in the bundle.

## Files changed

- `.hiveai/codex-logs/SB-LF03-010-C001_SOLVER_BUG_REPRODUCTION_CODEX_LOG.md`
- `docs/SB_LF03_010_SOLVER_BUG_REPRODUCTION_V1.md`
- `src/scrubbots_pixel_factory/__init__.py`
- `src/scrubbots_pixel_factory/reproduction.py`
- `tests/unit/test_sb_lf03_010_reproduction.py`

The pre-existing untracked `level_factory/**/*.gd.uid` files remain unstaged and untouched.

## Publication

- Implementation commit and push are pending; exact commit SHA, push result, final status, and local/origin equality will be appended after publication.
