# SB-LFX-013-C001-R03 — Canonical-Only Failure Truth + Retry Evidence Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Material closure

R03 correctly closes the caller-created failure-authority gap:
- `record-failure` is removed from the product Studio launcher;
- product retry no longer falls back to free-form `extensions/failures/*.json`;
- canonical scanner evidence is required;
- originating evidence bytes/hash are checked before and after retry;
- retry attempts remain separate append-only evidence;
- successful control work is explicitly excluded from retryable failure truth;
- unavailable SOLVE/DIFFICULTY remains non-retryable.

These changes are retained.

## MAJOR-001 — successful prior stages are still actually rerun during pipeline retry

The authoritative acceptance criterion requires:

> successful stages are not redone

and the R03 prompt requires:

> prove already-successful prior stage identities/evidence are reused and are not silently rerun.

The current implementation builds a `reused_successful_stage_evidence` list from the parent pipeline, but then executes:

`run_pipeline(source_id=..., candidate_id=...)`

for a pipeline retry.

`run_pipeline()` reconstructs and executes the pipeline from its initial SOURCE / NORMALIZE / VALIDATION / CANDIDATE path. Therefore the code **reports** prior PASS/NOT_APPLICABLE stages as reused while the retry execution actually runs the pipeline path again.

The runtime assertion only checks that the returned `reused_successful_stage_evidence` list is non-empty. It does not prove those stages were skipped, nor does it compare new execution stage identities against a continuation point.

This is precisely the remaining semantic gap: evidence labeling is ahead of actual execution behavior.

### Required follow-up

Implement a real stage-aware retry/continuation contract:
- determine the originating failed stage from canonical pipeline evidence;
- carry forward immutable successful prior-stage records by reference/digest;
- execute only the eligible failed stage / continuation path and later applicable stages;
- do not call the full `run_pipeline()` from the beginning for a stage retry;
- record exactly which prior stage evidence was reused and which stages were newly attempted;
- runtime must prove no new execution/evidence is produced for previously successful stages;
- preserve original failure evidence and append-only retry lineage.

If the pipeline has no safe partial-stage retry API for a given failure, mark it NOT_AVAILABLE rather than claiming reuse.

## Disposition

`SB-LFX-013` remains open for R04.
