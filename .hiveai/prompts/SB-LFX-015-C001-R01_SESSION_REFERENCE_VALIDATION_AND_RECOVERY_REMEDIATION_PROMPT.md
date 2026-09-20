# SB-LFX-015-C001-R01 — Session Reference Validation + Recovery Remediation

Work only on:
.hiveai/audits/SB-LFX-015-C001_SESSION_RECOVERY_AUTOSAVE_STRICT_AUDIT.md

Original criteria:
.hiveai/audit-criteria/SB-LFX-015-C001_FACTORY_STUDIO_SESSION_RECOVERY_AUTOSAVE_AUDIT_CRITERIA.md

Builder log:
.hiveai/codex-logs/SB-LFX-015-C001-R01_SESSION_REFERENCE_VALIDATION_AND_RECOVERY_REMEDIATION_CODEX_LOG.md

Create the builder log before edits.

## Mission
Close BLOCKER-001 and MAJOR-001..004.

### Safe session schema
Replace heuristic top-level secret scrubbing with an explicit allowlisted versioned session schema.
Persist only approved UI continuity fields, canonical record IDs/references and bounded non-canonical drafts.
Reject unknown nested structures rather than recursively preserving arbitrary data. Never persist secrets/provider tokens.

### Reference validation
On restore, resolve and validate each typed canonical reference through its real reader/validator: source, candidate, batch, pipeline, revision, retry as applicable.
Missing/corrupt/mismatched references must be reported and never recreated from session data.
Never emit validated_references=true unless the referenced records were actually validated.

### Recovery classification
Derive RESUMED / RETRIED / NEW / NOT_RESUMABLE / NEEDS_OPERATOR_ACTION from verified durable job state and capability.
Do not relabel every parsed session RESUMED.
Do not rerun successful durable stages by default.

### Real Studio + interruption integration
Implement actual save/autosave/restore UI/controller.
Simulate interruption during a real batch/pipeline workflow, restart Studio, restore context and prove completed stage identities unchanged, eligible work resumes, no duplicate sources/candidates, corrupt session fails closed, missing references are reported and secrets are absent.

Do not edit TASKS.md. Run full regressions and publish one R01 terminal log-only commit.