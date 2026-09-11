# PAG-SP01-C001 — Semantic Contracts & Provider Boundary

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authority

Read first:

1. `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
2. `review/m10/M10_OWNER_REVIEW_DECISION.md`
3. root `TASKS.md` for historical M00-M10 contracts
4. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`

The owner has rejected the M10 visual pack 100/100. M00-M10 deterministic/validation/export infrastructure remains retained. This cycle begins the semantic conversion and must not restart or rewrite accepted subsystems.

## Mission

Implement **SP01 only**: the provider-neutral semantic generation contracts and boundary.

Do not install or integrate ComfyUI/model workflows yet. Do not begin SP02.

## Required production work

Create a new semantic package/layer under the existing Python project with names consistent with repository conventions.

### 1. Output class

Define versioned output-class semantics:

- `LEVEL_ART`
- `ASSET_ART`

`LEVEL_ART` must remain bound to existing ScrubBots difficulty/dimension/palette legality.

`ASSET_ART` must be explicitly separate from LevelData legality and support explicit logical dimensions including at least 16x16, 24x24, 32x32, 48x48, and 64x64 without pretending those are ScrubBots level difficulties.

### 2. SemanticGenerationRequest

Add an immutable/canonical/versioned request model containing at least:

- schema version;
- output class;
- description;
- optional negative description;
- optional semantic category;
- difficulty for LEVEL_ART where applicable;
- explicit/derived width and height;
- seed;
- no-background flag;
- outline;
- shading;
- detail;
- view;
- direction;
- isometric flag;
- coverage percentage;
- reference-image descriptors;
- optional style-image descriptor + strength;
- optional init-image descriptor + strength;
- optional color/palette-reference descriptor;
- provider id;
- provider workflow/config version;
- desired candidate count where appropriate.

Canonical serialization must be deterministic and must not use timestamps/UUIDs/Python hash as identity.

### 3. Image input descriptor

Define immutable source-image descriptors based on content identity, not absolute local paths. At minimum record:

- role;
- content SHA-256;
- media type/format where known;
- width/height where known;
- optional stable owner/source label.

A request must not depend on machine-specific absolute paths for canonical identity.

### 4. SemanticGeneratorProvider interface

Define provider-neutral interface/protocol/abstract base with explicit capabilities and failure semantics.

Provider methods must support at least:

- provider identity/version;
- capability declaration;
- request validation;
- generation returning typed result(s);
- explicit unavailable/unsupported/failure result rather than partially valid success.

Core contracts must not import ComfyUI-specific code.

### 5. SemanticImageCandidate / provider result

Define a typed immutable candidate/result boundary containing at least:

- candidate/source id;
- request digest;
- provider id/version;
- provider workflow/model identity fields;
- seed;
- requested dimensions;
- returned image dimensions;
- raw image content SHA-256;
- image bytes or a safe project-owned immutable binary representation boundary;
- reference/style/init/color provenance echoes;
- success/failure state;
- failure/retry reason;
- generation metadata separated from canonical deterministic identity where non-deterministic fields exist.

No semantic result is allowed to masquerade as a validated M08 logical-grid bundle yet. Ingestion/normalization belongs to SP03.

### 6. Capability model

Create a versioned capability structure able to express at least:

- text-to-image;
- negative prompt;
- transparent background;
- reference images;
- style image;
- init image;
- palette/color reference;
- inpaint support;
- view/direction controls;
- isometric;
- rotation variants;
- animation.

SP01 does not implement all capabilities. It defines the truthful contract for future providers.

### 7. Deterministic identity

Define project-owned canonical digest rules for semantic requests/results.

Prove:

- same canonical request => same request digest;
- field-order differences do not change identity;
- material prompt/seed/dimension/provider/workflow/reference-image changes do change identity;
- non-identity audit timestamps do not alter canonical identity;
- machine-specific path differences cannot alter identity when source content is identical.

### 8. Preserve existing system

Do not modify behavior of accepted MASK/RULES/WFC/HYBRID/AUTO generators in this cycle.

Do not weaken:

- existing deterministic RNG contracts;
- M07 structural quality;
- M08 export/provenance;
- M09 CLI/batch/reproduce;
- M10 tests/performance artifacts.

No existing generated output should change because SP01 exists.

## Tests

Add focused unit/property/integration tests covering at least:

- valid LEVEL_ART semantic request;
- valid 16x16 ASSET_ART request;
- valid rectangular ASSET_ART request;
- LEVEL_ART illegal dimensions rejected by existing difficulty rules;
- ASSET_ART 16x16 accepted without creating fake EASY difficulty;
- empty description rejected;
- invalid outline/shading/detail/view/direction rejected;
- invalid strengths/coverage rejected;
- canonical request serialization/digest determinism;
- source descriptor content-hash identity;
- same content with different local path remains same canonical source identity;
- changed reference image hash changes request digest;
- provider capability validation;
- unsupported capability fails closed;
- failed provider result cannot be consumed as success;
- semantic candidate is not accepted as M08 logical-art bundle without future SP03 normalization;
- full existing regression suite passes unchanged.

## Documentation

Add concise semantic contract documentation and package README if appropriate.

Explicitly document:

- PixelLab-like controls are product/interface inspiration only;
- PixelLab proprietary backend is not copied;
- first automated provider target will be local ComfyUI in SP02;
- no new paid image API is required by architecture;
- LEVEL_ART and ASSET_ART are separate contracts;
- current procedural generators are retained as downstream/control infrastructure.

## Builder log

Create before implementation edits:

`.hiveai/codex-logs/PAG-SP01-C001_SEMANTIC_CONTRACTS_AND_PROVIDER_BOUNDARY_CODEX_LOG.md`

Use exact H1:

`# PAG-SP01-C001 — Semantic Contracts & Provider Boundary`

Role line:

`Document role: CODEX BUILDER LOG`

Record start HEAD/origin/divergence before production edits, focused tests, full tests, compile/import checks, final scoped diff, commits, push, and final HEAD == origin/main divergence 0 0.

## Forbidden

- Do not delete/rewrite M00-M10 accepted infrastructure.
- Do not implement ComfyUI yet.
- Do not add model weights.
- Do not add a paid image API.
- Do not scrape/automate PixelLab website.
- Do not copy PixelLab proprietary backend code.
- Do not begin Studio UI.
- Do not modify the rejected M10 grids.
- Do not mark owner rejection as resolved.
- Do not begin M11.
- Do not self-audit.

## Stop condition

Stop after SP01 implementation, tests, publication, push, and completed builder log. Return the builder log for independent ChatGPT strict audit.
