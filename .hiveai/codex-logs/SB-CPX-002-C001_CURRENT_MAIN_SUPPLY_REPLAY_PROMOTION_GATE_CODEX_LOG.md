# SB-CPX-002-C001 - Current-Main Supply Replay Promotion Gate

Document role: CODEX BUILDER LOG

## Start and synchronization preflight

- Starting timestamp: `2026-10-06T22:34:57+03:00`.
- Canonical Level Factory root verified: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; branch `main`; persistent HEAD `7c6051589d0a95fc785d7f182ccd0d7f8d7013ce`.
- Ran `git fetch --prune origin` in the persistent checkout. `origin/main` is `a30f957b2ff848616ea4cb8bd62641bdf151e78b`; persistent state is 0 ahead / 374 behind with 177 dirty paths (123 tracked, 54 untracked), 18 stashes and 22 worktree entries. Owner-local data remains untouched.
- Reused the authorized TEMP M14 worktree `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\M14-CP03-001-012-CPX002-MASTER`, clean and 0/0 with `origin/main` at `a30f957b2ff848616ea4cb8bd62641bdf151e78b` before CPX-002.
- Read current `origin/main:TASKS.md`; M14 remains the current authorized master sequence and lists CPX-002 immediately after CP03-007. Read the live CPX-002 prompt from `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-CPX-002-C001_CURRENT_MAIN_SUPPLY_REPLAY_PROMOTION_GATE_PROMPT.md`, its audit criteria, M14 master prompt, `AGENTS.md`, and `GOVERNANCE.md`.
- This child builder log was created before implementation or product tests. The mandatory authentic-current-game/Godot availability gate will be established before implementation; if the exact current-main authority or Godot replay cannot be resolved, record the true blocker and stop without fabricating evidence.

## Contracts and evidence

- Before implementation, inspect CP03-007 receipt, CPX-001 solver identity evidence, the approved Route A current-game verifier approach, current `Sekiph82/Scrubbots` origin/main authority, and exact loader/ProofState/solver source contracts. Use only the prompt-authorized isolated TEMP game authority; never inspect or mutate an owner Desktop Scrubbots checkout.

## Contracts and current-main authority

- Read the live CPX-002 prompt and audit criteria from the authorized GitHub URL, the M14 master sequence, CP03-007 exact-byte staging verification, CPX-001 artifact binding/verification, the Route A current-game verifier, and the game’s LevelLoader, SupplyPlanLoader, ProofState, SolvabilitySolver, and ProofKernel sources.
- Authorized game authority: `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\CPX-002-GAME-AUTHORITY`; origin is exactly `https://github.com/Sekiph82/Scrubbots.git`; fetched `origin/main` and detached HEAD are both `2fd60ae69055c6c26c1f5f1b9d3869c743093786`; state is clean. Godot is `4.7.2.stable.official.ed1daf0bf`.
- Current authority source hashes at final recheck:
  - `scripts/data/level_loader.gd`: `2116e86da8464babc6c29fb4ea9cf7d1d9b8d54cda85c07dba7b475545d7c897`
  - `scripts/gameplay/supply/supply_plan_loader.gd`: `def8b2297e9448ee81ce487e78c6999cc9156b276c0d86de093cbc2a915c3fe1`
  - `scripts/gameplay/solver/proof_state.gd`: `3376d5efc329f239e5e8076b61a09caa5d1056c6a9ce4156e0ceef04b88720a8`
  - `scripts/gameplay/solver/solvability_solver.gd`: `92bfa3dde8051bf52e38c956ace044d3cdfe4ab2050be1687c5f178fe1d0d112`
  - `scripts/gameplay/solver/proof_kernel.gd`: `937b8b486727c3db6aaaf88d01bd7fad04ba8ef11495ecc586b77be1a655ff16`

## Implementation and chronological verification

- Added a pure Content Pipeline gate that validates the CP03-007 verified receipt, exact manifest and downloaded pack bytes, M12 archive evidence, CPX-001 solver identity artifacts, level/plan schema and digest identity, exact FIFO columns, current-game solver result, full replay, empty slots/active state, and supply exhaustion. A second authority snapshot must match the first before a frozen STAGING receipt is returned.
- Added `scripts/cpx002_current_main_replay_adapter.py` for process/filesystem boundaries: it requires a clean TEMP checkout at exact fetched `origin/main` with the canonical remote, hashes the loader/solver sources before and after replay, writes exact verified member bytes into an isolated job directory, invokes the external Godot harness, and classifies errors/timeouts fail-closed. The game repository is not modified by this adapter.
- Extended CP02-009 pack-reference validation to verify a present CPX-001 solver identity artifact along with the exact pack, so a solver-proven M12 build remains eligible for the CP03-007 staging readback path.
- Added `tests/fixtures/cpx002_current_main_replay.gd`. It calls current-main LevelLoader, SupplyPlanLoader (including real Cxx palette mapping and per-color/grand conservation), ProofState, SolvabilitySolver, ProofKernel and solver replay. It requires exact level/plan SHA, FIFO, CPX state/evidence digests, `SOLVED`, replay success, zero active/occupied slots, and exhausted supply. Python screening is not substituted for game authority.
- Early harness attempts: an initial Godot executable path did not exist; corrected to the installed `godot_console.exe`. The first GDScript compile found an uninferable boolean; annotated it. The canonical current game then passed a real Godot replay of `level_003_palm_tree`, with exact level/plan hashes, SOLVED, replay true, active 0, unresolved 0, supply exhausted.
- Initial focused test iteration had assertion/setup failures; corrected the fixture callbacks and timeout expectation. Final focused CPX-002 unit tests: **6 passed**; combined new CPX-002 plus two package-boundary governance tests: **30 passed**. Authentic end-to-end integration generated a real Factory READY/owner-accepted CPX-001 solver-proven pack, built and byte-verified a CP03-007 staging readback, then replayed it through current-main Godot: **1 passed**.
- One early end-to-end attempt omitted `SCRUBBOTS_PROJECT`; the Factory’s configured default selected `C:\Users\sekip\Desktop\ScrubBots` for the solver bridge and the resulting CPX-001 authority SHA was correctly rejected as mismatched. I stopped using that result and explicitly set `SCRUBBOTS_PROJECT` to the authorized TEMP game authority on every subsequent run. The first attempt used the checkout only through the existing solver bridge and did not invoke a game-repository mutation path; ignored/local Godot cache state was not inspected or cleaned because the Desktop checkout is outside this task’s authority. This was an execution-boundary error and is recorded here for independent review.
- First cumulative run exposed the Content Pipeline static boundary checks rejecting `subprocess` and dynamic imports inside its package (**2 failed, 1,425 passed, 4 skipped**). Moved Git/Godot/filesystem orchestration to the root adapter and kept the package gate byte-oriented with injected authority/game callbacks. Corrected run: **1,427 passed, 4 skipped in 174.50s**.
- First required unfiltered run: **1,624 passed, 19 skipped in 653.14s**. After adding explicit two-level all-pass and authority source-hash drift cases, final required unfiltered rerun: **1,625 passed, 19 skipped in 632.14s**. The 19 skips are the repository’s explicit missing canonical-game/Godot capability cases; the new CPX-002 real current-main integration passed in both runs.
- `python -m compileall -q content_pipeline/src src scripts tests` passed; all **16** Content Pipeline JSON files parsed; `git diff --check` passed (Windows LF-to-CRLF notices only). No dependency/license changes, provider access, STAGING/PRODUCTION mutation, tracker edit, audit edit, or authorized TEMP game source change was made.
- Final `git fetch --prune` authority check on the TEMP game retained HEAD/origin/main SHA `2fd60ae69055c6c26c1f5f1b9d3869c743093786`, clean status, and unchanged source hashes above. Level Factory execution worktree remains at initial CPX-002 base `a30f957b2ff848616ea4cb8bd62641bdf151e78b` pending its separate implementation and evidence commits.
- Product implementation commit: `bffe95ed47c3d5daf9a6ff270cd29837150af2a0`. Normal `git push origin HEAD:main` succeeded. Post-push fetch confirmed `HEAD == origin/main == bffe95ed47c3d5daf9a6ff270cd29837150af2a0`, 0/0; only child/master builder logs remain modified/untracked for their separate evidence publication. No tracker/audit changes.
- Builder-log evidence commit and final parity confirmation will be appended after the separate log publication.
- Separate child/master builder-log evidence commit: `16aa8593775ef8d72265ad1b2baf90c1842cb9b5`; normal push succeeded, and post-push fetch confirmed clean `HEAD == origin/main == 16aa8593775ef8d72265ad1b2baf90c1842cb9b5`, 0/0. CPX-002 current-main builder gate passed; M14 master sequence continues immediately at CP03-008.
