# SB-LFX-015-C001-R02 — Typed Session Schema + Real Recovery Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Material closure

R02 closes the unsafe session-schema and fake-reference problems:
- heuristic recursive secret scrubbing is replaced by a versioned explicit allowlist;
- unknown fields/structures are rejected;
- canonical source/candidate/batch/pipeline/retry/revision references are resolved through real readers;
- session records have an integrity digest;
- syntactically valid but nonexistent references become NEEDS_OPERATOR_ACTION;
- corruption fails closed;
- NEW / RETRIED / RESUMED / NOT_RESUMABLE / NEEDS_OPERATOR_ACTION are distinguished.

## MAJOR-001 — recovery classification exists, but real recovery/resume execution does not

The task target is session recovery that **resumes eligible durable jobs without redoing successful stages**.

Current `restore_session()`:
- validates references;
- classifies the session;
- returns `RESUMED`, `RETRIED`, etc.

It does not dispatch an operation-specific resume coordinator or continue any interrupted durable work.

The real integration creates a batch and pipeline, saves their references, and restores them in the same Studio process. It does not:
- destroy/restart Studio or a fresh process;
- resume an interrupted stage/job;
- prove completed stage IDs/evidence remain unchanged after recovery;
- prove successful stages are not rerun;
- prove no duplicate source/candidate/job is created by recovery.

Thus `RESUMED` is presently a truthful reference-state classification, not proof that work was resumed.

### Required follow-up

Implement a bounded recovery coordinator that:
- performs real operation-specific safe resume only for eligible durable work;
- reuses already-successful stage evidence;
- never reruns successful stages by default;
- records RETRIED only for explicit retry attempts;
- uses NOT_RESUMABLE / NEEDS_OPERATOR_ACTION when no safe continuation exists.

The real integration must reinstantiate/restart Studio, recover actual interrupted work, prove stage/evidence identity reuse, and prove no duplicate source/candidate/job creation.

## Disposition

`SB-LFX-015` remains open for R03.
