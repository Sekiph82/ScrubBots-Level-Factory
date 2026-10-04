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

The versioned `EnvironmentTarget` model gives staging and production distinct
logical target IDs, state namespaces, and content namespaces. Production targets
do not permit direct publication and require an explicit promotion intent.
`validate_environment_pair()`, `validate_target_binding()`, and
`validate_target_use()` are pure local checks; they reject collisions,
environment mismatches, unknown labels, and staging-to-production use without
promotion intent. Dry-run reports name the environment and target namespaces
explicitly. The target model contains no provider endpoint or credentials.

`release_state.py` provides a versioned in-memory release ledger. Callers supply
event IDs, transition IDs, and sequence numbers; events carry the content digest,
environment, expected state, and previous-event digest. Replay verifies the
append-only hash chain and transition order before rebuilding each record.
Promotion creates a separate production record linked to a staged source, and
rollback appends a new event that references a previously promoted record.
Serialization is deterministic; the state machine does not read clocks, use
random IDs, access storage, or contact providers.

## App code and remote content boundary

The versioned descriptor contract is `schemas/v1/content-boundary.schema.json`.
The local `classify_content()` API accepts only an explicit allow-list of
versioned JSON descriptors for Level Data V1, supply-plan V1, and current
publisher metadata V1. Each `descriptor_contract_id` names this package's
normalized descriptor contract; it is not a field claimed to exist inside the
payload. `payload_contract` separately records the production authority and
version. Supply plans bind to the emitted/loaded
`scrubbots.level_supply_plan.v1`, and publisher metadata binds to
`scrubbots.level.metadata.v1`.
Descriptor attributes are normalized projections of production fields: `id`
maps to `level_id`, `columnCount` maps to `columns`, and
`visiblePreviewDepth` maps to `preview_depth`. They do not claim those renamed
attributes are embedded in the production payload.

Level Data V1 has no embedded schema string. Its descriptor therefore uses the
boundary-owned `scrubbots.content-pipeline.level-data.v1` identity and records
`payload_contract.authority = "Level Data Specification"` with version `1`;
the Level Data payload itself remains `version: 1` with its current `id`,
`name`, `difficulty`, dimensions, palette, and cells fields. Cross-authority
tests inspect the current Level Factory exporter/publisher source and a
commit-pinned read-only fixture of current Scrubbots loader/spec authority.
The classifier returns `REMOTE_DECLARATIVE`, `APP_OWNED`, or `REJECTED` with
the boundary version and stable reason codes. It never opens, imports,
evaluates, or executes the referenced payload.

Examples under `schemas/v1/examples/` show the three eligible data families.
Scripts, Python, native binaries, plugins/addons, scenes/resources, shaders,
absolute paths, traversal, unknown types/extensions/schemas, and descriptors
that include executable fields or script references fail closed as
`APP_OWNED` or `REJECTED`. A future content family is ineligible until its
versioned contract and classification rules are explicitly added.

`validate_remote_payload(descriptor, payload)` adds payload-level validation
for descriptors already classified as `REMOTE_DECLARATIVE`. Prefer UTF-8
payload bytes so the declared SHA-256 binds to those exact bytes; parsed data is
rejected when a descriptor carries a digest because its byte provenance cannot
be established. Results use stable reason codes under validation version
`1.0`. Parsing does not import, execute, or load payload content.

The deterministic resource limits are 1 MiB per byte payload, nesting depth
32, 65,536 members per collection, 8,192 characters per string, and 256 cells
per LevelData dimension. Current LevelData V1, supply-plan V1, and publisher
metadata V1 each use explicit field allow-lists. Unknown fields, duplicate JSON
keys, non-finite numbers, executable references, and descriptor/payload
projection mismatches fail closed.

Executable-capable content remains app-owned because shipping it remotely
would change application behavior and expand the runtime attack surface. Level
Factory remains the producer of accepted data; this package owns the
classification contract. Runtime enforcement and cross-version compatibility
remain deferred to separately authorized pack/runtime milestones.

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
