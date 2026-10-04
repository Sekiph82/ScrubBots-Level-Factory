# SB-CP00-003-C001 — Declarative-Only Remote Payload Policy

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent:
`SB-CP00-002 = PASS / CLOSED`

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

Before implementation, tests, or builder-log work:

1. Verify the canonical persistent Level Factory path, repository identity, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Fetch/prune current `origin/main`.
3. Read task authority from GitHub/`origin/main:TASKS.md`. Accept either standalone authority for `SB-CP00-003 / SB-CP00-003-C001`, or the explicit M11 master authority `.hiveai/prompts/M11_CP00_003_009_MASTER_IMPLEMENTATION_PROMPT.md` that lists this child first.
4. Preserve legitimate owner-local dirty work. Do not reset, clean, stash, rebase, force, overwrite, restore, or discard it.
5. If the persistent checkout cannot be safely synchronized, use only an explicitly authorized temp worktree under `%TEMP%\ScrubBots-Level-Factory\SB-CP00-003-C001`, based on current `origin/main`.
6. Do not create a Desktop sibling clone/worktree.
7. Stop if incoming remote changes overlap implementation scope ambiguously.

## Goal

Implement:

`SB-CP00-003 — Remote content declarative only; forbid executable payloads.`

SB-CP00-002 classifies descriptors. This task adds the **payload-level** trust boundary.

Do not implement remote download, upload, provider mutation, CDN/storage, runtime activation, credentials, or game integration.

## Required payload validator

Under `content_pipeline/`, add a pure local validator for payload bytes/data associated with an already REMOTE_DECLARATIVE descriptor.

The validator must:
- accept only the current allow-listed declarative JSON families;
- parse without executing/importing payload content;
- fail closed;
- return deterministic versioned validation results/reason codes;
- bind validation to the descriptor's content family and payload contract;
- verify the descriptor digest against exact payload bytes where the descriptor carries a payload digest;
- reject a payload whose structure/identity does not match its descriptor.

## JSON safety

Require strict JSON handling:
- UTF-8 only;
- top-level object where current contract requires object;
- reject duplicate object keys;
- reject NaN/Infinity/non-standard numeric values;
- reject malformed JSON;
- enforce bounded nesting/collection/string sizes appropriate for current declarative content;
- no dynamic object construction, eval, exec, import, reflection, script loading, or resource loading.

Limits must be deterministic constants and documented.

## Executable-content prohibition

Even inside otherwise JSON-shaped payloads, fail closed on executable/application behavior surfaces that are outside current declarative contracts.

At minimum reject:
- script/script-path fields;
- executable expressions;
- plugin/addon/autoload/native-code/module references;
- Godot resource/script references such as `res://*.gd`, scenes/resources/shaders where not explicitly part of an approved declarative contract;
- arbitrary command/process/network/file-operation descriptors;
- unknown extra fields that could smuggle future behavior.

Do not reject legitimate inert current production fields merely because their text contains harmless words. Structural contract validation is the primary authority.

## Current family validation

### LevelData V1
Validate the current Level Data Spec V1 structure needed by the current contract:
- version 1;
- id/name/difficulty;
- positive dimensions within the existing accepted production envelope;
- palette;
- cells;
- cell count = width × height;
- cell indices valid for palette;
- no unknown executable-bearing fields.

Do not import Scrubbots runtime code.

### Supply plan V1
Validate current `scrubbots.level_supply_plan.v1` structure, including at least:
- schema/version;
- levelId;
- columnCount 3..5;
- visiblePreviewDepth exactly 3;
- positive per-plan max bound where present/current;
- complete columns matching columnCount;
- batch IDs/color IDs/positive robot counts structurally valid;
- no executable-bearing extras.

Do not reproduce gameplay solve logic. This is payload safety/schema validation only.

### Publisher metadata V1
Validate current `scrubbots.level.metadata.v1` structural identity and the fields represented by the accepted remote descriptor.

Do not turn metadata validation into Difficulty/gameplay reimplementation.

## Descriptor/payload binding

Reject when:
- descriptor content type and payload type disagree;
- descriptor payload contract and payload embedded schema/version disagree;
- level IDs disagree;
- descriptor dimensions/columns/preview depth disagree with payload;
- descriptor SHA-256 does not match exact payload bytes.

## Architecture preservation

Retain SB-CP00-001 and SB-CP00-002:
- no live remote mutation;
- no provider implementation;
- no credentials;
- no game/runtime imports;
- no reverse dependency;
- no second tracker;
- app-vs-remote classifier remains fail closed.

Do not duplicate generator, solver, Difficulty V1, or gameplay logic.

## Tests

Add focused positive tests using current contract-shaped payload fixtures and negative corpus covering:
- malformed JSON;
- duplicate keys;
- non-finite numbers;
- invalid UTF-8;
- wrong family/schema/version;
- descriptor/payload mismatch;
- hash mismatch;
- extra executable-bearing fields;
- script/resource/plugin/native/expression smuggling;
- excessive nesting/collection/string size;
- no payload execution/import/I/O/network mutation.

Run:
- focused SB-CP00-003 tests;
- SB-CP00-002 + R01 tests;
- SB-CP00-001 tests;
- governance/tracker tests;
- full pytest;
- compileall;
- git diff --check.

## Builder log

Create before product edits:
`.hiveai/codex-logs/SB-CP00-003-C001_DECLARATIVE_ONLY_REMOTE_PAYLOAD_POLICY_CODEX_LOG.md`

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.

## Publication

After all gates pass:
- commit implementation;
- commit builder log separately;
- fetch/prune;
- normal non-force update to Level Factory `main`;
- verify local/remote 0/0.

Standalone mode: stop for independent ChatGPT audit.

M11 master mode: do NOT stop for audit and do NOT edit `TASKS.md`; return control to the master prompt and continue directly to `SB-CP00-004-C001`.

## Final response

Standalone mode: return only the child builder-log URL below.

M11 master mode: do not produce a user handoff here. Record the child result in its builder log and return control to the master.

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-003-C001_DECLARATIVE_ONLY_REMOTE_PAYLOAD_POLICY_CODEX_LOG.md
