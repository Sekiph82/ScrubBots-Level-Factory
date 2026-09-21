# SB-LFX-013-C001-R02 — Canonical Failure Discovery + Retry UI Remediation

Work only on:
`.hiveai/audits/SB-LFX-013-C001-R01_FAILURE_ELIGIBILITY_REAL_RETRY_AND_RUNTIME_REMEDIATION_STRICT_AUDIT.md`

Create log first:
`.hiveai/codex-logs/SB-LFX-013-C001-R02_CANONICAL_FAILURE_DISCOVERY_AND_RETRY_UI_REMEDIATION_CODEX_LOG.md`

Stop using caller-created `record-failure` evidence as product truth.

Build Failure Inbox by scanning/verifying actual canonical:
- import-validation evidence;
- pipeline-run evidence;
- batch/job failure/rejection/inconclusive evidence.

Every normalized inbox entry must bind its originating evidence ID/path/hash.

Retry must continue using operation-specific canonical execution and append-only retry evidence.

Studio must render:
- selectable failure rows;
- operation/stage;
- reason;
- originating evidence ID;
- retryable state;
- non-retryable reason;
- Retry button disabled unless selected entry is genuinely retryable.

Real integration must generate/discover real validation rejection, real pipeline/stage failure or inconclusive evidence, successful control item, and unavailable SOLVE/DIFFICULTY. Refresh Inbox without manually recording failure truth. Prove only eligible entries retry, original evidence remains, no successful work is retried, and duplicate/successful-stage protections remain.

No TASKS edit.
