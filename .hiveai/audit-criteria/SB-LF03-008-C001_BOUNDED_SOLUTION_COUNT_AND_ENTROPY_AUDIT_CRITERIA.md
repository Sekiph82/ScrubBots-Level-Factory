# SB-LF03-008-C001 - Bounded Solution Count / Entropy Analysis - Strict Audit Criteria

Target:
`SB-LF03-008 - Add bounded solution-count/entropy analysis.`

## Definition

Count canonical legal decision sequences leading to canonical solved terminal states.

Do not count UI actions, target choices or internal forced kernel operations as player solutions.

## Bounded truth

The analysis must distinguish:
- `EXACT`: reachable relevant search space exhaustively counted within configured deterministic bounds;
- `LOWER_BOUND`: at least N solutions found but counting stopped at a solution cap;
- `INCONCLUSIVE`: state/depth/provider bound prevents a reliable exact count;
- `UNAVAILABLE` / `ERROR`.

Never label a bounded count as exact unless exhaustion is proven.

## Entropy

If entropy is reported, define and version it.

Recommended base measure:
`log2(solution_count)` only for exact positive counts.

For lower-bound counts, label entropy as lower-bound/advisory, never exact difficulty.

Zero exact solutions may be represented explicitly without logarithm.

Entropy is analysis evidence, not Difficulty V1.

## Deduplication

Define whether identical move sequences reaching equivalent states are distinct solutions.

The chosen definition must be deterministic, documented, and tested.

Do not use Factory structural digest as gameplay equivalence unless canonical key authority provides it.

## Required tests

Fixtures:
- exactly one solution;
- multiple known solutions;
- zero-solution exhaustive fixture;
- solution-cap lower bound;
- depth/state bound inconclusive;
- deterministic repeat.

## PASS

PASS when counting/entropy are bounded, versioned, deterministic and never overclaim exactness.
