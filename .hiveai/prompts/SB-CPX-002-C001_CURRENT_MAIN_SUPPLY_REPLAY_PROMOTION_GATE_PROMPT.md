# SB-CPX-002-C001 - Current-Main Supply Replay Promotion Gate

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Audit criteria:
`.hiveai/audit-criteria/SB-CPX-002-C001_CURRENT_MAIN_SUPPLY_REPLAY_PROMOTION_GATE_AUDIT_CRITERIA.md`

## FIRST OPERATION - mandatory GitHub ↔ Desktop synchronization

1. Verify canonical Level Factory root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repo identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone `SB-CPX-002-C001` authority or M14 master authority.
4. Preserve all owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard.
5. Use only prompt-authorized TEMP execution worktree if persistent checkout is unsafe.
6. Never use or mutate an implicitly discovered owner Desktop Scrubbots checkout.
7. Require clean 0/0 Level Factory execution authority.

## Goal

Before any STAGING -> PRODUCTION promotion, replay every exact staged packaged supply plan through the exact current `Sekiph82/Scrubbots` main-game loader + canonical solver/ProofState authority.

This child produces a promotion-gate receipt only. It performs no production mutation.

## Game authority

Create an isolated TEMP current-main authority, for example under:
`%TEMP%\ScrubBots-Level-Factory\CPX-002-GAME-AUTHORITY`

Hard rules:
- configured remote must normalize exactly to `https://github.com/Sekiph82/Scrubbots.git`;
- fetch/prune;
- checkout exact `origin/main`;
- record commit SHA;
- clean state;
- never branch/push/create PR;
- never use owner Desktop game checkout;
- no game-main mutation outside the disposable TEMP authority.

Reuse/extract the proven current-game Godot verification approach from Route A where practical rather than inventing a fake solver.

## Inputs

Require:
- CP03-007 verified staging-download receipt;
- exact downloaded staging manifest bytes;
- exact downloaded pack bytes;
- CPX-001 solver-proven identity evidence for every level.

Revalidate all receipt/byte hashes before Godot.

## Replay requirements

For every packaged level:

1. Safely inspect/extract the exact pack bytes.
2. Read exact LevelData and supply-plan bytes.
3. Require supply schema `scrubbots.level_supply_plan.v1`.
4. Require exact level ID and CPX-001 byte/digest identity.
5. In the current-main TEMP game authority, execute a Godot headless verifier using current:
   - `scripts/gameplay/supply/supply_plan_loader.gd`;
   - canonical ProofState;
   - canonical SolvabilitySolver/solver entry point actually used by current game.
6. Require SupplyPlanLoader acceptance.
7. Require exact FIFO/batch/CID/robot-count binding.
8. Recompute exact per-color demand from LevelData and supply totals from plan; require equality.
9. Require solver `SOLVED`.
10. Require replay `ok=true`, solved=true, zero active/unresolved remainder.

Do not substitute the Python screening solver for current-game authority.

## Drift fence

After every level passes:
- fetch current Scrubbots origin/main again;
- require remote main SHA unchanged;
- require loader/ProofState/solver authority source hashes unchanged;
- only then emit PASS receipt.

Any drift means STALE_GAME_AUTHORITY and promotion remains blocked.

## Tests

Add deterministic fixture tests for:
- schema rejection;
- level mismatch;
- CPX-001 digest mismatch;
- per-color mismatch;
- loader rejection;
- UNSOLVED/INCONCLUSIVE/ERROR/timeout;
- replay failure;
- game-main SHA drift;
- authority source drift;
- multi-level all-pass requirement.

Also run one authentic current `Sekiph82/Scrubbots` origin/main integration replay with Godot during builder verification. If unavailable, stop as a true blocker.

## Builder log

`.hiveai/codex-logs/SB-CPX-002-C001_CURRENT_MAIN_SUPPLY_REPLAY_PROMOTION_GATE_CODEX_LOG.md`

Record current game SHA and source hashes, but no credentials/secrets.

## Verification/publication

Run focused CPX-002, prior M14, M13/M12/M11, governance, safe full pytest, compileall, JSON parse and diff check.

Do not edit `TASKS.md` or audits. Separate implementation/log commits, normal non-force main publication, 0/0 clean parity.

Standalone mode stops for ChatGPT audit. M14 master mode continues to `SB-CP03-008-C001` only if authentic CPX-002 gate evidence passes.

## Final response

Return only the builder log URL.
