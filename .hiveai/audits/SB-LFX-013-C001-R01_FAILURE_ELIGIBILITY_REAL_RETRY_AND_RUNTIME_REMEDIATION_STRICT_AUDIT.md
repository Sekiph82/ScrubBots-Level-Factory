# SB-LFX-013-C001-R01 — Failure Eligibility, Real Retry + Runtime Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 3
- MINOR: 0
- NOTE: 1

## Audited chain

- R01 start: `23ef20b37fa20d766e5fe380e14c9c946a06973a`
- R01 implementation: `f99878fc8f69d1f6869ec0867acf7417934c0fb1`
- R01 terminal log-only: `e0872be`

## Material improvements

R01 correctly improves several original gaps:
- operation/stage-specific retry eligibility replaces the coarse blanket rule;
- retry changes are restricted to bounded `operator_note`;
- eligible import-validation/pipeline retries now execute real canonical functions;
- retry outcome is independently recorded as RETRY_EXECUTED / RETRY_FAILED;
- unavailable SOLVE/DIFFICULTY remains non-retryable;
- Studio now exposes Refresh Inbox and Retry controls.

## MAJOR-001 — Failure Inbox still does not derive failures from canonical job evidence

The central original finding remains.

`record_failure(...)` is still a product operation that accepts caller-provided:
- operation;
- stage;
- disposition;
- reason;
- inputs.

Although values are now constrained, this still lets the caller manufacture an authoritative failure record rather than deriving it from:
- canonical batch manifests;
- import-validation evidence;
- persisted pipeline-run evidence;
- other real job evidence.

The criteria explicitly require the Failure Inbox to be a derived view over real durable failure/rejection/inconclusive records.

### Required remediation

Remove free-form failure creation from the operator/product truth path.

Implement canonical scanners/adapters that:
- inspect verified validation/pipeline/batch/job evidence;
- derive normalized inbox entries bound to exact originating evidence IDs;
- never accept caller reason/disposition/input as failure authority.

A helper for tests/internal normalization is acceptable only if it cannot become product truth without an originating canonical evidence record.

## MAJOR-002 — runtime matrix still uses synthetic failure evidence rather than real failed work

The real Godot suite begins by calling:

`record-failure(import-validation, VALIDATE, REJECTED, SOURCE_INVALID, owner-upload-missing)`

This does not demonstrate that a real validation rejection is automatically discovered by the Failure Inbox.

It also does not exercise:
- a real generator/stage failure;
- a real persisted pipeline failure discovered from pipeline evidence;
- a successful control item that is provably absent from retry-failed-only;
- a retry that succeeds and produces a bound output identity;
- duplicate protection / successful-stage reuse.

### Required remediation

Drive the runtime integration from actual canonical evidence:
1. create a real validation rejection;
2. create a real pipeline/generator-stage failure where supported;
3. create an unavailable/inconclusive stage;
4. create a successful control item;
5. refresh the Inbox without manually recording failure truth;
6. prove only eligible failures appear/retry;
7. include at least one successful retry or, if impossible by contract, a real retry execution whose expected failure and lack of output are authoritative;
8. prove successful prior stages are not rerun and duplicate protections remain intact.

## MAJOR-003 — UI does not expose the required failure evidence / eligibility detail

The Failure Inbox UI currently renders only aggregate count and retry attempt ID.

It does not visibly present:
- failure list/items;
- operation/stage;
- reason;
- originating evidence ID;
- retryable vs non-retryable state;
- disabled/non-retryable reason.

The Retry button is not disabled based on selected failure eligibility; backend rejection alone is not equivalent to the required operator-visible capability state.

### Required remediation

Render real failure rows/details, selection, eligibility and reason. Disable Retry for non-retryable/unavailable entries and bind the selected row to its canonical originating evidence.

## NOTE

The remediation-batch global suite retains the unrelated protected tracker-contract failure.

## Disposition

`SB-LFX-013` remains open pending a focused R02 canonical-evidence/runtime/UI remediation.
