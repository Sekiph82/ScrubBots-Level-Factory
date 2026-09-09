# SCRUBBOTS LEVEL FACTORY — PIXEL ART GENERATOR V1 TASK PLAN

> Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory  
> Scope: **Offline procedural pixel-art generation engine only**  
> Target user: SCRUBBOTS development tooling on the owner's Windows laptop  
> Status: Active implementation under H!veAI governance  
> Primary implementation agent: Codex  
> Independent auditor / tracker owner: ChatGPT  
> Canonical local repository root: `C:\\Users\\sekip\\Desktop\\Scrubbots - Pixel Art Generator`  
> Source-of-truth game repository: https://github.com/Sekiph82/Scrubbots

---

## 0. PURPOSE

This repository exists to build and prove the **SCRUBBOTS Procedural Pixel Art Generator V1** before the generator is integrated back into the main SCRUBBOTS Level Factory.

This V1 is **not** the complete Level Factory.

V1 does only this:

```text
difficulty + seed + optional style/theme + optional dimensions
                         |
                         v
                 dimension resolver
                         |
                         v
                 generator router
              /          |          \
             /           |           \
      MASK/SPRITE        WFC      RULE/SHAPE
             \           |           /
              \          |          /
                         v
                 logical color grid
                         |
                         v
             SCRUBBOTS art constraints
                         |
                         v
                 quality validation
                  /             \
              reject           accept
                                |
                                v
              PNG + logical-grid JSON + metadata
```

No cloud service, API key, online image-generation model or runtime network access is allowed.

The generator must work **entirely offline on the owner's laptop**.

---

# 1. OWNER-LOCKED SCRUBBOTS CONTRACT

These rules come from the main SCRUBBOTS repository and must not be silently changed in this repository.

## Board-size legality

Width and height are validated independently. Rectangular boards are allowed.

| Difficulty | Width | Height | Maximum cells |
| --- | ---: | ---: | ---: |
| EASY | 20–29 | 20–29 | 841 |
| MEDIUM | 30–39 | 30–39 | 1,521 |
| HARD | 40–49 | 40–49 | 2,401 |
| VERY_HARD | 50–59 | 50–59 | 3,481 |

Examples:

- EASY: 20×27
- MEDIUM: 37×34
- HARD: 48×41
- VERY_HARD: 53×59

Legacy 16×16, 18×18, fixed 40×40, Extra Hard and 2,500-cell assumptions are forbidden.

## Logical-pixel rule

**One generated logical pixel = one SCRUBBOTS gameplay cell.**

The engine must never generate a large conventional image and then arbitrarily resize/pixelate it into a board.

The requested logical board dimensions are the artwork dimensions.

Example:

```text
difficulty = MEDIUM
width      = 37
height     = 34

generated artwork = 37 logical pixels × 34 logical pixels
gameplay cells     = 1,258
```

## Canonical logical palette

Production logical artwork may use only the canonical C01..C16 palette:

| ID | HEX |
| --- | --- |
| C01 | #E94B4B |
| C02 | #F28C3C |
| C03 | #F2C94C |
| C04 | #55B85A |
| C05 | #63D6A3 |
| C06 | #42C7D9 |
| C07 | #3E7EDB |
| C08 | #3451A3 |
| C09 | #845EC2 |
| C10 | #E66FA5 |
| C11 | #956447 |
| C12 | #E8CFA0 |
| C13 | #B8C2CC |
| C14 | #3D4652 |
| C15 | #FFFFFF |
| C16 | #000000 |

No C17+ and no off-palette logical RGB are permitted.

## Difficulty color-count legality

Count only distinct canonical logical colors actually used by artwork cells.

| Difficulty | Required distinct used colors |
| --- | ---: |
| EASY | 3–5 |
| MEDIUM | 6–7 |
| HARD | 8–9 |
| VERY_HARD | 10–12 |

## Background

BG01 Midnight Slate = `#202533`.

BG01 is presentation/background only.

It is:

- not C01..C16,
- not a logical artwork color,
- never stored as a logical cell color,
- never counted toward difficulty colors.

## Render restrictions

Every logical cell must render as one flat solid canonical color.

Forbidden:

- antialiasing,
- interpolation,
- gradients inside cells,
- gloss,
- highlights,
- bevel,
- drop shadows,
- 3D bulges,
- bead/plastic effects.

A preview may draw presentation-only grid separation, but those lines are not logical artwork colors.

---

# 2. SOURCE PROJECT DECISION

The V1 engine may **study, adapt or port small algorithmic components** from the following projects, subject to license compliance and attribution.

## A. WFC reference and implementation

### Primary Python implementation reference

https://github.com/ikarth/wfc_2019f

Role:

- overlapping-pattern Wave Function Collapse,
- arbitrary output width/height,
- pattern-size control,
- rotations/reflections,
- retries,
- optional backtracking,
- local image-array input,
- fully offline execution.

License: MIT.

### Algorithm authority/reference

https://github.com/mxgmn/WaveFunctionCollapse

Role:

- reference WFC behavior,
- pattern extraction,
- observation/propagation model,
- contradiction semantics.

License: MIT for software. Bundled example images are not automatically reusable assets.

## B. Rule/shape generation reference

https://github.com/mxgmn/MarkovJunior

Role:

Study and reimplement only the 2D procedural ideas useful to SCRUBBOTS, such as:

- random growth,
- connected growth,
- self-avoiding walks,
- islands,
- rings,
- corridors,
- branching,
- region growth,
- Voronoi-like partitioning,
- rewrite-rule concepts.

Do **not** embed MarkovJunior as a required C# runtime in V1 unless a later explicit task changes the architecture.

License: MIT.

## C. Mask/sprite generation reference

https://github.com/zfedoran/pixel-sprite-generator

Role:

Study/reimplement:

- 2D masks,
- random mask mutation,
- horizontal/vertical symmetry,
- silhouette generation,
- recognizable object templates.

License: MIT.

## D. Optional references only

- https://github.com/KilledByAPixel/ZzSprite
- https://github.com/AliasFactory/Godot_Fast_WFC
- https://github.com/kchapelier/wavefunctioncollapse

These are reference material unless a later task explicitly promotes them.

## Projects explicitly NOT used as the generation core

- Pixelorama: editor, not procedural generation core.
- Piskel: editor, not procedural generation core.
- Pixel It: image-to-pixel converter, not original content generator.
- Twilio open-pixel-art: collaborative canvas project, not a generator.
- PixelLab Python SDK: online API client, violates offline-only V1 requirement.

---

# 3. V1 TECHNICAL ARCHITECTURE

## Language

**Python** is the V1 generator language.

Target:

- Python 3.12+ where dependencies permit.
- Windows-first.
- No GPU requirement.
- No network requirement after dependencies/source are installed.

## Planned package layout

```text
ScrubBots-Level-Factory/
  tasks.md
  README.md
  LICENSES/
  THIRD_PARTY_NOTICES.md
  pyproject.toml

  src/
    scrubbots_pixel_factory/
      __init__.py

      contracts/
        palette.py
        difficulty.py
        generation_request.py
        generation_result.py

      random/
        deterministic_rng.py

      generators/
        base.py
        router.py

        mask/
          generator.py
          templates.py
          mutation.py
          symmetry.py

        wfc/
          generator.py
          pattern_source.py
          adapter.py

        rules/
          generator.py
          primitives.py
          growth.py
          composition.py

        hybrid/
          generator.py

      constraints/
        palette_guard.py
        dimension_guard.py
        color_count_guard.py
        logical_grid_guard.py

      quality/
        occupancy.py
        connectivity.py
        fragmentation.py
        edge_balance.py
        symmetry.py
        recognizability_proxy.py
        duplicate.py
        scorer.py

      output/
        logical_grid.py
        png_writer.py
        metadata_writer.py
        manifest_writer.py

      cli/
        main.py

  data/
    palette/
      scrubbots_palette_v2.json

    templates/
      masks/

    exemplars/
      README.md

  output/
    .gitkeep

  tests/
    unit/
    property/
    golden/
    integration/
    performance/
```

Exact file names may change during implementation if Codex documents the reason, but layer boundaries must remain.

---

# 4. GLOBAL DEFINITION OF DONE

H!veAI task-state legend: `[x]` validated complete, `[~]` active/in progress, `[ ]` planned/pending, `[!]` blocked.

Only ChatGPT, acting as the independent auditor/tracker owner, may change task completion state or milestone/sprint closure state. Codex builder logs are claims/evidence and never final acceptance.


A task may be marked `[x]` only when relevant evidence exists.

Minimum completion rules:

- implementation exists,
- tests exist,
- tests pass,
- deterministic behavior is verified where applicable,
- invalid inputs are tested,
- no network dependency is introduced,
- output obeys SCRUBBOTS palette/dimension rules,
- same seed/config reproducibility is proven where applicable,
- rectangular dimensions are tested,
- 59×59 workload is exercised where cost scales with cells,
- docs match implementation,
- third-party license/attribution requirements are preserved,
- generated/cached output does not pollute source control,
- a focused commit exists.

---

# 5. MILESTONE OVERVIEW

- [x] **PAG-M00 — Repository Bootstrap & Governance**
- [x] **PAG-M01 — Canonical SCRUBBOTS Contracts**
- [x] **PAG-M02 — Deterministic Generation Core**
- [x] **PAG-M03 — Mask / Sprite Generator**
- [~] **PAG-M04 — Procedural Shape / Rule Generator**
- [ ] **PAG-M05 — Wave Function Collapse Generator**
- [ ] **PAG-M06 — Hybrid Generator Router**
- [ ] **PAG-M07 — Artwork Quality & Diversity Filters**
- [ ] **PAG-M08 — Output / Export Contract**
- [ ] **PAG-M09 — CLI & Local Batch Generation**
- [ ] **PAG-M10 — Validation, Performance & V1 Acceptance**
- [ ] **PAG-M11 — Godot/Main-Level-Factory Handoff Gate**

---

# PAG-M00 — Repository Bootstrap & Governance

M00 final state: `PASS / CLOSED`  
Closing cycle: `PAG-M00-C003 — Bootstrap Reliability & Offline Enforcement Remediation`  
Closing audit: `.hiveai/audits/PAG-M00-C003_BOOTSTRAP_RELIABILITY_AND_OFFLINE_ENFORCEMENT_REMEDIATION_STRICT_AUDIT.md`  
Previous C002 verdict: `FAIL / REMEDIATED`  
Recovery `RECOVERY-R001`: `AUDIT_PASSED / CLOSED`

## Sprint PAG-S00.1 — Project bootstrap

- [x] PAG-0001 Create Python package structure under `src/scrubbots_pixel_factory/`.
- [x] PAG-0002 Add `pyproject.toml` with pinned/minimum supported Python and dependencies.
- [x] PAG-0003 Add a Windows-friendly local setup command.
- [x] PAG-0004 Add a local test command.
- [x] PAG-0005 Add `.gitignore` entries for virtualenv, Python caches, generated PNG/JSON, logs and temporary WFC caches.
- [x] PAG-0006 Add `output/.gitkeep` while ignoring generated output contents.
- [x] PAG-0007 Add a minimal README explaining this repository is Pixel Art Generator V1 only.
- [x] PAG-0008 Add an explicit OFFLINE_ONLY policy.
- [x] PAG-0009 Add a rule that runtime HTTP/API calls are forbidden.
- [x] PAG-0010 Add a test that fails if a production generation path attempts network access.

## Sprint PAG-S00.2 — Third-party provenance

- [x] PAG-0011 Create `THIRD_PARTY_NOTICES.md`.
- [x] PAG-0012 Record `ikarth/wfc_2019f` source URL, license and exact commit/tag used for study/adaptation.
- [x] PAG-0013 Record `mxgmn/WaveFunctionCollapse` source URL, license and exact commit/tag.
- [x] PAG-0014 Record `mxgmn/MarkovJunior` source URL, license and exact commit/tag.
- [x] PAG-0015 Record `zfedoran/pixel-sprite-generator` source URL, license and exact commit/tag.
- [x] PAG-0016 Preserve required MIT notices for any copied/substantially adapted code.
- [x] PAG-0017 Do not copy example artwork/assets unless their asset license is independently verified.
- [x] PAG-0018 Add provenance comments to substantial adapted source modules.
- [x] PAG-0019 Document which algorithms were reimplemented from concepts versus copied/adapted code.

### M00 acceptance

- [x] PAG-0020 Clean checkout installs locally.
- [x] PAG-0021 Tests run locally without requiring Scrubbots main repo.
- [x] PAG-0022 Generator package imports without network access.

---

# PAG-M01 — Canonical SCRUBBOTS Contracts

M01 final state: `PASS / CLOSED`  
Closing cycle: `PAG-M01-C001 — Canonical SCRUBBOTS Contracts`  
Closing audit: `.hiveai/audits/PAG-M01-C001_CANONICAL_SCRUBBOTS_CONTRACTS_STRICT_AUDIT.md`

## Sprint PAG-S01.1 — Palette authority

- [x] PAG-0101 Add machine-readable C01..C16 palette data copied from the owner-locked main-game contract.
- [x] PAG-0102 Include palette schema/version metadata.
- [x] PAG-0103 Implement canonical palette loader.
- [x] PAG-0104 Reject duplicate color IDs.
- [x] PAG-0105 Reject duplicate RGB values if they would make ID mapping ambiguous.
- [x] PAG-0106 Reject C17+ logical colors.
- [x] PAG-0107 Reject BG01 as a logical artwork color.
- [x] PAG-0108 Expose deterministic C-ID ↔ RGB lookup.
- [x] PAG-0109 Keep local output palette ordered by ascending canonical C-ID.
- [x] PAG-0110 Test all 16 exact HEX/RGB values.

## Sprint PAG-S01.2 — Difficulty/dimensions

- [x] PAG-0111 Implement canonical difficulty enum: EASY, MEDIUM, HARD, VERY_HARD.
- [x] PAG-0112 Implement dimension bands: 20–29, 30–39, 40–49, 50–59.
- [x] PAG-0113 Validate width independently.
- [x] PAG-0114 Validate height independently.
- [x] PAG-0115 Explicitly support rectangular boards.
- [x] PAG-0116 Reject legacy Extra Hard.
- [x] PAG-0117 Reject legacy fixed-size assumptions.
- [x] PAG-0118 Implement automatic random dimension selection inside a requested difficulty band.
- [x] PAG-0119 Ensure automatic selection can generate both square and rectangular dimensions.
- [x] PAG-0120 Test every boundary: 19/20/29/30/39/40/49/50/59/60.

## Sprint PAG-S01.3 — Difficulty color counts

- [x] PAG-0121 Implement EASY = 3–5 distinct used colors.
- [x] PAG-0122 Implement MEDIUM = 6–7.
- [x] PAG-0123 Implement HARD = 8–9.
- [x] PAG-0124 Implement VERY_HARD = 10–12.
- [x] PAG-0125 Count colors from actual logical cell use, not merely requested palette.
- [x] PAG-0126 Exclude BG01 from the count.
- [x] PAG-0127 Reject outputs outside the required band.
- [x] PAG-0128 Create deterministic palette-subset selection from seed/config.
- [x] PAG-0129 Support an explicitly supplied valid canonical palette subset.
- [x] PAG-0130 Reject explicitly supplied palette subsets incompatible with difficulty.

### M01 acceptance

- [x] PAG-0131 Every legal difficulty can construct a valid generation request.
- [x] PAG-0132 Every illegal dimension/color-band combination is rejected before generation.
- [x] PAG-0133 Contract tests are independent of generator implementation.

---

# PAG-M02 — Deterministic Generation Core

M02 final state: `PASS / CLOSED`  
Closing cycle: `PAG-M02-C003 — Result Construction Boundary Remediation`  
Closing audit: `.hiveai/audits/PAG-M02-C003_RESULT_CONSTRUCTION_BOUNDARY_REMEDIATION_STRICT_AUDIT.md`

## Sprint PAG-S02.1 — Generation request

- [x] PAG-0201 Define immutable/versioned `GenerationRequest`.
- [x] PAG-0202 Include request schema version.
- [x] PAG-0203 Include difficulty.
- [x] PAG-0204 Include optional explicit width.
- [x] PAG-0205 Include optional explicit height.
- [x] PAG-0206 Include seed.
- [x] PAG-0207 Include generator mode.
- [x] PAG-0208 Include optional style/theme.
- [x] PAG-0209 Include optional requested palette subset.
- [x] PAG-0210 Include generator-specific options under a versioned namespace.
- [x] PAG-0211 Canonicalize request serialization so key-order differences cannot alter reproducibility.

## Sprint PAG-S02.2 — Deterministic RNG

- [x] PAG-0212 Define one project-owned deterministic RNG abstraction.
- [x] PAG-0213 Do not let generator modules call uncontrolled global randomness.
- [x] PAG-0214 Derive sub-seeds deterministically for dimension, palette, geometry, colorization and post-processing stages.
- [x] PAG-0215 Record RNG algorithm/version in metadata.
- [x] PAG-0216 Test same seed + same config = same generated logical grid.
- [x] PAG-0217 Test same seed + same config = byte-identical canonical JSON.
- [x] PAG-0218 Test different seeds can generate distinct outputs.
- [x] PAG-0219 Ensure retries derive deterministic retry seeds.
- [x] PAG-0220 Ensure failure/retry order cannot depend on Python hash randomization.

## Sprint PAG-S02.3 — Generator interface

- [x] PAG-0221 Define common `PixelGenerator` interface.
- [x] PAG-0222 Define common `GenerationResult`.
- [x] PAG-0223 Require exact width×height logical grid.
- [x] PAG-0224 Require canonical C-ID logical cells.
- [x] PAG-0225 Require generator mode/version.
- [x] PAG-0226 Require seed/provenance.
- [x] PAG-0227 Require explicit failure reason on unsuccessful generation.
- [x] PAG-0228 Never return partially valid production output as success.

### M02 acceptance

- [x] PAG-0229 Golden deterministic test fixtures exist for at least one Easy, Medium, Hard and Very Hard request.
- [x] PAG-0230 Same-request reruns are byte-identical across repeated executions on the same supported environment.

---

# PAG-M03 — Mask / Sprite Generator

M03 final state: `PASS / CLOSED`  
Closing cycle: `PAG-M03-C003 — Semantic Role Binding & Weak-Family Recognizability Remediation`  
Closing audit: `.hiveai/audits/PAG-M03-C003_SEMANTIC_ROLE_BINDING_AND_WEAK_FAMILY_RECOGNIZABILITY_REMEDIATION_STRICT_AUDIT.md`

Goal: produce recognizable silhouettes and structured pixel-art objects without AI.

Primary algorithm reference: `zfedoran/pixel-sprite-generator`.

## Sprint PAG-S03.1 — Generic mask engine

- [x] PAG-0301 Implement 2D logical mask representation.
- [x] PAG-0302 Support required/forbidden/random mask cells.
- [x] PAG-0303 Implement seeded random mask resolution.
- [x] PAG-0304 Implement horizontal symmetry.
- [x] PAG-0305 Implement optional vertical symmetry.
- [x] PAG-0306 Implement asymmetric mode.
- [x] PAG-0307 Implement deterministic mutation amount.
- [x] PAG-0308 Ensure resulting mask stays inside requested dimensions.
- [x] PAG-0309 Support placement/centering inside rectangular boards.
- [x] PAG-0310 Add occupancy floor/ceiling controls.

## Sprint PAG-S03.2 — Template families

Create templates as **SCRUBBOTS-owned definitions**, not copied artwork.

- [x] PAG-0311 Define ROBOT family.
- [x] PAG-0312 Define CREATURE family.
- [x] PAG-0313 Define FISH family.
- [x] PAG-0314 Define OCTOPUS/SEA-CREATURE family.
- [x] PAG-0315 Define SPACE_SHIP family.
- [x] PAG-0316 Define BUTTERFLY/INSECT family.
- [x] PAG-0317 Define FACE/EMBLEM family.
- [x] PAG-0318 Define TREE/PLANT family.
- [x] PAG-0319 Define CORAL family.
- [x] PAG-0320 Define ABSTRACT_SYMBOL family.

Each family:

- [x] PAG-0321 supports multiple seeds,
- [x] PAG-0322 supports all legal difficulty dimensions,
- [x] PAG-0323 scales logically without interpolation,
- [x] PAG-0324 can intentionally reserve negative/background space,
- [x] PAG-0325 produces a non-empty artwork mask.

## Sprint PAG-S03.3 — Region coloring

- [x] PAG-0326 Convert silhouette regions to canonical C01..C16.
- [x] PAG-0327 Use exactly a legal distinct-color count for difficulty.
- [x] PAG-0328 Avoid single-pixel color salt unless style explicitly requests it.
- [x] PAG-0329 Prefer coherent connected color regions.
- [x] PAG-0330 Support outline/body/detail semantic color roles without introducing non-canonical colors.
- [x] PAG-0331 Prevent BG01 assignment to cells.
- [x] PAG-0332 Ensure every requested palette color actually appears when output is accepted.
- [x] PAG-0333 Add deterministic recoloring while preserving geometry.

### M03 acceptance

- [x] PAG-0334 Generate at least 100 deterministic mask candidates across the four difficulties.
- [x] PAG-0335 Zero accepted candidates violate palette or dimension contracts.
- [x] PAG-0336 Manual contact sheet demonstrates recognizably different families and seeds.

---

# PAG-M04 — Procedural Shape / Rule Generator

H!veAI active cycle: `PAG-M04-C001 — Procedural Shape / Rule Generator`  
State: `READY_FOR_IMPLEMENTATION`  
Required actor: `CODEX`  
Authoritative prompt: `.hiveai/prompts/PAG-M04-C001_PROCEDURAL_SHAPE_RULE_GENERATOR_PROMPT.md`  
Previous strict audit: `.hiveai/audits/PAG-M03-C003_SEMANTIC_ROLE_BINDING_AND_WEAK_FAMILY_RECOGNIZABILITY_REMEDIATION_STRICT_AUDIT.md`  
Forward dependency: `PAG-0441` requires the V1 performance budget established later in M10; benchmark now, do not invent a budget.

Goal: build original structured art from reusable procedural geometry.

Primary conceptual reference: `mxgmn/MarkovJunior`.

Do not require MarkovJunior/C# at runtime.

## Sprint PAG-S04.1 — Core primitives

- [ ] PAG-0401 Implement BLOB primitive.
- [ ] PAG-0402 Implement ISLAND primitive.
- [ ] PAG-0403 Implement RING primitive.
- [ ] PAG-0404 Implement CORRIDOR primitive.
- [ ] PAG-0405 Implement POCKET primitive.
- [ ] PAG-0406 Implement SNAKE/self-avoiding-walk primitive.
- [ ] PAG-0407 Implement BRANCH primitive.
- [ ] PAG-0408 Implement CHAMBER primitive.
- [ ] PAG-0409 Implement SPIRAL primitive.
- [ ] PAG-0410 Implement WAVE primitive.
- [ ] PAG-0411 Implement RADIAL/BURST primitive.
- [ ] PAG-0412 Implement VORONOI-LIKE region primitive.

## Sprint PAG-S04.2 — Growth operations

- [ ] PAG-0413 Implement seeded frontier growth.
- [ ] PAG-0414 Implement constrained connected growth.
- [ ] PAG-0415 Implement erosion.
- [ ] PAG-0416 Implement dilation.
- [ ] PAG-0417 Implement hole carving.
- [ ] PAG-0418 Implement contour/outline extraction.
- [ ] PAG-0419 Implement nested-region creation.
- [ ] PAG-0420 Implement controlled fragmentation.
- [ ] PAG-0421 Implement local rewrite-rule operation.
- [ ] PAG-0422 Bound every operation by deterministic step/attempt limits.

## Sprint PAG-S04.3 — Composition recipes

- [ ] PAG-0423 Define layered composition recipe format.
- [ ] PAG-0424 Compose multiple primitives without resizing final grid.
- [ ] PAG-0425 Prevent accidental overwrite of protected semantic regions.
- [ ] PAG-0426 Support symmetry recipe.
- [ ] PAG-0427 Support organic/asymmetric recipe.
- [ ] PAG-0428 Support central-subject recipe.
- [ ] PAG-0429 Support multi-island recipe.
- [ ] PAG-0430 Support border/frame-emblem recipe.
- [ ] PAG-0431 Support dense-full-board recipe.
- [ ] PAG-0432 Support sparse-negative-space recipe.

## Sprint PAG-S04.4 — Color-region assignment

- [ ] PAG-0433 Color generated regions using legal palette subset.
- [ ] PAG-0434 Guarantee legal distinct-used-color count.
- [ ] PAG-0435 Avoid pathological checkerboard noise by default.
- [ ] PAG-0436 Add minimum region-size controls.
- [ ] PAG-0437 Add maximum region dominance control.
- [ ] PAG-0438 Support deliberate accent regions.

### M04 acceptance

- [ ] PAG-0439 Generate deterministic examples for every primitive.
- [ ] PAG-0440 Generate deterministic examples for every composition recipe.
- [ ] PAG-0441 59×59 generation completes within the V1 performance budget established in M10.
- [ ] PAG-0442 Outputs show substantially more structure than uniform random board filling.

---

# PAG-M05 — Wave Function Collapse Generator

Goal: generate new pixel-art arrangements that preserve local pattern language from approved exemplars.

Primary implementation reference: `ikarth/wfc_2019f`.

## Sprint PAG-S05.1 — WFC isolation

- [ ] PAG-0501 Pin/document exact upstream reference commit.
- [ ] PAG-0502 Identify the minimum WFC modules required.
- [ ] PAG-0503 Remove/avoid irrelevant GUI/logging/demo dependencies.
- [ ] PAG-0504 Wrap WFC behind the common `PixelGenerator` interface.
- [ ] PAG-0505 Ensure WFC receives in-memory logical pixel arrays.
- [ ] PAG-0506 Ensure WFC output dimensions equal requested logical dimensions.
- [ ] PAG-0507 Prohibit automatic output resampling.
- [ ] PAG-0508 Pass project deterministic RNG/seed into WFC behavior.
- [ ] PAG-0509 Make contradiction/retry handling deterministic.
- [ ] PAG-0510 Bound retries.

## Sprint PAG-S05.2 — Exemplar contract

- [ ] PAG-0511 Define exemplar metadata schema.
- [ ] PAG-0512 Require explicit source/provenance for every exemplar.
- [ ] PAG-0513 Require exemplar logical pixels to be canonical C01..C16 or pass an explicit deterministic mapping process.
- [ ] PAG-0514 Reject antialiased/interpolated exemplars.
- [ ] PAG-0515 Reject exemplars with illegal dimensions only when they are intended as production artifacts; allow smaller training motifs under a separate exemplar role.
- [ ] PAG-0516 Never treat external project sample images as SCRUBBOTS-owned exemplars.
- [ ] PAG-0517 Add an empty exemplar inbox/documentation path rather than fabricating owner art.

## Sprint PAG-S05.3 — Pattern extraction/configuration

- [ ] PAG-0518 Support pattern width N=2.
- [ ] PAG-0519 Support pattern width N=3.
- [ ] PAG-0520 Allow N=4 experimentally but keep it non-default until performance/quality is proven.
- [ ] PAG-0521 Support configurable input periodicity.
- [ ] PAG-0522 Support configurable output periodicity.
- [ ] PAG-0523 Support controlled rotations/reflections.
- [ ] PAG-0524 Record WFC config in metadata.
- [ ] PAG-0525 Reject configs that cannot satisfy requested palette legality.

## Sprint PAG-S05.4 — SCRUBBOTS palette enforcement

- [ ] PAG-0526 Ensure WFC cannot introduce unseen/off-palette colors.
- [ ] PAG-0527 Remap WFC's used colors to the requested canonical palette subset only through deterministic explicit mapping.
- [ ] PAG-0528 Enforce target distinct-color count after generation.
- [ ] PAG-0529 Reject rather than silently “fix” an output that violates logical contract.
- [ ] PAG-0530 Record contradiction/rejection reasons.

### M05 acceptance

- [ ] PAG-0531 Produce deterministic outputs from at least three legal synthetic/unit-test exemplars.
- [ ] PAG-0532 Same exemplar + same config + same seed reproduces byte-identical logical output.
- [ ] PAG-0533 Rectangular WFC outputs are tested.
- [ ] PAG-0534 59×59 WFC workload is benchmarked.
- [ ] PAG-0535 No production dependency on network/API/cloud exists.

---

# PAG-M06 — Hybrid Generator Router

Goal: combine generator families while keeping each generator independently testable.

## Sprint PAG-S06.1 — Router

- [ ] PAG-0601 Implement modes: MASK, RULES, WFC, HYBRID.
- [ ] PAG-0602 Route explicit mode deterministically.
- [ ] PAG-0603 Implement AUTO mode only after explicit modes are stable.
- [ ] PAG-0604 AUTO mode selection must itself be seed-deterministic.
- [ ] PAG-0605 Record actual selected engine/version in result metadata.
- [ ] PAG-0606 Never hide engine failure behind a different mode unless fallback policy explicitly permits it.

## Sprint PAG-S06.2 — Hybrid strategies

- [ ] PAG-0607 MASK_GEOMETRY + RULE_COLOR_REGIONS strategy.
- [ ] PAG-0608 RULE_GEOMETRY + MASK_SYMMETRY strategy.
- [ ] PAG-0609 RULE_BASE + WFC_DETAIL strategy.
- [ ] PAG-0610 MASK_BASE + WFC_DETAIL strategy.
- [ ] PAG-0611 Keep final logical dimensions fixed throughout all stages.
- [ ] PAG-0612 Keep final palette inside C01..C16.
- [ ] PAG-0613 Preserve stage-by-stage provenance/sub-seeds.
- [ ] PAG-0614 Reject hybrid stages that destroy required topology/quality constraints.

### M06 acceptance

- [ ] PAG-0615 At least two hybrid strategies produce valid deterministic outputs.
- [ ] PAG-0616 Hybrid result metadata can reproduce every stage.
- [ ] PAG-0617 No hybrid path performs interpolation/resizing.

---

# PAG-M07 — Artwork Quality & Diversity Filters

These are **visual/structural quality gates**, not gameplay difficulty or solvability rules.

V1 must not pretend these heuristics understand game difficulty.

## Sprint PAG-S07.1 — Structural quality metrics

- [ ] PAG-0701 Compute occupied-cell ratio.
- [ ] PAG-0702 Compute number of connected occupied components.
- [ ] PAG-0703 Compute connected components per color.
- [ ] PAG-0704 Compute isolated single-cell count.
- [ ] PAG-0705 Compute tiny-region count.
- [ ] PAG-0706 Compute largest-region dominance.
- [ ] PAG-0707 Compute edge-touch ratio.
- [ ] PAG-0708 Compute symmetry score.
- [ ] PAG-0709 Compute color-distribution entropy.
- [ ] PAG-0710 Compute color adjacency statistics.
- [ ] PAG-0711 Compute bounding box and center-of-mass.
- [ ] PAG-0712 Compute negative-space ratio.

## Sprint PAG-S07.2 — Reject obvious garbage

- [ ] PAG-0713 Reject empty artwork.
- [ ] PAG-0714 Reject effectively full single-shape slabs when outside configured style.
- [ ] PAG-0715 Reject excessive salt-and-pepper single pixels.
- [ ] PAG-0716 Reject excessive tiny fragmented regions.
- [ ] PAG-0717 Reject illegal color dominance thresholds when configured.
- [ ] PAG-0718 Reject accidental all-checkerboard/noise patterns.
- [ ] PAG-0719 Reject color-count violations.
- [ ] PAG-0720 Reject any off-palette data.
- [ ] PAG-0721 Reject dimension mismatch.
- [ ] PAG-0722 Produce machine-readable rejection codes.

## Sprint PAG-S07.3 — Diversity

- [ ] PAG-0723 Define logical-grid hash.
- [ ] PAG-0724 Detect exact duplicates.
- [ ] PAG-0725 Define a deterministic near-duplicate metric.
- [ ] PAG-0726 Measure occupancy-mask similarity.
- [ ] PAG-0727 Measure color-layout similarity separately.
- [ ] PAG-0728 Allow batch-level duplicate threshold.
- [ ] PAG-0729 Keep “visual quality” and “diversity” scores separate.
- [ ] PAG-0730 Never silently mutate an accepted candidate to make it different; regenerate with a recorded seed instead.

## Sprint PAG-S07.4 — Human review artifacts

- [ ] PAG-0731 Generate contact sheet of candidates.
- [ ] PAG-0732 Show candidate ID, mode, seed, difficulty, dimensions and color count.
- [ ] PAG-0733 Allow nearest-neighbor preview scaling only.
- [ ] PAG-0734 Make preview scaling presentation-only; logical PNG remains exact logical dimensions unless a separate preview file is explicitly produced.
- [ ] PAG-0735 Add simple ACCEPT/REJECT review manifest format for future UI use.

### M07 acceptance

- [ ] PAG-0736 Quality filters eliminate deliberately constructed garbage fixtures.
- [ ] PAG-0737 Good fixtures are not systematically rejected.
- [ ] PAG-0738 Scores/reasons are reproducible from logical grid alone.

---

# PAG-M08 — Output / Export Contract

## Sprint PAG-S08.1 — Logical-grid JSON

- [ ] PAG-0801 Define versioned generator artifact schema.
- [ ] PAG-0802 Store candidate ID.
- [ ] PAG-0803 Store difficulty.
- [ ] PAG-0804 Store exact width and height.
- [ ] PAG-0805 Store local palette as ascending canonical C-IDs.
- [ ] PAG-0806 Store row-major logical cells.
- [ ] PAG-0807 Canonical row-major index = `y * width + x`.
- [ ] PAG-0808 Store generator mode/version.
- [ ] PAG-0809 Store master seed.
- [ ] PAG-0810 Store stage sub-seeds.
- [ ] PAG-0811 Store generation config/version.
- [ ] PAG-0812 Store source/exemplar provenance where relevant.
- [ ] PAG-0813 Store quality metrics.
- [ ] PAG-0814 Store acceptance/rejection state separately from immutable generated grid.

## Sprint PAG-S08.2 — PNG output

- [ ] PAG-0815 Generate logical-resolution PNG exactly width×height.
- [ ] PAG-0816 One PNG pixel equals one logical cell.
- [ ] PAG-0817 Use exact canonical RGB for every cell.
- [ ] PAG-0818 No antialiasing/interpolation.
- [ ] PAG-0819 Do not bake presentation grid lines into the logical PNG.
- [ ] PAG-0820 Generate optional enlarged preview PNG using integer nearest-neighbor scaling.
- [ ] PAG-0821 Optional preview may show BG01 and presentation grid, but logical source PNG/JSON remain unchanged.

## Sprint PAG-S08.3 — Round-trip validation

- [ ] PAG-0822 Reconstruct PNG from logical JSON.
- [ ] PAG-0823 Reconstruct logical JSON from generator's own PNG where format permits unambiguous exact mapping.
- [ ] PAG-0824 Compare raw logical RGB bytes.
- [ ] PAG-0825 Prove no resize/interpolation occurred.
- [ ] PAG-0826 Prove JSON cell count = width×height.
- [ ] PAG-0827 Prove every cell references the local palette.
- [ ] PAG-0828 Prove local palette is an actually-used ascending C-ID subset.

### M08 acceptance

- [ ] PAG-0829 Golden PNG/JSON pairs pass byte-level round-trip tests.
- [ ] PAG-0830 Re-running accepted output with same config/seed creates no meaningless diff.

---

# PAG-M09 — CLI & Local Batch Generation

## Sprint PAG-S09.1 — Single generation CLI

Target UX:

```text
scrubbots-pixel generate \
  --difficulty MEDIUM \
  --width 37 \
  --height 34 \
  --mode RULES \
  --style fish \
  --seed 849323
```

- [ ] PAG-0901 Implement `generate` CLI command.
- [ ] PAG-0902 Support explicit difficulty.
- [ ] PAG-0903 Support optional width/height.
- [ ] PAG-0904 Auto-select legal width/height when omitted.
- [ ] PAG-0905 Support explicit seed.
- [ ] PAG-0906 Generate and print a seed when seed is omitted, then record it.
- [ ] PAG-0907 Support mode.
- [ ] PAG-0908 Support style/theme.
- [ ] PAG-0909 Support output directory.
- [ ] PAG-0910 Print concise success/failure summary.
- [ ] PAG-0911 Return non-zero exit code for invalid/rejected generation.

## Sprint PAG-S09.2 — Reproduce CLI

- [ ] PAG-0912 Implement `reproduce <metadata.json>`.
- [ ] PAG-0913 Reproduce candidate from recorded config.
- [ ] PAG-0914 Compare reproduced logical-grid hash.
- [ ] PAG-0915 Fail loudly if generator version/config is unsupported.
- [ ] PAG-0916 Never silently substitute current defaults for missing historical parameters.

## Sprint PAG-S09.3 — Batch CLI

Target UX:

```text
scrubbots-pixel batch \
  --difficulty EASY \
  --count 100 \
  --mode AUTO \
  --seed 100000
```

- [ ] PAG-0917 Implement deterministic batch orchestration.
- [ ] PAG-0918 Separate attempts from accepted count.
- [ ] PAG-0919 Record every attempted seed.
- [ ] PAG-0920 Record rejection codes.
- [ ] PAG-0921 Stop at explicit max attempts.
- [ ] PAG-0922 Never loop forever chasing acceptance.
- [ ] PAG-0923 Support resumable batch manifest.
- [ ] PAG-0924 Prevent duplicate candidate IDs.
- [ ] PAG-0925 Detect exact duplicate logical grids.
- [ ] PAG-0926 Generate contact sheet/report.
- [ ] PAG-0927 Batch rerun from same manifest is deterministic.

### M09 acceptance

- [ ] PAG-0928 Owner can generate valid candidates from Windows command line without opening Godot.
- [ ] PAG-0929 No internet connection is needed during generation.
- [ ] PAG-0930 Single and batch generation both preserve provenance.

---

# PAG-M10 — Validation, Performance & V1 Acceptance

## Sprint PAG-S10.1 — Property/fuzz tests

- [ ] PAG-1001 Randomly test thousands of valid GenerationRequests.
- [ ] PAG-1002 Every successful result has exact requested width.
- [ ] PAG-1003 Every successful result has exact requested height.
- [ ] PAG-1004 Every successful result has exactly width×height logical cells.
- [ ] PAG-1005 Every successful cell is C01..C16.
- [ ] PAG-1006 Every successful output satisfies difficulty color band.
- [ ] PAG-1007 Every successful local palette contains only actually used colors.
- [ ] PAG-1008 Every successful local palette is sorted by C-ID.
- [ ] PAG-1009 No BG01 appears as logical color.
- [ ] PAG-1010 Same request reproducibility holds across repeated calls.
- [ ] PAG-1011 Invalid requests never crash the batch process.

## Sprint PAG-S10.2 — Performance

Measure each generator mode separately.

- [ ] PAG-1012 Benchmark EASY representative boards.
- [ ] PAG-1013 Benchmark MEDIUM representative boards.
- [ ] PAG-1014 Benchmark HARD representative boards.
- [ ] PAG-1015 Benchmark VERY_HARD representative boards.
- [ ] PAG-1016 Explicitly benchmark 59×59.
- [ ] PAG-1017 Record peak memory.
- [ ] PAG-1018 Record median generation time.
- [ ] PAG-1019 Record p95 generation time across a fixed deterministic benchmark seed set.
- [ ] PAG-1020 Record rejection/contradiction rate.
- [ ] PAG-1021 Establish per-mode V1 performance budgets from measured laptop results rather than inventing arbitrary targets.
- [ ] PAG-1022 Optimize only measured bottlenecks.

## Sprint PAG-S10.3 — V1 visual acceptance set

Generate a fixed review pack:

- [ ] PAG-1023 25 EASY candidates.
- [ ] PAG-1024 25 MEDIUM candidates.
- [ ] PAG-1025 25 HARD candidates.
- [ ] PAG-1026 25 VERY_HARD candidates.
- [ ] PAG-1027 Include MASK examples.
- [ ] PAG-1028 Include RULES examples.
- [ ] PAG-1029 Include WFC examples if approved exemplars are available.
- [ ] PAG-1030 Include HYBRID examples if M06 is accepted.
- [ ] PAG-1031 Produce contact sheets grouped by mode/difficulty.
- [ ] PAG-1032 Produce metrics/rejection report.
- [ ] PAG-1033 Owner manually reviews the 100-candidate acceptance pack.
- [ ] PAG-1034 Record which styles/families are approved, rejected or need tuning.

## Sprint PAG-S10.4 — V1 release gate

V1 is complete only when:

- [ ] PAG-1035 Engine is fully offline.
- [ ] PAG-1036 No GPU is required.
- [ ] PAG-1037 All four difficulty dimension bands work.
- [ ] PAG-1038 Rectangular boards work.
- [ ] PAG-1039 Seed reproduction works.
- [ ] PAG-1040 C01..C16 palette enforcement works.
- [ ] PAG-1041 Difficulty distinct-color enforcement works.
- [ ] PAG-1042 MASK generator passes.
- [ ] PAG-1043 RULES generator passes.
- [ ] PAG-1044 WFC generator passes or is explicitly documented as awaiting approved exemplars while the engine itself is tested using synthetic fixtures.
- [ ] PAG-1045 Output PNG/JSON round trip passes.
- [ ] PAG-1046 Batch generation passes.
- [ ] PAG-1047 Duplicate detection passes.
- [ ] PAG-1048 59×59 performance is measured and acceptable for an offline factory workflow.
- [ ] PAG-1049 Third-party attribution audit passes.
- [ ] PAG-1050 Owner accepts the visual V1 review pack.

---

# PAG-M11 — Godot / Main Level Factory Handoff Gate

This milestone **does not implement the full Level Factory**.

Its only goal is to make Pixel Art Generator V1 consumable by the existing SCRUBBOTS project later.

## Sprint PAG-S11.1 — Compatibility adapter

- [ ] PAG-1101 Inspect the current main-repo Level Data V1 contract before writing an adapter.
- [ ] PAG-1102 Do not duplicate/rewrite the audited main-game M09 importer.
- [ ] PAG-1103 Define Pixel Generator artifact → main Level Factory candidate adapter.
- [ ] PAG-1104 Preserve width/height exactly.
- [ ] PAG-1105 Preserve row-major cells exactly.
- [ ] PAG-1106 Preserve canonical palette IDs exactly.
- [ ] PAG-1107 Preserve generator seed/config/provenance as sidecar metadata where the main Level Data schema does not own those fields.
- [ ] PAG-1108 Add compatibility tests against representative main-repo Level Data fixtures.
- [ ] PAG-1109 Keep main mobile game independent of Python generator runtime.

## Sprint PAG-S11.2 — Integration decision

- [ ] PAG-1110 Decide after V1 acceptance whether to:
  - keep the Python Pixel Generator as an external offline tool,
  - embed a thin Godot UI that invokes the local tool,
  - port selected proven algorithms to GDScript,
  - or use a mixed architecture.
- [ ] PAG-1111 Base the decision on measured reliability/performance/maintenance, not preference.
- [ ] PAG-1112 Document migration plan back into `Sekiph82/Scrubbots/level_factory`.
- [ ] PAG-1113 Do not merge experimental generator code into the mobile game runtime.
- [ ] PAG-1114 Keep future puzzle solver/gameplay-level validation outside Pixel Generator V1.

### M11 acceptance

- [ ] PAG-1115 A generated candidate can be handed to the main Level Factory without image resizing or palette reinterpretation.
- [ ] PAG-1116 Main SCRUBBOTS runtime has zero dependency on Python/WFC/Markov generator code.
- [ ] PAG-1117 V1 integration architecture is explicitly owner-approved before larger Level Factory work begins.

---

# 6. EXPLICITLY OUT OF SCOPE FOR PIXEL ART GENERATOR V1

Do not implement these merely because they exist in the larger Level Factory roadmap:

- gameplay solver,
- win-condition simulation,
- Scrubbot slots/stacks,
- gameplay dependency graph,
- legal cleaning move logic,
- reachability,
- deadlock detection,
- campaign sequencing,
- player difficulty prediction,
- telemetry calibration,
- weekly publishing,
- remote content delivery,
- Google Play injection,
- monetization,
- runtime procedural generation,
- AI/cloud image generation,
- full Godot Level Factory editor.

Those belong to later SCRUBBOTS Level Factory milestones.

---

# 7. CODEX EXECUTION RULES

Codex should work milestone-by-milestone.

For each implementation cycle:

1. Read this entire `tasks.md`.
2. Inspect repository state.
3. Identify the first incomplete milestone/sprint explicitly requested by the owner.
4. Do not work ahead into unrelated milestones.
5. Preserve deterministic behavior.
6. Add tests with implementation.
7. Run all relevant tests.
8. Do not mark a task complete merely because code was written.
9. Mark `[x]` only after validation evidence exists.
10. Keep commits focused.
11. Never add an online API dependency.
12. Never add an AI model just to make artwork “better”.
13. Never resize final logical art to force it into a board.
14. Never introduce colors outside C01..C16.
15. Never treat BG01 as a logical pixel.
16. Never modify the SCRUBBOTS owner-locked difficulty dimension/color rules without explicit owner instruction.
17. Never copy third-party example artwork into production assets without verified asset licensing.
18. Prefer small project-owned implementations over importing large editor frameworks.
19. Keep the generator core headless and testable.
20. Stop and document any conflict with the main SCRUBBOTS canonical contract rather than silently choosing a new rule.

---

# 8. FIRST IMPLEMENTATION ORDER FOR CODEX

Codex should build V1 in this order:

```text
PAG-M00
Repository/bootstrap/licenses
        |
        v
PAG-M01
SCRUBBOTS palette + dimensions + color bands
        |
        v
PAG-M02
deterministic request/RNG/generator interfaces
        |
        v
PAG-M03
MASK generator
        |
        v
PAG-M04
RULES generator
        |
        v
PAG-M08
logical JSON + PNG output/roundtrip
        |
        v
PAG-M09
single CLI
        |
        v
PAG-M07
quality filters
        |
        v
PAG-M05
WFC engine
        |
        v
PAG-M06
hybrid routing
        |
        v
PAG-M09
batch/reproduce completion
        |
        v
PAG-M10
100-candidate owner acceptance pack
        |
        v
PAG-M11
main Level Factory handoff
```

Reason for this order:

The engine must first prove it can generate **valid original structured logical art without any exemplar dependency**. WFC comes after MASK and RULES because WFC quality depends on approved exemplar art that may not yet exist. This prevents the whole project from being blocked by training/example assets.

---

# 9. V1 SUCCESS DEFINITION

Pixel Art Generator V1 succeeds when the owner can run something conceptually equivalent to:

```text
scrubbots-pixel generate
  difficulty=MEDIUM
  style=fish
  seed=849323
```

and receive:

```text
candidate_849323/
  artwork.png
  artwork.preview.png
  artwork.json
  metadata.json
```

where:

- width and height are legal for MEDIUM,
- every PNG pixel corresponds to exactly one gameplay cell,
- every logical cell is C01..C16,
- exactly 6–7 distinct logical colors are used,
- no interpolation or antialiasing exists,
- the result is locally generated without internet,
- the same seed/config reproduces the same logical art,
- a different seed can create a different artwork,
- the output is ready to be consumed later by the SCRUBBOTS Level Factory.

That is the boundary of Pixel Art Generator V1.
