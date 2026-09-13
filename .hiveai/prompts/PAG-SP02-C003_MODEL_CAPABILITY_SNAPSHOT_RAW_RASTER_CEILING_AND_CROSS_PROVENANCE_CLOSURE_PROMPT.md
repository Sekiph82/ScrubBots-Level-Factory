# PAG-SP02-C003 — Model Capability Snapshot, Raw Raster Ceiling & Cross-Provenance Closure
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before coding:

1. root `TASKS.md` — ONLY current project-status tracker;
2. `.hiveai/audits/PAG-SP02-C002_PROVIDER_CONTRACT_FIDELITY_RESULT_IDENTITY_AND_SMOKE_READINESS_REMEDIATION_STRICT_AUDIT.md`;
3. `.hiveai/prompts/PAG-SP02-C002_PROVIDER_CONTRACT_FIDELITY_RESULT_IDENTITY_AND_SMOKE_READINESS_REMEDIATION_PROMPT.md`;
4. `.hiveai/audits/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_STRICT_AUDIT.md`;
5. `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`;
6. `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`;
7. `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`;
8. accepted SP01 semantic contracts/provider boundary;
9. current Magnific provider bridge/tests/fixtures;
10. current PixelLab provider bridge/tests/fixtures;
11. official public PixelLab SDK references already authorized;
12. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do not use local/untracked legacy `.hiveai` tracker/control-plane files as status authority.

## Mission

Implement **SP02-C003 only** and close exactly:

- `F-PAG-SP02-C002-001` — raw candidate returned-raster ceiling;
- `F-PAG-SP02-C002-002` — inaccurate/fail-open Magnific model capability snapshots;
- `F-PAG-SP02-C002-003` — failure diagnostic text contaminating provider-result identity;
- `F-PAG-SP02-C002-004` — incomplete cross-object provenance binding;
- `F-PAG-SP02-C002-005` — failure actual-model semantics, if the schema is touched.

Preserve all C002 fixes that passed audit.

Do **not** begin SP03 normalization or SP04 qualification.

Do **not** perform live Magnific or PixelLab generation.

Do **not** spend credits.

Do **not** edit root `TASKS.md`.

---

# 1. Separate logical/requested bounds from raw returned-raster bounds

C002 made Magnific manifests accept provider rasters up to 8192, but `SemanticImageCandidate.__post_init__()` still applies the historical 1024 limit to `returned_width` / `returned_height`.

This must be closed without loosening ScrubBots logical board/asset request rules.

Required behavior:

- keep `SemanticGenerationRequest` requested dimension limits unchanged unless an existing accepted contract explicitly says otherwise;
- keep LEVEL_ART difficulty dimensions unchanged;
- keep ASSET_ART request validation unchanged;
- change only the raw semantic candidate's **returned provider raster** validation so valid external provider rasters above 1024 can be represented;
- use one explicit/versioned/documented upper bound, recommended `8192`, consistent with SP02 Magnific result-manifest validation and current provider tool surface;
- do not resize/crop/pad/downsample in SP02;
- requested dimensions and returned dimensions remain separately represented;
- raw provider bytes/hash remain exact;
- `as_m08_artwork()` must still raise `SemanticNormalizationRequiredError` before SP03.

Do not accidentally raise image-input descriptor or logical board limits merely because provider output can be larger.

Required tests:

- 16x16 request + 2048x2048 Magnific raw result -> valid raw candidate;
- 16x16 request + 4096x4096 Magnific raw result -> valid raw candidate;
- returned dimension above the new explicit raw bound -> fail closed;
- requested/logical dimension contracts remain unchanged;
- >1024 raw candidate still cannot masquerade as M08 artwork.

---

# 2. Replace permissive Magnific metadata with one truthful versioned model-capability snapshot

The current bridge uses a global 12-ratio tuple for every model and lets unknown models inherit that global tuple. This is forbidden.

Create one small immutable/versioned project-owned capability snapshot abstraction, e.g. `MagnificModelCapabilitySnapshot` or equivalent.

Each pinned model entry must explicitly carry only the capability data needed by SP02, at minimum:

- exact model slug;
- supported aspect ratios;
- supported SP01 reference roles (`REFERENCE` / `STYLE`) that can truthfully map to the authorized Magnific generation surface;
- supported explicit `resolution` values, if the connected model exposes them;
- supported explicit `quality` values, if the connected model exposes them;
- snapshot/version identifier used in job identity;
- optional documentation-only observation date outside mutable runtime identity.

Do not query the live catalog at ordinary job runtime.

## 2.1 Read-only catalog inspection at implementation start

Codex may inspect the current read-only Magnific model catalog available to the project if accessible in its environment. If it is not accessible, use the auditor-recorded observations below as the minimum pinned authority for C003 and do not invent unsupported fields.

Auditor-observed current catalog facts:

### `recraft-v4-1`

- aspect ratios:
  - `1:1`
  - `2:1`
  - `1:2`
  - `3:2`
  - `2:3`
  - `4:3`
  - `3:4`
  - `5:4`
  - `4:5`
  - `16:9`
  - `9:16`
- `21:9` is **not** listed;
- reference support is present;
- listed reference type: `style` only;
- no explicit resolution/quality enum was present in the auditor's returned catalog entry.

### `seedream-5-pro`

- aspect ratios:
  - `1:1`
  - `4:3`
  - `3:4`
  - `16:9`
  - `9:16`
  - `3:2`
  - `2:3`
  - `21:9`
- resolutions: `1.5k`, `2k`;
- reference types: `style`, `character`, `product`, `image`.

Under the current SP01 request surface:

- SP01 `STYLE` may map only to provider `style`;
- SP01 generic `REFERENCE` may map to provider `image` only when that model exposes generic image reference semantics;
- do not silently reinterpret generic `REFERENCE` as `character` or `product`.

### `imagen-nano-banana-2-lite`

Auditor-observed aspect ratios:

- `1:1`
- `2:3`
- `3:2`
- `4:3`
- `3:4`
- `5:4`
- `4:5`
- `16:9`
- `9:16`
- `21:9`

Reference types include `style`, `character`, `product`, `image`.

No need to pin every Magnific model. It is preferable to pin a small set intended for upcoming smoke/SP04 than to invent a broad catalog mirror.

## 2.2 Unknown model must fail closed

An explicit model slug absent from the pinned snapshot must raise/fail before a canonical executable Magnific job is produced.

Remove behavior equivalent to:

`MODEL_CAPABILITIES.get(model, GLOBAL_PERMISSIVE_DEFAULT)`.

There must be no permissive unknown-model fallback.

## 2.3 Model-specific aspect mapping

Aspect mapping must use only the selected model snapshot.

- exact supported ratio wins;
- otherwise deterministic nearest supported ratio;
- deterministic tie-break;
- logical dimensions remain separate;
- selected snapshot/version and supported-ratio set are included in job identity;
- changing snapshot version or mapped ratio changes job digest.

## 2.4 Model-specific reference role validation

`MagnificProvider.capabilities` may remain a provider-level union if required by SP01, but `validate_request()` / `prepare_job()` must narrow truthfully using the explicit request model snapshot.

Examples:

- `recraft-v4-1` + STYLE -> allowed when binding is exact;
- `recraft-v4-1` + generic REFERENCE -> reject before job execution;
- `seedream-5-pro` + generic REFERENCE -> allowed only as provider `image` reference;
- unsupported role -> fail closed.

Job reference bindings must remain ordered and exact by role + content hash + owner-authorized creation identifier.

## 2.5 Model-specific resolution / quality

If `MagnificJobSpec.from_request(... resolution=..., quality=...)` remains exposed:

- explicit values must be checked against the selected pinned model snapshot;
- if the model exposes no explicit value for that field, non-None input must fail closed rather than accept an arbitrary string;
- do not treat omitted provider defaults as a canonical explicit value unless versioned policy says so.

If a field is not needed for SP02, it is acceptable to disable explicit override support rather than maintain a false capability.

---

# 3. Correct the committed Magnific smoke fixture snapshot

The smoke model remains `recraft-v4-1` unless the current read-only catalog proves it unavailable.

The fixture must contain the exact pinned capability snapshot relevant to its job identity.

At minimum:

- model slug `recraft-v4-1`;
- 16x16 logical ASSET_ART wizard target;
- count 1;
- mapped aspect `1:1`;
- exact current pinned `recraft-v4-1` aspect-ratio set, without `21:9`;
- no generic REFERENCE capability claimed;
- no invented explicit resolution/quality;
- no mutable timestamp in job identity.

Do not execute the fixture in C003.

---

# 4. Remove failure diagnostic prose from deterministic provider-result identity

Both provider result manifests currently include `failure_reason` in `identity_dict()`.

For C003:

- keep `status` in deterministic identity;
- keep exact request/job/provider/model/engine/workflow/seed/raw-hash/dimensions fields where applicable;
- remove free-text `failure_reason` from deterministic identity/digest;
- preserve `failure_reason` in full/canonical/audit serialization;
- preserve `audit_metadata` and PixelLab `usage_usd` in full serialization only;
- do not erase useful diagnostic text.

This applies to:

- `MagnificResultManifest`;
- `PixelLabResultManifest`.

Do **not** reopen `SemanticImageCandidate` identity semantics in C003 unless strictly necessary for a compile/test invariant. The required closure is the provider result-manifest identity introduced by SP02.

Required tests for both providers:

- same failed request/job/status with failure reason A vs B -> same manifest digest;
- FAILURE vs UNAVAILABLE or another materially different status -> different digest if the manifest type permits that status;
- different job/model/engine/request binding -> different digest;
- success raw hash/dimensions changes -> different digest.

---

# 5. Close Magnific request <-> job <-> manifest cross-binding

Current import checks manifest/request and manifest/job independently but does not prove the job itself belongs to the supplied request.

Add one explicit fail-closed request-job binding check before result import.

At minimum prove all of the following:

- `job.request_digest == request.digest()`;
- `job.provider_id == MAGNIFIC`;
- job provider version/config match adapter/request;
- job model equals request explicit model;
- job logical width/height equal request resolved dimensions;
- job original seed equals request seed;
- job reference/style binding identities correspond exactly to request descriptors + supplied owner execution bindings;
- manifest request digest equals request digest;
- manifest job digest equals the exact checked job digest;
- success actual model equals requested/job model;
- failure actual model semantics follow section 7 below.

A coordinated mismatch must fail even when each object is individually well-formed.

Required tests:

- request A + job B + manually coordinated manifest -> reject;
- same model but different description/seed/dimensions -> reject;
- exact request/job/manifest -> accept.

---

# 6. Close PixelLab request <-> job <-> candidate <-> manifest cross-binding

`PixelLabResultManifest.from_candidate()` / `PixelLabProvider.manifest_for()` must not emit a provenance manifest for a candidate that does not belong to the supplied request/job.

Implement one checked construction path.

At minimum validate before manifest creation:

- request digest;
- provider id/version/config;
- workflow version;
- explicit engine/model;
- original seed / derived provider seed through job;
- requested dimensions;
- reference/style/init/color descriptors;
- candidate success raw hash/returned dimensions when success;
- candidate status consistency when non-success;
- job digest belongs to exact request.

Do not trust caller pairing merely because both objects are individually typed.

Required tests:

- candidate from request A + request/job B -> reject;
- candidate with wrong provider/version/workflow/model -> reject;
- candidate with wrong input descriptor provenance -> reject;
- exact checked candidate/request/job -> manifest succeeds;
- no secret appears in errors or manifest.

---

# 7. Make Magnific failure actual-model semantics truthful

If the result schema is modified in C003:

- `model_slug` remains the requested/job model and is mandatory provenance;
- `actual_model_slug` should be optional for non-success when the provider never reported an executed model;
- success requires an actual model equal to the requested/job model for this cycle;
- if a failure result explicitly reports an actual model, it must match the requested/job model or fail closed;
- do not fabricate `actual_model_slug` merely because a requested model exists.

Do not lose requested model provenance.

---

# 8. Preserve all accepted C002 closures

Do not regress:

- explicit provider selection;
- no silent provider/model fallback;
- Magnific external orchestration only;
- PixelLab official SDK direct provider boundary;
- optional/lazy PixelLab package import;
- PixelLab secret exclusion;
- exact PixelLab requested image size;
- deterministic PixelLab provider seed mapping;
- PixelLab native control mapping;
- PixFlux generic REFERENCE/STYLE restrictions;
- BitForge 0..1 -> 0..100 style-strength mapping;
- success audit/cost metadata exclusion from digest;
- Magnific raw-vs-logical dimension separation;
- Magnific requested/actual success model binding;
- SP03 normalization gate;
- M00-M10 algorithms;
- rejected M10 visual evidence.

---

# 9. Required focused test matrix

At minimum add/adjust tests proving:

## Raw raster boundary

1. 16x16 logical -> 2048x2048 Magnific raw candidate accepted;
2. 16x16 logical -> 4096x4096 Magnific raw candidate accepted;
3. raw returned dimension above explicit max rejected;
4. requested logical limits unchanged;
5. no raw candidate can export as M08 artwork before SP03.

## Magnific model capability snapshot

6. `recraft-v4-1` snapshot exactly excludes `21:9`;
7. `recraft-v4-1` STYLE allowed;
8. `recraft-v4-1` generic REFERENCE rejected;
9. `seedream-5-pro` exact 8-ratio snapshot;
10. `seedream-5-pro` generic REFERENCE allowed as generic provider image reference;
11. explicit unsupported ratio is never emitted;
12. unknown/unpinned model rejected;
13. explicit unsupported resolution/quality rejected;
14. fixture equals canonical job output with the exact pinned snapshot.

## Result identity

15. Magnific failure reason A/B -> same digest;
16. PixelLab failure reason A/B -> same digest;
17. material status/job/model/engine/raw-hash/dimension differences -> different digest.

## Cross-provenance

18. Magnific request A + job B coordinated manifest -> reject;
19. exact Magnific request/job/manifest -> accept;
20. PixelLab candidate A + request/job B -> reject;
21. wrong PixelLab provider/workflow/model/input provenance -> reject;
22. exact PixelLab candidate/request/job -> manifest succeeds.

## Failure semantics

23. Magnific failure with no observed actual model is valid/truthful;
24. reported drifted actual model fails closed.

Retain all existing SP01 and SP02 tests.

---

# 10. Builder log

Create BEFORE any C003 source/test/doc edit:

`.hiveai/codex-logs/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_CODEX_LOG.md`

Exact H1:

`# PAG-SP02-C003 — Model Capability Snapshot, Raw Raster Ceiling & Cross-Provenance Closure`

Role line:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- repository and branch;
- starting local HEAD;
- fetched `origin/main`;
- starting divergence `0 0`;
- preserved user-owned dirt;
- authority files read from GitHub;
- read-only provider capability evidence used to pin snapshots;
- exact files changed;
- every focused test failure and correction;
- focused SP02 suite;
- full SP01 suite;
- full repository suite;
- compileall;
- standalone imports;
- CLI help;
- network/private-endpoint scan;
- secret scan;
- `git diff --check`;
- final scoped status;
- commit/push;
- final fetch and `HEAD == origin/main`, divergence `0 0`;
- explicit statement that no provider credit/live call occurred.

---

# 11. Verification

Run and record at minimum:

- focused SP02 C003 tests;
- all SP02 provider tests;
- full SP01 semantic tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- standalone import of package + provider modules;
- module CLI help;
- installed CLI help where practical;
- source scan proving historical procedural paths still have no provider network dependency;
- scan for browser/private Magnific automation;
- secret/credential scan;
- `git diff --check`;
- final scoped diff/status.

Do not rely only on test pass counts. The builder log must state what each new sensitivity test proves.

---

# 12. Forbidden

- Do not edit root `TASKS.md`.
- Do not self-audit or mark SP02 PASS/CLOSED.
- Do not begin SP03.
- Do not begin SP04.
- Do not reopen M11.
- Do not spend Magnific credits.
- Do not call live PixelLab API.
- Do not store PixelLab credentials.
- Do not scrape or drive Magnific browser UI.
- Do not use undocumented/private provider endpoints.
- Do not make normal job preparation depend on a mutable live model catalog.
- Do not create a permissive unknown-model fallback.
- Do not loosen logical LevelData dimensions/palette contracts.
- Do not normalize provider images in SP02.
- Do not change M00-M10 accepted algorithms.
- Do not change the M10 rejected visual evidence.

## Stop condition

Commit and push the bounded SP02-C003 remediation to `main`, publish the completed matching builder log, fetch origin and verify exact local `HEAD == origin/main` with divergence `0 0`, then stop for independent ChatGPT strict audit.

No live provider smoke is authorized by this builder prompt.
