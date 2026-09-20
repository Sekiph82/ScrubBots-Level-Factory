# SB-LFX-017-C001-R01 — Canonical Provider Accounting Evidence Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 4
- MINOR: 0
- NOTE: 1

## Audited chain

- R01 start: `18d92cfc42d49c3289c9d9d1a7a2d81ab61b7870`
- R01 implementation: `3aaaa71dd997b6e019d9f0e6d178b8ea62971504`
- R01 terminal log-only: `a919f0b8291d80f6928610c28c2702f76fd31a20`

## Material improvements

R01 closes the original direct-request financial injection path:
- Studio/launcher Cost Center now accepts only `scope` and `provider` filters;
- caller-supplied `records` are ignored by the authoritative launcher path;
- local accounting files require an exact versioned schema;
- provider/unit/scope/status and nonnegative consumed/remaining types are checked;
- timestamps are parsed;
- provider+unit are kept separate;
- latest timestamp drives remaining/as-of inside a group;
- owner-accepted count is bound to the current validated owner-review ID and ACCEPT disposition;
- absent consumed/remaining values remain unknown/None;
- no network/provider call or credit spend is introduced.

These are substantial and retained.

## MAJOR-001 — “validated accounting evidence” is not bound to originating provider/job evidence

The canonical reader validates the accounting record's own JSON shape, but `evidence_reference` is not resolved or verified.

A well-formed file placed under:

`studio-extensions/accounting/*.json`

can assert arbitrary:
- provider;
- unit;
- scope;
- SUCCESS/FAILED status;
- consumed;
- remaining;
- candidate/review IDs;
- recorded_at;

and be counted as trusted accounting evidence as long as its shape is valid.

The real integration itself writes those accounting JSON files directly with `FileAccess`; it does not derive them from a verified provider/job execution record.

This improves over request injection, but it still does not establish why the financial facts are reliable provider evidence.

### Required follow-up

Define one trusted accounting-record creation/ingestion boundary that binds each record to real local provider/job evidence when such evidence exists.

At minimum:
- validate `evidence_reference` through a known provider/job record schema or trusted adapter evidence;
- derive provider/status/consumed/remaining from that record rather than duplicate unchecked facts where possible;
- if a provider has no reliable accounting evidence, return NOT AVAILABLE instead of accepting manually asserted financial values.

Deterministic test fixtures may use a dedicated test-only canonical evidence writer, but product runtime must not treat arbitrary dropped JSON as provider truth.

## MAJOR-002 — different scopes can be silently merged

`canonical_cost_center()` groups by:

`(provider, unit)`

but each accounting record also has a `scope`.

When the user leaves the scope filter blank, two records with:
- same provider;
- same unit;
- different scopes

are combined into one group while `group["scope"]` remains whichever scope was seen first.

That produces a misleading mixed-scope aggregate.

### Required follow-up

Either:
- include scope in the grouping key; or
- require an explicit scope before aggregating.

Never merge different accounting scopes while labeling the result as a single scope.

Add a mixed-scope runtime test.

## MAJOR-003 — real Cost Center UI still does not expose the required accounting facts

The R01 Studio surface now has scope/provider filters and Refresh, but its rendered output is only:

`Groups: <count>`
`Validated local evidence only; read-only.`

It does not display per-provider/group:
- jobs;
- success/failure;
- consumed;
- remaining;
- cost per success;
- cost per owner accepted;
- UNKNOWN/NOT AVAILABLE fields;
- unit/currency;
- scope;
- as-of timestamp;
- evidence record IDs/references.

This leaves the original operator-surface finding only partially remediated.

### Required follow-up

Render a bounded per-group summary/detail view directly from the canonical projection, including explicit UNKNOWN/NOT AVAILABLE values and evidence/as-of information. Do not recompute accounting in GDScript.

## MAJOR-004 — runtime acceptance matrix remains incomplete

The real R01 integration proves:
- mixed provider/unit separation;
- success/failure counts;
- consumed aggregation;
- owner-accepted denominator;
- latest remaining within one group;
- unknown values;
- forged request records ignored;
- real Studio refresh invokes the canonical projection.

It does not prove:
- refresh reflects a **new accounting record added after the first refresh**;
- mixed scopes are not merged;
- malformed/unbound accounting evidence is rejected;
- candidate bundle and owner-review evidence remain byte-identical before/after Cost Center refresh;
- secret-bearing/extra-field accounting records are excluded.

### Required follow-up

Extend the existing real integration with those cases.

## Publication / regression

Task-final publication is log-only.

Builder reports focused unit PASS and real accounting-evidence integration PASS. The remediation-batch global suite retains the unrelated protected tracker-contract failure.

## NOTE

The old pure `cost_center(records)` helper remains for a standalone unit contract, but the authoritative Studio launcher no longer uses it. This is acceptable provided product runtime continues to use only `canonical_cost_center()`.

## Disposition

`SB-LFX-017` remains open pending trusted accounting-source binding, scope-safe aggregation, full UI rendering and runtime evidence.
