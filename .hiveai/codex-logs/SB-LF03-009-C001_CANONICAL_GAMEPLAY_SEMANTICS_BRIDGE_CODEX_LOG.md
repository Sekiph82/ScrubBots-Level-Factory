# SB-LF03-009-C001 - Canonical Gameplay Semantics Bridge

Document role: CODEX BUILDER LOG

## Start and authority

- Starting timestamp: `2026-09-22T13:34:40.5449225+03:00`.
- Repository root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repository `Sekiph82/ScrubBots-Level-Factory`; branch `main`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Starting local/origin HEAD: `531e8c8c295ee2dfa6eb17c73ebe8d7aade3b648`; divergence `0 0`.
- Initial status: only pre-existing untracked `level_factory/**/*.gd.uid` files; no tracked changes.
- Canonical gameplay authority remains `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`; required ProofState source identity is `408893348e8abab089de98586999fc15bafc3b07b83f21458152788a34e78620`; accepted LF03-001..008 contracts are retained.
- Root `TASKS.md`, LF03 batch index, LF03-009 prompt/criteria, accepted predecessor contracts, and prior audits/logs were read. `TASKS.md` is protected and will not be modified.
- Environment probe: `SCRUBBOTS_CANONICAL_CHECKOUT` is unset; `godot_console.exe` is available.

## Scope decision

Add a strict read-only external runner adapter that verifies the canonical checkout HEAD, exact ProofState bytes/source contract, required authority files, request identity, and response identity before any invocation. The adapter never copies gameplay mechanics. With no configured canonical checkout and no caller-supplied external runner, production remains truthfully `UNAVAILABLE`; no simulation result will be fabricated.

## Implementation record

To be appended chronologically: implementation decisions, bridge/capability tests, retained/full tests, failed commands and corrections, checkout immutability evidence, offline/safety checks, final diff/status, implementation commit/push, terminal log-only commit/push, and final SHA equality.

## Implementation record

- Added `CanonicalHeadlessBridge` with strict request/response envelopes. It verifies canonical checkout HEAD, exact committed/working ProofState bytes, the locked source contract and required authority files before invocation.
- The adapter accepts only a caller-configured external runner outside the canonical checkout and uses temporary request/response files outside that checkout. It binds bridge version, operation, compact-state digest, LevelData source hash, payload hash, authority SHA, and ProofState source SHA.
- No gameplay logic, routing, targeting, placement, clearing, completion, solver, or WFC logic was copied into Factory Python. With `SCRUBBOTS_CANONICAL_CHECKOUT` and `SCRUBBOTS_CANONICAL_BRIDGE_RUNNER` unset, production remains `UNAVAILABLE` and no canonical result is fabricated.
- Added deterministic contract tests and a capability-gated real checkout/runner immutability fixture.

## Verification so far

- Focused `python -m pytest -q tests/unit/test_sb_lf03_009_canonical_bridge.py`: `4 passed, 1 skipped, 1 warning`; the real checkout/runner fixture skipped because both capabilities were absent.
- Retained LF03/M01/M02 regression using explicit `rg --files tests | rg 'test_(m01|m02)|test_sb_lf03'`: `127 passed, 2 skipped, 1 warning`; skips are the absent canonical checkout/runner fixture and the pre-existing compact-state canonical-checkout fixture.
- Full `python -m pytest -q`: `820 passed, 2 skipped, 1 warning` in `180.64s`; skips are the same two capability-gated fixtures. Pytest emitted only the existing Windows cache-permission warning.
- `python -m compileall -q src tests`: passed.
- `godot_console.exe --headless --editor --path . --quit`: passed; Godot `4.7.2.stable.official.ed1daf0bf` booted and exited successfully.
- `git diff --check`: passed; only a normal LF-to-CRLF working-copy notice was emitted. `git diff --exit-code -- TASKS.md`: passed.
- Offline/safety review: no canonical checkout was configured or modified; no runtime network, gameplay semantics, WFC, or dependency/license changes were added.

## Files changed

- `.hiveai/codex-logs/SB-LF03-009-C001_CANONICAL_GAMEPLAY_SEMANTICS_BRIDGE_CODEX_LOG.md`
- `docs/SB_LF03_009_CANONICAL_GAMEPLAY_SEMANTICS_BRIDGE_V1.md`
- `src/scrubbots_pixel_factory/__init__.py`
- `src/scrubbots_pixel_factory/canonical_bridge.py`
- `tests/unit/test_sb_lf03_009_canonical_bridge.py`

The pre-existing untracked `level_factory/**/*.gd.uid` files remain unstaged and untouched.

## Publication

- Implementation commit and push are pending; exact commit SHA, push result, final status, and local/origin equality will be appended after publication.
