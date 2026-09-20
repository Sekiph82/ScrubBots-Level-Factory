# SB-LFX-008-C001-R01 — Preset Schema + Real Execution + Provenance Remediation

Work only on:
`.hiveai/audits/SB-LFX-008-C001_PRESETS_PRODUCTION_RECIPES_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-008-C001_PRESETS_PRODUCTION_RECIPES_EXPANDED_REQUEST_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-008-C001-R01_PRESET_SCHEMA_REAL_EXECUTION_AND_PROVENANCE_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Mission

Close MAJOR-001..003.

### Operation schemas
For every supported preset operation in this remediation:
- define/reuse the real canonical request/control schema;
- reject unknown/missing/invalid fields;
- validate types/ranges;
- resolve every canonical default;
- emit a full expanded request.

Do not support operations that cannot yet be validated truthfully.

### Real execution
Wire Apply Preset to at least the real canonical Generate action.

The execution must:
- use the expanded request, not preset ID, as canonical input;
- persist normal canonical GenerationRequest/metadata;
- remain reproducible if the preset is later edited/deleted.

### Lifecycle integration
Real Godot test:
1. create preset;
2. apply to Generate;
3. prove canonical recorded generation request equals expanded preset request;
4. update preset;
5. prove prior execution unchanged/reproducible;
6. run again and prove new execution uses updated expanded request;
7. delete preset;
8. prior execution still valid;
9. invalid/unknown preset field fails closed.

No LFX-009+ expansion. Full regressions, one R01 log-only terminal commit, no TASKS edit.
