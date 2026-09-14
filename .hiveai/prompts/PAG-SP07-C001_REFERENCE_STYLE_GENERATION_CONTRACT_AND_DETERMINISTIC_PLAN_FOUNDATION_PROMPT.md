# PAG-SP07-C001 — Reference / Style Generation Contract & Deterministic Plan Foundation
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read completely from GitHub before implementation:

1. root `TASKS.md`;
2. `.hiveai/audits/PAG-SP06-C002_DURABLE_REVIEW_EVIDENCE_AND_ACCEPTANCE_GATE_STRICT_AUDIT.md`;
3. accepted SP06 `semantic/quality` source/tests;
4. current `src/scrubbots_pixel_factory/semantic/contracts.py`;
5. current provider-neutral semantic request contracts and `ImageInputDescriptor` roles;
6. current Magnific and PixelLab provider bridge contracts only as read-only integration references;
7. accepted SP05 LEVEL_ART compiler/normalization contracts only as read-only boundaries;
8. `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V02.md`;
9. `GOVERNANCE.md` and `AGENTS.md`.

GitHub is authoritative.

Canonical local repository:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Do not use `C:\Users\sekip\Desktop\ScrubBots`.

Do not edit root `TASKS.md`.

Create the matching builder log before product/test edits:

`.hiveai/codex-logs/PAG-SP07-C001_REFERENCE_STYLE_GENERATION_CONTRACT_AND_DETERMINISTIC_PLAN_FOUNDATION_CODEX_LOG.md`

---

## Mission

Begin SP07 by defining a provider-neutral, deterministic and content-addressed contract for reference/style guided semantic generation planning.

C001 is an **offline planning/foundation cycle**. It must not execute Magnific, PixelLab or any other provider and must spend zero provider credits.

The goal is to transform one canonical `SemanticGenerationRequest` containing reference/style/color/init inputs into a deterministic, auditable generation plan that a later explicitly authorized cycle can execute through a provider bridge.

Do not generate images in this cycle.

---

# 1. Dedicated reference/style planning boundary

Add a narrow package outside SP05/SP06 implementation modules, preferably:

`src/scrubbots_pixel_factory/semantic/generation/`

or another clearly isolated semantic-generation planning package.

A clean public surface may include names such as:

- `SemanticReferenceStylePlan`
- `SemanticGenerationVariant`
- `SemanticInputBinding`
- `plan_reference_style_generation`
- equivalent typed names if clearer.

Do not put SP07 planning into the SP05 compiler or SP06 quality modules.

---

# 2. Canonical request as source truth

The plan must accept an intact canonical `SemanticGenerationRequest` and bind its exact digest.

Do not accept loose prompt text plus caller-asserted hashes as a trusted plan.

At minimum preserve/bind:

- request digest;
- output class;
- description and negative description through request identity, not duplicated mutable truth unless needed for execution payload;
- semantic category when present;
- requested/resolved dimensions;
- deterministic seed identity;
- requested candidate count;
- provider selection fields already present in the canonical request;
- reference/style/init/color-reference identities;
- reference/style strengths where applicable;
- relevant view/direction/isometric/outline/shading/detail/background/coverage intent already carried by the request.

The planner must not rewrite accepted request semantics silently.

---

# 3. Content-addressed input bindings

Reference/style inputs must remain bound by canonical `ImageInputDescriptor` identity and content SHA-256.

Support the existing roles without inventing aliases that blur meaning:

- REFERENCE;
- STYLE;
- INIT;
- COLOR_REFERENCE.

Required behavior:

- deterministic ordering for multiple references;
- preserve each descriptor digest/content SHA/role;
- preserve optional source metadata only according to existing canonical identity rules;
- preserve style/init strengths exactly as canonical request values;
- no filesystem path may become canonical generation identity;
- duplicate content/role handling must be explicit and deterministic rather than silently ambiguous.

Do not read or upload image bytes in this planning cycle unless an existing canonical descriptor contract explicitly requires it. The plan is content-identity metadata, not provider execution.

---

# 4. Deterministic candidate/variant planning

Create a deterministic variant plan for `desired_candidate_count` candidates.

Each planned candidate must have a stable identity derived from the canonical request and candidate ordinal/seed derivation.

Requirements:

- same request → byte-identical plan;
- candidate ordering is deterministic;
- candidate IDs are deterministic;
- per-candidate seed/seed-material is deterministic;
- no global randomness or current time;
- repeated planning produces identical canonical bytes and digest;
- changing canonical request identity changes plan identity;
- changing candidate count changes plan identity and planned variant set.

Use the project's accepted deterministic RNG/seed conventions if applicable. Do not invent provider-specific randomness behavior as product truth.

---

# 5. Provider-neutral execution intent

The plan may carry a narrow provider execution intent derived from the request, but must remain provider-neutral at the product contract level.

At minimum make explicit:

- selected provider ID from the canonical request;
- requested model if present;
- workflow/config version identity;
- whether reference/style/init/color inputs are present;
- candidate ordinal and deterministic seed identity.

Do not silently fall back from one provider to another.

Do not call provider SDKs, HTTP endpoints, browser automation or remote generation.

Do not claim provider capability support merely because a field exists in the generic plan. Capability validation/execution belongs to a later cycle or the existing provider bridge contract.

---

# 6. Output-class safety

Preserve LEVEL_ART and ASSET_ART separation.

For LEVEL_ART:

- keep accepted production dimensions/semantic request legality unchanged;
- do not compile or normalize in SP07-C001;
- do not bypass SP05 or SP06 gates.

For ASSET_ART:

- preserve explicit dimensions and existing semantic request rules;
- do not force C01..C16 merely because LEVEL_ART uses that palette.

The plan is pre-provider execution intent. It is not a LEVEL_ART artifact, not a quality assessment and not M08 LevelData.

---

# 7. Integrity and immutability

Follow accepted contract style:

- frozen typed values;
- canonical dict/bytes/digest;
- versioned schema/policy constants;
- immutable nested tuples/mappings;
- deterministic ordering;
- fail-closed validation;
- private checked construction when needed;
- no public assertion-based trusted-plan minting.

A plan must be reconstructible/verifiable from the canonical request rather than relying on caller-provided derived facts.

---

# 8. Required tests

Add focused offline tests proving at minimum:

1. same canonical request produces identical plan bytes/digest across repeated runs;
2. request digest is exactly bound;
3. multiple REFERENCE descriptors retain deterministic ordering and exact identities;
4. STYLE descriptor and style strength are preserved;
5. INIT descriptor and init strength are preserved;
6. COLOR_REFERENCE identity is preserved;
7. local paths do not affect canonical input identity when existing descriptor rules exclude them;
8. changing reference content SHA changes plan identity;
9. changing style content SHA changes plan identity;
10. changing style/init strength changes request/plan identity;
11. candidate count N yields exactly N deterministic variants in stable order;
12. variant IDs/seeds are repeatable;
13. changing candidate count changes plan identity;
14. changing canonical seed changes variant identities/seeds;
15. provider/model/workflow/config selection is bound without silent fallback;
16. LEVEL_ART and ASSET_ART requests remain separate and legal under their existing contracts;
17. malformed/untrusted request-like values cannot mint a trusted plan;
18. public construction/replace cannot forge derived plan facts if constructor-like surfaces exist;
19. accepted SP06 focused tests remain green;
20. accepted SP05 tests remain green.

Use no network and no provider execution.

---

# 9. Documentation and exports

Export only the intended SP07-C001 planning surface.

Append a concise SP07-C001 section to `src/scrubbots_pixel_factory/semantic/README.md` explaining:

- reference/style generation planning is deterministic and content-addressed;
- image paths are not canonical identity;
- plans are provider-neutral execution intent;
- C001 does not call providers or generate images;
- later provider execution must use an explicitly authorized/audited cycle;
- SP05 compilation and SP06 acceptance gates remain downstream and unchanged.

Do not rewrite historical sections unnecessarily.

---

# 10. Verification

Run and record at minimum:

1. new SP07-C001 focused tests;
2. SP06 quality/evidence tests;
3. SP05 LEVEL_ART tests;
4. relevant SP01/SP02 semantic/provider contract tests;
5. full `python -m pytest -q`;
6. `python -m compileall -q src tests`;
7. package import smoke for new public types/functions;
8. module CLI smoke;
9. installed CLI smoke if installed;
10. `git diff --check`;
11. scoped provider/network/credential scan over changed production/tests;
12. `git diff -- TASKS.md` must be empty.

Record failed commands and corrections truthfully.

No Magnific call. No PixelLab call. Zero provider credits.

---

# 11. Scope prohibitions

Do not begin or modify:

- live/reference-guided provider execution;
- provider model qualification;
- SP08 edit/inpaint;
- SP09 Studio UI;
- SP10 weekly batching;
- SP11+ asset production/animation;
- SP05 compiler behavior;
- SP06 quality/evidence behavior;
- M08/LevelData bridge;
- solver;
- Challenge Score;
- Session Load;
- Frustration Risk;
- M11;
- main-game source;
- root `TASKS.md`.

Do not call Magnific, PixelLab or external vision/generation APIs.

---

# Builder log requirements

H1 exactly:

`# PAG-SP07-C001 — Reference / Style Generation Contract & Deterministic Plan Foundation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record:

- start timestamp;
- repository/local root/branch/remote;
- starting HEAD/origin/main/divergence;
- pre-existing dirt;
- authorities read;
- exact files changed;
- public contract introduced;
- canonical request binding;
- input binding/order rules;
- candidate/variant seed and identity derivation;
- provider-selection binding behavior;
- all focused/adversarial tests;
- every materially relevant failed/final test result;
- regression results;
- provider/network/credential scan;
- zero provider calls and credits;
- implementation commit SHA and push result;
- root `TASKS.md` non-edit statement;
- truthful main-game access/write statement.

Stop after final push for independent ChatGPT strict audit.

---

# Acceptance criteria

C001 is eligible for PASS only if all are true:

- [ ] SP07 planning lives outside SP05/SP06 modules;
- [ ] plans derive from and bind exact canonical `SemanticGenerationRequest` identity;
- [ ] reference/style/init/color-reference descriptors remain content-addressed and role-correct;
- [ ] local filesystem paths do not become canonical plan identity;
- [ ] input ordering/duplicate handling is explicit and deterministic;
- [ ] candidate count yields exactly that many deterministic variants;
- [ ] variant identity/seed derivation is stable and repeatable;
- [ ] provider/model/workflow/config selection is bound without fallback;
- [ ] plan is immutable/versioned/canonical;
- [ ] caller assertions cannot mint trusted derived plan facts;
- [ ] LEVEL_ART and ASSET_ART separation is preserved;
- [ ] no provider call or image generation occurs;
- [ ] accepted SP05 and SP06 behavior remains green;
- [ ] zero provider credits;
- [ ] no root `TASKS.md` builder edit;
- [ ] no main-game writes;
- [ ] builder log is complete and truthful.
