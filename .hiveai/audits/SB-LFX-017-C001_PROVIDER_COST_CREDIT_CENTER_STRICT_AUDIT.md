# SB-LFX-017-C001 — Provider Cost / Credit Center — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 1
- MAJOR: 3
- MINOR: 0
- NOTE: 1

## Audited chain

- Start: `1bbf65bcb33fc52593e8652527c27efc93a8ae39`
- Actual implementation: `2999d941098140fd068b0f8df96e777b80a238a6`
- Actual task-final log-only: `dd2221d7e5adcea836c6d888c088cb3957d230fe`

## Accepted implementation semantics

The aggregation math keeps provider/unit groups separate, leaves absent consumed/remaining values as `None`/unknown, uses an owner-acceptance field rather than QA status in the arithmetic, performs no provider/network call, and does not mutate candidates/reviews inside the helper.

## BLOCKER-001 — accounting accepts caller-supplied records as financial truth

`cost_center(records)` accepts arbitrary mappings from the Studio extension request and treats these fields as authoritative:
- provider;
- unit;
- status;
- consumed;
- remaining;
- owner_acceptance.

It does not load or verify durable provider execution/accounting records.

Therefore a caller can fabricate:
- provider identity;
- success/failure counts;
- consumed credits/cost;
- remaining balance;
- owner acceptance;
- cost-per-owner-accepted.

This violates the core requirement that accounting display only reliable recorded provider evidence.

### Required remediation

Define or reuse a canonical read-only provider accounting evidence contract and make Cost Center discover/validate those durable records internally. The UI/request may select scope/filters, but must not submit the financial facts themselves.

If no reliable provider accounting evidence exists for a provider, display NOT AVAILABLE rather than allowing injected fixture-style facts in product runtime.

## MAJOR-001 — owner-accepted denominator is not bound to canonical owner review

The helper increments accepted count whenever caller input contains:

`owner_acceptance == "ACCEPT"`

It does not verify owner-review evidence, candidate identity or review lineage.

### Required remediation

Where cost-per-owner-accepted is supported, derive the denominator from canonically validated candidate-bound owner-review evidence. Otherwise return NOT AVAILABLE.

## MAJOR-002 — required accounting evidence metadata is absent

The criteria require every metric to expose evidence source/scope/currency or credit unit and UI to show evidence timestamps/record identities where available.

Current groups expose provider/unit and totals only. They do not expose:
- source record IDs;
- accounting evidence IDs;
- timestamps/as-of semantics;
- scope;
- currency vs credit semantics beyond an arbitrary unit string.

`remaining` is simply replaced by whichever input record is encountered last, without authoritative ordering/timestamp validation.

## MAJOR-003 — real Cost Center UI/integration is absent

`FactoryStudioCost` is informational only:
- no provider/scope selector;
- no refresh action;
- no accounting rows;
- no UNKNOWN/NOT AVAILABLE metric rendering;
- no evidence references.

The focused test calls `cost_center()` directly with synthetic dictionaries. Missing required proof includes:
- canonical/local durable accounting records;
- mixed provider/unit evidence through real Studio;
- refresh after adding records;
- secret absence in records/logs;
- owner-accepted denominator bound to review evidence;
- zero candidate/review mutation.

## NOTE — master batch SHA mismatch

The master batch summary recorded different SB-LFX-017 SHAs. The task log/GitHub establish the actual chain above. Remediation evidence should correct the summary metadata.

## Disposition

`SB-LFX-017` remains open pending remediation and re-audit.
