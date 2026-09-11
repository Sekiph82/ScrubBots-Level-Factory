# ScrubBots Level Factory → Semantic Pixel Studio Conversion Plan V01

Status: OWNER-APPROVED DIRECTION / IMPLEMENTATION READY
Date: 2026-09-11

## 1. Product correction

M00-M10 proved that the repository can generate deterministic, reproducible, bounded, validated, exportable logical pixel grids. The M10 owner review rejected 100/100 owner-visible artworks because structural validity is not semantic recognizability.

The project is therefore **not restarted**. The accepted infrastructure is retained and converted into a PixelLab-like semantic pixel-art factory.

The corrected product goal is:

> Generate small, crisp, recognizable semantic pixel art from text and/or reference images, then run that artwork through the existing deterministic ScrubBots factory for normalization, palette legality, quality, provenance, reproduction, batch review, puzzle validation, and export.

A recognizable 16x16-style wizard proves that low logical resolution is not the problem. Semantic synthesis is the missing layer.

## 2. What remains unchanged

The following accepted M00-M10 infrastructure stays authoritative and must be reused rather than rewritten:

- canonical GenerationRequest / typed configuration discipline;
- deterministic seed derivation and retry streams;
- difficulty dimension bands and rectangular-board support;
- C01..C16 logical palette authority for LEVEL_ART;
- difficulty used-color bands for LEVEL_ART;
- existing MASK generator primitives and topology machinery;
- existing RULES composition machinery;
- WFC exemplar/replay infrastructure;
- HYBRID/AUTO routing infrastructure;
- M07 structural quality/diversity analysis;
- M08 JSON/PNG exact export, provenance, byte-level round trip;
- M09 CLI, exact reproduce, deterministic/resumable batch manifests;
- M10 property corpus, benchmark harness, review tooling, performance evidence;
- offline/local-first architecture;
- no runtime dependency from the ScrubBots mobile game onto this development tool.

## 3. What changes

The generator boundary is expanded so that procedural geometry is no longer the default owner-visible art source.

Old owner-visible flow:

```text
MASK / RULES / HYBRID
        ↓
logical grid
        ↓
quality/export
```

New flow:

```text
TEXT / REFERENCE / STYLE / INIT IMAGE
                ↓
        SEMANTIC ART PROVIDER
                ↓
      semantic pixel-art candidate
                ↓
  PIXEL NORMALIZATION / SEGMENTATION
                ↓
 existing MASK / RULES / WFC / HYBRID
   as control, mutation, region, puzzle,
   style/detail and fallback infrastructure
                ↓
 existing M07 QUALITY + new semantic gate
                ↓
 existing M08/M09/M10 factory pipeline
```

## 4. PixelLab parity target

The public PixelLab SDK exposes the product controls we will mirror conceptually:

- text description;
- negative description;
- image size;
- deterministic seed;
- transparent/no-background mode;
- outline style;
- shading style;
- detail level;
- camera/view preset;
- eight subject directions;
- isometric/oblique flags;
- coverage percentage;
- init image + strength;
- color/palette image;
- style/reference image + strength;
- inpainting image + mask;
- rotation/directional variants;
- text animation and skeleton-guided animation.

We are not copying PixelLab proprietary backend code. We are reproducing the product capability pattern around our own/open generation providers.

Reference repositories:

- https://github.com/pixellab-code/pixellab-python
- https://github.com/pixellab-code/pixellab-js
- https://github.com/pixellab-code/pixellab-mcp

## 5. Provider architecture

Introduce a provider-neutral semantic generation layer.

```text
SemanticGenerationRequest
        ↓
SemanticGeneratorProvider
        ├── LOCAL_COMFYUI
        ├── IMPORTED_EXTERNAL_RESULT
        └── future provider adapters
        ↓
SemanticImageCandidate
```

The Factory must never hard-code itself to one model or UI.

### 5.1 Local-first requirement

The default automation path must not require another paid subscription or paid image API.

The first automated provider target is a **local ComfyUI-compatible HTTP workflow**, because it is free/open and provides a programmable queue/API boundary. Model/workflow selection remains versioned configuration rather than application architecture.

ChatGPT, Claude Code and Magnific may assist the project, but the weekly generation pipeline must not depend on manually operating a paid website.

### 5.2 Provider contract

Every provider result must record:

- provider id/version;
- workflow/model identifiers and hashes where available;
- prompt and negative prompt;
- semantic subject/category;
- seed;
- requested and returned dimensions;
- reference/style/init/color-image provenance;
- generation parameters;
- raw provider image hash;
- timestamps only as non-deterministic audit metadata, never candidate identity;
- explicit network/local provenance;
- failure/retry reason.

## 6. Two output classes

The product must stop conflating LEVEL_ART with all game pixel art.

### 6.1 LEVEL_ART

Used as ScrubBots playable level artwork.

Hard legality remains:

- EASY: 20-29 cells per axis;
- MEDIUM: 30-39;
- HARD: 40-49;
- VERY_HARD: 50-59;
- rectangular allowed;
- one logical artwork pixel = one gameplay cell;
- C01..C16 only;
- difficulty distinct-used-color bands remain hard legality;
- solver/level validation applies;
- M08 LevelData export applies.

LEVEL_ART semantic generation should preferentially ask the upstream model to generate directly near the target logical dimensions rather than create 256x256 art and destroy it by arbitrary downscaling.

### 6.2 ASSET_ART

Standalone characters, enemies, objects, items, icons, decorations and animation frames.

ASSET_ART gets its own contract. Initial supported logical sizes should include at least:

- 16x16;
- 24x24;
- 32x32;
- 48x48;
- 64x64;
- configurable rectangular sizes.

ASSET_ART is not forced into LEVEL_ART difficulty color bands or LevelData solver legality. It can later support richer palette budgets, transparency, multiple directions and animation.

## 7. Semantic request model

Add a versioned SemanticGenerationRequest containing at least:

- output_class: LEVEL_ART | ASSET_ART;
- description;
- negative_description;
- semantic_category;
- width/height or difficulty-derived size;
- seed;
- no_background;
- outline;
- shading;
- detail;
- view;
- direction;
- isometric;
- coverage_percentage;
- reference_images[];
- style_image;
- style_strength;
- init_image;
- init_strength;
- color_reference/palette reference;
- desired candidate count;
- provider/workflow version.

All persisted forms must be canonical and schema-versioned.

## 8. Semantic candidate ingestion

Provider output must pass through a deterministic ingestion pipeline:

1. Decode source image without interpolation.
2. Preserve raw source bytes/hash as provenance.
3. Remove/validate transparency/background as requested.
4. Detect logical-pixel structure or convert using explicit deterministic nearest-neighbor / segmentation rules.
5. Crop/pad to the requested logical canvas without hidden resampling.
6. For LEVEL_ART, map colors deterministically to legal C01..C16 and enforce used-color bands.
7. For ASSET_ART, use the asset palette policy rather than LevelData bands.
8. Create immutable normalized logical grid.
9. Run structural quality analysis.
10. Run semantic recognizability gate.
11. For LEVEL_ART, run gameplay/puzzle validation when available.
12. Export with full raw-source + normalized-art provenance.

The original provider image must never be silently overwritten.

## 9. Recognizability becomes a first-class gate

M07 structural ACCEPT remains necessary but is no longer sufficient.

Add `SemanticQualityReport` with at least:

- intended semantic label/description;
- metadata-blind owner status;
- silhouette/readability metrics where deterministic metrics are useful;
- optional automated semantic scorer/evaluator as advisory evidence;
- explicit `PENDING_OWNER_REVIEW`, `OWNER_ACCEPT`, `OWNER_REJECT` state;
- rejection reason codes.

V1 production rule:

> A candidate cannot be promoted because structural metrics pass. Owner-visible semantic art must pass recognizability review.

The M10 rejected 100-pack becomes a permanent negative regression set.

## 10. Repurposing the existing engines

### MASK

Retain. New roles:

- silhouette extraction/reference masks;
- occupancy control;
- semantic candidate segmentation;
- controlled mutation;
- background/foreground geometry;
- puzzle-active-region constraints.

Do not use crude geometric templates as the primary semantic renderer.

### RULES

Retain. New roles:

- region/layout constraints;
- symmetry/composition constraints when desired;
- palette-region post-processing;
- negative-space and board-readability rules;
- puzzle geometry derived from semantic artwork.

### WFC

Retain and expand after approved exemplars exist:

- owner-approved style/detail propagation;
- texture/detail completion;
- local pattern transfer;
- tileset research.

Synthetic fixtures remain technical test data only.

### HYBRID

Retain. Add semantic-provider-aware compositions, e.g.:

```text
SEMANTIC_IMAGE -> MASK_OCCUPANCY -> RULE_REGION_CONTROL
SEMANTIC_IMAGE -> APPROVED_WFC_STYLE_DETAIL
SEMANTIC_IMAGE -> MASK -> PUZZLE_REGION_BUILDER
```

### AUTO

Retain as orchestration layer. It may choose provider/workflow/normalization strategy from explicit policy, but must preserve full provenance.

## 11. Local semantic provider implementation

### Stage A: ComfyUI bridge

Add a provider adapter that can:

- health-check a configured local ComfyUI endpoint;
- submit a versioned workflow JSON;
- inject prompt, negative prompt, seed, width/height and reference inputs;
- poll job state with bounded timeout;
- collect generated image(s);
- persist workflow/model hashes;
- fail closed if workflow/model identity differs from requested configuration;
- operate behind a provider interface so ComfyUI can later be replaced.

No browser scraping or UI automation is the architecture.

### Stage B: model qualification

Model/workflow selection is a measured product task. Candidate workflows must be tested at small pixel-art resolutions against a semantic benchmark set, including:

- wizard;
- dwarf/warrior;
- elf;
- robot;
- fish;
- sea creature;
- mushroom;
- ghost;
- rocket/space ship;
- tree;
- skull;
- potion;
- crab;
- alien;
- simple building/object.

The model is accepted only if metadata-blind recognizability materially exceeds the rejected procedural baseline.

## 12. Reference/style generation

PixelLab-like reference workflows are required after text generation works.

Support:

- 1-N reference images;
- separate style reference;
- palette/color reference;
- init image strength;
- style strength;
- owner-approved style collections;
- deterministic provenance for every input image.

Use cases:

- generate a new character matching an approved ScrubBots style;
- create multiple objects in one visual language;
- regenerate a level at another difficulty while preserving subject identity;
- turn owner art into legal LEVEL_ART without losing the source.

## 13. Editing/inpainting

Add a semantic edit workflow rather than regenerating an entire candidate.

Required actions:

- mask-based inpaint;
- replace/repair selected region;
- erase/background cleanup;
- recolor/palette remap;
- expand/crop/pad canvas;
- re-run normalization and all downstream validation;
- retain parent-child lineage.

## 14. Variants, directions and animation

After static semantic generation is accepted:

### Variants

- same prompt, deterministic seed series;
- same subject, alternative palette/style;
- same subject, difficulty-size variants;
- owner-approved mutation families.

### Direction/rotation

For ASSET_ART:

- N, NE, E, SE, S, SW, W, NW;
- front/side/top-down presets as useful;
- identity-preservation review.

### Animation

Later milestone:

- text action generation;
- skeleton/pose-guided frames;
- consistent palette/identity across frames;
- sprite-sheet export.

Animation is not required to repair LEVEL_ART V1.

## 15. Pixel Studio UI

The current CLI/batch core remains authoritative. Add a local Studio UI later, modeled on the useful product concepts of PixelLab rather than copying its proprietary implementation.

Primary Create panel:

- Description;
- Negative prompt;
- output class;
- difficulty or custom size;
- transparent background;
- reference images;
- style image;
- palette/color reference;
- seed;
- number of generations;
- outline;
- shading;
- detail;
- view;
- direction;
- Generate button.

Gallery:

- generated candidates;
- provider/source metadata;
- normalized preview;
- recognizability status;
- structural quality;
- accept/reject;
- edit/inpaint;
- reproduce;
- export.

The UI is not the source of truth. Versioned requests/manifests remain canonical.

## 16. Weekly automated production

Target owner workflow:

```text
weekly semantic job specification
          ↓
local semantic provider batch
          ↓
normalization + palette contract
          ↓
structural QA + semantic prefilter
          ↓
duplicate/diversity filtering
          ↓
LEVEL_ART puzzle/solver validation
          ↓
owner HTML/Studio review
          ↓
ACCEPT / REJECT
          ↓
existing M08/M09 export/handoff
```

The owner should not need to manually type 100 prompts into ChatGPT.

## 17. Revised milestone roadmap

Existing M00-M10 accepted technical work remains historical foundation. M10 owner visual release is rejected and the release train pivots here.

### SP00 — Owner rejection + semantic pivot record

- Record 100/100 rejected pack.
- Freeze rejected grids as negative evidence.
- Publish this conversion plan.

### SP01 — Semantic contracts & provider boundary

- `SemanticGenerationRequest` schema;
- `SemanticImageCandidate` schema;
- provider interface;
- canonical provider provenance;
- LEVEL_ART vs ASSET_ART separation;
- no provider implementation coupled into core.

### SP02 — Local ComfyUI provider

- endpoint configuration;
- health check;
- workflow submission;
- deterministic parameter injection;
- bounded polling;
- output collection;
- workflow/model identity recording;
- mocked integration tests;
- real local smoke test when environment is available.

### SP03 — Semantic normalization pipeline

- raw image preservation;
- transparency/background handling;
- logical grid extraction;
- deterministic crop/pad/nearest-neighbor rules;
- LEVEL_ART palette mapping;
- ASSET_ART pipeline;
- provenance.

### SP04 — Model/workflow qualification

- semantic benchmark dataset;
- multiple local workflow/model candidates;
- small-resolution testing including ~16x16/20-59 targets;
- metadata-blind recognizability review;
- select default workflow only after evidence.

### SP05 — LEVEL_ART semantic integration

- semantic provider becomes owner-visible source;
- existing MASK/RULES/HYBRID become post/control/puzzle layers;
- maintain all LevelData contracts;
- preserve exact export/reproduce.

### SP06 — Semantic quality gate

- `SemanticQualityReport`;
- owner review state;
- rejected-pack regression;
- optional advisory automated evaluator;
- structural ACCEPT cannot auto-promote semantic artwork.

### SP07 — Reference/style generation

- reference images;
- style image;
- palette image;
- init image + strength;
- style strength;
- owner-approved style library.

### SP08 — Edit/inpaint

- mask edit;
- region replace;
- recolor;
- lineage/revalidation.

### SP09 — Pixel Studio Create/Gallery UI

- local application/web UI;
- PixelLab-like create controls;
- review gallery;
- reproduce/edit/export;
- backed entirely by canonical request files.

### SP10 — Automated weekly semantic batch

- requested counts;
- local provider batching;
- resume/retry;
- duplicate filtering;
- review queue;
- exact handoff.

### SP11 — ASSET_ART production

- 16/24/32/48/64 and rectangular assets;
- characters/enemies/items/objects/icons;
- transparent background;
- richer asset palette policy;
- export contract separated from LevelData.

### SP12 — Direction/rotation variants

- eight-direction character/object variants;
- identity preservation;
- sprite-set export.

### SP13 — Animation

- text/skeleton animation provider interface;
- frame consistency;
- sprite sheets;
- game asset export.

### SP14 — ScrubBots Level Factory bridge

Consume the original `Sekiph82/Scrubbots` Level Factory plan rather than duplicating it. Semantic LEVEL_ART output becomes the visual/art input to the future solver/difficulty/human-editor/content-pipeline work defined under `SB-LF00..SB-LF10`.

References:

- https://github.com/Sekiph82/Scrubbots/blob/main/TASKS.md
- https://github.com/Sekiph82/Scrubbots/blob/main/level_factory/docs/00_VISION_AND_SCOPE.md
- https://github.com/Sekiph82/Scrubbots/blob/main/level_factory/docs/01_ARCHITECTURE.md

## 18. Acceptance standard for the next visual milestone

A replacement owner review pack may not be generated from the old procedural primary-art path.

The next visual acceptance set must:

- be generated through the semantic provider path;
- include labels hidden during owner recognizability review;
- include representative concrete subjects;
- preserve requested logical resolution;
- prove zero unintended interpolation;
- satisfy LEVEL_ART palette/dimension contracts where applicable;
- include exact provider/workflow/seed provenance;
- demonstrate material recognizability improvement over the rejected M10 pack.

## 19. Non-goals

- Do not clone/scrape proprietary PixelLab backend code.
- Do not automate PixelLab website UI as the core architecture.
- Do not discard M00-M10 infrastructure.
- Do not silently relax LevelData contracts to make AI output pass.
- Do not treat generated 256x256 images simply downscaled to 20x20 as automatically acceptable.
- Do not make the mobile game depend on ComfyUI or any development-time generator.
- Do not promote semantic artwork without owner acceptance.

## 20. First implementation step

Start with **SP01 Semantic Contracts & Provider Boundary**.

No real model should be wired into core until the provider interface, request schema, result schema, provenance contract, output-class separation, and tests exist.

The first code cycle must therefore add the semantic boundary without rewriting accepted generators or export systems.
