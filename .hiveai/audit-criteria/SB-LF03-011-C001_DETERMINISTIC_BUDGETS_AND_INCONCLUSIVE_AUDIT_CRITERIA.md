# SB-LF03-011-C001 - Deterministic Budgets / UNSOLVED vs INCONCLUSIVE - Strict Audit Criteria

Target:
`SB-LF03-011 - Define budgets/timeouts and UNSOLVED vs INCONCLUSIVE.`

## Required semantic separation

The Level Factory must never equate budget exhaustion with proven unsolvability.

Canonical mapping should preserve main-game truth:
- canonical SOLVED -> SOLVED;
- exhaustive canonical DEADLOCK/no-completion proof -> PROVEN_UNSOLVABLE or equivalent;
- canonical UNKNOWN_BOUND, deterministic state/depth bound exhaustion, provider interruption or operational timeout -> INCONCLUSIVE;
- provider unavailable -> UNAVAILABLE;
- malformed execution -> ERROR.

Do not invent a plain ambiguous `UNSOLVED` that conflates proof failure with inconclusive search.

## Deterministic budgets

Primary proof budgets must be deterministic, such as:
- max visited states;
- max depth;
- max solutions;
- other versioned operation counts.

Wall-clock timeout is allowed only as operational safety:
- monotonic;
- separately recorded;
- maps to INCONCLUSIVE;
- cannot produce PROVEN_UNSOLVABLE;
- must not be part of canonical replay identity unless explicitly versioned as an operational policy.

## Validation

Reject zero/negative/boolean/non-integer deterministic bounds where invalid.

Budgets must be versioned and included in reproduction evidence.

## Tests

Prove:
- solved within budget;
- exhaustive no-solution proof;
- max-state exhaustion -> INCONCLUSIVE;
- max-depth exhaustion -> INCONCLUSIVE;
- operational timeout -> INCONCLUSIVE;
- UNKNOWN_BOUND never maps to unsolvable;
- deterministic repeat under same operation budgets.

## PASS

PASS when proof, inconclusive and unavailable/error outcomes are impossible to confuse.
