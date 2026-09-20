# SB-LFX-013-C001-R02 — Canonical Failure Discovery + Capability-Gated Retry Remediation

Work only on:
`.hiveai/audits/SB-LFX-013-C001-R01_FAILURE_ELIGIBILITY_REAL_RETRY_AND_RUNTIME_REMEDIATION_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-013-C001_FAILURE_INBOX_RETRY_CENTER_LINEAGE_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-013-C001-R02_CANONICAL_FAILURE_DISCOVERY_AND_CAPABILITY_GATED_RETRY_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Mission

Close the remaining canonical-source, UI-capability and runtime findings.

### Failure discovery authority
Stop treating free-form `record_failure()` records as product failure truth.

Build canonical adapters/readers over real evidence:
- import-validation rejected/error evidence;
- pipeline stage FAIL/BLOCKED/INCONCLUSIVE evidence;
- canonical batch-manifest attempt failure/rejection evidence where applicable.

Each Inbox row must bind:
- originating evidence type;
- exact evidence ID/path/hash;
- operation/stage;
- disposition;
- canonical original inputs/config or exact references;
- retryability + reason.

A normalized view/cache may exist only as derived in-memory truth. Do not make it a new failure authority store.

### Retry
Retry must operate from the originating canonical evidence, not a free-form record.

Keep operation-specific change allowlists. Preserve original evidence bytes. Record new retry attempt lineage/outcome/output identity.

### Capability-gated UI
- list/select real failure rows;
- render evidence identity, operation, stage, reason and eligibility;
- Retry button disabled by default and for non-retryable rows;
- enable only for selected verified retryable evidence;
- show explicit disabled reason.

### Real integration
Create real canonical:
1. validation rejection;
2. pipeline/stage failure or inconclusive evidence;
3. non-retryable unavailable stage;
4. successful control item.

Prove:
- only genuine failure evidence enters Inbox;
- successful control excluded from failed-only;
- eligible retry executes;
- at least one successful retry records output identity;
- original failure evidence remains byte-identical;
- successful prior stages are not rerun;
- duplicate protections remain;
- UI button gating is correct.

Do not edit TASKS.md. Full regressions, one R02 implementation + one terminal log-only commit.
