# SB-LFX-005-C001-R01 — Pipeline Stage Lineage + Runtime Matrix Remediation

Work only on:
`.hiveai/audits/SB-LFX-005-C001_ONE_CLICK_PIPELINE_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-005-C001_ONE_CLICK_PIPELINE_TRUTHFUL_ORCHESTRATION_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-005-C001-R01_PIPELINE_STAGE_LINEAGE_AND_RUNTIME_MATRIX_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Mission

Close MAJOR-001 and MAJOR-002 without broad redesign.

### Stage contract
Give every persisted stage record a consistent versioned shape containing:
- stage;
- disposition;
- canonical input identity/reference list;
- canonical output identity/reference list when produced;
- evidence reference;
- exact reason.

Populate this even for NOT_APPLICABLE / NOT_AVAILABLE / BLOCKED stages. Do not fabricate an output identity when none exists.

### Runtime acceptance
Extend real Godot pipeline integration to prove:
- exact OWNER_UPLOAD path;
- real canonical generated-candidate path;
- validation-failure path;
- unavailable dependency stop;
- rerun/history retention;
- successful prior stage evidence is retained rather than silently overwritten/redone;
- source/candidate bytes unchanged;
- no false QA/review/readiness.

Use real canonical candidate/bundle identities.

Do not implement missing M03/M04/M05 authorities.

Run focused + retained tests + full suite and publish one R01 log-only terminal commit. Do not edit TASKS.
