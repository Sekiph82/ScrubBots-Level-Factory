# PAG-SP02-C002 — Provider Contract Fidelity, Result Identity & Smoke Readiness Remediation
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authority

Read from GitHub before coding:

1. root `TASKS.md` — ONLY current project-status tracker
2. `.hiveai/audits/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_STRICT_AUDIT.md`
3. `.hiveai/prompts/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_PROMPT.md`
4. `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`
5. `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
6. closing SP01-C003 strict audit
7. official `https://github.com/pixellab-code/pixellab-python` files required by the C001 prompt
8. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`

Do **not** use local/untracked `.hiveai/RULES.md`, `.hiveai/PROJECT.json`, `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, `.hiveai/STATE.json`, `.hiveai/HANDOFF.md`, or `.hiveai/CYCLE_INDEX.md` as current status authority. They are legacy/historical or local migration debris. Do not delete user-owned dirty files; simply ignore them as authority.

## Mission

Implement **SP02-C002 only** and close:

- `F-PAG-SP02-C001-001`
- `F-PAG-SP02-C001-002`
- `F-PAG-SP02-C001-003`
- `F-PAG-SP02-C001-004`
- `F-PAG-SP02-C001-005`
- `F-PAG-SP02-C001-006`
- `F-PAG-SP02-C001-007` as a builder-process rule

This is a bounded provider-contract remediation. Preserve the accepted SP01 architecture and the useful SP02-C001 provider isolation/registry/config work.

Do not begin SP03 or SP04. Do not perform live paid provider generation.

---

# 1. Fix Magnific raw-raster vs logical-dimension boundary

The Magnific provider surface does not guarantee returned raster dimensions equal the requested ScrubBots logical target.

Remove the incorrect success requirement:

`returned_width/height == request.resolved_dimensions()`

for Magnific raw imports.

Required behavior:

- requested logical width/height remain the exact SP01 candidate requested dimensions;
- Magnific returned width/height record the actual provider raster dimensions;
- returned dimensions must be positive/sane integers and complete on success;
- raw hash/media/provider/job checks remain strict;
- do not resize/crop/pad/quantize/segment in SP02;
- SP03 remains the only normalization stage;
- `SemanticImageCandidate.success(...)` must preserve logical requested dimensions from the request and returned provider raster dimensions separately.

Add a test with a 16x16 ASSET_ART request and a much larger valid Magnific returned raster, e.g. 1024x1024. The raw candidate must import successfully and still be blocked from M08 logical-art masquerade.

---

# 2. Implement truthful Magnific aspect-ratio mapping

Current arbitrary reduced ratio output such as `20:21` is not a valid general provider contract.

Define an explicit versioned Magnific aspect-ratio vocabulary compatible with the owner-authorized image-generation surface. At minimum account for the currently surfaced generation vocabulary:

- `1:1`
- `21:9`
- `16:9`
- `9:16`
- `2:3`
- `3:4`
- `1:2`
- `2:1`
- `5:4`
- `4:5`
- `3:2`
- `4:3`

If the selected Magnific model supports a stricter subset, the job must fail closed or use an explicit versioned model-capability snapshot; never send a ratio known to be unsupported by the chosen model.

Deterministic mapping requirements:

- exact supported ratio wins;
- otherwise choose nearest supported ratio using a documented deterministic metric;
- deterministic tie-break;
- preserve original logical width/height separately;
- changing the mapped aspect ratio changes job identity;
- test non-square legal examples, including at least a ratio not exactly supported.

Do not query the live catalog at ordinary generation runtime unless a later explicit contract authorizes mutable catalog dependence. Static/versioned capability data is preferred for deterministic jobs.

---

# 3. Make Magnific capability declaration truthful

Do not advertise prompt-only art-direction hints as native provider capabilities.

The current C001 bridge marks native flags true for controls that the owner-authorized Magnific `images_generate` surface does not expose as dedicated fields.

At minimum review and correct:

- `negative_prompt`;
- `transparent_background`;
- `view_direction_controls`;
- `isometric`.

Text-rendered hints may remain in deterministic prompt rendering where product policy allows them, but:

- native capability flags must remain truthful;
- capability validation/routing must not imply native support;
- provider-specific metadata may explicitly say `prompt_guided_*` where useful;
- do not weaken generic SP01 capability honesty globally.

If a semantic request requires a native capability that Magnific does not provide under SP01 semantics, fail closed. If a particular control is explicitly defined as prompt guidance rather than native capability for Magnific, document/test that distinction without lying in the common capability schema.

---

# 4. Separate deterministic result identity from audit/cost metadata

Both provider result manifests must distinguish deterministic identity from full/audit serialization.

Non-identity fields include at minimum:

- transient URLs;
- timestamps;
- `audit_metadata`;
- PixelLab `usage.usd` / cost data;
- other mutable provider accounting/observability fields.

Required design:

- add/retain an `identity_dict()` or equivalent deterministic representation;
- result `digest()` hashes identity only;
- `canonical_dict()` may either mean identity-only or full deterministic artifact according to existing naming conventions, but the separation must be explicit and tested;
- full/audit serialization may retain usage and transient metadata;
- identical request/job/raw provider result with different audit URL/timestamp/cost => identical result identity digest;
- material provider/request/job/model/status/raw-hash/dimensions changes => different identity.

Do not remove audit/cost metadata; only remove it from identity.

---

# 5. Enforce exact Magnific model binding

A Magnific job may not silently execute a model different from the explicit `SemanticGenerationRequest.provider_model`.

Required:

- `MagnificJobSpec.from_request()` must require the final job `model_slug` to equal the explicit request provider model in C002;
- remove or fail closed on an override that differs from the request;
- import must verify request model == job requested model;
- if result supplies `actual_model_slug`, an unexpected drift must fail closed for this cycle rather than constructing a candidate that claims another model;
- candidate `model_id` must truthfully represent the exact accepted provider model;
- coordinated request/job/manifest model mismatch tests are required.

Do not introduce hidden provider auto-selection or model fallback.

---

# 6. Correct BitForge STYLE support

Official PixelLab BitForge exposes both `style_image` and `style_strength`.

C001 advertises BitForge `style_image` capability but does not map the SP01 request's `style_strength`; the official SDK default is `0.0`.

Choose one bounded C002 solution:

## Preferred

Fully map style strength:

- represent SP01 `style_strength` in `PixelLabJobSpec` identity;
- map SP01 normalized 0..1 strength deterministically to PixelLab's official 0..100 style-strength scale;
- pass it as `style_strength` to `generate_image_bitforge`;
- same request => same value/job digest;
- changed style strength => changed job digest and SDK kwargs;
- test 0, representative middle value, and 1 boundaries;
- verify PIXFLUX still rejects STYLE input.

## Acceptable alternative

Disable advertised BitForge STYLE support in SP02 and reject style-image requests until a later cycle.

Do not leave `style_image=True` while silently executing native strength 0.

---

# 7. Replace Magnific smoke fixture with a current valid model slug

The current fixture uses `magnific-sd3`, which is not present in the current connected Magnific image-model catalog.

Replace the fixture with one current catalog-valid explicit model slug suitable for a single bridge smoke. A currently observed example is `recraft-v4-1`; however, inspect the current read-only catalog at implementation start and choose a valid model intentionally.

Requirements:

- no live image generation;
- fixture remains count 1, ASSET_ART 16x16 logical target, simple wizard;
- fixture aspect ratio must be supported by the selected model;
- do not declare the smoke model the permanent/default product model;
- document the catalog observation date/contract snapshot in provider docs or fixture metadata without adding mutable timestamps to job identity.

---

# 8. Harden Magnific result manifest validation

While fixing the above, also fail closed for malformed direct manifest construction/import where relevant:

- success requires nonblank creation id, valid raw SHA-256, valid returned dimensions, media type, SUCCESS status consistency;
- failure must not fabricate provider creation IDs that never existed; creation id should be optional where provider supplied none;
- failure/non-success must not fabricate raw bytes/hash/dimensions;
- requested model and actual model semantics must be exact;
- request/job/provider/config/execution-surface binding remains exact.

Do not broaden scope into SP03.

---

# 9. Required focused tests

Add/adjust tests proving at minimum:

## Magnific

- square exact aspect mapping;
- at least two rectangular exact mappings;
- unsupported logical ratio maps deterministically to nearest supported ratio;
- tie-break is deterministic;
- selected model rejects unsupported aspect ratios where model snapshot is stricter;
- 16x16 logical request successfully imports a larger valid raw provider raster;
- candidate requested dimensions remain 16x16 while returned dimensions remain provider raster dimensions;
- prompt-only hints are not advertised as native capabilities;
- different request-vs-job model rejected;
- different actual-vs-requested model rejected;
- valid current smoke model fixture matches canonical job output;
- failure without a provider creation id remains valid and truthful.

## Result identity for both providers

- changing audit timestamp does not change result digest;
- changing transient URL does not change result digest;
- changing PixelLab usage cost does not change result digest;
- changing raw hash/dimensions/model/status/job binding does change result digest.

## PixelLab BitForge

If style support remains enabled:

- `style_strength` is present in job identity;
- 0.0 -> provider 0;
- 0.5 -> provider 50 (or documented deterministic equivalent);
- 1.0 -> provider 100;
- SDK fake client asserts exact `style_strength` kwarg;
- changed strength changes job digest;
- PIXFLUX rejects STYLE.

Retain:

- PixelLab secret leakage tests;
- exact PixelLab 16x16 size tests;
- deterministic provider-seed tests;
- role/hash binding tests;
- explicit provider/no-fallback tests;
- full SP01 suite.

---

# 10. Builder log

Create BEFORE any C002 source/test/doc edit:

`.hiveai/codex-logs/PAG-SP02-C002_PROVIDER_CONTRACT_FIDELITY_RESULT_IDENTITY_AND_SMOKE_READINESS_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-SP02-C002 — Provider Contract Fidelity, Result Identity & Smoke Readiness Remediation`

Role line:

`Document role: CODEX BUILDER LOG`

Record:

- GitHub repository/branch;
- local HEAD and fetched `origin/main`;
- divergence `0 0` before work;
- worktree dirt without treating legacy hidden trackers as authority;
- exact files changed;
- focused test chronology including failures/corrections;
- full suite;
- compile/import/CLI checks;
- provider-network isolation scan;
- secret scan;
- final scoped diff/status;
- commit/push;
- final fetched HEAD == origin/main and divergence `0 0`.

---

# 11. Verification

Run and record at minimum:

- focused SP02 tests;
- full SP01 semantic tests;
- all provider identity/tamper tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- standalone package/provider imports;
- module CLI help;
- installed CLI help where practical;
- network/browser/private-endpoint boundary scan;
- credential/secret scan;
- `git diff --check`;
- final scoped diff/status.

Auditor will independently decide whether the bridge is ready for one owner-authorized smoke. Codex must not perform paid generation in C002.

---

# 12. Forbidden

- Do not begin SP03 normalization.
- Do not begin SP04 qualification.
- Do not spend Magnific credits.
- Do not call live PixelLab API.
- Do not store any PixelLab secret.
- Do not scrape/drive Magnific UI.
- Do not use undocumented provider private endpoints.
- Do not change M00-M10 accepted algorithms.
- Do not weaken SP01 provenance binding.
- Do not change rejected M10 visual evidence.
- Do not silently fall back providers/models.
- Do not use stale hidden `.hiveai` trackers as current status authority.
- Do not self-audit.

## Stop condition

Commit/push the bounded SP02-C002 remediation to `main`, publish the completed matching builder log, fetch origin and verify exact local HEAD == `origin/main` with divergence `0 0`, then stop for independent ChatGPT strict audit.
