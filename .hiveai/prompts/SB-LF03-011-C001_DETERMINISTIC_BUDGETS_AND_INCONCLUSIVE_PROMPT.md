# SB-LF03-011-C001 - Deterministic Budgets / UNSOLVED vs INCONCLUSIVE

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Mission

Implement only:

`SB-LF03-011 - Define budgets/timeouts and UNSOLVED vs INCONCLUSIVE.`

Create first:

`.hiveai/codex-logs/SB-LF03-011-C001_DETERMINISTIC_BUDGETS_AND_INCONCLUSIVE_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Implementation

Define versioned solver/search budget policy.

Use deterministic operation budgets as canonical proof limits:
- visited states;
- depth;
- solution count where relevant.

Optional wall-clock timeout is an operational kill switch only.

Map outcomes explicitly:
- SOLVED;
- PROVEN_UNSOLVABLE only after exhaustive proof / canonical DEADLOCK;
- INCONCLUSIVE for UNKNOWN_BOUND or any budget/timeout exhaustion;
- UNAVAILABLE;
- ERROR.

Do not use ambiguous UNSOLVED as a terminal truth unless it is only a UI label backed by one of the explicit dispositions above.

Integrate budgets into reproduction manifests and solver evidence.

## Tests

Cover exact boundary values, malformed budgets, state/depth exhaustion, UNKNOWN_BOUND mapping, timeout mapping, proven no-solution and deterministic repeat.

Run retained LF03 and full repository gates. Publish task implementation + task log + terminal log-only commit.
