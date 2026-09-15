# Project-Local Directory Boundaries

These roles describe the `level_factory/` project shell and are not tracker
truth.

- `scenes/` — Godot scenes owned by the Factory project.
- `scripts/` — authorized Godot-side adapter/presentation scripts and the
  narrow `factory_core_launcher.py` transport entrypoint. The launcher only
  delegates to the canonical repository Python CLI and is not a duplicated
  implementation.
- `tests/` — future Godot-local tests and fixtures; the root Python tests remain
  the canonical Factory implementation test suite.
- `output/` — Factory-produced or export staging boundary. Its existence does
  not declare the broader generated, candidate, cache, or secret policy
  complete.
- `docs/` — project-local technical documentation, not tracker truth.

`SB-LF00-006` still owns the broader generated/candidate/cache/secret folder
and exclusion policy. No project-local directory is a second task ledger or
acceptance authority.
