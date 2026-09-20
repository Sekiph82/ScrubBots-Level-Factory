# SB-LFX-008-C001 — Presets / Production Recipes with Expanded Canonical Request — Strict Audit Criteria

Target:
`SB-LFX-008 — Add reusable Presets / Production Recipes while always persisting the fully expanded canonical request/config. [EXTENSION]`

## Principle

A preset is UI convenience, never canonical execution provenance.

## Requirements

Implement versioned operator preset/recipe records for supported Studio operations. Presets may include dimensions, generation mode, import-validation choices and other currently real controls.

Every execution launched from a preset must persist the fully expanded canonical request/config exactly as if the operator entered values manually.

The canonical execution record must not depend on the preset still existing later.

## BLOCKERS

FAIL if:
- canonical provenance stores only preset ID/name;
- changing a preset changes history of past jobs;
- hidden/default values are omitted from expanded request;
- preset can inject unsupported provider/solver/difficulty truth;
- preset overwrites source/candidate truth;
- preset storage becomes project tracker;
- TASKS is edited.

## Preset lifecycle

Require create/read/update/delete or immutable-revision semantics with:
- versioned schema;
- bounded name/description;
- operation kind;
- validated settings;
- deterministic serialization;
- explicit unsupported-field rejection.

Updating a preset affects only future applications.

## Real integration

Prove:
- create preset;
- apply to real supported action;
- expanded execution request exactly matches resolved controls;
- mutate preset;
- prior execution remains unchanged/reproducible;
- new execution uses new values;
- deletion does not invalidate prior execution;
- invalid preset fails closed.

## PASS rule

PASS when presets improve operator reuse without weakening explicit canonical request provenance or historical reproducibility.
