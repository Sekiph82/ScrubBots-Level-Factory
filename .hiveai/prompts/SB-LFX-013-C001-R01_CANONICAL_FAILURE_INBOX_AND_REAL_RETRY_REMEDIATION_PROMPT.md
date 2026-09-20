# SB-LFX-013-C001-R01 — Canonical Failure Inbox + Real Retry Remediation

Work only on:
.hiveai/audits/SB-LFX-013-C001_FAILURE_INBOX_RETRY_CENTER_STRICT_AUDIT.md

Original criteria:
.hiveai/audit-criteria/SB-LFX-013-C001_FAILURE_INBOX_RETRY_CENTER_LINEAGE_AUDIT_CRITERIA.md

Builder log:
.hiveai/codex-logs/SB-LFX-013-C001-R01_CANONICAL_FAILURE_INBOX_AND_REAL_RETRY_REMEDIATION_CODEX_LOG.md

Create the builder log before edits.

## Mission
Close MAJOR-001..005.

### Failure Inbox
Derive failure/rejection/inconclusive entries from verified canonical batch manifests, import-validation evidence, pipeline runs and other real committed job evidence.
Free-form UI text must never create authoritative failure truth. Any normalized entry must bind the exact originating evidence ID.

### Retry eligibility
Define operation/stage-specific retry capability. Unavailable SOLVE/DIFFICULTY stay disabled. Successful work must never enter retry-failed-only.
Validate operator changes against allowed retry fields for that operation and record exact differences.

### Real retry
Retry Eligible must invoke the actual failed canonical operation/stage with original canonical inputs plus validated explicit changes.
Create a new attempt linked to the parent failure, record disposition and produced output/evidence if successful, preserve original failure evidence, retain duplicate protections and reuse successful prior stages.

### UI/runtime
Build real list/filter/reason/eligibility UI and Retry action.
Integration must cover validation rejection, generator/stage failure, unavailable/inconclusive stage and successful control item, then prove lineage, no redo, duplicate safety and independent retry outcome.

Do not edit TASKS.md. Run full regressions and publish one R01 terminal log-only commit.