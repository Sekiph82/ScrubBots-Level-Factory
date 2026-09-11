# PAG-SP02-C001 — Magnific Job Spec & Result Import Bridge
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authority

Read first:

1. root `TASKS.md`
2. `.hiveai/audits/PAG-SP01-C003_NON_SUCCESS_PROVENANCE_ECHO_AND_MISMATCH_TEST_SENSITIVITY_CLOSURE_STRICT_AUDIT.md`
3. `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
4. `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
5. `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`
6. `src/scrubbots_pixel_factory/semantic/`
7. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`

SP01 is `PASS / CLOSED`. Magnific is the owner-selected primary semantic provider while credits are available, but the Factory core must remain provider-neutral.

## Mission

Implement **SP02-C001 only**: a deterministic, fail-closed **Magnific external-orchestration job specification and result-import bridge** behind the SP01 semantic contracts.

This cycle must NOT scrape the Magnific website, use undocumented/private Magnific endpoints, add credentials, or directly spend Magnific credits from Codex.

The local Factory cannot assume it owns the connected ChatGPT Magnific tool. Instead:

1. the Factory prepares a canonical/versioned Magnific job spec;
2. an owner-authorized orchestration surface executes that spec externally;
3. the external surface returns a result manifest plus raw image bytes;
4. the Factory verifies and imports them into an exact `SemanticImageCandidate`.

Independent ChatGPT audit will perform the first live Magnific smoke generation after the bridge is technically accepted enough to test.

## Current Authorized Magnific Tool Reality

The currently available owner-authorized image-generation surface conceptually exposes these relevant fields:

- prompt;
- model/mode slug;
- aspect ratio;
- count;
- optional references with explicit reference type;
- optional provider resolution/quality when supported by the selected model.

Important limitations for SP02:

- the surfaced text-to-image call does **not** expose a deterministic provider seed;
- it does **not** expose exact 16x16 / 20x20 / 20-59 raster dimensions;
- it does **not** expose a dedicated negative-prompt field in the current image-generation call;
- it does not expose PixelLab-style explicit outline/shading/detail/direction controls as provider-native parameters;
- returned provider raster may be much larger than the requested logical ScrubBots dimensions;
- logical resizing/normalization is **SP03**, not SP02.

Do not fabricate provider capabilities that do not exist. Do not claim provider-level deterministic regeneration from the ScrubBots seed.

## Required Production Work

Create a provider-specific package consistent with repository conventions, e.g. under:

`src/scrubbots_pixel_factory/semantic/providers/magnific/`

Exact filenames may follow existing style, but the responsibilities below must remain explicit.

### 1. Stable Magnific Provider Identity

Define versioned constants/contracts for at least:

- provider id: `MAGNIFIC`;
- provider adapter version;
- provider config version;
- Magnific job-spec schema/version;
- Magnific result-manifest schema/version;
- current execution surface identity, e.g. an explicit `images_generate` bridge version.

Do not make transient URLs, timestamps or creation IDs part of the SP01 request identity.

### 2. Truthful Magnific Capabilities

Declare only capabilities truthfully supported by the current authorized image-generation surface.

At minimum SP02 may support:

- text-to-image: true;
- generic image reference(s): true where execution bindings are supplied;
- style image: true where execution bindings are supplied.

Do **not** mark unsupported features true merely because they can be described in prose.

Unless implemented through an explicit, tested, separate authorized provider operation, keep false in SP02 for:

- negative prompt as a native provider field;
- transparent background as a native text-to-image field;
- init-image semantics distinct from a generic image reference;
- palette/color-reference semantics distinct from a generic image reference;
- inpaint;
- native view/direction controls;
- native isometric control;
- rotation variants;
- animation.

The bridge may deterministically render ordinary non-native art-direction hints such as `outline`, `shading`, `detail`, default view and target logical size into the textual prompt, but this must not be mislabeled as a native provider capability.

### 3. Canonical Magnific Job Spec

Define an immutable/versioned `MagnificJobSpec` (or equivalent) derived from:

- exact `SemanticGenerationRequest`;
- explicit Magnific execution bindings for any external images.

The canonical spec must include at least:

- schema/version;
- request digest;
- provider id/version/config;
- execution-surface version;
- explicit model slug;
- canonical rendered prompt;
- selected provider aspect ratio;
- candidate count;
- provider resolution/quality only if explicitly requested/supported;
- deterministic ordered reference entries;
- requested logical width/height retained separately from provider raster settings;
- explicit statement/field that provider seed forwarding is unsupported in this integration;
- request seed retained as ScrubBots provenance but not falsely represented as a Magnific generation seed.

Canonical serialization/digest must be deterministic.

### 4. Explicit Model Slug

Canonical Magnific jobs must require an explicit provider model slug.

Do not use a silently drifting `auto` model as reproducible canonical intent.

The bridge must not declare any model to be the final ScrubBots pixel-art default in SP02. SP04 will qualify models.

### 5. Deterministic Prompt Rendering

Create a project-owned deterministic prompt renderer.

It must preserve the owner's semantic description and encode only truthful art-direction intent, such as:

- pixel-art / sprite intent;
- requested target logical dimensions as design intent, not provider raster dimensions;
- LEVEL_ART vs ASSET_ART context;
- outline/shading/detail textual guidance where appropriate;
- default background/art-direction guidance where supported by the request and provider capability policy.

Do not silently discard material request intent. If a requested feature cannot be represented truthfully by the provider bridge, fail closed through capability validation rather than pretending it was honored.

Prompt rendering must be byte-deterministic for the same canonical request/bindings.

### 6. Aspect-Ratio Mapping

The provider surface accepts a bounded aspect-ratio vocabulary rather than exact logical dimensions.

Implement deterministic mapping from requested logical `width:height` to a supported provider aspect ratio.

Requirements:

- exact supported ratio wins when available;
- otherwise select the nearest supported ratio using a documented deterministic metric/tie-break;
- preserve the original requested logical width/height separately;
- never claim that the provider raster dimensions equal the logical ScrubBots dimensions;
- SP03 remains solely responsible for normalization.

### 7. Magnific Execution Bindings

Define an immutable/versioned execution-binding structure that maps content-identified SP01 input descriptors to owner-authorized Magnific creation identifiers.

At minimum:

- each binding identifies the exact request image by content SHA-256 and role;
- records the Magnific creation identifier;
- generic REFERENCE maps to the authorized surface's generic image-reference type;
- STYLE maps to its style-reference type;
- reject missing required bindings;
- reject extra ambiguous bindings;
- reject duplicate content/role bindings that cannot be resolved deterministically;
- reject role mismatch;
- execution identifiers may affect the **job-spec** identity but must not retroactively change SP01 request identity.

INIT/COLOR_REFERENCE must fail capability validation in SP02 unless the bridge implements and proves truthful distinct semantics for them.

### 8. Result / Import Manifest

Define an immutable/versioned `MagnificResultManifest` or equivalent for one provider attempt.

For success, record at least:

- request digest;
- job-spec digest;
- provider id/version/config;
- execution-surface version;
- requested model slug;
- actual/echoed model slug when available;
- Magnific creation identifier;
- status;
- returned raster width/height;
- raw image SHA-256;
- media type/format;
- provider metadata allowed as audit metadata;
- optional transient full-resolution/preview URL only as non-identity audit metadata.

For failure/unavailable/retry, record:

- exact request/job binding;
- typed status;
- explicit failure/retry reason;
- creation identifier if one exists;
- no fabricated image output.

Timestamps/URLs must not create canonical artifact identity.

### 9. Raw Result Import

Implement a pure/local importer taking:

- canonical semantic request;
- canonical Magnific job spec;
- result manifest;
- raw image bytes for success.

It must validate before producing `SemanticImageCandidate`:

- request digest matches;
- job-spec digest matches;
- provider identity/version/config matches;
- execution surface matches;
- requested model slug matches job/result contract;
- creation identifier is nonblank on success;
- raw bytes SHA-256 matches manifest;
- returned dimensions are valid;
- reference/style provenance remains the exact SP01 request provenance;
- candidate requested dimensions equal the semantic request's resolved dimensions.

Then construct a normal SP01 `SemanticImageCandidate` with exact provider/model/request provenance.

Do not normalize, resize, quantize or otherwise alter the raw image bytes in SP02.

### 10. Failure Import

Support a real typed non-success manifest/import path.

It must create a provenance-complete SP01 non-success candidate that can survive exact request/provider binding checks.

No missing model/reference provenance regression is allowed.

### 11. External-Orchestration Boundary

Do not add direct browser/network execution to the local Factory.

It is acceptable and preferred to expose pure methods such as:

- `prepare_job(request, bindings) -> MagnificJobSpec`
- `import_success(request, job, manifest, raw_bytes) -> SemanticImageCandidate`
- `import_failure(request, job, manifest) -> SemanticImageCandidate`

If a concrete `SemanticGeneratorProvider` subclass is added, its local `generate()` behavior must truthfully represent that actual execution is external/owner-authorized. Do not fake successful generation locally.

### 12. Smoke Fixture / Audit Handoff

Create a deterministic smoke-request fixture and generated canonical job-spec fixture under an appropriate `review/sp02/` or test-fixture path.

Use a low-cost single-candidate semantic test, preferably:

- output class: `ASSET_ART`;
- logical target: 16x16;
- subject: clearly recognizable small wizard or similarly simple character;
- explicit model slug selected only for **bridge smoke**, not product acceptance;
- count: 1;
- no references for the first smoke job.

Do not call Magnific from Codex. Independent ChatGPT audit will execute the published smoke job using the owner-authorized Magnific integration and record creation metadata separately.

## Tests

Add focused tests covering at minimum:

### Job identity

- same semantic request + same bindings => byte-identical job JSON/digest;
- material model slug change => different job digest;
- material reference creation binding change => different job digest;
- map/dict ordering does not change canonical digest where order is semantically irrelevant;
- transient timestamps/URLs are excluded from canonical identity.

### Capability honesty

- simple text-to-image request accepted;
- reference request accepted with valid binding;
- style request accepted with valid binding;
- native negative prompt request rejected if unsupported;
- no-background request rejected if unsupported as a native bridge capability;
- INIT request rejected unless truthful support is explicitly implemented/tested;
- COLOR_REFERENCE request rejected unless truthful support is explicitly implemented/tested;
- unsupported view/direction/isometric requests fail closed where SP01 capability rules require them.

### Aspect ratio

- exact square mapping;
- exact rectangular mapping where supported;
- nearest-ratio deterministic mapping;
- deterministic tie-break;
- logical dimensions remain unchanged in provenance.

### Bindings

- missing reference binding rejected;
- wrong role rejected;
- duplicate/ambiguous binding rejected;
- extra unexpected binding rejected;
- valid deterministic reference/style ordering.

### Result import

- valid success manifest + matching bytes imports successfully;
- raw hash mismatch rejected;
- request digest mismatch rejected;
- job digest mismatch rejected;
- provider/version/config mismatch rejected;
- model mismatch rejected;
- execution surface mismatch rejected;
- missing/blank creation id rejected;
- invalid returned dimensions rejected;
- transient URL change does not change canonical result identity where defined as audit metadata;
- imported candidate remains raw and cannot masquerade as M08 artwork.

### Failure path

- valid non-success manifest imports as a provenance-complete typed non-success candidate;
- explicit model and reference/style provenance are retained;
- no image bytes/hash/dimensions are fabricated for non-success.

### Regression

- all SP01 tests remain green;
- full existing suite remains green;
- no M00-M10 output changes.

## Documentation

Document clearly:

- Magnific execution is external/owner-authorized in SP02;
- Codex/local Factory does not scrape or drive the Magnific website;
- the current authorized image tool does not expose provider seed, exact logical raster size or a native negative-prompt field;
- ScrubBots seed remains request provenance but is not falsely claimed as a Magnific seed;
- provider raster size and logical target size are different concepts;
- SP03 owns normalization;
- model quality/default selection belongs to SP04;
- Magnific credits must remain bounded and auditable.

## Builder Log

Create BEFORE the first SP02 source/test/doc edit:

`.hiveai/codex-logs/PAG-SP02-C001_MAGNIFIC_JOB_SPEC_AND_RESULT_IMPORT_BRIDGE_CODEX_LOG.md`

Exact H1:

`# PAG-SP02-C001 — Magnific Job Spec & Result Import Bridge`

Role line:

`Document role: CODEX BUILDER LOG`

Record actual starting HEAD, origin/main, divergence and worktree state before edits.

The previous SP01 audits noted repeated builder-log ordering defects. **Do not repeat them.** Create the log before production/test edits.

## Verification

Run and record at minimum:

- focused SP02 tests;
- full SP01 semantic tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- standalone package import;
- module CLI help;
- installed CLI help where practical;
- forbidden network/browser/private-API scan;
- `git diff --check`;
- final scoped diff/status;
- final HEAD == origin/main and divergence `0 0`.

## Forbidden

- Do not call Magnific or consume credits from Codex.
- Do not add browser scraping/UI automation.
- Do not add undocumented Magnific HTTP/private endpoint calls.
- Do not store credentials/tokens.
- Do not install ComfyUI.
- Do not normalize/resize/quantize raw semantic images yet.
- Do not begin SP03/SP04.
- Do not select a permanent/default pixel-art model based only on one smoke test.
- Do not weaken SP01 provenance binding.
- Do not modify accepted MASK/RULES/WFC/HYBRID/AUTO algorithms.
- Do not modify the M10 rejected grids.
- Do not begin M11.
- Do not self-audit.

## Stop Condition

Commit and push the bounded SP02-C001 implementation to `main`, publish the completed matching builder log, fetch origin and verify exact HEAD equality/divergence `0 0`, then stop for independent ChatGPT strict audit and owner-authorized Magnific smoke execution.
