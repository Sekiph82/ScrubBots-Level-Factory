# SB-LFX-013-C001-R02 — Canonical Failure Discovery + Retry UI Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Material closure

R02 makes substantial progress:
- Failure Inbox now derives rows from verified validation, pipeline and batch evidence.
- Each normalized row binds originating evidence ID/path/hash.
- Studio exposes selectable rows, operation/stage/reason/evidence identity, retryability and disabled reasons.
- Retry remains append-only and unavailable SOLVE/DIFFICULTY is non-retryable.
- The real Godot suite creates actual invalid/valid source work and discovers canonical evidence without first manufacturing the Inbox row.

## MAJOR-001 — caller-created failure evidence remains reachable from the product retry path

The R01 finding required caller-created `record-failure` evidence to stop being product truth.

R02 retains:
- the launcher `record-failure` operation;
- persisted free-form failure files;
- a fallback in `retry_failure()` that loads `extensions/failures/<failure_id>.json` when the failure is absent from the canonical scanner.

Therefore a caller can still manufacture a failure record, know its ID, and invoke the product retry operation against that record. Calling this path an internal compatibility helper does not make it inaccessible from the product launcher.

The runtime matrix also does not explicitly snapshot originating canonical failure evidence bytes before retry and prove they remain unchanged, nor does it strongly prove successful prior stages are reused rather than rerun.

### Required follow-up

- Remove/privatize `record-failure` from the product launcher/Studio path.
- Product `retry_failure` must accept only scanner-derived canonical failure entries; remove the free-form file fallback from the production path.
- In real runtime, snapshot originating evidence before retry and prove byte identity afterward.
- Prove successful control work is absent from retryable Inbox entries.
- Prove successful prior stage identities/evidence are reused and retry attempts are append-only.
- Retain UI-disabled behavior for non-retryable/unavailable stages.

## Disposition

`SB-LFX-013` remains open for R03.
