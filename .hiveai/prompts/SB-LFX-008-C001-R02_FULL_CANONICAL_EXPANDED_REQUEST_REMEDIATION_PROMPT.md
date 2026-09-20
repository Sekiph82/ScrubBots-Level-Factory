# SB-LFX-008-C001-R02 — Fully Expanded Canonical Preset Request Remediation

Work only on:
`.hiveai/audits/SB-LFX-008-C001-R01_PRESET_SCHEMA_REAL_EXECUTION_AND_PROVENANCE_REMEDIATION_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-008-C001_PRESETS_PRODUCTION_RECIPES_EXPANDED_REQUEST_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-008-C001-R02_FULL_CANONICAL_EXPANDED_REQUEST_REMEDIATION_CODEX_LOG.md`

Create the builder log before edits.

## Mission

Close the single remaining canonical-request finding.

The editable preset may stay as the bounded operator-facing Generate fields, but applying it must first construct the real canonical `GenerationRequest`.

Persist the **complete**:
`GenerationRequest.canonical_dict()`

as the preset execution's expanded canonical request, or persist an immutable exact reference + digest while still returning the complete canonical request in the execution projection.

The expanded canonical request must include all canonical/defaulted fields, including:
- request schema/version;
- typed seed;
- generator_mode;
- difficulty;
- width/height;
- style;
- theme;
- palette subset;
- generator options.

## Required real runtime proof

1. Create/apply a preset.
2. Read the produced candidate bundle `metadata.json`.
3. Require preset execution `expanded_request` == `metadata.generation.request` exactly.
4. Require typed seed/schema/version/defaults to be present.
5. Update preset and launch again.
6. Prove prior execution expanded request + candidate bundle remain byte-identical.
7. Delete preset.
8. Prove prior execution remains valid and canonical Reproduce still uses its recorded request.

Do not broaden preset scope beyond truthful currently supported operations.

Run full required regressions. Publish one R02 implementation commit and one terminal R02 log-only commit. Do not edit TASKS.md.
