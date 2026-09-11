# PAG-SP02-C001 — Magnific + PixelLab Provider Bridges & Result Ingestion
Document role: CHATGPT STRICT AUDIT

## 1. VERDICT

**FAIL**

The implementation establishes a useful provider registry, lazy PixelLab dependency boundary, secret-safe runtime configuration, explicit PIXFLUX/BITFORGE selection, deterministic PixelLab seed mapping, reference-byte hash verification, and an offline Magnific job/import skeleton. The builder reports 11 focused SP02 tests, 48 combined SP01+SP02 tests, and 429 full-suite tests passing.

However, SP02 cannot be accepted because several production-facing provider contracts contradict the authoritative prompt/provider surfaces. In particular, the Magnific bridge cannot faithfully ingest a normal provider raster that differs from the requested logical ScrubBots dimensions, produces unsupported arbitrary aspect-ratio strings for many legal rectangular requests, and advertises non-native controls as native capabilities. Cross-provider result identity also incorrectly includes audit/cost metadata. Magnific model binding is not exact, and the BitForge style path advertises style support while silently omitting the request's style strength.

No paid/live provider smoke was executed during this audit because the pre-smoke bridge contract is not yet valid. Spending owner credits against a knowingly invalid ingestion path would not produce useful acceptance evidence.

Severity summary:

- BLOCKER: 0
- MAJOR: 5
- MINOR: 2
- NOTE: 2

## 2. CONTRACT RECOVERY

Audited against:

- root `TASKS.md` current SP02 state;
- `.hiveai/prompts/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_PROMPT.md`;
- `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`;
- `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`;
- closing SP01-C003 strict audit;
- official `pixellab-code/pixellab-python` public SDK contracts, including `client.py`, `generate_image_pixflux.py`, `generate_image_bitforge.py`, `types.py`, and `models/base64_image.py`;
- current owner-authorized Magnific image model catalog and image-generation surface, read-only.

Recovered critical contract points:

1. Provider selection must be explicit; no silent fallback.
2. Magnific is external orchestration and does not expose exact logical raster dimensions or provider seed forwarding.
3. Magnific's generated raster must remain raw provider output until SP03 normalization.
4. Magnific aspect ratio must be one supported by the selected execution surface/model, with deterministic mapping from arbitrary logical rectangles.
5. Magnific non-native prompt hints must not be declared as native provider capabilities.
6. PixelLab PixFlux supports exact `image_size`, negative description, seed, outline/shading/detail, view/direction, isometric, no-background, coverage, init image, and forced color image.
7. PixelLab BitForge additionally exposes style image and `style_strength`.
8. Usage/cost/transient audit data are non-identity metadata.
9. Provider/model/job/result provenance must remain exact and fail closed.
10. SP03 owns normalization; SP02 must not pretend a large provider raster is already a logical grid.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder start HEAD: `a29cd55d0e016140b8e2e640b01e81f10d039f06`.

Implementation commit: `9e6945c4e53b19851731853ff221da7552f1e06d`.

Builder-log terminal commit on `main`: `40f18f8d03ad60d882e5ece87b31722dcd4f7cfd`.

Compare `a29cd55..40f18f8` is ahead by 2 commits and contains only the SP02 log, optional PixelLab dependency, semantic provider modules, fixtures, and focused tests. Accepted M00-M10 generator algorithms were not modified.

Scope is structurally appropriate.

## 4. ACCEPTANCE CRITERIA MATRIX

| Area | Result | Audit assessment |
|---|---|---|
| Explicit provider registry | PASS | `MAGNIFIC`, `PIXELLAB`, deterministic registry, unknown provider fail-closed |
| Lazy provider isolation | PASS | Optional PixelLab SDK is lazy; Magnific has no network client |
| Secret-safe PixelLab config | PASS | Secret excluded from repr/canonical job identity in inspected path |
| PixelLab exact size | PASS | Job sends exact requested dimensions and direct execution checks return dimensions |
| PixelLab deterministic provider seed | PASS | SHA-256/project-owned stable non-negative integer derivation |
| PixelLab control mapping | PARTIAL | Core PixFlux mapping exists; unsupported controls fail closed |
| PixelLab BitForge style support | FAIL | Style image advertised, but `style_strength` is not represented/sent |
| Magnific job determinism | PARTIAL | Canonical job exists, but aspect-ratio output may be unexecutable |
| Magnific truthful capabilities | FAIL | Native capability flags overclaim prompt-only hints |
| Magnific raw result import | FAIL | Import incorrectly requires provider raster == logical target dimensions |
| Provider model exact binding | FAIL | Magnific job model can diverge from request model; actual model drift can be accepted |
| Audit/cost non-identity | FAIL | Result canonical identity includes audit metadata and PixelLab usage/cost |
| No normalization in SP02 | PASS/PARTIAL | No image-grid normalization, but Magnific import incorrectly enforces normalized-size equality |
| No paid calls in builder | PASS | Builder reports none; code/test evidence consistent |
| Live smoke readiness | FAIL | Magnific smoke fixture uses a currently unresolved model slug and import contract rejects normal larger rasters |
| Full regression | BUILDER PASS / AUDITOR UNVERIFIED | Builder: 429 passed; independent clean checkout blocked by audit-container DNS |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder claims about provider isolation, optional dependency, deterministic registry, exact PixelLab image size, secret exclusion, hash-checked PixelLab bindings, and absence of live credit spend are supported by repository inspection.

The claim that the Magnific bridge has valid raw-result ingestion is not supported. `MagnificResultManifest.import_result()` rejects a success unless returned provider dimensions exactly equal the semantic request's logical dimensions. That contradicts the same bridge's own metadata (`exact_logical_dimensions: False`) and the governing architecture that defers resizing/normalization to SP03.

The claim that committed provider smoke fixtures are executable canonical examples is also not currently true for Magnific. The committed fixture uses `model_slug: "magnific-sd3"`; a read-only query against the current connected Magnific image-model catalog returned no such model. Current catalog-valid slugs include examples such as `recraft-v4-1`.

## 6. FILE / SYMBOL EVIDENCE

Primary audited implementation:

- `src/scrubbots_pixel_factory/semantic/providers/registry.py`
- `src/scrubbots_pixel_factory/semantic/providers/magnific/bridge.py`
- `src/scrubbots_pixel_factory/semantic/providers/pixellab/bridge.py`
- `tests/unit/test_sp02_provider_bridges.py`
- `tests/fixtures/sp02/magnific_smoke_job.json`
- `tests/fixtures/sp02/pixellab_pixflux_job.json`
- `pyproject.toml`

Official PixelLab reference evidence:

- `generate_image_pixflux.py` exposes exact `image_size`, native `negative_description`, native outline/shading/detail/view/direction/isometric/no-background/coverage, init image, color image, and integer seed.
- `generate_image_bitforge.py` additionally exposes `style_image` and `style_strength`.
- `Base64Image` exposes the provider image as base64 plus a PIL decoder.

## 7. FOCUSED TEST EVIDENCE

Builder reported:

- initial SP02 focused run: 9 passed / 1 failed;
- after correction: 11 passed;
- SP01 + SP02: 48 passed;
- full suite: 429 passed.

The focused suite has useful tests for registry selection, deterministic job identity, reference/hash binding, secret exclusion, injected PixelLab client execution, exact 16x16 return dimensions, typed unavailability, and engine separation.

Coverage gaps materially explain the escaped defects:

- only square Magnific aspect ratio is tested;
- Magnific success test uses artificial 16x16 provider bytes, so it does not exercise the explicit large-raster/SP03 boundary;
- no test asserts that Magnific native capability flags remain false for prompt-only hints;
- no result-identity test changes transient audit metadata/usage and proves digest stability;
- no test builds a Magnific job with a model override different from `request.provider_model`;
- BitForge test checks that STYLE is selectable but never asserts the native `style_strength` argument sent to the SDK.

## 8. REGRESSION EVIDENCE

Builder reports 429 repository tests passing, compileall passing, CLI help passing, and `git diff --check` passing.

No GitHub Actions/status checks exist on terminal HEAD.

Independent auditor clean-clone replay was attempted but the audit container could not resolve `github.com`; therefore runtime regression is marked UNVERIFIED, not failed.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive:

- no Magnific browser scraping/private endpoint code found;
- PixelLab network capability is isolated behind the explicit provider adapter;
- PixelLab SDK dependency is optional;
- secrets are runtime-only and excluded from job identity/repr in inspected implementation;
- no provider call occurs at ordinary import;
- builder did not spend credits.

Residual security severity: none identified in this cycle.

## 10. ARCHITECTURE CONSISTENCY

Provider-neutral SP01 architecture is preserved.

The major inconsistency is at the Magnific raw-to-SP03 boundary. The architecture says:

`logical target -> Magnific raw provider raster -> SP03 normalization`

but current import implements:

`logical target -> require Magnific raster already equals logical target -> candidate`.

That collapses the SP03 boundary and makes the external Magnific provider unusable for the exact scenario it was introduced to support.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Root `TASKS.md` remained untouched by Codex, which is correct for builder ownership.

Builder log accurately records test chronology and the pre-existing dirty worktree.

MINOR governance issue: the log says `.hiveai/RULES.md`, `.hiveai/PROJECT.json`, `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, and `.hiveai/CYCLE_INDEX.md` were read as current repository authority. Under the migrated H!veAI rules, root `TASKS.md` is the only current project-status tracker and those hidden/legacy control-plane artifacts must not be treated as current authority. No scoped implementation damage was observed from this, but future cycles must ignore them as status authority.

## 12. FINAL REPOSITORY STATE

GitHub `main` terminal inspected HEAD: `40f18f8d03ad60d882e5ece87b31722dcd4f7cfd`.

Commit status checks: none.

Workflow runs associated with terminal commit: none.

The SP02 implementation is present and isolated but not technically acceptable for provider smoke/normalization handoff.

## 13. OPEN CROSS-MILESTONE FINDINGS

- SP03 remains blocked.
- SP04 provider/model qualification remains blocked.
- M11 remains blocked pending later semantic visual acceptance.
- M10 rejected 100-pack remains negative regression evidence.

## 14. DEFECTS BY SEVERITY

### MAJOR — F-PAG-SP02-C001-001 — Magnific provider-raster/logical-dimension boundary is inverted

`MagnificResultManifest.import_result()` requires `returned_width/height == request.resolved_dimensions()` for success.

This is incompatible with the owner-approved Magnific architecture, where the provider may return a much larger raster and SP03 performs deterministic logical normalization. The candidate type already supports separate requested vs returned dimensions, so the equality requirement is neither necessary nor correct.

Required closure: accept valid provider raster dimensions independently from requested logical dimensions, preserve both sets of dimensions, validate positive/sane returned dimensions, and leave all resize/quantization to SP03.

### MAJOR — F-PAG-SP02-C001-002 — Magnific job surface is not executable for general legal rectangles and overclaims native capabilities

`_aspect_ratio(width,height)` emits an arbitrary reduced ratio such as `20:21`, while the authorized Magnific image surface accepts a finite ratio vocabulary and models may support subsets of it. Only `1:1` is tested.

Additionally, `MagnificProvider.capabilities` marks `negative_prompt`, `transparent_background`, `view_direction_controls`, and `isometric` true even though this integration only renders such intent into prompt text. The prompt explicitly forbids presenting prompt guidance as native provider capability.

Required closure: deterministic nearest-supported aspect-ratio mapping with documented tie-break and model/surface-compatible vocabulary; native capability flags must be truthful. If prompt-only hints are permitted, represent them as bridge/prompt metadata rather than native SP01 capability truth.

### MAJOR — F-PAG-SP02-C001-003 — Result identity includes non-identity audit/cost data

`MagnificResultManifest.canonical_dict()` includes `audit_metadata`, and its `digest()` hashes that canonical dictionary. PixelLab result serialization likewise includes `usage_usd` and `audit_metadata` in its canonical result representation/digest path.

The provider authority and C001 prompt explicitly classify transient URLs/timestamps and usage/cost as audit metadata, not semantic/result identity. Two byte-identical provider results can therefore receive different canonical identities solely because a URL, timestamp, or charge differs.

Required closure: split deterministic result identity from audit serialization. Result digest must exclude audit metadata, transient URLs/timestamps, and usage/cost while preserving them in a separate audit/full representation.

### MAJOR — F-PAG-SP02-C001-004 — Magnific requested/actual model provenance is not fail-closed

`MagnificJobSpec.from_request()` accepts a `model_slug` override without requiring it to equal the explicit `request.provider_model`. A job may therefore execute model B while request identity says model A. Import then constructs `SemanticImageCandidate` with `model_id=request.provider_model`, not the job/actual model. `actual_model_slug` may also differ without causing rejection.

This violates SP01 exact model binding and can make a candidate claim the wrong provider model.

Required closure: canonical job model must equal explicit request provider model for this cycle, unless a separately versioned explicit model-resolution contract is introduced. On import, actual model drift must fail closed or be represented without lying to the SP01 candidate model binding.

### MAJOR — F-PAG-SP02-C001-005 — BitForge style capability silently drops `style_strength`

The adapter declares BitForge `style_image=True` and sends `style_image`, but `PixelLabJobSpec`/`sdk_kwargs()` do not carry the SP01 request's `style_strength`. The official SDK exposes `style_strength` and defaults it to `0.0`.

A style-image request can therefore be advertised as supported while being executed with zero native style strength, materially changing/neutralizing the requested intent.

Required closure: either fully map/version/test SP01 `style_strength` to the official BitForge 0–100 scale, or do not advertise BitForge STYLE support in SP02-C002.

### MINOR — F-PAG-SP02-C001-006 — Magnific smoke fixture model slug is not currently catalog-valid

`tests/fixtures/sp02/magnific_smoke_job.json` uses `magnific-sd3`. A read-only lookup of the current owner-authorized Magnific image model catalog returned no model with that slug.

Required closure: regenerate the smoke fixture with a current catalog-valid explicit model slug suitable for a single low-cost bridge smoke. Do not treat that model as the permanent product default.

### MINOR — F-PAG-SP02-C001-007 — Legacy hidden trackers were treated as authority during builder startup

Builder log explicitly lists hidden/legacy `.hiveai` tracker/control-plane files as authority reads. Root `TASKS.md` is the only current status tracker.

Required closure: future builder logs must use GitHub root `TASKS.md` plus current authority/prompt/audit documents, and must not consult stale local hidden trackers for status truth.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

- PixelLab real SDK response currently falls back through PIL and re-encodes PNG. This can be acceptable as a deterministic lossless boundary if explicitly defined, but later provenance docs should distinguish provider wire bytes from project-owned lossless imported bytes.
- Provider capability taxonomy may eventually benefit from separating `native`, `prompt-guided`, and `unsupported`; do not expand SP01 contracts in C002 unless required for a clean bounded fix.
- Magnific model-specific ratio/resolution/quality support will eventually need versioned capability snapshots for reproducible jobs.

## 16. UNVERIFIED ITEMS

- Independent execution of builder's 429-test suite: UNVERIFIED due audit-container DNS failure.
- Live Magnific generation/import: intentionally NOT RUN because the current bridge is known-invalid before smoke.
- Live PixelLab generation: NOT RUN; no owner secret was provided to this audit environment and live paid execution is not required before fixing static contract defects.
- Provider server-side determinism across future model revisions: outside SP02 guarantee.

## 17. REGRESSION RISK

Current risk if SP02 were accepted as-is: **HIGH**.

Most concerning failure mode is provenance that looks valid while describing a different model or identity, plus Magnific outputs being rejected exactly because they require the later SP03 normalization stage.

C002 can remain narrow because no accepted M00-M10 or SP01 architecture needs redesign.

## 18. AUDIT CONFIDENCE

**HIGH for static/contract findings; MEDIUM-HIGH overall.**

Confidence basis:

- exact implementation inspected on GitHub main;
- official PixelLab SDK source inspected;
- current Magnific model catalog/surface inspected read-only;
- focused tests inspected for sensitivity gaps;
- no material ambiguity in the Magnific dimension/aspect/model issues.

Confidence reduction:

- audit container could not independently clone/run tests due DNS.

## 19. FINAL VERDICT

**FAIL**

SP02-C001 is not authorized for SP03 handoff or paid live smoke acceptance.

SP01 remains PASS/CLOSED. M00-M10 technical foundation remains preserved. No architectural restart is required.

## 20. REQUIRED REMEDIATION

Open one bounded cycle:

`PAG-SP02-C002 — Provider Contract Fidelity, Result Identity & Smoke Readiness Remediation`

It must close exactly the findings above by:

1. separating Magnific returned raster dimensions from logical target dimensions;
2. implementing supported deterministic Magnific aspect-ratio mapping and truthful native capability flags;
3. separating result deterministic identity from audit/cost/transient metadata for both providers;
4. enforcing exact Magnific request/job/actual-model binding;
5. either correctly mapping BitForge style strength or disabling advertised style capability until later;
6. replacing the Magnific smoke fixture with a current valid explicit model slug;
7. adding sensitivity tests for every defect;
8. preserving provider isolation, SP01 exact binding, M00-M10 behavior, and no-normalization-before-SP03;
9. performing no paid live generation from Codex;
10. stopping for independent audit before SP03 or live smoke acceptance.
