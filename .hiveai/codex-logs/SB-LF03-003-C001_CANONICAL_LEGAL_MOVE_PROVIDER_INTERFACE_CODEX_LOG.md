# SB-LF03-003-C001 — Canonical Legal-Move Provider Interface

Document role: CODEX BUILDER LOG

## Start and authority

- Starting timestamp: `2026-09-22T12:35:35.0167566+03:00`.
- Repository root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Repository identity: `Sekiph82/ScrubBots-Level-Factory`; branch `main`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Starting local/origin HEAD: `6bf21712485dd261fa30a4d0bd3a823eb0529c68`; divergence `0 0`.
- Initial status: only pre-existing untracked `level_factory/**/*.gd.uid` files; no tracked changes.
- Existing worktrees and stashes were inspected and left unchanged. No reset, rebase, force-push, clean, stash, or discard operation was used.
- Root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, the SB-LF03-002-R01 strict audit, the indexed SB-LF03-003 prompt/criteria, accepted `simulation_boundary.py`, and accepted `compact_solver_state.py` were read before implementation.
- Current canonical gameplay authority resolved at start: `https://github.com/Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`.
- Required canonical source identities inspected:
  - `scripts/gameplay/solver/proof_state.gd` SHA-256 `408893348e8abab089de98586999fc15bafc3b07b83f21458152788a34e78620`.
  - `scripts/gameplay/solver/proof_kernel.gd` SHA-256 `c96d0c4add15488504166b8cd3a03457a05457e2b8c62fd6488b61efa00db294`.
  - `scripts/gameplay/solver/solvability_solver.gd` SHA-256 `7cbedb3be2eef0d267e910c9f1784aa3aaf6426224a8365a23bd2122f4d74ce7`.
  - `scripts/gameplay/slots/slot_batch_state.gd` SHA-256 `462918bae4290a255ae9bfb1da99dc8dbd2f155ef1fee59e80801643b90e14c9`.
  - `scripts/gameplay/slots/five_slot_batch_engine.gd` SHA-256 `3d15f54024e4914580282a34b710d3bd450f036e2f089d178271aced4e9abb77`.
  - `scripts/gameplay/supply/batch_supply_engine.gd` SHA-256 `71eb456d8f5e03faef0c95bf6d6cfa619ecbe8c7502056f60b401c1fbeebe019`.

## Scope decision

Implement only an immutable/versioned legal-move provider interface and truthful production capability boundary. The Factory will transport canonical column/front moves returned by a verified provider, never derive them from supply/slot state. No move application, child-state generation, search, canonical-key implementation, solution/deadlock classification, metrics, difficulty, WFC coupling, provider credits, or runtime network dependency will be added.

Because no stable canonical main-game invocation path is configured in this Level Factory checkout, the production adapter will remain explicit `UNAVAILABLE`. Test-only fixtures will validate schemas and dispatch without being exported or selected as gameplay authority.

## Implementation record

To be appended chronologically: implementation decisions, changed files, focused/retained/full tests, failed commands and corrections, offline/safety checks, final diff/status, implementation commit/push, terminal log-only commit/push, and final SHA equality.

## Implementation record

- Added `src/scrubbots_pixel_factory/legal_move_provider.py` with immutable/versioned query, canonical column/front move, provider capability/evidence, result, and protocol types.
- Added `CanonicalLegalMoveProvider` as a truthful production boundary. It reuses the accepted authority/source verification gates but remains `UNAVAILABLE` because no stable canonical headless executor is configured; it never derives or fabricates moves.
- Added focused tests and durable boundary documentation. Exported only the provider contract through the package root; test-only fixtures remain local to the test module.
- No move application, child-state transition, canonical-key/memoization, search, solver verdict, difficulty, WFC, provider, or runtime network behavior was added.

## Verification so far

- Focused `python -m pytest -q tests/unit/test_sb_lf03_003_legal_move_provider.py`: `7 passed, 1 warning`.
- Retained LF03 + M01/M02/LevelData immutability set including SB-LF03-001, SB-LF03-002, SB-LF03-003: `169 passed, 1 skipped, 1 warning`; the skip is the existing capability-gated real canonical checkout test because `SCRUBBOTS_CANONICAL_CHECKOUT` is not supplied.
- No provider credits, credentials, main-game writes, or runtime network dependency were used.

## Final verification and publication

- Full `python -m pytest -q`: `788 passed, 1 skipped, 1 warning` in `210.80s`; the only skip is the capability-gated canonical checkout test because `SCRUBBOTS_CANONICAL_CHECKOUT` is not supplied. Warning is the known pytest-cache `WinError 5` permission warning.
- `python -m compileall -q src tests`: passed.
- `godot_console.exe --headless --path level_factory --editor --quit`: Godot 4.7.2 exit `0`.
- `git diff --check`: passed. `git diff --exit-code -- TASKS.md`: empty/passed.
- Implementation scope is limited to this provider contract, package export, tests, docs, and this builder log. Pre-existing `.uid` files remain untracked and untouched; no dependencies/licenses changed.
- Implementation commit, push result, terminal log-only commit, and final local/remote equality will be appended after publication.
