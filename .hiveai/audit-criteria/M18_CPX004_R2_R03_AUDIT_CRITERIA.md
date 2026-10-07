# M18 + CPX-004 R03 — FINAL HANDOFF EDGE-CLOSURE AUDIT CRITERIA

Repository: `Sekiph82/ScrubBots-Level-Factory`

Retain all accepted R01/R02 architecture.

## A. Canonical Studio UTC timestamp

PASS only if:

- the actual Factory Studio preflight path emits a timezone-explicit canonical UTC instant;
- reviewed identity binds the canonical timestamp;
- STAGING rebuild uses the exact same canonical timestamp;
- timezone-less/ambiguous timestamp input fails closed;
- the implementation does not depend on a hidden wall clock inside the pack builder;
- a regression covers the actual GDScript-produced timestamp boundary.

## B. Production approval adversarial regression

PASS only if permanent tests prove:

- missing approval rejects before production mutation;
- approval with wrong manifest SHA rejects;
- approval with wrong content_version rejects;
- exact approval remains accepted by the existing M14 production gates;
- STAGING success alone never implies production approval.

No production redesign is required if the existing implementation passes these tests.

## C. Regression

Require:

- R03 focused tests green;
- CPX-004 R02 tests green;
- R01 ledger/idempotency tests green;
- M11-M14 production/publisher regressions green;
- governance/tracker tests green;
- safe full pytest green except truthful existing optional/live skips;
- compileall/JSON/schema/diff/secret checks green;
- no builder edit to root `TASKS.md`;
- no builder write to `.hiveai/audits/**`.

## Outcome

If A-C pass and only real credentials/content/approval remain external:

`TECHNICAL PASS / EXTERNAL LIVE GATES PENDING`
