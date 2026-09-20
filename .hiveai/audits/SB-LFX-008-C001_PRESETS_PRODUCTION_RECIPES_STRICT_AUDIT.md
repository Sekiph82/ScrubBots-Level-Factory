# SB-LFX-008-C001 — Presets / Production Recipes — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 3
- MINOR: 0
- NOTE: 0

## Audited chain

- Start: `5987ec84eaabf2ae7440c25bef6d40f2c048a7f0`
- Implementation: `4b01e116526800d0fc0133834f0843df1fef1814`
- Task-final log-only: `71705420e697cb9f9a08fe6275a37860071cc0a2`

## Accepted implementation semantics

Preset files are versioned, deterministically serialized, bounded in name/description and separated from source/candidate truth. Secret and fabricated solver/difficulty top-level fields are rejected. Updating/deleting a preset does not mutate an already materialized expanded dictionary.

## MAJOR-001 — preset application does not execute a real supported action

The Studio `apply_preset()` action only calls `preset-expand` and displays the resulting JSON.

It does not apply the expanded request to:
- canonical Generate;
- Import Validation;
- Pipeline;

and therefore no canonical execution record is persisted from a preset-derived request.

This fails the central requirement that every execution launched from a preset persist the fully expanded canonical request exactly as manual entry would.

### Required remediation

Wire preset application to at least one real supported canonical action (Generate is preferred) while preserving the expanded request as the execution input/provenance. The execution must not depend on the preset file after launch.

## MAJOR-002 — preset settings are not schema-complete or operation-validated

`save_preset()` accepts an arbitrary settings mapping for a supported operation except for four forbidden keys. It does not validate:
- required fields;
- allowed fields;
- types/ranges;
- canonical defaults;
- operation-specific request schema.

Therefore an incomplete or unknown-field preset can be saved and “expanded” without proving it is a valid full canonical request.

### Required remediation

Validate presets against the real operation request/control contract, reject unknown/unsupported fields, and resolve all required defaults into the expanded request.

## MAJOR-003 — required integration/provenance lifecycle evidence is absent

The criteria require proof of:
- create preset;
- apply to a real action;
- exact expanded request equality;
- mutate preset;
- prior execution unchanged/reproducible;
- new execution uses new values;
- delete preset without invalidating prior execution;
- invalid preset fail-closed.

The committed tests only exercise Python save/expand/update/delete data objects. No real Godot preset execution integration exists.

### Required remediation

Add real Factory Studio integration covering the complete lifecycle above and inspect the produced canonical execution records.

## Disposition

`SB-LFX-008` remains open pending remediation and re-audit.
