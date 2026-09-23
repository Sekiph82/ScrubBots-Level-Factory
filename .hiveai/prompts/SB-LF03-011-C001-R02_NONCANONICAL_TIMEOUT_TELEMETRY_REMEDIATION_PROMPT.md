# SB-LF03-011-C001-R02 — Non-Canonical Timeout Telemetry Remediation

Document role: CODEX REMEDIATION PROMPT

Target: SB-LF03-011 — Define budgets/timeouts and UNSOLVED vs INCONCLUSIVE.

R01 re-audit:
.hiveai/audits/SB-LF03-011-C001-R01_REAL_BUDGET_AND_TIMEOUT_SEPARATION_REMEDIATION_STRICT_REAUDIT.md

Create first:
.hiveai/codex-logs/SB-LF03-011-C001-R02_NONCANONICAL_TIMEOUT_TELEMETRY_REMEDIATION_CODEX_LOG.md

Do not edit TASKS.md.

## Retain accepted R01 behavior

The real max-visited-state traversal bound is accepted. Preserve it.

## Finding to close

Operational timeout still changes canonical outcome/evidence through timeout-specific source_disposition, reason and OPERATIONAL_TIMEOUT exhaustion. Removing only the boolean field was insufficient.

## Required architecture

Separate deterministic solver truth from operational timeout telemetry.

Canonical deterministic identity may include deterministic max-visited/max-depth/max-solutions, SOLVED/PROVEN_UNSOLVABLE/deterministic INCONCLUSIVE and deterministic exhaustion reasons such as MAX_VISITED_STATES, MAX_DEPTH, MAX_SOLUTIONS, UNKNOWN_BOUND.

Wall-clock timeout:
- is an operational kill switch only;
- maps operator-visible execution to INCONCLUSIVE;
- is recorded in a distinct non-canonical operational/telemetry object;
- must not alter canonical solver-evidence bytes/digest;
- must not alter reproduction identity;
- timeout duration/occurrence/reason must not appear in canonical deterministic result.

If physical timeout prevents a deterministic result from existing, represent canonical deterministic result as absent/unavailable/incomplete rather than inventing a canonical timeout result.

## Tests

Prove max-visited still stops traversal exactly; deterministic state/depth/solution/UNKNOWN_BOUND outcomes remain correct; timeout maps operationally to INCONCLUSIVE; changing timeout seconds/occurrence changes only operational telemetry; canonical deterministic bytes stay identical when underlying deterministic result is identical; no OPERATIONAL_TIMEOUT marker exists in canonical solver evidence/reproduction identity; PROVEN_UNSOLVABLE is impossible after bound exhaustion.

Update 010/012 integrations where required.
Run focused 011 plus affected LF03 tests, retained LF03 and full repository gates.
Publish R02 implementation/log/terminal commit.