# SB-LF03-011-C001-R01 — Real Budget Enforcement + Timeout Separation Remediation

Document role: CODEX REMEDIATION PROMPT

Target: `SB-LF03-011 — Define budgets/timeouts and UNSOLVED vs INCONCLUSIVE.`

Audit:
`.hiveai/audits/SB-LF03-011-C001_DETERMINISTIC_BUDGETS_UNSOLVED_VS_INCONCLUSIVE_STRICT_AUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-011-C001-R01_REAL_BUDGET_AND_TIMEOUT_SEPARATION_REMEDIATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Mission A — enforce max visited states during search

A state budget must stop baseline traversal, not classify after full execution.

Integrate deterministic visit-count bound into baseline search/evidence execution.

When exhausted:
- stop further expansion;
- return AVAILABLE + INCONCLUSIVE;
- reason/exhaustion = MAX_VISITED_STATES;
- never PROVEN_UNSOLVABLE.

Define exact boundary semantics and test them.

## Mission B — keep wall-clock timeout non-canonical

Operational timeout policy and timeout occurrence are telemetry/safety only.

Do not include timeout seconds or timeout occurrence in canonical solver evidence digest or reproduction identity.

A timeout still maps operationally to INCONCLUSIVE, but canonical deterministic bytes must not vary merely because one machine hit a wall-clock timeout.

Preserve deterministic max-depth/max-state/max-solution budgets in canonical policy.

## Tests

Prove:
- wide graph stops at configured visit bound;
- visited count cannot run far beyond cap;
- exact boundary behavior;
- state/depth/solution/UNKNOWN_BOUND remain INCONCLUSIVE;
- operational timeout maps to INCONCLUSIVE;
- canonical evidence bytes are unchanged by operational timing metadata;
- PROVEN_UNSOLVABLE is impossible after any bound exhaustion.

Run focused 011 + 004/006/008/010 dependencies + retained LF03 + full gates. Publish R01 implementation/log/terminal commit.
