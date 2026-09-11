# ScrubBots Level Factory — PixelLab-Like Transformation Plan

Status: OWNER-DIRECTED PRODUCT PIVOT PLAN  
Date: 2026-09-11

## 1. Non-negotiable direction

This is **not a from-scratch rebuild**.

M00-M10 produced valuable deterministic production infrastructure. The failure is concentrated in the current primary visual-synthesis core: MASK/RULES/HYBRID can satisfy structural contracts but do not reliably create semantically recognizable pixel-art subjects.

The transformation therefore follows one rule:

> **Keep the factory. Replace/demote the painter.**

The existing deterministic contracts, seeds, batch orchestration, provenance, palette enforcement, structural quality, export, reproduction, benchmark and owner-review systems remain and are wrapped around a new semantic AI pixel-art synthesis backend.

## 2. Owner M10 decision

The entire current 100-image M10 review pack is owner-rejected.

Machine-readable decision:
`review/m10/M10_OWNER_REVIEW_DECISION.json`

Human-readable decision:
`review/m10/M10_OWNER_REVIEW_DECISION.md`

M11 remains blocked until a replacement semantic visual pack receives owner acceptance.

## 3. What stays exactly because it is useful

### Keep M01
- difficulty dimension bands;
- rectangular-board support;
- C01..C16 canonical palette;
- BG01 presentation-only rule;
- difficulty used-color bands.

### Keep M02
- typed GenerationRequest concepts;
- deterministic seeds/sub-seeds;
- canonical serialization/digests;
- reproducibility/provenance framework.

### Keep M03/M04, but change their role
MASK and RULES stop being the default final-image painters.

They remain useful as:
- optional silhouette/layout/control-map generators;
- composition constraints;
- masks for inpainting;
- deterministic subject-placement guides;
- fallback/debug generators;
- synthetic test fixtures.

They are no longer evidence that an image is semantically recognizable.

### Keep M05 WFC, but change its role
WFC remains useful for:
- local texture/style propagation from approved art;
- background/detail variation;
- controlled local pattern synthesis.

It is not the primary semantic subject generator.

### Keep M06 router/hybrid infrastructure
The router becomes the insertion point for a new `AI_PIXEL` / semantic backend.

Legacy MASK/RULES/WFC/HYBRID paths stay available but are not the default visual product path.

### Keep M07
M07 remains the second-stage **structural** quality gate.

A new semantic-recognizability gate will be added before owner acceptance. Structural ACCEPT must never again be displayed as equivalent to artistic/semantic ACCEPT.

### Keep M08
Reuse:
- artwork JSON;
- PNG export;
- exact dimensions;
- palette records;
- provenance binding;
- deterministic file naming;
- bundle integrity.

Extend metadata with model/checkpoint hashes, inference parameters, prompt/reference hashes and semantic scores.

### Keep M09
Reuse:
- single generate CLI;
- reproduce;
- deterministic batch IDs;
- resumable batch manifests;
- duplicate detection;
- atomic output handling.

The AI backend becomes another generator used by the same orchestration.

### Keep M10 infrastructure
Reuse:
- benchmark harness;
- review-pack builder;
- HTML review UI;
- metrics/rejection ledgers;
- release-gate concept.

Replace the rejected image population with AI-generated semantic candidates.

## 4. PixelLab functionality we are targeting

The local product should provide a PixelLab-Create-like workflow, independently implemented:

- text description;
- model/backend selector;
- exact/custom output size;
- optional reference images;
- optional style image;
- remove-background option;
- seed;
- forced ScrubBots palette option;
- generation count, including batch generation;
- center preview;
- right-side gallery/history;
- download/export;
- regenerate/variation;
- edit/inpaint later;
- local project gallery.

The UI may be visually inspired by the workflow but must be our own implementation. Do not scrape or copy PixelLab's proprietary frontend/backend source.

## 5. Primary free semantic model candidate

### Pixel Party XL

Primary first benchmark:
`pixelparty/pixel-party-xl`

Why it is first:
- released publicly by the PixelLab team/community;
- SDXL-based;
- specifically trained for pixel-art adherence;
- local Diffusers instructions are published;
- model card permits use in projects while asking users not to host the model;
- model card recommends nearest-neighbor reduction and says init images are useful.

Model weights are NEVER committed to this repository. They live in a local model cache and are identified in provenance by model ID, revision and file hashes.

### Secondary local backends

Only if Pixel Party XL does not meet quality/performance on the owner's hardware:
- a lighter local Stable Diffusion pixel-art checkpoint/LoRA with acceptable licensing;
- an SDXL pixel-art LoRA;
- a ComfyUI-backed local workflow using the same approved weights.

No new paid cloud service becomes mandatory.

## 6. Hardware capability gate

Before changing the generator, collect the owner's actual current laptop capability:
- CPU;
- system RAM;
- GPU model;
- dedicated VRAM;
- CUDA/DirectML availability;
- free disk space.

Then run a tiny isolated Pixel Party XL proof on the machine.

Outcomes:

A. GPU can run it acceptably: use local Diffusers backend directly.

B. GPU can run only with memory optimizations: use attention slicing/model CPU offload or a local ComfyUI low-VRAM workflow.

C. Hardware cannot run Pixel Party XL at a useful speed: benchmark one lighter free backend before any decision about paid services or hardware. Do not silently substitute low-quality generation.

## 7. New generator mode, without breaking old modes

Add a new mode, conceptually:

`AI_PIXEL`

Do not delete MASK/RULES/WFC/HYBRID.

New flow:

```text
GenerationRequest v2
    |
    +-- prompt / negative prompt
    +-- difficulty / logical dimensions
    +-- seed
    +-- optional reference image(s)
    +-- optional style image
    +-- optional MASK/RULES control layout
    +-- palette policy
    v
Semantic Prompt Compiler
    v
Local AI Pixel Backend
    v
Raw semantic pixel-art candidate
    v
Logical lattice extraction / background handling
    v
C01..C16 deterministic palette mapping
    v
Semantic recognizability gate
    v
Existing M07 structural gate
    v
Existing M08 bundle/export
    v
Existing M09 batch/reproduce
    v
Existing M10 review system
```

## 8. GenerationRequest v2 extension

Keep backward compatibility with v1.

Add fields such as:
- `description`;
- `negative_prompt`;
- `semantic_subject_class` optional;
- `model_backend`;
- `model_revision`;
- `reference_images[]` by local content hash;
- `style_image` by local content hash;
- `remove_background`;
- `source_scale` / lattice policy;
- `semantic_quality_threshold`;
- `control_layout` optional;
- inference steps/guidance where backend supports them.

Every field affecting pixels must be part of reproducibility/provenance identity.

## 9. Prompt compiler

The owner may type something short such as:

`cute wizard character`

The local prompt compiler expands it deterministically into an image-generation instruction emphasizing:
- one clear subject;
- centered readable silhouette;
- full subject visible;
- no text/logo;
- no duplicate subjects;
- hard pixel edges;
- flat pixel-art color regions;
- strong pose/readability;
- requested view where relevant.

The compiler is deterministic and local. It does not require ChatGPT/Claude at generation time.

ChatGPT or Claude may help author prompt templates during development but are not runtime dependencies.

## 10. Exact game-grid transformation

The old V1 rule forbade taking arbitrary conventional artwork and blindly pixelating it. That remains a good safety principle, but a PixelLab-like AI backend needs an explicitly owner-approved semantic-source stage.

The new rule should be:

> An AI source image may be generated only as an intermediate semantic artifact. The gameplay artifact remains an exact logical grid with one logical pixel per gameplay cell, produced by a versioned deterministic lattice-extraction/palette pipeline whose parameters and source hash are recorded.

For Pixel Party XL specifically, first test the model-card-recommended nearest-neighbor pixel lattice. Prefer exact integer lattice extraction rather than arbitrary interpolated resize.

No bilinear/bicubic interpolation is allowed in final logical-art conversion.

The source image is stored as evidence, not confused with the final gameplay PNG.

## 11. Palette conversion

Reuse the current C01..C16 contract.

New stage:
1. identify/remove background if requested;
2. derive the legal difficulty color count;
3. choose the best subset of C01..C16 deterministically;
4. map generated color regions to that subset;
5. no dithering by default because dithering can destroy sprite readability;
6. verify actual used-color count;
7. reject rather than patch pathological results.

The unquantized source is retained for audit so quality loss can be diagnosed.

## 12. Semantic recognizability gate

This is the missing layer in V1.

Add `M07-Semantic` or a new milestone quality stage before structural acceptance.

Automated local signals:
- prompt/image embedding similarity using a free local vision-language encoder;
- intended-subject similarity against negative/competing subject labels;
- foreground occupancy and centered-subject checks;
- connected readable silhouette heuristics;
- duplicate/multiple-subject detection where feasible;
- background contamination checks.

Keep M07 structural metrics separately.

New statuses must distinguish:
- `SEMANTIC_REJECT`;
- `STRUCTURAL_REJECT`;
- `ACCEPTED_FOR_REVIEW`;
- `OWNER_ACCEPTED`.

Never label a merely structural pass as artistic ACCEPT again.

## 13. Existing procedural engines become controls

Examples:

### MASK as control
A ROBOT mask can tell the AI where the main body should exist, but the AI supplies semantic visual detail.

### RULES as composition control
CENTRAL_SUBJECT can enforce placement/negative space while AI produces an actual character/object.

### WFC as detail/style
Once owner-approved ScrubBots exemplars exist, WFC can add local pattern language without inventing the subject identity.

### HYBRID becomes AI-aware
New hybrid examples:
- MASK_CONTROL -> AI_PIXEL -> PALETTE;
- AI_PIXEL -> WFC_DETAIL -> PALETTE;
- RULE_LAYOUT -> AI_PIXEL -> SEMANTIC_GATE;
- AI_PIXEL -> deterministic cleanup -> M07.

Existing hybrid code/provenance patterns are reused instead of discarded.

## 14. PixelLab-like local web UI

Add a thin local web application on top of the current Python factory.

Do not move generation logic into the browser.

### Left rail
- Create
- Edit
- Inpaint later
- Gallery
- Batch
- Settings

### Create panel
- backend/model selector;
- description;
- negative prompt under Advanced;
- output logical size / difficulty;
- reference images up to a bounded count;
- style image;
- remove background;
- force ScrubBots palette;
- seed/randomize seed;
- number of generations: 1 / 4 / 20 / custom;
- Generate.

### Center
- selected generated image;
- zoom with nearest-neighbor rendering;
- logical grid overlay;
- before/after source vs final logical grid;
- semantic/structural score summary.

### Right gallery
- generated candidates;
- selected/rejected status;
- regenerate/variation;
- export;
- open in editor.

The web app calls the SAME Python application service used by the M09 CLI, so CLI and UI cannot drift into separate generators.

## 15. Editor functionality

Do not clone the entire PixelLab editor in the first cycle.

Use Piskel/Pixelorama as licensed implementation references for pixel-editor interactions.

First editing set:
- pencil;
- eraser;
- eyedropper;
- fill;
- C01..C16 palette;
- zoom/grid;
- undo/redo;
- selection/move;
- transparent/background toggle;
- export.

Later:
- layers;
- animation timeline;
- onion skin;
- rotation/views;
- AI inpaint.

The current logical-grid JSON is the editor's canonical document, so manual corrections remain compatible with M08/M09 provenance.

## 16. Role of the repositories supplied by the owner

### `pixellab-code/pixellab-python`
Use as an API/interface behavior reference only. It is an SDK for PixelLab's hosted API, not the source of their proprietary generation backend.

### `pixelparty/pixel-party-xl`
Primary free local model candidate from the PixelLab ecosystem.

### `Orama-Interactive/Pixelorama`
Use as an MIT-licensed editor UX/algorithm reference: palettes, grids, pixel-specific transforms, layers, animation concepts.

### `piskelapp/piskel`
Use as an Apache-2.0 browser sprite-editor implementation reference, especially browser canvas/editor workflows.

### `giventofly/pixelit`
Use only where its image-to-pixel/palette conversion ideas are better than our existing deterministic conversion. Our current palette/export contracts remain authoritative.

### `twilio-labs/open-pixel-art`
Do not use as a generation engine. It is an educational collaborative one-pixel art project, not a semantic image generator.

## 17. Zero-additional-service-cost policy

Runtime production target:
- local open-source image model;
- local Python inference;
- local web UI;
- no PixelLab API bill;
- no OpenAI API requirement;
- no Magnific requirement;
- no Claude requirement at runtime.

Existing paid subscriptions may be used during development/review:
- ChatGPT: planning, audit, occasional human-driven comparison/reference generation;
- Claude Code: implementation agent;
- Magnific: optional visual experiment only, never a required weekly production dependency.

If local hardware cannot meet the quality/speed target, the system must report that fact explicitly. It may not hide a paid cloud dependency behind the UI.

## 18. New blind visual acceptance methodology

The next 100-image pack must NOT reveal the intended label before visual judgment.

For each candidate:
1. show only the image;
2. owner decides whether a clear subject is visible;
3. optionally enter what the subject appears to be;
4. reveal intended prompt/category only after the judgment;
5. record semantic hit/miss;
6. separately record artistic approval.

This prevents metadata from unconsciously teaching the reviewer what a vague shape is supposed to represent.

Release must require explicit owner acceptance. Machine semantic scores cannot override an owner rejection.

## 19. Transformation milestones

### T00 — Preserve and pivot
- record 100/100 owner rejection;
- freeze current review pack as failed baseline;
- version the new owner scope;
- do not delete accepted M00-M10 infrastructure.

### T01 — Hardware + Pixel Party XL proof
- inspect actual hardware;
- one-time download/cache model;
- generate a small fixed prompt set locally;
- measure speed/RAM/VRAM;
- compare recognizable output before integrating anything.

**Stop gate:** if model quality is not clearly superior to current procedural output, do not integrate it.

### T02 — AI backend adapter
- `AI_PIXEL` interface;
- model cache/provenance;
- deterministic seed handling;
- source artifact storage;
- failure handling;
- optional low-VRAM path.

### T03 — Game-grid compiler
- exact logical-size transform;
- background handling;
- C01..C16 mapping;
- difficulty color-band enforcement;
- source-to-final evidence;
- deterministic reproduce.

### T04 — Semantic quality
- local prompt/image similarity;
- subject readability heuristics;
- structural M07 chaining;
- ranking/rejection reasons.

### T05 — Existing M09 batch integration
- AI single generate;
- AI reproduce;
- AI batch;
- resume;
- dedupe;
- oversample/rank until requested accepted count or bounded exhaustion.

### T06 — PixelLab-like local Create UI
- description;
- sizes;
- model;
- references/style;
- remove background;
- gallery;
- generate 1/4/20;
- source/final comparison;
- export.

### T07 — Reference/style conditioning
- init-image support first;
- then style/reference adapter if hardware permits;
- deterministic content hashes and provenance.

### T08 — Local pixel editor
- minimal browser editor over logical-grid JSON;
- palette/grid/tools/undo;
- later layers/animation.

### T09 — New blind 100-pack
- generate 100 semantic candidates;
- hide labels during owner judgment;
- record semantic recognizability and artistic approval;
- only then reopen M11.

## 20. First implementation cycle

Do NOT start by building the full web UI.

The first cycle should prove the one thing the old system failed to prove:

> Can the owner's actual machine, using a free local model, generate recognizable pixel-art subjects at useful quality?

First cycle deliverables:
1. hardware report;
2. local Pixel Party XL setup outside Git-tracked model weights;
3. fixed 12-prompt proof set across character/object/creature/prop categories;
4. raw source outputs;
5. initial logical-grid conversions;
6. runtime/VRAM/RAM report;
7. side-by-side HTML review page;
8. NO change to production AUTO default yet;
9. independent audit and owner review.

Only after this proof passes do we wire AI generation into the existing M09 batch pipeline and build the PixelLab-like UI.
