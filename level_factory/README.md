# SCRUBBOTS Level Factory

`level_factory/` is the project-local shell for Factory-facing Godot work. It
is an independently openable Godot 4 project rooted at this directory.

The existing Python Factory Core and semantic implementation at the repository
root remain canonical. They are not moved, copied, or reimplemented in
GDScript by this project shell.

## Local boundaries

- `docs/` contains concise technical documentation for this project boundary.
- `scenes/` contains Godot scenes owned by the Factory project.
- `scripts/` contains the authorized Studio-side adapter and presentation
  scripts. `factory_core_launcher.py` is only a thin local entrypoint that
  adds the repository `src/` path and delegates to the canonical Python CLI;
  it is not a second Factory Core.
- `tests/` contains committed Godot-local smoke and integration tests; the
  root Python test suite remains canonical for Factory Core semantics.
- `output/` is the Factory-produced/export staging boundary.

The root `TASKS.md` is the sole live task ledger. Project-local documentation
must not create a second tracker or acceptance authority. Main-game runtime
implementation belongs to `Sekiph82/Scrubbots` only when separately
authorized. Generated or provider-backed features are not implied by this
project shell.

Owner-approved future Studio/operator workflows, including the Factory
Operations Dashboard, manual Pixel Art import, Source Art Library, one-click
pipeline, unified review workflow, retry/recovery tools, comparison/search
surfaces, and provider accounting, are specified in
`../docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`. That
product plan does not imply those capabilities are already implemented and it
must remain an orchestration/presentation layer over canonical Factory truth.

The broader generated, candidate, cache, and secret-folder policy remains
owned by `SB-LF00-006`; this document does not claim that policy is complete.

## Verification

The focused editor-smoke and headless-Core gate is runnable with:

```text
python -m pytest -q tests/unit/test_sb_lf06_012_factory_studio_editor_smoke_and_headless_core_test_gate.py
```

The project boot check is:

```text
godot --headless --path level_factory --quit
```

Run the complete Python regression suite with:

```text
python -m pytest -q
```

The smoke gate executes without GUI interaction, provider/network access, or
credentials. It directly exercises the canonical Python Factory Core and
cleans its bounded temporary output.
