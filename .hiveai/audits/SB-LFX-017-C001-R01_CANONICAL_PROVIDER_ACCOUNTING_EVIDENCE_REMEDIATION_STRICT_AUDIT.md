# SB-LFX-017-C001-R01 — Canonical Provider Accounting Evidence Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 1
- MAJOR: 2
- MINOR: 0
- NOTE: 1

## Audited chain

- R01 start: `18d92cfc42d49c3289c9d9d1a7a2d81ab61b7870`
- R01 implementation: `3aaaa71dd997b6e019d9f0e6d178b8ea62971504`
- R01 terminal log-only: `a919f0b8291d80f6928610c28c2702f76fd31a20`

## Material improvements

R01 materially improves the original implementation:
- Studio launcher no longer accepts caller-supplied provider/financial facts;
- product path accepts only scope/provider filters;
- records are discovered from a bounded local accounting directory;
- schema/key/type/nonnegative/timestamp validation is applied;
- provider/unit groups remain separated;
- remaining balance uses latest validated timestamp;
- owner-accepted denominator requires matching validated owner review ID/disposition;
- UI has scope/provider filters and Refresh;
- no network/provider calls are made.

These improvements are retained.

## BLOCKER-001 — the new “accounting evidence” has no authoritative producer/binding to real provider execution

The original blocker was that arbitrary caller records could masquerade as financial truth.

R01 moves those records from the request body into:

`level_factory/output/studio-extensions/accounting/*.json`

but no canonical provider/job subsystem produces or signs/binds those records.

The real integration itself writes the accounting JSON files directly with a test helper:

`_write_record({... provider, consumed, remaining ...})`

Then `canonical_cost_center()` trusts any local file that matches the schema.

This means arbitrary local JSON can still fabricate:
- provider identity;
- status;
- consumed credits/cost;
- remaining balance;
- candidate association;
- evidence reference.

The transport changed, but financial authority is still self-asserted rather than bound to real provider execution/accounting evidence.

### Required remediation

One of the following must be true before a metric is authoritative:

1. **Existing provider execution records** already contain reliable cost/credit facts:
   - define a canonical adapter that derives accounting rows directly from those immutable job records; or

2. **No reliable provider accounting source exists yet**:
   - Cost Center must report NOT AVAILABLE for consumed/remaining/cost metrics instead of inventing a new free-standing accounting source.

If a new accounting-evidence schema is retained, its records must be produced only by an authoritative provider/job execution path and bind:
- provider job/run ID;
- immutable execution evidence identity/hash;
- metric source;
- unit/currency;
- recorded timestamp/as-of;
- candidate linkage where applicable.

A manually dropped JSON file must never establish financial truth.

## MAJOR-001 — Studio UI does not render the required accounting facts/evidence

The actual `FactoryStudioCost` result text shows only:

`Groups: N`

It does not present:
- provider;
- unit/currency;
- scope;
- jobs/success/failure;
- consumed;
- remaining;
- cost per success;
- cost per owner accepted;
- UNKNOWN / NOT AVAILABLE fields;
- evidence record IDs;
- as-of timestamp.

The criteria explicitly require those operator-visible summaries and evidence metadata.

### Required remediation

Render real read-only group rows/details with explicit UNKNOWN/NOT AVAILABLE values and evidence references.

## MAJOR-002 — required runtime evidence remains incomplete

The real integration proves:
- two providers/units separated;
- success/failure arithmetic;
- consumed aggregation;
- latest remaining;
- owner-accepted denominator;
- one unknown provider group;
- caller-forged request records ignored;
- UI invocation.

It does not prove:
- refresh after adding a new authoritative accounting record;
- malformed/secret-bearing accounting record is rejected;
- candidate/review bytes remain unchanged across Cost Center refresh;
- evidence-reference/as-of values are rendered in Studio.

These are required by the original criteria/remediation prompt.

## NOTE

The remediation-batch global suite retains the unrelated protected tracker-contract failure.

## Disposition

`SB-LFX-017` remains open pending R02.
