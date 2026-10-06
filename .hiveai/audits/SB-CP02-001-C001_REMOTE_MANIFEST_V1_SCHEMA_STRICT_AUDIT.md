# SB-CP02-001-C001 — Remote Manifest V1 Schema

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Implementation:
`1ed02965620bfbcc7ac39a8c52a97a2c390701a4`

Builder evidence:
`.hiveai/codex-logs/SB-CP02-001-C001_REMOTE_MANIFEST_V1_SCHEMA_CODEX_LOG.md`

## VERDICT

**PASS / CLOSED**

## Contract

PASS.

The implementation defines:
- immutable `ManifestPackV1`;
- immutable `ManifestLevelV1`;
- immutable `ContentManifestV1`;
- exact schema identity `scrubbots.content.manifest.v1`;
- exact integer `schema_version = 1`;
- closed root and child item shapes;
- deterministic pack and level ordering;
- canonical deterministic UTF-8 JSON serialization.

Unknown root/item fields and unsupported schema identity/version fail closed.

## Explicit model ownership

PASS.

`packs` and `levels` are typed immutable tuples of explicit manifest model types rather than arbitrary mappings.

Duplicate pack and level identities are rejected.

## Declarative-only boundary

PASS.

The new manifest model:
- performs no network access;
- contains no provider endpoint/credential behavior;
- performs no upload/download;
- performs no game/runtime mutation;
- does not modify `.scrubpack` identity;
- leaves content-version, compatibility, location/hash, disable/schedule, references, history and strict bytes parser to later M13 children.

The schema is closed and contains only declarative identity fields introduced by this child.

## Documentation / fixtures / tests

PASS.

Present:
- `content_pipeline/schemas/v1/content-manifest.schema.json`;
- canonical minimal fixture;
- `docs/content_platform/REMOTE_CONTENT_MANIFEST_V1.md`;
- focused child tests.

Focused child result: 9 passed.

M11/M12 + governance + child regression set: 261 passed.

compileall, schema/example JSON parse and diff check passed.

## Publication / scope

PASS.

Independent GitHub comparison from the M13 authority base through the builder publication shows no Codex modification of root `TASKS.md` or `.hiveai/audits/**`.

Implementation and builder log commits are separate.

## Master-level note

The unfiltered full pytest suite was intentionally stopped because a historical integration test automatically discovered `~/Desktop/ScrubBots` and attempted to use that separate owner checkout without explicit task capability.

That is a **master test-harness scope blocker**, not a defect in SB-CP02-001 product semantics.

The child audit criteria themselves are satisfied.

## FINAL

`SB-CP02-001 = PASS / CLOSED`
