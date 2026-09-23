# SB-LF03-011-C001-R03 — Operational Execution Wrapper Remediation

Document role: CODEX REMEDIATION PROMPT

Target:
`SB-LF03-011 — Define budgets/timeouts and UNSOLVED vs INCONCLUSIVE.`

R02 re-audit:
`.hiveai/audits/SB-LF03-011-C001-R02_NONCANONICAL_TIMEOUT_TELEMETRY_REMEDIATION_STRICT_REAUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-011-C001-R03_OPERATIONAL_EXECUTION_WRAPPER_REMEDIATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Retain accepted behavior

Preserve:
- real max-visited execution enforcement;
- deterministic max-depth/max-solutions budgets;
- UNKNOWN_BOUND => INCONCLUSIVE;
- deterministic budget exhaustion never => PROVEN_UNSOLVABLE;
- timeout seconds excluded from `SolverBudgetPolicy.canonical_dict()`.

## Finding to close

R02 hides the literal timeout marker from canonical serialization, but timeout occurrence still replaces an existing deterministic result with a synthetic canonical INCONCLUSIVE result.

For the same completed deterministic search result:
- timeout false => canonical SOLVED/other deterministic result;
- timeout true => canonical generic INCONCLUSIVE.

That still lets wall-clock occurrence change canonical truth.

## Required architecture

Separate two domains completely.

### A. Canonical deterministic solver result

This is produced only from deterministic search/count state and deterministic budgets.

It must not know:
- wall-clock timeout seconds;
- whether a wall-clock timeout occurred;
- operational timeout reason.

Recommended: remove `operational_timeout_exhausted` from canonical classifier APIs.

### B. Operational execution outcome

Create a separate non-canonical wrapper/value, for example:
- operational disposition;
- canonical deterministic result: optional;
- operational timeout telemetry: optional;
- elapsed/timeout values: non-canonical.

Rules:

1. If a deterministic result already exists and an operational timeout flag/telemetry is attached later, the canonical deterministic result bytes/digest remain **exactly identical**.
2. If wall-clock timeout interrupts execution before any deterministic result exists:
   - operational disposition = INCONCLUSIVE;
   - canonical deterministic result = None / absent / incomplete;
   - do not synthesize a canonical INCONCLUSIVE solver result.
3. OPERATIONAL_TIMEOUT belongs only to operational telemetry/reason enums, never canonical budget-exhaustion enums/serialization.
4. Reproduction identity must never contain wall-clock timeout occurrence/duration.

## Tests

Required:
- same deterministic SOLVED result, timeout absent vs attached => identical canonical result bytes/digest;
- same deterministic INCONCLUSIVE deterministic-bound result, timeout absent vs attached => identical canonical bytes;
- timeout before deterministic result => operational INCONCLUSIVE + no canonical result;
- different timeout durations => operational metadata differs, canonical result unchanged/absent;
- canonical serialization contains no timeout marker/reason/duration;
- reproduction manifest/context unaffected;
- max-visited/depth/solutions/UNKNOWN_BOUND remain correct;
- PROVEN_UNSOLVABLE impossible after any deterministic bound exhaustion.

Update all affected callers cleanly; do not leave a compatibility overload that can reintroduce timeout into canonical classifier truth.

Run focused 011 + 010/012 affected regressions, retained LF03, full repository gates.

Publish R03 implementation + finalized task log + terminal log-only commit.
