# Factory Studio Workspace Foundation

This document describes the `SB-LF06-001-C001` workspace foundation. It is
implementation documentation, not a tracker or acceptance record. Root
`TASKS.md` remains the only live project-status ledger.

## Ownership and structure

`level_factory/project.godot` opens `scenes/factory_studio.tscn` as the main
scene. The scene is a real, deterministic shell with four presentation layers:

- `factory_studio_shell.gd` owns application composition and connects the
  navigation, workspace page, and Core status footer.
- `factory_studio_navigation.gd` owns the single future-surface navigation
  list. It emits selection events but does not implement later operations.
- `factory_studio_workspace_page.gd` owns the current page presentation and
  truthfully labels unavailable or unimplemented surfaces.
- `factory_core_gateway.gd` owns the narrow canonical-Core status contract.

The shell presents the following future surfaces exactly once as navigation:
Dashboard, Generate, Import, Library, Batches, Candidates, Review, QA,
Providers, Outputs, and Settings. They are presentation placeholders only.
There are no generated records, fake metrics, balances, solver results, QA
dispositions, provider calls, import operations, or persistent Studio state.

## Canonical-Core gateway boundary

The Python Factory Core at the repository root remains canonical. This Godot
project does not copy its algorithms, compile a second representation, or
silently invoke a subprocess. `FactoryCoreGateway` currently exposes truthful
status-only values: `AVAILABLE`, `UNAVAILABLE`, and `ERROR`, with the current
foundation status fixed to `UNAVAILABLE`. A later audited integration may add a
local invocation adapter and capability-specific status source, but it must
preserve canonical Core ownership, explicit failure states, provenance, and
the offline boundary.

No credentials, environment-secret values, provider services, runtime HTTP, or
network dependency are used by this workspace.

## Run and verification commands

From the repository root, open the project with:

```text
godot --editor --path level_factory
```

The headless project/editor load contract is:

```text
godot --headless --path level_factory --editor --quit
```

The root Python Factory Core and its root test suite remain the canonical
implementation and regression surface. This Factory-local shell does not
replace those tests with Godot-local truth.

## Future extension direction

Later Dashboard, import, library, provider, pipeline, review, batch, search,
readiness, reproduction, and edit-lineage behavior must be added only through
separately authorized and independently audited tasks. The owner-approved
extension plan is a product direction, not an implementation license for this
foundation. Future surfaces must remain derived presentation over canonical
records rather than a second tracker, compiler, solver, validator, or
production database.
