# SB-LFX-015-C001-R02 — Typed Session Schema + Real Recovery Remediation

Work only on:
`.hiveai/audits/SB-LFX-015-C001-R01_SESSION_SECRET_CONTAINMENT_REFERENCE_RECOVERY_AND_RUNTIME_REMEDIATION_STRICT_AUDIT.md`

Create log first:
`.hiveai/codex-logs/SB-LFX-015-C001-R02_TYPED_SESSION_SCHEMA_AND_REAL_RECOVERY_REMEDIATION_CODEX_LOG.md`

Replace heuristic recursive scrubbing with an explicit versioned allowlist session schema. Reject unknown fields/structures.

Define typed canonical reference fields and resolve each with real readers/validators:
- source;
- candidate;
- batch;
- pipeline run;
- retry;
- revision;
as applicable.

A syntactically valid but nonexistent ID must not validate.

Recovery classification must derive from real durable state:
RESUMED / RETRIED / NEW / NOT_RESUMABLE / NEEDS_OPERATOR_ACTION.

Real interruption/restart integration must:
- create real durable batch/pipeline work;
- save recovery state;
- restart Studio;
- validate references;
- prove completed stages are not duplicated/rerun;
- prove missing/corrupt reference -> operator action;
- corrupt session -> fail closed;
- prove no duplicate source/candidate;
- prove secrets cannot be persisted under arbitrary innocuous nested keys because only allowlisted schema fields exist.

No TASKS edit.
