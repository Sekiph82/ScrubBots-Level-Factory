# SB-LF03-004-C001 - Deterministic Baseline Search - Strict Audit Criteria

Target:
`SB-LF03-004 - Implement deterministic baseline search when semantics available.`

## Authority and dependency

Gameplay semantics remain authoritative in `Sekiph82/Scrubbots`.

SB-LF03-004 may implement generic search orchestration in Level Factory, but it must obtain:
- legal moves through the accepted SB-LF03-003 provider interface;
- state transition/completion truth only through an accepted canonical simulation/provider boundary.

It must not copy ProofKernel, ProofState legal-action logic, routing, slot, target or clear semantics into Python.

## Required search contract

Define a versioned deterministic baseline search policy.

A valid baseline may use DFS or BFS, but must:
- specify the algorithm and ordering version;
- consume provider-returned legal moves in deterministic canonical order;
- never use wall-clock time to choose branches or classify canonical results;
- return explicit AVAILABLE / UNAVAILABLE / ERROR execution truth;
- distinguish search execution availability from solver verdict.

Production search must remain UNAVAILABLE when canonical move or transition providers are unavailable.

## Test provider rule

A test-only graph provider may prove search behavior.

It must be clearly fixture-only and cannot be selected as production gameplay authority.

Tests must include:
- deterministic repeated traversal;
- alternate branch success where the first branch fails;
- zero-move terminal fixture;
- malformed provider output fail-closed;
- provider error propagation;
- no mutation of input state.

## Scope

Do not implement:
- canonical memoization equivalence beyond the minimum local path-cycle safety needed by the chosen baseline;
- SB-LF03-005 visited-state authority;
- solver evidence metrics assigned to SB-LF03-006;
- pruning/heuristics assigned to SB-LF03-007;
- solution counting assigned to SB-LF03-008.

If a simple per-path loop guard is required for termination, it must not be presented as canonical visited-state memoization.

## Verdict truth

Until canonical completion/deadlock semantics are available through a verified provider, the production adapter may not claim SOLVED or PROVEN_UNSOLVABLE.

A generic test provider may expose fixture terminal truth strictly for algorithm tests.

## PASS

PASS when a deterministic, headless, generic baseline search engine exists and is correctly gated on canonical providers, without reimplementing gameplay semantics.
