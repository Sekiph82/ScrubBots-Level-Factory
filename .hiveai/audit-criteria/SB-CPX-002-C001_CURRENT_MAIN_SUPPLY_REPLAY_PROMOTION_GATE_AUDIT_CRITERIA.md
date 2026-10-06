# SB-CPX-002-C001 - Current-Main Supply Replay Promotion Gate - Audit Criteria

## PASS rule

PASS only if production promotion authorization requires a fresh replay of every exact staged packaged supply plan through the exact current `Sekiph82/Scrubbots` `origin/main` game authority and any drift/failure blocks before production mutation.

## A. Current game authority

Require:
- exact repository identity `Sekiph82/Scrubbots`;
- exact fetched `origin/main` commit SHA captured immediately before replay;
- isolated TEMP clone/worktree only, never implicit owner Desktop game checkout;
- game checkout treated as disposable/read-only authority except ephemeral test runner/data inside that TEMP copy;
- authoritative loader/solver source hashes recorded;
- Godot availability required for authentic gate evidence.

## B. Exact staged content identity

For every level referenced by the verified STAGING receipt:
- exact staged manifest bytes/hash;
- exact downloaded pack bytes/hash;
- exact packaged LevelData bytes;
- exact packaged `scrubbots.level_supply_plan.v1` bytes;
- exact level ID;
- exact CPX-001 solver-proven identity/digests.

Any cross-level or stale CPX-001 identity fails.

## C. Current-main replay

Through current game main authority require:
- current `SupplyPlanLoader` accepts schema and exact plan;
- exact level binding;
- exact FIFO columns/batch IDs/CIDs/robot counts;
- exact per-color supply conservation to LevelData;
- canonical ProofState/solver path builds;
- solver status SOLVED;
- replay succeeds and ends solved with zero active remainder;
- loader/solver error, unsupported schema, inconclusive, timeout, unsolved or replay failure blocks.

## D. Authority drift fence

After all replays and immediately before returning promotion authorization:
- fetch/resolve `origin/main` again;
- require the same game commit SHA;
- require the exact loader/solver authority files used in replay remain byte-identical.

Any drift invalidates the receipt and no production mutation may occur.

## E. Receipt

Return deterministic immutable receipt containing:
- game repo identity;
- current-main commit SHA;
- authority source hashes;
- staging manifest hash/content_version;
- per-level pack/LevelData/supply-plan/CPX-001 identities;
- per-level conservation and solver/replay outcomes;
- final authority-drift check.

No credentials or free-form secret-bearing logs.

## F. Regression

Require isolated fixture tests plus one authentic current-main integration run in the builder evidence. If current-main/Godot authority cannot be resolved, STOP as a true blocker rather than claiming PASS.

No production manifest/provider mutation may be performed by this child.
