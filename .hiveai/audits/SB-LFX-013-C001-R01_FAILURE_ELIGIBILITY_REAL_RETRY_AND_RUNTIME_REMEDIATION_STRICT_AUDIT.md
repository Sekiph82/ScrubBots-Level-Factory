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
- R01 terminal log-only: `e0872bef72ef85e3062724db4bd13598c9e7961b`

## Material improvements

R01 materially improves retry execution:
- operation/stage combinations are bounded;
- secret-like top-level input fields are rejected;
- eligibility is narrower than the original generic stage rule;
- retry changes are restricted to bounded `operator_note`;
- eligible import-validation retries call `validate_owner_source()`;
- eligible pipeline retries call `run_pipeline()`;
- retry attempts record parent failure ID, original inputs, authorized changes, disposition and execution diagnostics;
- SOLVE/DIFFICULTY remain non-retryable;
- Studio now has refresh and retry controls;
- real Godot integration proves an eligible retry actually executes and unauthorized identity change is rejected.

These improvements are retained.

## MAJOR-001 — Failure Inbox still does not derive failure truth from canonical job evidence

The authoritative criteria require the Inbox to consume real failed/rejected/inconclusive evidence from:
- batch manifests;
- pipeline runs;
- import-validation evidence;
- other committed canonical job evidence.

R01 still uses `record_failure(...)` to manufacture a separate failure record from caller-supplied:
- operation;
- stage;
- disposition;
- reason;
- inputs.

`list_failures()` then reads only those separately created `failure-*.json` records.

The real Godot integration itself demonstrates the problem by calling:

`record-failure(import-validation, VALIDATE, REJECTED, SOURCE_INVALID, source_id=owner-upload-missing)`

rather than producing and discovering a real canonical validation rejection.

Therefore Failure Inbox truth remains a parallel normalized failure store, not a derived view over actual canonical failures.

### Required follow-up

Build failure discovery adapters/readers over real canonical evidence:
- validation evidence with reject/error disposition;
- pipeline-run stage failure/block/inconclusive evidence;
- batch-manifest attempt failure/rejection evidence where applicable.

A normalized Inbox row may reference those records, but the authoritative failure facts must come from the originating evidence ID/path/hash. Free-form `record_failure` must not be a product authority path.

## MAJOR-002 — Studio Retry action is not eligibility-aware

The real `FactoryStudioFailures` surface always renders an enabled `Retry` button.

It does not:
- select a failure row with a verified `retryable` state;
- disable retry for non-retryable/unavailable entries;
- show the non-retryable reason before action;
- expose operation/stage/reason/eligibility details in the Inbox.

Backend rejection is useful, but the criteria explicitly require a Failure Inbox with eligibility and a Retry Eligible action.

### Required follow-up

Make the UI selection-driven and capability-gated:
- disabled by default;
- enabled only for the selected canonically derived retryable failure;
- show exact operation/stage/reason/evidence identity and non-retryable reason.

## MAJOR-003 — required no-redo / successful-control / duplicate-protection runtime proof is incomplete

The R01 real integration covers:
- one fabricated validation failure;
- one retry that fails against a missing source;
- unauthorized change rejection;
- one non-retryable SOLVE record;
- refresh.

It does not prove:
- a real validation rejection discovered from canonical evidence;
- a real pipeline/generator-stage failure from canonical evidence;
- a successful control item is excluded from Retry Failed Only;
- successful prior pipeline stages are reused rather than rerun;
- retry success produces and records canonical output identity;
- duplicate accepted output protections remain intact;
- original originating failure evidence remains byte-identical across retry.

### Required follow-up

Extend the real integration with real originating evidence and snapshot the originating records before/after retry. Include at least one successful retry path and one successful control item.

## Publication / regression

Task-final publication is log-only.

Builder reports focused test PASS and real Failure Retry integration PASS. The remediation-batch global suite retains the unrelated protected tracker-contract failure.

## NOTE

R01 correctly transformed retry from a PENDING-only stub into a real local operation call. The remaining findings are primarily about authoritative failure-source truth, capability-gated UI, and acceptance evidence, not about the new retry invocation itself.

## Disposition

`SB-LFX-013` remains open pending a canonical-evidence-derived Failure Inbox follow-up and re-audit.
