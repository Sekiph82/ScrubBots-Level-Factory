# PAG-SP02-C002 — Provider Contract Fidelity, Result Identity & Smoke Readiness Remediation
Document role: CHATGPT STRICT AUDIT

## 1. VERDICT

**FAIL**

SP02-C002 closes most of the concrete C001 defects and materially improves the provider layer. The Magnific raw-raster/logical-dimension equality bug is removed, prompt-only controls are no longer advertised as native, request/job/actual-model drift is rejected, PixelLab BitForge `style_strength` is mapped, and success-result audit/cost metadata is separated from digest identity.

However, SP02 is still not smoke-ready because four production-facing contract defects remain:

1. raw semantic candidates still cap returned provider raster dimensions at 1024, contradicting the new Magnific manifest allowance up to 8192 and current authorized provider models that can return 1.5k/2k/4k images;
2. the static Magnific model-capability snapshot is materially inaccurate and fails open for unknown models, so jobs can still claim/send unsupported aspect ratios and unsupported reference roles;
3. result identity still includes mutable diagnostic `failure_reason`, contradicting C002's own stable identity definition;
4. cross-object provenance is not exact: Magnific import does not prove `job.request_digest == request.digest()`, and PixelLab result-manifest construction does not prove the supplied candidate belongs to the supplied request/job/provider/engine/workflow/model.

No live Magnific or PixelLab generation was executed. Provider credit spend remains blocked.

Severity summary:

- BLOCKER: 0
- MAJOR: 4
- MINOR: 1
- NOTE: 2

## 2. CONTRACT RECOVERY

Audited against:

- root `TASKS.md` as the only current status tracker;
- `.hiveai/prompts/PAG-SP02-C002_PROVIDER_CONTRACT_FIDELITY_RESULT_IDENTITY_AND_SMOKE_READINESS_REMEDIATION_PROMPT.md`;
- `.hiveai/audits/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_STRICT_AUDIT.md`;
- `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`;
- `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`;
- accepted SP01 contracts in `src/scrubbots_pixel_factory/semantic/`;
- official public PixelLab SDK contracts;
- the current owner-authorized Magnific image-model catalog, read-only.

Recovered C002 closure requirements:

1. Magnific raw returned raster is independent from requested logical dimensions and is not normalized in SP02.
2. Magnific aspect ratios are selected from a truthful, versioned model-compatible capability snapshot.
3. Provider-native capability claims must be truthful and model/surface compatible.
4. Result identity excludes mutable audit/cost/observability data.
5. Magnific request/job/actual model binding is exact.
6. BitForge STYLE support either maps `style_strength` or is disabled.
7. Smoke fixture uses a current valid explicit Magnific model.
8. Success/failure manifests are fail-closed and provenance-complete.
9. SP01 exact request/provider/result binding remains intact.
10. No provider credit is spent before independent smoke-readiness acceptance.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder start HEAD: `09d3732d529bb231d40f8f0b45bfce39fbe4ad4e`.

Implementation commit: `0131e14bb7cc43beb8216308e5a5664925f10511`.

Builder-log terminal commit: `bfccf279d57bc8238a84de5087e3e8cb55ab7361`.

Compare `09d3732..bfccf27` is ahead by 2 commits and changes only:

- matching C002 builder log;
- semantic provider README;
- Magnific bridge/export;
- PixelLab bridge;
- two SP02 smoke fixtures;
- focused SP02 tests.

No M00-M10 production generator algorithm, root tracker, rejected M10 visual evidence, SP03, SP04, or main ScrubBots repository code was modified by Codex.

Scope discipline: **PASS**.

## 4. ACCEPTANCE CRITERIA MATRIX

| Area | Result | Audit assessment |
|---|---|---|
| Magnific raw raster != logical target | PASS/PARTIAL | Equality check removed; 1024 test passes conceptually, but SP01 candidate still rejects >1024 returned rasters |
| Magnific aspect mapping algorithm | PASS | Exact/nearest mapping and deterministic tie-break exist |
| Magnific model-specific ratio truth | FAIL | Hard-coded snapshots do not match current catalog; unknown models fall back to global vocabulary |
| Magnific native capability truth | PASS/PARTIAL | Prompt-only flags corrected, but generic reference/style truth is still model-insensitive |
| Result audit/cost separation | PASS/PARTIAL | `audit_metadata` and PixelLab usage excluded, but `failure_reason` remains digest identity |
| Magnific model binding | PASS | request model == job model == accepted actual model enforced |
| BitForge style strength | PASS | normalized request strength maps to 0..100 and is sent to SDK kwargs |
| Magnific fixture model slug | PASS | `recraft-v4-1` is current and valid |
| Fixture model capability snapshot | FAIL | fixture records unsupported ratio capability (`21:9`) for `recraft-v4-1` |
| Exact cross-object provenance | FAIL | coordinated request/job/candidate mismatches are not fully rejected |
| Failure manifest truth | PARTIAL | no fabricated image/creation data; requested-vs-actual failure model semantics remain slightly over-specified |
| Full regression | BUILDER PASS / AUDITOR UNVERIFIED | builder reports 435 pass; clean-clone replay blocked by DNS |
| Live provider smoke | NOT RUN | intentionally blocked pending technical acceptance |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Supported builder claims:

- large Magnific raster no longer has to equal logical requested dimensions;
- 1024x1024 raw result can coexist with a 16x16 requested target;
- native Magnific capability flags for negative prompt/transparency/view/isometric are now false;
- success manifest identity excludes audit metadata and PixelLab cost;
- explicit request-vs-job and actual-vs-requested model drift is rejected;
- BitForge style strength is represented in job identity and SDK kwargs;
- `recraft-v4-1` is a current catalog-valid model slug;
- no paid/live provider generation occurred.

Unsupported or incomplete builder claims:

- "model capability snapshot" is not truthful enough for execution. `recraft-v4-1` is recorded with all 12 global aspect ratios, while the current connected catalog exposes 11 and does not expose `21:9`. `seedream-5-pro` is also recorded with the same 12 global ratios although the current catalog exposes only 8. Unknown model slugs silently inherit the global 12-ratio set instead of failing closed.
- "Magnific native capabilities now advertise only text, reference, and style support" remains too broad because reference types are model-specific. The current `recraft-v4-1` catalog entry accepts `style` reference only, but the bridge globally accepts generic `REFERENCE` plus `STYLE`.
- "identity hashes only stable ... identity" is not fully true because both result-manifest identity dictionaries still include free-text `failure_reason`.

## 6. FILE / SYMBOL EVIDENCE

Primary audited implementation:

- `src/scrubbots_pixel_factory/semantic/providers/magnific/bridge.py`
  - `MAGNIFIC_SUPPORTED_ASPECT_RATIOS`
  - `MAGNIFIC_MODEL_ASPECT_RATIOS`
  - `_map_aspect_ratio()`
  - `_expected_images()`
  - `MagnificJobSpec.from_request()`
  - `MagnificResultManifest.identity_dict()`
  - `MagnificResultManifest.import_result()`
  - `MagnificProvider.capabilities`
- `src/scrubbots_pixel_factory/semantic/providers/pixellab/bridge.py`
  - `PixelLabJobSpec.style_strength`
  - `PixelLabResultManifest.identity_dict()`
  - `PixelLabResultManifest.from_candidate()`
  - `PixelLabProvider.manifest_for()`
- `src/scrubbots_pixel_factory/semantic/contracts.py`
  - `SemanticImageCandidate.__post_init__()` returned-dimension ceiling
- `tests/unit/test_sp02_provider_bridges.py`
- `tests/fixtures/sp02/magnific_smoke_job.json`
- `src/scrubbots_pixel_factory/semantic/providers/README.md`

Current read-only Magnific catalog observations during audit:

- `recraft-v4-1`: ratios `1:1, 2:1, 1:2, 3:2, 2:3, 4:3, 3:4, 5:4, 4:5, 16:9, 9:16`; reference type `style` only.
- `seedream-5-pro`: ratios `1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3, 21:9`; reference types `style, character, product, image`; resolutions `1.5k, 2k`.
- `imagen-nano-banana-2-lite`: ratios `1:1, 2:3, 3:2, 4:3, 3:4, 5:4, 4:5, 16:9, 9:16, 21:9`; reference types include `image`; current bridge snapshot does not reproduce this model-specific subset.

## 7. FOCUSED TEST EVIDENCE

Builder reports:

- initial expanded focused run: 16 passed / 1 failed;
- corrected SP02 + SP01 focused suite: 54 passed;
- full repository: 435 passed;
- compileall/import/CLI/diff/network/secret checks passed after correcting shell scan commands.

The new tests correctly cover:

- 1024x1024 raw Magnific result for 16x16 logical target;
- nearest/exact aspect mapping;
- prompt-only capability flags;
- request/job/actual model drift;
- success audit/cost identity separation;
- BitForge 0/50/100 style-strength mapping.

Residual test gaps directly match escaped defects:

1. no Magnific raw result above 1024 is tested;
2. no test compares model snapshots to their pinned model-specific capability sets;
3. no test proves an unknown Magnific model fails closed instead of inheriting global ratios;
4. no test rejects generic REFERENCE for a style-only model such as `recraft-v4-1`;
5. no test changes only `failure_reason` and expects result digest stability;
6. no coordinated request/job mismatch test checks `job.request_digest == request.digest()` at import;
7. no PixelLab manifest test supplies a candidate from request A and request/job B and expects fail-closed rejection.

## 8. REGRESSION EVIDENCE

Builder evidence:

- 435 repository tests passed in 302.64s;
- compileall passed;
- provider imports and CLI help passed;
- secret/network scans passed after false-positive/shell-quoting corrections;
- `git diff --check` passed.

Independent audit clean-clone replay was attempted again but the audit container could not resolve `github.com`, so runtime replay is **UNVERIFIED**, not failed.

No GitHub commit statuses exist on terminal HEAD.

No GitHub workflow runs are associated with terminal HEAD.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

PASS with notes.

Positive:

- Magnific remains non-networked inside the local Factory bridge;
- no browser scraping/private endpoint code introduced;
- PixelLab SDK remains optional/lazy and scoped to explicit provider execution;
- secrets remain runtime-only;
- no credits were consumed;
- mutable audit URLs/cost data are no longer in success result digest identity.

No new security defect was identified.

## 10. ARCHITECTURE CONSISTENCY

The provider-neutral architecture remains sound.

Correct architectural shape:

`SemanticGenerationRequest -> explicit provider job -> raw provider raster -> provenance-complete candidate -> SP03 normalization`.

Residual inconsistency:

- Magnific manifest now permits raw dimensions up to 8192, but `SemanticImageCandidate` still rejects returned dimensions greater than 1024. The abstraction boundary therefore says "large raw provider raster allowed" in one layer and "max 1024" in the next.
- Magnific provider capability truth is currently provider-global while the actual execution surface is model-specific.

No architecture restart is required. These are bounded contract closures.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Builder correctly treated root `TASKS.md` as the only current status tracker and explicitly ignored legacy hidden tracker debris.

The log was created before scoped edits as required.

The README's statement that the selected model's recorded capability snapshot travels in job identity is structurally true, but the snapshot values themselves are not accurate for the current catalog. Therefore documentation is **PARTIAL**, not fully truthful.

Root `TASKS.md` still shows C002 awaiting audit, which is correct until this audit is published and tracker ownership updates it.

## 12. FINAL REPOSITORY STATE

Terminal builder HEAD inspected: `bfccf279d57bc8238a84de5087e3e8cb55ab7361`.

Implementation commit: `0131e14bb7cc43beb8216308e5a5664925f10511`.

Builder reported post-push local HEAD == `origin/main` and divergence `0 0` before the builder-log publication commit. The builder log itself was then published as the terminal commit.

GitHub status checks: none.

GitHub workflow runs: none.

SP02 remains **ACTIVE / REMEDIATION REQUIRED**.

## 13. OPEN CROSS-MILESTONE FINDINGS

- SP03 normalization remains blocked.
- SP04 provider/model/workflow qualification remains blocked.
- M11 remains blocked.
- Real Magnific smoke remains blocked until C003 acceptance.
- Real PixelLab smoke remains blocked until SP02 technical acceptance plus owner secret/live-run authorization.
- M10 rejected 100-pack remains permanent negative semantic regression evidence.

## 14. DEFECTS BY SEVERITY

### MAJOR — F-PAG-SP02-C002-001 — Raw candidate returned-dimension ceiling still rejects valid >1024 provider rasters

C002 correctly allows Magnific result manifests up to 8192x8192 and removes the equality requirement against logical dimensions. But accepted SP01 `SemanticImageCandidate.__post_init__()` still rejects any `returned_width` or `returned_height` greater than 1024.

The focused regression uses exactly 1024x1024, so it passes at the ceiling and does not prove the intended larger-raster contract. Current authorized Magnific catalog entries can expose 1.5k/2k/4k output modes.

Impact: a valid 2048x2048 or 4096x4096 raw provider result can pass the Magnific manifest and then fail when converted into the required raw semantic candidate, before SP03 has any chance to normalize it.

Required closure:

- keep request/logical dimension rules unchanged;
- separately raise/version the raw candidate **returned** raster dimension ceiling to a provider-safe bound, recommended 8192 to match the manifest/tool surface;
- do not loosen LEVEL_ART logical dimensions or image-input descriptor limits accidentally;
- add 2048x2048 and preferably 4096x4096 Magnific raw-candidate tests.

### MAJOR — F-PAG-SP02-C002-002 — Magnific model capability snapshots are inaccurate and unknown models fail open

`MAGNIFIC_MODEL_ASPECT_RATIOS` assigns the full global 12-ratio vocabulary to every listed model. That does not match the current owner-authorized catalog.

Examples observed during audit:

- `recraft-v4-1` does not list `21:9` but the committed snapshot says it does;
- `seedream-5-pro` lists only 8 ratios but the committed snapshot says 12;
- model resolution support also varies;
- `MAGNIFIC_MODEL_ASPECT_RATIOS.get(model, MAGNIFIC_SUPPORTED_ASPECT_RATIOS)` lets any unknown explicit model silently inherit the global ratio set instead of failing closed.

Reference support is also model-specific. `recraft-v4-1` currently accepts style reference only, yet `MagnificProvider.capabilities` globally advertises both generic `reference_images` and `style_image`, and `_expected_images()` accepts both for any model.

Impact: canonical jobs can be deterministic yet unexecutable or semantically false for the chosen model.

Required closure:

- define a versioned per-model capability snapshot, not only per-model aspect ratios;
- snapshot at least supported ratios, supported reference role types, explicit resolution/quality enums when exposed, and whether references are supported at all;
- unknown/unpinned model slug must fail closed in SP02 rather than inherit permissive global defaults;
- validate request image roles against the selected model snapshot;
- validate explicitly supplied resolution/quality against the model snapshot;
- regenerate the Magnific fixture with the exact truthful `recraft-v4-1` snapshot;
- add model-specific tests for `recraft-v4-1`, `seedream-5-pro`, and an unknown model.

### MAJOR — F-PAG-SP02-C002-003 — Failure diagnostic text still changes deterministic result identity

Both `MagnificResultManifest.identity_dict()` and `PixelLabResultManifest.identity_dict()` still include `failure_reason`.

C002 defines stable result identity around request/job/provider/model/status/raw-hash/dimensions, while diagnostic/audit detail is non-identity. Builder documentation also says full serialization retains "failure details" without affecting `digest()`.

Two failed attempts with the same request/job/provider/status but provider messages such as `timeout` vs `gateway timeout` therefore receive different result digests.

Required closure:

- remove free-text `failure_reason` from deterministic result identity for both provider manifests;
- preserve it in full/canonical audit serialization;
- keep `status` in identity;
- add success and non-success sensitivity tests proving diagnostic text changes do not alter digest while status/job/model changes do.

### MAJOR — F-PAG-SP02-C002-004 — Exact cross-object provenance binding remains incomplete

Magnific import validates manifest request digest and job digest independently, but does not assert `job.request_digest == request.digest()`. A directly constructed/tampered manifest can therefore carry request A's digest plus job B's digest and pass the current coordinated checks when the remaining model/provider fields align.

PixelLab has the mirror problem on manifest creation: `PixelLabResultManifest.from_candidate()` and `PixelLabProvider.manifest_for()` do not assert that the candidate belongs to the supplied request/job/provider/engine/workflow/model before emitting a provenance manifest.

Impact: provenance artifacts can cryptographically identify individually valid objects while binding the wrong objects together.

Required closure:

- Magnific import must independently assert request <-> job binding before trusting manifest binding;
- PixelLab manifest construction must use one checked request/job/candidate path and reject mismatched candidate request digest, provider id/version, workflow, model/engine, requested dimensions and image input provenance;
- direct manifest constructors should remain fail-closed for malformed/coordinated mismatches where applicable;
- add coordinated-mismatch tests, not only one-field corruption tests.

### MINOR — F-PAG-SP02-C002-005 — Failure `actual_model_slug` is over-specified

`MagnificResultManifest.failure()` sets `actual_model_slug = job.model_slug` even when external execution may have failed before an actual model was selected/run.

This is not the main acceptance blocker because requested model provenance is retained elsewhere, but it blurs requested-vs-observed semantics.

Required closure in C003 if touching the schema: allow failure `actual_model_slug` to be absent unless the external provider actually reports an executed model, while keeping requested `model_slug` exact.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

- Replace multiple parallel Magnific capability dictionaries with one immutable/versioned `MagnificModelCapabilitySnapshot` value type.
- Keep the snapshot deliberately small and pinned to only models actually intended for SP04 qualification; there is no need to mirror the whole provider catalog.
- Distinguish `provider wire image bytes` from `project-owned deterministic lossless PNG bytes` in PixelLab provenance documentation before long-term archival workflows.
- Later add a controlled catalog-refresh tool/process, but do not make ordinary job identity depend on mutable live catalog queries.

## 16. UNVERIFIED ITEMS

- Independent execution of the builder's 435-test suite: **UNVERIFIED** because audit-container DNS could not resolve `github.com` during clean clone.
- Live Magnific smoke: **NOT RUN** by design.
- Live PixelLab smoke: **NOT RUN** by design and no owner secret is available to the auditor.
- Actual long-term server-side deterministic regeneration: explicitly outside guarantee.

## 17. REGRESSION RISK

Current risk if SP02 were accepted now: **MEDIUM-HIGH**.

C002 removed several high-risk C001 problems, but remaining defects affect exactly the first real provider execution boundary: a legitimate high-resolution Magnific result can fail at candidate construction, a job may encode a capability unsupported by its selected model, and provenance manifests can still bind the wrong cross-object combination.

The remediation remains narrow and does not require reopening M00-M10 or redesigning SP01 architecture.

## 18. AUDIT CONFIDENCE

**HIGH** for static contract findings and live Magnific catalog mismatch.

**MEDIUM** for runtime regression evidence because independent clean checkout could not run due DNS failure.

The remaining failures are visible directly in current repository code and do not depend on speculative runtime behavior.

## 19. FINAL VERDICT

**FAIL**

C002 is a substantial improvement but does not close SP02. Do not spend provider credits yet. Do not begin SP03/SP04.

Disposition:

- C001 raw-raster equality defect: CLOSED, with residual >1024 cross-layer ceiling moved to new C002 finding;
- C001 prompt-only native capability overclaim: CLOSED;
- C001 success audit/cost identity contamination: CLOSED, with residual failure diagnostic identity finding;
- C001 Magnific model drift: CLOSED;
- C001 BitForge style-strength omission: CLOSED;
- C001 stale smoke model slug: CLOSED;
- C001 legacy authority-process issue: CLOSED;
- SP02 overall: **FAIL / C003 REQUIRED**.

## 20. REQUIRED REMEDIATION

Create one bounded cycle:

`PAG-SP02-C003 — Model Capability Snapshot, Raw Raster Ceiling & Cross-Provenance Closure`

C003 must do only the following:

1. separate raw returned-raster dimension bounds from logical/requested bounds and support authorized provider rasters through at least 4096, preferably 8192;
2. replace permissive Magnific model metadata with truthful versioned per-model capability snapshots and reject unknown/unpinned models;
3. validate model-specific aspect ratios, reference roles, resolution and quality where explicitly supplied;
4. remove free-text failure diagnostics from deterministic provider-result identity while preserving full audit serialization;
5. close request <-> job <-> manifest/candidate coordinated-binding gaps for both Magnific and PixelLab;
6. make failure actual-model semantics truthful if schema is touched;
7. add focused sensitivity tests for every residual;
8. preserve SP01 architecture, M00-M10, provider isolation and no-credit-spend rule;
9. do not begin SP03/SP04;
10. stop for independent audit before any live provider smoke.
