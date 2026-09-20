# SB-LFX-013-C001 — Failure Inbox / Retry Center — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 5
- MINOR: 0
- NOTE: 0

## Audited chain

- Start: `c6904e2fb9bed6b0a8dc28313f1ebaab66ba453d`
- Implementation: `a1c8c05730abcb627017e2bcdc19d0f59ebac017`
- Task-final log-only: `861ac9e9fd87d19275207ad1e7401dd0c80e8abd`

## Accepted implementation semantics

New failure/retry JSON evidence is written immutably and preserves parent failure ID, original inputs and authorized_changes. SOLVE/DIFFICULTY are disabled from retry in the narrow helper.

## MAJOR-001 — Failure Inbox is not derived from real canonical failure evidence

The criteria require a derived view over real batch manifests, pipeline runs, validation attempts and other committed job evidence.

Current implementation instead introduces `record_failure(...)`, which creates a new failure record from caller-supplied operation/stage/reason/inputs. This can manufacture a failure entry independently from canonical job evidence.

### Required remediation

Build the inbox by reading/verifying real failure/rejection/inconclusive evidence from existing canonical records. Any normalized retry record must bind the exact originating evidence identity rather than accept free-form UI claims as authority.

## MAJOR-002 — Retry does not actually retry the failed operation

`retry_failure()` only writes a `PENDING` retry-attempt JSON file.

It does not:
- invoke the failed canonical operation;
- record success/failure outcome;
- record produced output identity;
- preserve/verify duplicate protections;
- prove successful stages are not rerun.

This misses the core Retry Center function.

## MAJOR-003 — eligibility is too coarse and not operation-specific

Eligibility is currently:

`retryable = stage not in {"SOLVE", "DIFFICULTY"}`

The contract requires stage/operation-specific deterministic eligibility based on real capability. Validation, generation, pipeline and other failures cannot safely share this blanket rule.

## MAJOR-004 — authorized changes are unrestricted

`changes` is accepted as an arbitrary mapping and written as `authorized_changes` without operation-specific allowed-field validation.

This allows silent semantic changes to source/config under the label of retry.

## MAJOR-005 — real Failure Inbox UI/integration is absent

`FactoryStudioFailures` is informational only and always reports AVAILABLE. It has no:
- failure list;
- filters/reasons;
- eligibility status;
- Retry Eligible action;
- disabled/non-retryable reason.

No real Godot integration proves the required validation rejection, generator failure, unavailable/inconclusive stage, successful control item, no-redo behavior, lineage, duplicate safety or retry outcome.

## Disposition

`SB-LFX-013` remains open pending remediation and re-audit.
