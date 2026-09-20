# SB-LFX-005-C001-R02 — Pipeline Rerun Evidence + Candidate Immutability Remediation

Work only on the remaining finding in:
`.hiveai/audits/SB-LFX-005-C001-R01_PIPELINE_STAGE_LINEAGE_AND_RUNTIME_MATRIX_REMEDIATION_STRICT_AUDIT.md`

Original criteria remain authoritative:
`.hiveai/audit-criteria/SB-LFX-005-C001_ONE_CLICK_PIPELINE_TRUTHFUL_ORCHESTRATION_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-005-C001-R02_PIPELINE_RERUN_EVIDENCE_IMMUTABILITY_REMEDIATION_CODEX_LOG.md`

Create the builder log before edits.

## Mission

Do not redesign the pipeline. Close only the remaining runtime-evidence gap.

Extend the real Godot pipeline integration to prove:

1. First pipeline run JSON/evidence bytes are snapshotted.
2. A second run creates a distinct run while leaving the first run record byte-identical.
3. Reused successful validation/source evidence references remain stable and are not silently replaced.
4. A real generated candidate bundle is snapshotted before pipeline execution:
   - metadata.json;
   - artwork.json;
   - artwork.png;
   - preview if present;
   and remains byte-identical afterward.
5. On the generated-candidate path:
   - CANDIDATE may be PASS where canonical evidence supports it;
   - SOLVE/DIFFICULTY stay NOT_AVAILABLE;
   - QA and REVIEW must not become PASS/accepted/ready without authority.
6. Source/candidate identities remain unchanged across rerun.

Only change product code if the stronger acceptance test reveals an actual defect.

Run focused integration, retained pipeline/LFX dependencies, full pytest, compileall, headless boot, diff-check and TASKS diff empty.

Publish one R02 implementation SHA and exactly one R02 terminal builder-log-only SHA. Do not edit TASKS.md.
