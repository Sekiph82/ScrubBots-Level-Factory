# SB-LF03-007-C001 - Correctness-Preserving Pruning and Order

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Mission

Implement only:

`SB-LF03-007 - Add correctness-preserving pruning/order only with tests.`

Create first:

`.hiveai/codex-logs/SB-LF03-007-C001_CORRECTNESS_PRESERVING_PRUNING_AND_ORDER_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Implementation

Add explicit versioned search-policy objects for:
- move ordering;
- pruning.

Preserve baseline behavior as a selectable control.

Only add optimizations with proof/testing that they preserve search correctness.

Visited-state duplicate suppression from SB-LF03-005 may be used.

If no further pruning is safely justified, implement `NONE_V1` rather than fabricating a heuristic.

Do not add difficulty heuristics or gameplay-rule shortcuts.

Under deterministic state/depth budgets, record ordering/pruning policy in evidence. UNKNOWN/INCONCLUSIVE remains distinct from proven failure.

## Tests

Run paired baseline-vs-policy fixtures for solved, exhausted, branching, duplicate-state and bounded cases.

Require identical truth verdict where exhaustive; bounded runs may find different paths but cannot fabricate proof.

Run retained LF03 and full repository gates. Publish implementation and finalized task log, then terminal log-only commit.
