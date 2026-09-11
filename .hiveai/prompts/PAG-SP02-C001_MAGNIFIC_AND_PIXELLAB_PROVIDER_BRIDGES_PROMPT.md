# PAG-SP02-C001 — Magnific + PixelLab Provider Bridges & Result Ingestion
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authority

Read first:

1. root `TASKS.md`
2. `.hiveai/audits/PAG-SP01-C003_NON_SUCCESS_PROVENANCE_ECHO_AND_MISMATCH_TEST_SENSITIVITY_CLOSURE_STRICT_AUDIT.md`
3. `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`
4. `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
5. `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
6. `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`
7. `src/scrubbots_pixel_factory/semantic/`
8. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`

Official PixelLab implementation references to inspect before coding:

- `https://github.com/pixellab-code/pixellab-python`
- `pixellab/client.py`
- `pixellab/settings.py`
- `pixellab/generate_image_pixflux.py`
- `pixellab/generate_image_bitforge.py`
- `pixellab/types.py`

SP01 is `PASS / CLOSED`.

Owner decision for SP02: the Semantic Pixel Studio must support **both Magnific and PixelLab API** behind the same provider-neutral SP01 boundary.

Magnific remains an approved owner-authorized provider while credits are available. PixelLab is now also an approved direct API provider.

## Mission

Implement **SP02-C001 only**: two truthful provider bridges behind the accepted SP01 contracts:

1. **MAGNIFIC** — deterministic external-orchestration job-spec + result-import bridge.
2. **PIXELLAB** — official PixelLab Developer API / official Python SDK direct provider, with deterministic request mapping and exact result provenance.

Do not normalize/resize/quantize provider images yet. That is SP03.

Do not begin provider-quality qualification. That is SP04.

Do not select a permanent default provider/model in this cycle.

---

# A. Shared Provider Rules

## A1. Explicit provider selection

Provider selection must be explicit.

Accepted provider IDs for this cycle:

- `MAGNIFIC`
- `PIXELLAB`

Do not silently fall back from one provider to another if generation fails.

Do not silently choose a provider based on availability or cost.

The SP01 `UNSPECIFIED` neutral-provider value may remain for provider-neutral construction/tests, but a concrete SP02 generation job must resolve to one explicit provider before execution.

## A2. Preserve SP01 exact binding

Do not weaken any SP01-C003 provenance checks.

All success and non-success results remain exactly bound to:

- request digest;
- provider id/version/config;
- workflow version;
- explicit model/engine identity;
- seed provenance;
- requested dimensions;
- reference/style/init/color provenance.

## A3. Provider-specific code isolation

Create provider packages consistent with repository conventions, for example:

```text
semantic/providers/
  __init__.py
  registry.py
  magnific/
    ...
  pixellab/
    ...
```

Exact filenames may differ, but:

- Factory core must not import provider SDKs eagerly;
- importing `scrubbots_pixel_factory` must not trigger network access;
- existing M00-M10 generators remain unchanged;
- provider-specific network permission must not become a global network exemption.

## A4. Provider registry/factory

Add a small deterministic provider registry/factory capable of resolving explicit provider IDs without importing/executing unrelated providers.

At minimum prove:

- `MAGNIFIC` resolves to Magnific bridge metadata/factory;
- `PIXELLAB` resolves to PixelLab provider metadata/factory;
- unknown provider fails closed;
- registry iteration/order is deterministic where exposed;
- selecting Magnific does not import/call PixelLab network code;
- selecting PixelLab does not invoke Magnific orchestration.

---

# B. Magnific Bridge

Preserve the previously authorized architecture:

```text
SemanticGenerationRequest
        ↓
canonical Magnific job spec
        ↓
owner-authorized external Magnific execution
        ↓
Magnific result manifest + raw bytes
        ↓
local verified import
        ↓
SemanticImageCandidate
```

Codex/local Factory must NOT:

- scrape the Magnific website;
- drive Magnific browser UI;
- use undocumented/private Magnific endpoints;
- store Magnific credentials;
- spend Magnific credits during this implementation cycle.

## B1. Stable Magnific identity

Define versioned contracts for at least:

- provider id `MAGNIFIC`;
- adapter version;
- config version;
- job-spec schema/version;
- result-manifest schema/version;
- execution-surface identity/version.

## B2. Truthful Magnific capabilities

Current authorized Magnific image surface supports conceptually:

- text-to-image;
- generic image references where supplied as creation bindings;
- style reference where supplied as a style creation binding;
- model/mode slug;
- aspect ratio;
- count;
- supported resolution/quality options depending on model.

Do not claim current Magnific provider-native support for fields that are not actually surfaced, including provider seed or exact logical raster dimensions.

Non-native art-direction hints may be rendered deterministically into text, but they must not be mislabeled as native provider capabilities.

## B3. Canonical `MagnificJobSpec`

Include at least:

- schema/version;
- request digest;
- provider id/version/config;
- execution-surface version;
- explicit Magnific model slug;
- canonical rendered prompt;
- supported aspect ratio;
- candidate count;
- optional supported provider quality/resolution;
- ordered reference bindings;
- requested logical width/height kept separately;
- original ScrubBots seed retained only as provenance;
- explicit marker that provider seed forwarding is unsupported.

Do not use silently drifting provider `auto` as canonical model intent.

## B4. Magnific execution bindings

Bind SP01 content hashes/roles to owner-authorized Magnific creation identifiers.

Reject missing, extra, duplicate, ambiguous or role-mismatched bindings.

The SP01 request identity remains content-based. Magnific creation IDs may affect Magnific job identity but must not retroactively change SP01 request identity.

## B5. Magnific result/import manifest

Define a versioned manifest for success and failure.

Success must record at least:

- exact request digest;
- job digest;
- provider id/version/config;
- execution surface;
- requested model slug;
- actual model slug if available;
- Magnific creation identifier;
- returned dimensions;
- raw SHA-256;
- media type;
- status;
- non-identity audit metadata including transient URLs if desired.

Failure/unavailable/retry must retain exact request/job/model provenance without fabricating image data.

## B6. Magnific pure local import

Implement pure/local import methods that validate the manifest and raw bytes before constructing SP01 candidates.

No normalization in SP02.

---

# C. PixelLab Direct API Provider

PixelLab integration is different from Magnific: **direct official API access is explicitly authorized inside the PIXELLAB provider adapter**.

Use the official PixelLab Python SDK semantics as authority. Prefer the official `pixellab` package rather than copying/reimplementing its proprietary/service client behavior.

Official inspected SDK facts:

- package: `pixellab`;
- inspected version: `1.0.8`;
- default base URL: `https://api.pixellab.ai/v1`;
- secret env var: `PIXELLAB_SECRET`;
- optional env base URL: `PIXELLAB_BASE_URL`;
- `generate_image_pixflux` endpoint: `/generate-image-pixflux`;
- `generate_image_bitforge` endpoint: `/generate-image-bitforge`.

## C1. Optional dependency / lazy loading

Do not force PixelLab SDK/network availability on users of the historical procedural engine.

Preferred implementation:

- add the official `pixellab` package as an **optional provider dependency/extra**, version constrained to an audited compatible range beginning at `1.0.8`;
- lazy-import it only when the PixelLab provider is instantiated/executed;
- if the optional dependency is absent, return/raise the existing typed provider-unavailable contract without breaking package import or unrelated tests.

If repository packaging conventions make a different optional-provider mechanism cleaner, document the reason and preserve the same isolation guarantees.

Do not vendor/copy PixelLab SDK source into this repository.

## C2. Secret-safe runtime configuration

Define an immutable runtime configuration boundary for PixelLab.

Requirements:

- read secret from environment only, preferably the official `PIXELLAB_SECRET` convention;
- optional base URL may use official `PIXELLAB_BASE_URL` behavior;
- secret must be excluded from repr/logs/manifests/canonical JSON/digests;
- never commit `.env` secret files;
- never print the secret on HTTP/auth failure;
- tests must prove a sentinel secret does not appear in canonical artifacts, repr or expected error text.

## C3. Stable PixelLab identity

Define versioned constants/contracts for at least:

- provider id: `PIXELLAB`;
- adapter version;
- config version;
- job-spec schema/version;
- result-manifest schema/version;
- supported engine identity: at least `PIXFLUX`; optionally `BITFORGE` in the same cycle only if fully mapped/tested.

Provider engine/model selection must be explicit in canonical generation intent.

Recommended SP01 mapping:

- `provider_id = "PIXELLAB"`;
- `provider_model = "pixflux"` or `"bitforge"`;
- `provider_workflow_version` identifies the ScrubBots-to-PixelLab mapping version.

Do not hide engine selection in non-identity metadata.

## C4. Canonical `PixelLabJobSpec`

Define an immutable/versioned job spec derived from the exact `SemanticGenerationRequest`.

Include at least:

- schema/version;
- request digest;
- provider id/version/config;
- engine (`pixflux` or supported alternative);
- mapping/workflow version;
- exact requested image width/height;
- exact original ScrubBots seed;
- derived PixelLab integer seed actually sent;
- description;
- negative description when used;
- mapped native outline/shading/detail/view/direction/isometric values;
- no-background flag;
- coverage percentage;
- content-hash identities of init/style/color inputs;
- provider guidance values only when explicitly configured by the mapping contract;
- deterministic canonical JSON/digest.

Secret/token/base authorization header must never enter the job spec.

## C5. Deterministic seed mapping

SP01 seed accepts integer or string. PixelLab generation expects integer seed.

Implement one documented deterministic project-owned mapping:

- integer ScrubBots seed -> validated deterministic provider integer;
- string ScrubBots seed -> stable SHA-256/project-RNG-derived provider integer;
- identical SP01 request -> identical PixelLab integer seed;
- materially different seed -> different derived provider seed with overwhelming practical probability;
- record both original seed and derived provider seed in job/result provenance.

Use a conservative non-negative integer range compatible with the official SDK/API. Do not use Python `hash()`.

Do not claim that a cloud model can reproduce identical bytes forever across future server/model revisions merely because the seed is stable. Claim only deterministic request-to-provider-seed mapping plus recorded provider provenance.

## C6. Exact image-size mapping

Unlike Magnific, PixelLab's official generation API accepts exact `image_size`.

For PixelLab jobs:

- send exact resolved SP01 logical width/height as `image_size` for the smoke path;
- 16x16 ASSET_ART must remain 16x16 provider intent;
- LEVEL_ART 20-59 dimensions must remain exact provider intent;
- do not run SP03 resizing/quantization in SP02;
- still verify returned raster dimensions before constructing success.

The official SDK test corpus includes 16x16 generation input, so do not artificially impose Magnific-style large-raster assumptions on PixelLab.

## C7. PixelLab native control mapping

Use an explicit deterministic mapping table from SP01 control values to PixelLab's official literal vocabulary.

Official inspected vocabularies include:

- camera view: `side`, `low top-down`, `high top-down`;
- direction: `south`, `south-east`, `east`, `north-east`, `north`, `north-west`, `west`, `south-west`;
- outline: `single color black outline`, `single color outline`, `selective outline`, `lineless`;
- shading: flat/basic/medium/detailed/highly detailed shading;
- detail: low/medium/highly detailed.

Rules:

- `AUTO` may omit an optional native field where omission is truthful;
- values with an exact/explicitly documented semantic mapping may be sent natively;
- values without a truthful native mapping must fail closed or be clearly handled as text guidance under a documented fallback policy;
- never silently map an unsupported value and then call it native support;
- tests must cover every accepted mapping and every rejected mapping.

## C8. PixFlux capability mapping

Initial `PIXFLUX` support may truthfully expose, when implemented/tested:

- text-to-image;
- native negative prompt;
- transparent/no-background;
- exact image size;
- deterministic provider seed;
- outline;
- shading;
- detail;
- view/direction where the exact requested values are mappable;
- isometric;
- coverage percentage;
- init image;
- color image / forced palette.

PixFlux does **not** gain generic REFERENCE or STYLE semantics merely because the SP01 contract defines them.

Reject generic reference/style requests for PixFlux unless a truthful official mapping exists and is implemented/tested.

## C9. BitForge capability mapping

If BitForge is implemented in C001, it may additionally expose, when fully mapped/tested:

- style image and style strength;
- init image;
- color image;
- supported style/extra guidance controls;
- inpainting inputs only if an explicit SP01-compatible request surface exists and is in scope.

Do not add ad-hoc new SP01 request fields merely to expose every BitForge feature in this cycle.

It is acceptable for C001 to implement **PixFlux fully and BitForge job-mapping foundation only**, provided capability declarations are truthful and no unsupported feature is advertised.

## C10. PixelLab image execution bindings

SP01 image descriptors are content-identified and path-independent. The direct provider still needs local bytes/PIL images at execution time.

Define an execution-binding layer that resolves requested INIT/STYLE/COLOR_REFERENCE descriptors to immutable local bytes without making local paths part of canonical request identity.

At minimum:

- binding keys include role + content SHA-256;
- raw bytes are verified against the declared SHA-256 before API invocation;
- wrong role/hash rejected;
- missing required binding rejected;
- extra ambiguous binding rejected;
- local filesystem path, if used as a loading convenience, remains non-identity/audit-only;
- no secret is stored in bindings.

For PixFlux, INIT and COLOR_REFERENCE are candidates for direct official mapping.

For BitForge, STYLE may additionally map directly.

## C11. Direct PixelLab execution adapter

Implement a real direct adapter that can call the official SDK **when explicitly invoked and correctly configured**.

Requirements:

- no call occurs at import/construction time;
- no call occurs during ordinary unit/full regression tests;
- SDK client is injectable/mockable for tests;
- call `generate_image_pixflux` for PixFlux using only fields proven supported by the official SDK;
- if BitForge is enabled, call `generate_image_bitforge` accordingly;
- convert the returned official SDK image representation into immutable raw bytes in a deterministic lossless format boundary suitable for SHA-256 provenance;
- capture available provider `usage.usd` as audit/cost metadata, not as semantic image identity;
- authentication/validation/network failures become typed provider failure/unavailable behavior without secret leakage;
- never silently retry in an unbounded loop.

## C12. PixelLab result manifest

Define a versioned PixelLab result manifest before/alongside candidate construction.

Success must record at least:

- request digest;
- PixelLab job digest;
- provider id/version/config;
- engine/workflow identity;
- original ScrubBots seed;
- derived PixelLab integer seed;
- returned dimensions;
- raw image SHA-256;
- media type/format;
- status;
- available `usage.usd` as audit metadata;
- SDK/service metadata when available and non-secret.

Failure must preserve exact request/job/engine provenance without image bytes/hash/dimensions fabrication.

## C13. Single-candidate scope

The direct SP01 provider method currently returns one typed candidate.

For SP02-C001 direct PixelLab execution, support `desired_candidate_count == 1` first and fail closed for larger counts unless this cycle introduces a separately tested orchestration result abstraction without changing SP01 contracts.

Do not create an accidental hidden batch API. Multi-candidate production belongs to later batch work.

---

# D. Smoke Fixtures

Publish **two deterministic smoke job fixtures** without executing paid calls from Codex:

## D1. Magnific smoke fixture

- provider: MAGNIFIC;
- output: ASSET_ART;
- logical target: 16x16;
- subject: simple recognizable wizard;
- one explicit low-cost bridge model slug suitable for connectivity smoke only;
- count: 1;
- no references.

## D2. PixelLab smoke fixture

- provider: PIXELLAB;
- engine: PIXFLUX;
- output: ASSET_ART;
- exact image size: 16x16;
- subject: simple recognizable wizard;
- explicit fixed seed;
- no background if supported by the request mapping;
- simple supported outline/shading/detail values;
- count: 1;
- no image references.

The PixelLab fixture must serialize into a request that could be executed through the official API once `PIXELLAB_SECRET` is supplied locally.

Codex must not perform the live PixelLab call unless the owner explicitly authorizes credit/API usage for that exact run.

---

# E. Tests

Add focused tests covering at minimum all of the following.

## E1. Shared/registry

- explicit MAGNIFIC resolution;
- explicit PIXELLAB resolution;
- unknown provider rejected;
- no cross-provider fallback;
- package import performs no network activity;
- existing SP01 exact provenance tests remain green.

## E2. Magnific

Retain the previously required tests for:

- canonical job identity;
- explicit model slug;
- deterministic prompt rendering;
- aspect-ratio mapping;
- reference/style execution bindings;
- success/failure manifests;
- raw hash verification;
- exact import binding;
- no normalized/M08 masquerade;
- no provider seed claim.

## E3. PixelLab job identity

- identical request + execution bindings -> byte-identical PixelLab job spec/digest;
- description change changes digest;
- original seed change changes job digest and derived provider seed;
- width/height change changes digest;
- engine change changes digest;
- init/style/color content hash change changes digest where supported;
- dict/map ordering does not affect identity where semantically irrelevant;
- secret value cannot affect canonical identity;
- timestamps/network URLs/cost metadata are excluded from request/job identity.

## E4. PixelLab size/seed

- 16x16 ASSET_ART maps to exact `{width:16,height:16}` provider image size;
- representative 20x27 EASY LEVEL_ART maps to exact size;
- rectangular sizes preserved;
- string seed mapping deterministic;
- integer seed mapping deterministic;
- no Python `hash()` identity usage.

## E5. PixelLab native controls

Test every supported control mapping and fail-closed behavior for unsupported values.

At minimum include:

- negative description;
- no background;
- supported outline mapping;
- supported shading mapping;
- detail mapping;
- direction mapping;
- supported view mapping;
- isometric;
- coverage percentage.

## E6. PixelLab image bindings

- valid init binding accepted for PixFlux if implemented;
- valid color binding accepted if implemented;
- valid style binding accepted only for an engine that truthfully supports it;
- missing binding rejected;
- wrong role rejected;
- hash mismatch rejected before network call;
- generic REFERENCE rejected when engine has no truthful mapping;
- unsupported STYLE request rejected for PixFlux;
- extra ambiguous binding rejected.

## E7. PixelLab client execution

Using an injected fake/mock official client, prove:

- exact official method selected by engine;
- exact generated request kwargs match the job spec;
- no secret appears in kwargs beyond SDK client construction boundary;
- returned image becomes immutable raw bytes + SHA-256;
- returned dimensions verified;
- usage USD captured as non-identity audit metadata;
- auth/validation/network-like exceptions map to typed provider failure/unavailable semantics;
- no automatic unbounded retry;
- candidate passes SP01 `generate_checked()` when all provenance is valid.

## E8. Secret safety

Use a sentinel such as `PIXELLAB_SECRET_DO_NOT_LEAK_123` and prove it is absent from:

- canonical job JSON;
- manifest JSON;
- candidate canonical data;
- repr of public config/job/result objects;
- expected exception messages;
- committed smoke fixtures.

## E9. Regression

- focused SP02 tests;
- full SP01 tests;
- full `python -m pytest -q`;
- compileall;
- package import;
- CLI help;
- `git diff --check`;
- no change to accepted MASK/RULES/WFC/HYBRID/AUTO behavior.

---

# F. Network / Security Policy

This cycle deliberately introduces one narrow direct-network exception for the semantic layer:

**Only the explicit PIXELLAB provider execution operation may call the official PixelLab API.**

Do not globally disable or weaken the historical offline guard.

Tests must prove:

- historical procedural generation remains offline;
- package import is offline;
- job preparation is offline;
- Magnific bridge is offline/local and external-execution only;
- PixelLab job preparation is offline;
- only explicit PixelLab execution can reach network;
- tests mock/inject the client and do not consume API credits.

No browser automation or scraping for PixelLab is allowed. Use only the official SDK/API contract.

No undocumented/private PixelLab endpoint is allowed.

---

# G. Documentation

Document clearly:

- why Magnific and PixelLab are both supported;
- Magnific external-execution vs PixelLab direct-API difference;
- PixelLab exact-size + seed advantage for small pixel art;
- provider selection is explicit and not automatic;
- PixelLab credentials are env-only and secret-safe;
- PixelLab provider outputs are still raw semantic candidates until SP03;
- provider/model/workflow quality is not accepted until SP04;
- costs/credits belong to auditable provider attempt metadata;
- no permanent provider default is selected in SP02.

---

# Builder Log

Create BEFORE the first SP02 source/test/doc edit:

`.hiveai/codex-logs/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_CODEX_LOG.md`

Exact H1:

`# PAG-SP02-C001 — Magnific + PixelLab Provider Bridges & Result Ingestion`

Role line:

`Document role: CODEX BUILDER LOG`

Record actual starting HEAD, `origin/main`, divergence and worktree state before edits.

The previous SP01 cycles had builder-log ordering defects. **Do not repeat them.**

---

# Verification

Run and record at minimum:

- focused SP02 multi-provider tests;
- full SP01 semantic tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- standalone package import;
- module CLI help;
- installed CLI help where practical;
- secret-leak scan;
- forbidden browser/private-endpoint scan;
- network-boundary tests;
- `git diff --check`;
- final scoped diff/status;
- final `HEAD == origin/main` and divergence `0 0`.

---

# Forbidden

- Do not call Magnific or consume Magnific credits from Codex.
- Do not call PixelLab or consume PixelLab API credits from Codex unless the owner explicitly authorizes that exact live run.
- Do not store any provider secret/token.
- Do not scrape/drive Magnific or PixelLab websites.
- Do not use undocumented/private provider endpoints.
- Do not silently auto-switch providers.
- Do not globally remove historical offline/network safeguards.
- Do not normalize/resize/quantize semantic raw images yet.
- Do not begin SP03/SP04.
- Do not select a permanent/default provider/model based on connectivity tests.
- Do not weaken SP01 provenance binding.
- Do not modify accepted MASK/RULES/WFC/HYBRID/AUTO algorithms.
- Do not modify M10 rejected grids.
- Do not begin M11.
- Do not self-audit.

# Stop Condition

Commit and push the bounded SP02-C001 implementation to `main`, publish the completed matching builder log, fetch origin and verify exact HEAD equality/divergence `0 0`, then stop for independent ChatGPT strict audit.

Live provider smoke execution is an audit/owner-authorized follow-up, not a Codex implementation prerequisite.
