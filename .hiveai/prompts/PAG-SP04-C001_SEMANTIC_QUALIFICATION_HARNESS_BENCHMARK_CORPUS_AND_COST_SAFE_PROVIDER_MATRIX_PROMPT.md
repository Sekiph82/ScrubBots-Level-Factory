# PAG-SP04-C001 — Semantic Qualification Harness, Benchmark Corpus & Cost-Safe Provider Matrix
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before coding:

1. root `TASKS.md` — ONLY current project-status tracker;
2. `.hiveai/audits/PAG-SP03-C003_PROVENANCE_SEAL_AND_CONSTRUCTION_INTEGRITY_CLOSURE_STRICT_AUDIT.md`;
3. `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`;
4. `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`;
5. `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`;
6. accepted SP01 provider-neutral contracts;
7. accepted SP02 Magnific/PixelLab provider bridges;
8. accepted SP03 normalization contracts;
9. `review/m10/M10_OWNER_REVIEW_DECISION.md` and the retained rejected M10 review evidence;
10. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do not use legacy hidden `.hiveai` tracker/control-plane files as current authority.

Do not edit root `TASKS.md`.

## Entering owner decisions

The owner has explicitly accepted:

- Magnific semantic visual direction from the live wizard smoke;
- `24x24 px` as the first owner-approved `ASSET_ART` baseline target;
- provider-neutral architecture with both MAGNIFIC and PIXELLAB available;
- the fact that provider/model promotion must be evidence-based rather than assumed from general image quality.

The owner has **not** yet accepted:

- any local Magnific 2048→24 resampler output as visually equivalent to the approved provider-produced 24x24 derivative;
- any default production provider/model/workflow;
- any PixelLab live result in this project;
- any relaxation of LEVEL_ART contracts;
- automatic semantic scoring as a replacement for owner review.

## Mission

Implement **SP04-C001 only**.

Build the deterministic, provider-neutral qualification harness and benchmark corpus needed to compare semantic providers/models/workflows safely, cheaply and metadata-blind in later live qualification cycles.

This cycle is **infrastructure and evidence-schema only**.

Do **not** call Magnific or PixelLab.

Do **not** spend provider credits.

Do **not** begin SP05, SP06, Studio UI or M11.

---

# 1. Qualification lifecycle

Add a small qualification subsystem under the semantic package, for example:

`src/scrubbots_pixel_factory/semantic/qualification/`

Exact filenames may differ, but expose equivalent concepts for:

- benchmark subject/case definition;
- provider/workflow qualification plan;
- qualification attempt/result record;
- cost/usage record kept separate from deterministic artwork identity;
- normalization compatibility state;
- metadata-blind review item/pack;
- owner review disposition;
- qualification summary/gate result.

The harness must distinguish lifecycle states such as:

```text
PLANNED
  ↓
RAW_PROVIDER_CAPTURED
  ↓
RAW_IMPORT_VERIFIED
  ↓
NORMALIZED
  ↓
READY_FOR_BLIND_REVIEW
  ↓
OWNER_ACCEPTED | OWNER_REJECTED
```

Equivalent typed states are acceptable.

A provider generation being successful must never imply normalization success or visual acceptance.

---

# 2. Canonical benchmark corpus

Create a versioned benchmark corpus with concrete recognizable subjects. At minimum include these subject labels:

1. wizard
2. dwarf or warrior
3. elf
4. robot
5. fish
6. sea creature
7. mushroom
8. ghost
9. rocket
10. tree
11. skull
12. potion
13. crab
14. alien
15. simple building or object

The corpus must use stable IDs and deterministic canonical serialization.

Each benchmark case must include enough versioned intent to make later provider requests comparable, including at minimum:

- stable case id;
- subject/category;
- positive semantic description;
- optional negative intent independent of provider syntax;
- output class;
- target width/height;
- transparency/background intent;
- semantic recognizability objective;
- visual complexity/detail intent;
- optional reference/style requirement flags;
- benchmark/corpus version.

For C001, the default ASSET_ART qualification target is `24x24` unless a case explicitly tests another already-supported asset size.

Do not turn 24x24 into a LEVEL_ART size.

Do not silently apply LEVEL_ART color bands or C01..C16 to ASSET_ART.

---

# 3. Provider / engine / model / workflow matrix

Build an explicit qualification matrix for the approved provider families:

- `MAGNIFIC`
- `PIXELLAB`

The matrix must model provider-specific execution truth without polluting the provider-neutral benchmark case.

At minimum represent:

### Magnific

- explicit model slug from the accepted/pinned SP02 capability snapshot;
- model capability snapshot/version identity;
- provider aspect ratio intent;
- provider raw resolution intent if explicitly supported;
- reference/style capability truth;
- expected raw-raster path requiring SP03 normalization when not exact-size;
- external owner-authorized orchestration mode.

### PixelLab

- explicit engine (`PIXFLUX` / eligible `BITFORGE` path);
- official SDK/provider identity;
- exact requested `image_size` where supported;
- deterministic provider seed intent where supported;
- provider-native pixel-art controls available through accepted SP02 mappings;
- reference/style capability truth;
- exact-size/no-resize normalization fast-path expectation when returned dimensions already match.

No silent provider/model/engine fallback.

Unknown/unpinned provider models or unsupported capabilities must fail closed when constructing a qualification plan.

Do not copy mutable cost or UI metadata into deterministic provider/workflow identity.

---

# 4. Real-provider compatibility gate

Carry forward the SP03 audit NOTE explicitly.

Before any real provider attempt may be marked `READY_FOR_BLIND_REVIEW`, the qualification harness must require evidence that the exact raw provider bytes were locally captured/imported and accepted by the SP03 normalization boundary.

For each live attempt later, require evidence fields equivalent to:

- raw SHA-256;
- raw media type;
- returned raw dimensions;
- exact provider/job/result provenance identity;
- local raw-artifact digest;
- normalization request digest;
- normalized artifact digest;
- target dimensions;
- normalization policy/resampler/fast-path facts;
- compatibility/gate status.

For Magnific, this is especially important because the owner-approved live smoke exists but the exact private raw PNG has not yet been exercised through the local strict decoder in this audit environment.

C001 must provide the schema/gate and tests. Do not fabricate or reconstruct the private image.

If no approved live file exists locally, use synthetic fixtures only.

Do not broaden the strict PNG decoder speculatively. If future real provider evidence exposes safe ancillary chunks or another format, that must be handled in a separate evidence-driven remediation/qualification cycle.

---

# 5. Metadata-blind review package

Implement deterministic review-package construction for normalized candidates.

The owner-facing visual review item must not reveal before disposition:

- provider name;
- model/engine name;
- seed;
- cost;
- prompt internals beyond a neutral subject label if the review protocol requires it;
- workflow ranking;
- prior accept/reject state;
- generated filename that leaks provider/model identity.

Use stable opaque review IDs and deterministic ordering/shuffling rules. If shuffling is supported, it must use an explicit deterministic review seed and be reproducible.

The hidden manifest may retain exact provenance and provider/workflow identity for post-review analysis.

The review package must preserve one-to-one binding between visible review item and hidden provenance. Position/index-only binding is forbidden; use stable IDs as learned from the M10 review-binding closure.

No HTML/UI is required unless a small static review index cleanly reuses existing M10 infrastructure. Prefer contract/harness correctness over UI breadth in C001.

---

# 6. Owner-review disposition

Define explicit owner review states at minimum equivalent to:

- `PENDING_OWNER_REVIEW`
- `OWNER_ACCEPTED`
- `OWNER_REJECTED`

Only owner/ChatGPT audit authority may promote project tracker state; qualification data may record an owner disposition but must not mark a milestone complete itself.

Structural/technical success must remain separate from semantic visual acceptance.

A provider/model/workflow cannot become `DEFAULT` merely because tests pass or generation succeeds.

---

# 7. Cost and usage accounting

Provider cost/usage must be visible and auditable but separate from deterministic artwork/result identity.

Represent, when available later:

- provider attempt count;
- provider-reported credits/usage;
- optional currency cost when an authorized source supplies it;
- failed generation cost;
- accepted/rejected candidate cost;
- normalization reject count;
- owner accept/reject count.

Rules:

- cost/timestamp/UI URL must not alter raw image, normalization, review-item or semantic-art identity;
- mutable provider pricing must not be embedded as canonical model identity;
- no invented USD conversion;
- missing cost must remain unknown/null, never guessed;
- no unbounded retries;
- future live batch plans must carry explicit attempt/credit budget limits.

C001 does not spend credits.

---

# 8. Qualification comparison metrics

Build deterministic technical metrics only. Do not invent an automated recognizability oracle.

Useful technical facts may include:

- raw dimensions;
- normalized dimensions;
- exact-size fast path yes/no;
- normalized RGBA hash;
- unique RGBA color count;
- alpha/transparency statistics;
- normalization policy/resampler;
- provider attempt status;
- raw-import compatibility;
- normalization status;
- owner review disposition;
- provider credits/usage if supplied;
- elapsed provider time only as mutable audit/operational metadata, not deterministic identity.

Do not use photorealism or generic image-quality scores as semantic pixel-art acceptance.

Do not add CLIP/vision/LLM semantic scoring in C001.

---

# 9. Positive and negative semantic references

The qualification harness must acknowledge two existing evidence classes without copying private image bytes into Git:

### Positive

- owner-approved Magnific wizard direction at 24x24 recorded in `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`.

### Negative

- M10 100-image pack rejected 100/100 for semantic recognizability.

Represent these as evidence references/labels or review baselines without pretending the private positive raster is committed if it is not.

Do not rewrite or delete the M10 evidence.

---

# 10. Qualification plan generation

Provide one deterministic function/tool that can build a finite qualification plan from:

- corpus version;
- selected benchmark cases;
- explicit provider/workflow matrix;
- target size;
- attempt count per matrix cell;
- optional review seed;
- explicit maximum attempts and/or credit-budget metadata.

Plan generation must be offline and must not execute providers.

The plan must make the number of future paid attempts obvious before execution.

Tests must prove no accidental provider call can occur during plan construction/import.

A small CLI command is acceptable, e.g.:

`semantic-qualification-plan`

if it fits current CLI architecture. It must be plan-only/offline in C001.

---

# 11. Required focused tests

At minimum prove:

1. benchmark corpus has all required subject classes and stable IDs;
2. corpus canonical bytes/digest are deterministic;
3. 24x24 ASSET_ART baseline is represented without LEVEL_ART rules;
4. provider matrix requires explicit MAGNIFIC/PIXELLAB selection;
5. unknown Magnific model snapshot/model fails closed;
6. unsupported provider capability combination fails closed;
7. PixelLab PixFlux exact-size plan retains exact requested target intent;
8. eligible BitForge STYLE plan retains accepted style semantics without inventing unsupported controls;
9. qualification plan has finite explicit attempt count;
10. plan construction performs no network/provider call;
11. raw-import compatibility must be PASS before a live attempt result can become review-ready;
12. normalized artifact must be bound to the exact raw/import evidence;
13. metadata-blind visible item does not expose provider/model/seed/cost;
14. hidden review manifest retains exact provider/workflow/raw/normalized provenance;
15. visible item binds to hidden record by stable ID, not list position;
16. deterministic review ordering/shuffle is reproducible;
17. owner accept/reject remains separate from technical generation/normalization status;
18. cost/usage changes do not change deterministic artwork/review identity;
19. missing cost stays unknown rather than guessed;
20. M10 negative evidence and owner-approved wizard evidence can be referenced without embedding private URLs/ids;
21. existing SP01/SP02/SP03 focused tests remain green;
22. full repository regression remains green.

---

# 12. Security / privacy / offline rules

- no live provider call in C001;
- no Magnific or PixelLab credit spend;
- no browser automation;
- no private/undocumented provider endpoint;
- no credential read required for plan construction;
- no `PIXELLAB_SECRET` value in logs/manifests/tests;
- no Magnific private creation identifier or signed CDN URL committed;
- no machine-local absolute path in deterministic identity;
- no hidden provider fallback;
- no arbitrary execution/deserialization from imported qualification records;
- bounded finite plan sizes; reject unreasonable/unbounded attempt counts.

---

# 13. Scope exclusions

Do NOT:

- edit root `TASKS.md`;
- call Magnific or PixelLab;
- spend credits;
- select a default production provider/model/workflow;
- claim local Magnific normalization is owner-accepted;
- begin SP05 LEVEL_ART semantic integration;
- begin SP06 semantic scoring;
- build Studio UI;
- begin weekly paid batches;
- change owner-locked LEVEL_ART dimensions/palette/color bands;
- force C01..C16 onto ASSET_ART;
- change SP03 normalization algorithm unless a compile/import compatibility adjustment is strictly required;
- broaden PNG/JPEG/WebP support speculatively;
- alter M10 negative evidence;
- begin M11;
- self-audit or mark SP04 accepted.

---

# 14. Builder log

Create BEFORE any C001 source/test/doc edit:

`.hiveai/codex-logs/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_CODEX_LOG.md`

Exact H1:

`# PAG-SP04-C001 — Semantic Qualification Harness, Benchmark Corpus & Cost-Safe Provider Matrix`

Role line:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- repository/branch/start HEAD/origin HEAD/divergence;
- preserved user-owned dirt;
- current authority files read from GitHub;
- no legacy tracker authority use;
- qualification schema/harness design;
- benchmark corpus design;
- provider/workflow matrix design;
- blind-review binding design;
- cost/usage separation;
- exact files changed;
- every focused test failure/correction;
- focused SP04 result;
- SP01-SP04 focused regression;
- full repository regression;
- compile/import/CLI/offline/network/secret scans;
- implementation commit/push;
- final local HEAD == origin/main and divergence `0 0`.

Builder must not write the independent audit.

---

# 15. Stop rule

After implementation and verification:

1. complete the builder log;
2. commit/push `main`;
3. verify local HEAD == origin/main and divergence `0 0`;
4. STOP for independent ChatGPT audit.

Do not perform any live qualification generation. Do not begin SP04-C002, SP05 or M11.
