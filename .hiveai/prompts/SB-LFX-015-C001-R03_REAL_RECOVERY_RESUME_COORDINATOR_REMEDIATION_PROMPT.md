# SB-LFX-015-C001-R03 — Real Recovery Resume Coordinator Remediation

Work only on:
`.hiveai/audits/SB-LFX-015-C001-R02_TYPED_SESSION_SCHEMA_AND_REAL_RECOVERY_REMEDIATION_STRICT_AUDIT.md`

Create builder log first:
`.hiveai/codex-logs/SB-LFX-015-C001-R03_REAL_RECOVERY_RESUME_COORDINATOR_REMEDIATION_CODEX_LOG.md`

Retain the accepted typed allowlist session schema, canonical reference validation and session integrity digest.

The remaining task is execution, not another classification-only layer.

Required:

1. Add a bounded operation-specific recovery coordinator for durable work types that can actually resume safely.
2. `RESUMED` must mean eligible interrupted work was really continued/re-entered through the canonical path, not merely that its references validated.
3. Already successful durable stages must be reused by exact identity/evidence and must not rerun by default.
4. `RETRIED` must represent a separate explicit retry attempt after failure.
5. Work that cannot safely resume must be `NOT_RESUMABLE` or `NEEDS_OPERATOR_ACTION`; do not fabricate continuation capability.
6. No source/candidate/job truth may be copied into the session as a second authority.

Real restart/interruption integration:

- create durable multi-stage/batch/pipeline work;
- establish an interrupted/resumable state using a real supported boundary;
- save typed recovery state;
- destroy/reinstantiate Studio or use a fresh process;
- restore and execute the recovery coordinator;
- prove completed stage IDs/evidence are unchanged and reused;
- prove eligible remaining work resumes only once;
- prove no duplicate source/candidate/job is created;
- prove missing/corrupt references require operator action;
- corrupt session and fail closed;
- prove unknown/secret-bearing state cannot enter the allowlisted session.

Do not claim a task is resumable if the canonical operation has no safe resume contract. No TASKS edit.

Publish one R03 implementation SHA and one terminal log-only SHA.
