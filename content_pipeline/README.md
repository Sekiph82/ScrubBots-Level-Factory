# Content Pipeline Boundary

`content_pipeline/` is a separate publisher/control-plane project. Level Factory
produces accepted declarative content and evidence; this project defines how
future packaging, validation, publishing, promotion, rollback, and reports are
organized. Scrubbots runtime may consume approved declarative output only under
later separately authorized milestones.

## Current capability

The Python package under `src/scrubbots_content_pipeline/` is a standalone
project with its own `pyproject.toml`. Its only executable path is local
validation-only/dry-run reporting:

```powershell
python -m pip install -e .\content_pipeline
scrubbots-content-pipeline --validate-only --environment staging
```

The versioned configuration schema is in `schemas/v1/`. Environment labels,
provider protocols, and publish/promote/rollback interfaces are placeholders.
No provider implementation, remote operation, credential, or network client is
present. Reports describe local validation only.

## Ownership and dependency direction

- Root `TASKS.md` remains the sole task ledger, owned by ChatGPT. This project
  does not define a second tracker or task state.
- Level Factory is the producer of accepted declarative content and evidence.
  This control plane may consume only stable, explicitly versioned contracts;
  it must not reach into private generator or solver internals.
- Level Factory product code must not depend on this publisher project.
- Gameplay/runtime code must not import publisher/control-plane code.
- This project must not import Godot, gameplay, runtime, or private
  Level Factory implementation modules.
- Remote payloads are declarative data. Executable scripts, expressions, or
  arbitrary remote code are outside this boundary.
- Credentials belong in a future separately reviewed secret-management
  integration, never in this repository's source or configuration files.

## Deferred work

Provider selection, storage/CDN, remote mutation, credentials, pack formats,
runtime consumption, store release, and operational scheduling require later
separately authorized tasks. The interfaces here do not establish that any
provider operation is safe or available.
