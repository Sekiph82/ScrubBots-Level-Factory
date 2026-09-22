# SB-LF03-006-C001 - Solver Evidence and Search Metrics

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Mission

Implement only:

`SB-LF03-006 - Record solution path/states/dead ends/depth/branching/solve time.`

Create first:

`.hiveai/codex-logs/SB-LF03-006-C001_SOLVER_EVIDENCE_AND_SEARCH_METRICS_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Implementation

Extend the accepted deterministic search layer with a versioned evidence report.

Record only evidence genuinely observed by the executed search:
- ordered canonical move path;
- bounded state/key references;
- visited count;
- memo hits;
- dead-end count;
- maximum depth;
- branch/child counts sufficient to derive branching statistics;
- frontier peak where applicable;
- terminal status/reason;
- elapsed monotonic duration as NON-CANONICAL telemetry.

Do not put elapsed time in canonical digest/identity and do not use it to choose search branches.

If production providers are unavailable, report search UNAVAILABLE and do not synthesize fake zero metrics.

Use fixture providers to prove evidence collection.

## Tests

Prove deterministic path/metrics on repeat; dead-end and branching accounting; bounded evidence size; timing exclusion from canonical bytes; unavailable behavior; input immutability.

Run focused + retained LF03 + full repository gates. Publish task implementation and finalized task log, then terminal log-only commit.
