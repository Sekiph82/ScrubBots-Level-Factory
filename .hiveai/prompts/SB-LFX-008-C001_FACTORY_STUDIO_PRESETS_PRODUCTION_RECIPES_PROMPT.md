# SB-LFX-008-C001 — Factory Studio Presets / Production Recipes

Builder log:
`.hiveai/codex-logs/SB-LFX-008-C001_PRESETS_PRODUCTION_RECIPES_CODEX_LOG.md`

Create log first. Work only on LFX-008.

Read current Generate, Import Validation and pipeline request contracts.

Implement versioned presets as operator convenience only. Support only controls that are genuinely canonical today.

When applying a preset:
- resolve all defaults/fields;
- show resolved values;
- send/persist the full expanded canonical request;
- never rely on preset ID for reproduction.

Preset edits affect future runs only.

Test create/apply/update/delete, invalid fields, expanded request equality, and historical execution immutability.

Do not add provider secrets, solver/difficulty fiction, smart collections or LFX-009+ work. Do not edit TASKS.

Commit/push implementation then one task-final log-only commit; continue only under batch master.
