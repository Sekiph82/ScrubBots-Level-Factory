# SCRUBBOTS Pixel Studio — Semantic Generation Conversion Plan

Document role: OWNER-AUTHORIZED PRODUCT / ARCHITECTURE PLAN  
Date: 2026-09-11  
Repository: `Sekiph82/ScrubBots-Level-Factory`  
Status: **AUTHORITATIVE / ACTIVE**

## 1. Why this plan exists

The deterministic procedural Pixel Art Generator built through M00–M10 is technically useful but failed the owner's visual product gate.

The owner reviewed the 100-candidate M10 pack and rejected **100 / 100** because the results did not reliably read as identifiable objects, characters, events or scenes without metadata labels.

The failure is not primarily resolution. The owner provided low-resolution PixelLab examples, including a tiny wizard sprite, that remain immediately recognizable.

Therefore the product requirement is clarified:

> SCRUBBOTS must generate recognizable semantic pixel art, not merely structurally valid colored geometry.

The existing architecture is **not discarded**. It is converted into the deterministic production, logicalization, validation, post-processing, provenance, batch and export layer around a new semantic pixel-art generator.

---

# 2. What is preserved from M00–M10

The following accepted work remains valuable and must be reused rather than rewritten:

- canonical difficulty/dimension rules;
- C01..C16 palette authority;
- difficulty used-color bands;
- deterministic request serialization;
- deterministic RNG/sub-seeds/retry provenance;
- MASK generator;
- RULES generator;
- WFC engine;
- HYBRID router;
- structural quality metrics;
- duplicate/near-duplicate metrics;
- JSON/PNG exact export;
- metadata and provenance;
- reproduce CLI;
- resumable deterministic batch orchestration;
- performance/property-test infrastructure;
- owner review manifest/gallery concepts.

The interpretation changes:

```text
OLD
MASK / RULES / WFC / HYBRID
        ↓
try to invent the picture itself
        ↓
structurally valid but often semantically unreadable art

NEW
SEMANTIC IMAGE MODEL
        ↓
recognizable subject / scene
        ↓
DETERMINISTIC LOGICALIZATION
        ↓
MASK / RULES / WFC / HYBRID
        ↓
structure repair / topology / palette / style-detail / controlled variants
        ↓
semantic + structural QA
        ↓
SCRUBBOTS logical art
```

MASK/RULES/WFC/HYBRID are not deleted. They become supporting production engines instead of being solely responsible for semantic understanding.

---

# 3. PixelLab is the product reference, not the runtime dependency

Reference organization:

- https://github.com/pixellab-code
- https://github.com/pixellab-code/pixellab-python
- https://github.com/pixellab-code/pixellab-js
- https://github.com/pixellab-code/pixellab-mcp
- https://www.pixellab.ai/create?tool=create_image_pro

The public PixelLab SDKs demonstrate useful product/API concepts:

- text description;
- negative description;
- deterministic seed;
- image size;
- transparent background;
- reference image;
- style image / style strength;
- init image / strength;
- color reference;
- outline;
- shading;
- detail;
- view;
- direction;
- isometric mode;
- inpainting;
- rotation/directional variants;
- animation.

We do **not** scrape PixelLab private code, bypass access controls, or depend on its paid generation API.

PixelLab is a UX/API reference only.

---

# 4. Cost rule

Owner constraint:

No new recurring paid image-generation service is allowed.

Existing paid tools available to the owner are:

- ChatGPT;
- Claude Code;
- Magnific.ai.

The automatic weekly generation pipeline must not require per-image payments to PixelLab, OpenAI API, Replicate, Stability API or another paid generation API.

Therefore the primary automated semantic provider will be a **local open-weight image-generation backend**.

First implementation target: **ComfyUI**, running locally and controlled through its local HTTP/workflow API.

Why ComfyUI is the first target:

- open source;
- runs locally;
- reusable deterministic workflows;
- supports queue/batch automation;
- supports model swapping and LoRAs;
- provides an API suitable for our Python orchestrator;
- supports Intel Arc/Core Ultra through PyTorch XPU on supported systems;
- does not impose a per-image generation fee.

The architecture remains provider-based so ComfyUI can later be replaced without rewriting the SCRUBBOTS pipeline.

---

# 5. Revised offline rule

The old V1 statement "no AI model" is superseded by this owner-authorized plan.

New rule:

- **generation runtime must remain local and capable of working offline**;
- installation/setup may access the network to install software and download open model weights;
- model files are never committed to Git;
- runtime generation must not require a remote paid API;
- every backend/model/workflow version is recorded in provenance.

The existing production network-ban tests must be revised narrowly so they distinguish:

1. setup/model acquisition, which may use network access; from
2. candidate generation runtime, which must remain local/offline.

---

# 6. Revised logical-pixel rule

The final SCRUBBOTS production contract remains:

> one final logical artwork pixel = one gameplay cell.

For LEVEL_ART:

- EASY: 20–29 per axis;
- MEDIUM: 30–39;
- HARD: 40–49;
- VERY_HARD: 50–59;
- rectangular boards remain legal;
- final logical colors remain C01..C16;
- final difficulty used-color bands remain enforced;
- final PNG/JSON continue to be exact logical dimensions;
- no antialiasing/interpolation exists in the final logical artifact.

However, the previous blanket rule forbidding a larger intermediate image is superseded **for the semantic AI stage only**.

A semantic model may create a source image at the resolution its architecture needs. That source is then converted by a **versioned deterministic Semantic-to-Logical compiler** into the exact target logical grid.

This is not an arbitrary resize operation. The compiler must record and test:

- source dimensions;
- crop/subject bounds;
- alpha/background extraction;
- target dimensions;
- projection/downsampling algorithm and version;
- palette quantization algorithm and version;
- color-band reduction/selection;
- silhouette/topology preservation metrics;
- semantic recognizability before and after logicalization;
- final exact grid hash.

The source image must be retained as provenance and may never be confused with the final gameplay grid.

---

# 7. New target architecture

```text
PIXELLAB-LIKE LOCAL STUDIO / CLI
                │
                ▼
        Generation Job Contract
     prompt / negative / seed / refs
                │
                ▼
       Semantic Provider Router
                │
         ┌──────┴──────┐
         │             │
     ComfyUI        future local
     provider        providers
         │
         ▼
   Raw Semantic Artifact
 recognizable subject/scene
         │
         ▼
 Semantic-to-Logical Compiler
 crop / alpha / pixel projection
 C01..C16 / difficulty color band
         │
         ▼
 Structural Processing Layer
 MASK / RULES / WFC / HYBRID
         │
         ▼
      QUALITY GATES
 semantic recognizability
 structural quality
 duplicate/diversity
         │
    reject     accept
                 │
                 ▼
       EXISTING M08 EXPORT
 PNG / JSON / metadata / provenance
                 │
                 ▼
       EXISTING M09 BATCH
                 │
                 ▼
       Owner Review Gallery
                 │
                 ▼
       Main Level Factory
```

---

# 8. Generation profiles

The system will support explicit output profiles rather than forcing every image into the same contract.

## 8.1 LEVEL_ART — first production priority

Purpose: artwork that becomes a SCRUBBOTS playable board.

Hard final constraints:

- 20–59 logical pixels by difficulty;
- rectangular allowed;
- C01..C16 only;
- exact difficulty color bands;
- one final logical pixel = one cell;
- flat cells;
- exact M08 export;
- structural + semantic acceptance.

Examples:

- wizard;
- robot;
- fish;
- mushroom;
- rocket;
- skull;
- ghost;
- tree;
- crab;
- potion;
- castle;
- alien;
- recognizable scene silhouettes.

## 8.2 SPRITE_ASSET — second profile

Purpose: characters, enemies, objects, items and decorative sprites comparable to the owner's PixelLab wizard/dwarf/elf examples.

This profile is not automatically subject to LEVEL_ART's 20–59 board or difficulty-color-band rules.

It receives its own later asset contract for:

- transparent background;
- sprite dimensions;
- palette policy;
- outline/shading/detail;
- directional views;
- export format.

The provider/UI architecture must support this profile even while LEVEL_ART remains the first acceptance target.

---

# 9. Semantic request contract

A versioned SemanticGenerationRequest will eventually include:

- asset profile;
- description / prompt;
- negative description;
- semantic category / expected label;
- seed;
- requested candidate count;
- target difficulty for LEVEL_ART;
- target logical width/height when applicable;
- source/model resolution;
- model ID/version/hash;
- workflow ID/version/hash;
- reference images, up to a bounded count;
- style image;
- style strength;
- init image;
- init strength;
- color/palette reference;
- remove-background flag;
- subject coverage percentage;
- outline preset;
- shading preset;
- detail preset;
- view;
- direction;
- isometric flag;
- provider-specific options under a versioned namespace.

No UI field may bypass canonical request serialization.

---

# 10. Semantic recognizability becomes a first-class quality gate

M07 structural quality remains useful but is insufficient.

New quality decision:

```text
STRUCTURALLY VALID ≠ SEMANTICALLY ACCEPTABLE
```

A production candidate must pass both.

The Semantic Quality layer will evaluate at least:

- prompt/label alignment using a local vision-text model such as CLIP/SigLIP or another audited open model;
- subject occupancy;
- silhouette readability;
- background leakage;
- connectedness/topology where category-relevant;
- semantic score before logicalization;
- semantic score after logicalization;
- degradation introduced by palette reduction;
- duplicate/near-duplicate semantic variants;
- owner calibration labels.

The rejected M10 100-candidate pack becomes a useful **negative calibration corpus**. It must remain rejected and may not be relabeled as production art.

Machine semantic scoring is a filter, not final artistic authority. Owner review remains required until acceptance data proves otherwise.

---

# 11. Existing engines in the new architecture

## MASK

New roles:

- extract/preserve subject silhouette;
- derive foreground masks;
- enforce subject coverage;
- repair small silhouette gaps;
- generate controlled masks for inpainting;
- create deterministic variants around an AI-generated semantic base.

MASK is no longer expected to invent a convincing wizard/fish/robot by itself.

## RULES

New roles:

- topology cleanup;
- connected-region repair;
- controlled border/negative-space changes;
- gameplay-specific region operations;
- deterministic local mutations;
- puzzle geometry after semantic art exists.

RULES is not a semantic image model.

## WFC

New roles:

- learn local texture/pattern language from **owner-approved semantic exemplars**;
- add detail without changing the core recognizable subject;
- generate style-consistent variants;
- operate only where semantic preservation tests pass.

## HYBRID

New roles:

- Semantic AI + MASK repair;
- Semantic AI + RULES topology;
- Semantic AI + WFC approved-detail pass;
- Semantic AI + deterministic palette compiler;
- multi-stage variants with full provenance.

No post-process stage may silently destroy recognizability.

---

# 12. PixelLab-like local Studio UX

The end-user product should resemble the workflow, not proprietary code, of PixelLab Create.

Local web app target:

```text
┌──────────────── LEFT CONTROLS ────────────────┐
│ Create Image                                  │
│ Description                                   │
│ Negative Description                          │
│ Asset Profile                                 │
│ Difficulty / logical size                     │
│ Remove Background                             │
│ Reference Images                              │
│ Style Image                                   │
│ Style Strength                                │
│ Seed                                          │
│ Model                                         │
│ Outline / Shading / Detail                    │
│ View / Direction                              │
│ Candidate Count                               │
│                                               │
│                GENERATE                       │
└───────────────────────────────────────────────┘

                 CENTER
        selected candidate / editor

                                    RIGHT
                           generation gallery
                           accept / reject
                           compare / reproduce
```

The Studio runs locally and talks to the existing Python factory plus the local semantic provider.

V1 Studio requirements:

- create prompt;
- variant count;
- deterministic seed;
- output profile;
- logical target size/difficulty;
- model/workflow selection;
- reference/style image upload;
- transparent-background option;
- central nearest-neighbor preview;
- candidate gallery;
- semantic + structural scores;
- ACCEPT / REJECT;
- reproduce;
- export.

Later Studio requirements:

- paint/erase;
- palette swap;
- mask editing;
- inpaint selected region;
- reference-guided regeneration;
- directional variants;
- animation workflows where relevant.

---

# 13. New milestone roadmap

Historical M00–M10 evidence remains preserved.

The previous unstarted M11 handoff plan is superseded and deferred until the semantic system passes owner acceptance.

## PAG-M11 — Local Semantic Backend & Provider Foundation

Goal: prove a zero-per-image-cost local semantic generation backend can be automated from the existing Python project.

Tasks:

- define `SemanticProvider` interface;
- implement ComfyUI local provider adapter;
- add provider health/doctor command;
- detect local hardware/backend capability;
- establish local-only generation API boundary;
- establish model/workflow registry schema;
- keep model weights outside Git;
- record model/workflow hashes;
- queue one/many jobs deterministically where backend permits;
- capture raw image + backend metadata + seed;
- mock provider for CI/tests;
- document Windows setup;
- verify runtime works without Internet after installation;
- benchmark actual owner hardware rather than assuming speed.

Acceptance:

- Python factory can submit a local semantic job and retrieve a deterministic result from the chosen backend;
- no paid remote generation API is required;
- backend/model identity is reproducibly recorded.

## PAG-M12 — Model Qualification & Semantic Generation Contract

Goal: choose the best practical open model/workflow for recognizable low-resolution pixel art.

Tasks:

- create canonical semantic request schema;
- create fixed evaluation prompts: wizard, robot, fish, ghost, rocket, tree, crab, potion, object and simple scene;
- evaluate at least three practical open-weight model/workflow candidates if hardware permits;
- measure generation time, memory, failure rate and seed stability;
- score recognizability before logicalization;
- test pixel-art-specific prompting/LoRA/workflow options;
- record licenses and model provenance;
- select default model/workflow based on measured quality, not popularity;
- select fallback model/workflow if useful.

Acceptance:

- chosen default reliably creates recognizably semantic source images on the owner's hardware;
- model licensing is compatible with intended project use;
- no model file is committed to Git.

## PAG-M13 — Semantic-to-Logical Pixel Compiler

Goal: turn semantic AI source images into exact SCRUBBOTS logical boards without losing recognizability.

Tasks:

- preserve immutable raw source artifact;
- background/alpha extraction;
- subject bounding box and coverage control;
- deterministic crop/pad;
- deterministic source→logical projection;
- pixel cluster/silhouette preservation;
- C01..C16 palette mapping;
- exact difficulty color-band reduction;
- flat logical-cell output;
- no final antialias/interpolation;
- topology preservation metrics;
- exact provenance of every transform;
- compare semantic score before/after compilation;
- rectangular targets;
- 20–59 targets;
- golden regression fixtures;
- exact M08 export reuse.

Acceptance:

- final logical output obeys every LEVEL_ART contract;
- target remains recognizably the requested semantic subject;
- same source + same compiler config reproduces byte-identical logical output.

## PAG-M14 — Semantic Quality / Recognizability Gate

Goal: automatically reject images that are valid geometry but do not look like what was requested.

Tasks:

- evaluate local CLIP/SigLIP-class vision-text scorers or equivalent;
- version semantic scoring model;
- score raw source;
- score final logical output;
- detect semantic degradation;
- add silhouette/occupancy/background metrics;
- define machine rejection reasons;
- use the rejected M10 100 pack as negative evidence;
- build a new owner-labelled calibration pack;
- calibrate thresholds from owner labels;
- never claim machine score replaces owner artistic review.

Acceptance:

- deliberately meaningless procedural examples are rejected as semantic failures;
- clearly recognizable wizard/fish/robot/etc. examples pass at useful rates;
- owner-reviewed threshold is recorded before production use.

## PAG-M15 — Semantic + Existing Engine Fusion

Goal: integrate the new semantic source with the M03–M06 engines rather than abandoning them.

Tasks:

- semantic→MASK silhouette workflow;
- semantic→RULES topology cleanup workflow;
- semantic→WFC approved-exemplar detail workflow;
- semantic→HYBRID multi-stage workflow;
- preserve subject identity across all stages;
- reject post-processing that damages recognizability;
- preserve deterministic stage provenance;
- support structural variations without replacing semantic subject;
- compare quality before/after every stage.

Acceptance:

- at least two fused strategies improve or preserve objective/owner quality;
- no accepted fused path degrades an identifiable object into an unreadable pattern.

## PAG-M16 — PixelLab-like Local Create Studio

Goal: give the owner a local interface modeled on the useful workflow of PixelLab Create.

Tasks:

- local web application;
- prompt/negative prompt;
- profile/difficulty/size;
- seed;
- variant count;
- model/workflow selector;
- remove background;
- reference image upload;
- style image upload;
- style strength;
- outline/shading/detail controls where backend supports them;
- view/direction controls where backend supports them;
- center preview;
- right-side gallery;
- progress/queue;
- semantic/structural scores;
- ACCEPT/REJECT;
- reproduce;
- export;
- zero dependency on PixelLab paid API.

Acceptance:

- owner can locally type `cute wizard character`, request variants, see recognizable candidates and accept/reject them without touching CLI internals.

## PAG-M17 — Reference, Edit, Inpaint & Variant Workflows

Goal: approach the useful editing capabilities of PixelLab without copying its proprietary implementation.

Tasks:

- reference-guided generation;
- style-guided generation;
- init image strength;
- palette/color reference;
- editable mask;
- local inpainting workflow;
- deterministic seed variants;
- directional variant research;
- sprite/object profile support;
- optional rotate/animation research after static quality is accepted.

Acceptance:

- selected region can be regenerated without replacing the entire accepted asset;
- style/reference workflows retain provenance;
- static semantic image quality remains the priority over animation.

## PAG-M18 — Automated Weekly Semantic Batch Factory

Goal: produce reviewable semantic candidates automatically at zero additional per-image service cost.

Tasks:

- prompt/category library;
- deterministic job manifests;
- resumable ComfyUI/local-provider queue;
- max-attempt budget;
- semantic pre-filter;
- logicalization;
- structural filter;
- duplicate filter;
- diversity selection;
- owner review queue;
- accepted/rejected statistics;
- batch HTML Studio/gallery;
- reproduce accepted result;
- no automatic production promotion without owner acceptance.

Acceptance:

- owner can request a weekly target such as 100 review candidates and let the laptop generate/filter them unattended;
- each final candidate has full semantic + logical + structural provenance;
- no extra paid image-generation service is required.

## PAG-M19 — Main SCRUBBOTS Level Factory Handoff

This is the deferred purpose of the old M11.

Tasks:

- inspect current main-repo Level Data contract;
- reuse audited import/reconstruction boundaries;
- semantic artifact→Level Factory adapter;
- preserve exact final logical grid;
- preserve source and generation provenance as sidecar metadata;
- keep mobile runtime independent of Python/ComfyUI/model files;
- integrate owner-approved art into `Sekiph82/Scrubbots/level_factory`;
- rejoin LF00–LF10 roadmap;
- keep semantic generation as development tooling, not mobile runtime generation.

Acceptance:

- owner-approved recognizable semantic artwork can enter the main Level Factory without palette reinterpretation or hidden resizing;
- mobile game has zero dependency on local AI runtime.

---

# 14. First implementation order

```text
OWNER REJECTION OF OLD 100 PACK
            │
            ▼
PAG-M11
Local semantic provider + ComfyUI foundation
            │
            ▼
PAG-M12
Model/workflow qualification
            │
            ▼
PAG-M13
Semantic-to-logical compiler
            │
            ▼
PAG-M14
Recognizability gate
            │
            ▼
PAG-M15
Fuse semantic source with MASK/RULES/WFC/HYBRID
            │
            ▼
PAG-M16
PixelLab-like local Create Studio
            │
            ▼
PAG-M17
Reference/edit/inpaint/variants
            │
            ▼
PAG-M18
Weekly semantic batch factory
            │
            ▼
OWNER VISUAL ACCEPTANCE
            │
            ▼
PAG-M19
Main Level Factory handoff
```

---

# 15. Immediate first cycle

The first cycle is intentionally narrow:

`PAG-M11-C001 — Local Semantic Backend & Provider Foundation`

It must **not** rewrite M00–M10.

It should:

1. create a clean semantic provider boundary;
2. create a ComfyUI adapter against localhost only;
3. create hardware/backend doctor diagnostics;
4. define model/workflow registry/provenance;
5. add mocked tests so CI does not need large model weights;
6. establish an installation path for the owner's Windows machine;
7. prove local API orchestration with a minimal real workflow when the local backend is available;
8. record measured feasibility before a large model is chosen.

Model selection itself belongs to M12 unless a lightweight test model is needed to prove the M11 pipeline.

---

# 16. Non-negotiable success definition

The project is not considered visually successful merely because generated files:

- have legal dimensions;
- use legal colors;
- are deterministic;
- pass structural metrics;
- are non-duplicate.

A successful semantic candidate must also satisfy the product-level blind test:

> If metadata and filename are hidden, can a human reasonably identify the intended subject or scene from the pixel art itself?

That is the visual standard the previous 100-candidate pack failed and the new plan must solve.