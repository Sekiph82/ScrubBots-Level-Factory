# PAG-M04-C001 — Procedural Shape / Rule Generator

Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M03-C003_SEMANTIC_ROLE_BINDING_AND_WEAK_FAMILY_RECOGNIZABILITY_REMEDIATION_STRICT_AUDIT.md`

Primary conceptual reference:
`https://github.com/mxgmn/MarkovJunior/tree/42aaf24bcf54ae164fba49c0a59348297904a676`

Verified provenance record:
`THIRD_PARTY_NOTICES.md`

## 1. Objective

Implement and prove **PAG-M04 — Procedural Shape / Rule Generator** only.

M04 must create original deterministic logical artwork from project-owned procedural geometry primitives, bounded growth/rewrite operations, layered composition recipes, and coherent canonical color regions.

Implement:

- 12 reusable procedural geometry primitives;
- 10 bounded growth/morphology/rewrite operations;
- immutable/versioned composition recipe model;
- 7 required composition recipe families;
- deterministic protected-region composition;
- exact legal palette use;
- minimum color-region size;
- maximum color dominance control;
- deliberate coherent accent regions;
- production `RULES` generator integrated with M02 core;
- deterministic golden/review evidence.

Do **not** begin PAG-M05 WFC, PAG-M06 HYBRID/AUTO, PAG-M07 production quality scoring, PAG-M08 production artifact/PNG export, PAG-M09 CLI, or Godot integration.

## 2. Authority and third-party boundary

GitHub is the sole task/prompt/audit authority.

Implementation repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

MarkovJunior is **conceptual reference only** for ideas such as:

- local rewrite rules;
- growth;
- region formation;
- walks;
- rings/corridors;
- bounded iterative transformation.

For M04:

- do not vendor MarkovJunior;
- do not require .NET/C#/Mono;
- do not port/copy source files;
- do not copy sample models/assets;
- do not create a runtime dependency on MarkovJunior;
- implement original project-owned Python algorithms.

If any substantial code is adapted despite this rule, stop, document the exact source/commit/file, update the applicable license/provenance notice, and do not represent it as original.

No main `Sekiph82/Scrubbots` repository mutation is allowed.

## 3. Mandatory control-plane read order

Before the first product/test/review edit, read completely:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. M03 C003 strict audit
9. `THIRD_PARTY_NOTICES.md`
10. current M01 contract modules
11. current M02 request/RNG/generator/result modules
12. current M03 package only to understand shared contracts and avoid duplication
13. this prompt

M04 is a separate generator family. Do not turn the M03 MASK generator into the RULES engine.

## 4. Mandatory builder log

Create **before the first source, test, golden, manifest, contact-sheet, or review-builder edit**:

`.hiveai/codex-logs/PAG-M04-C001_PROCEDURAL_SHAPE_RULE_GENERATOR_CODEX_LOG.md`

Exact H1:

`# PAG-M04-C001 — Procedural Shape / Rule Generator`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- start timestamp;
- GitHub authority URLs;
- conceptual-reference URL/commit;
- start branch/HEAD/origin/ahead-behind/status;
- safe synchronization;
- mandatory reads;
- architecture decisions;
- exact files changed;
- every material command;
- failed tests/attempts and corrections;
- primitive evidence;
- operation/rewrite evidence;
- recipe evidence;
- color-region evidence;
- deterministic acceptance batch;
- golden/review evidence;
- 59×59 benchmark evidence;
- full regression;
- provenance/license confirmation;
- implementation commit SHA(s);
- push/equality checkpoint;
- final changed-file summary.

Do not attempt to write the builder-log commit's own terminal SHA into the log.

Do not edit ChatGPT-owned task/H!veAI/audit acceptance state.

## 5. Core M04 architecture

Create an independent RULES package, expected conceptually:

```text
src/scrubbots_pixel_factory/generators/rules/
  __init__.py
  model.py
  primitives.py
  operations.py
  recipes.py
  colorize.py
  generator.py
```

Exact filenames may differ if cleaner.

### Required layering

```text
GenerationRequest (RULES)
       |
       v
canonical DeterministicRNG root
       |
       v
Recipe / primitive selection
       |
       v
RuleCanvas / protected region state
       |
       v
bounded operations / composition
       |
       v
logical region map
       |
       v
canonical coherent color assignment
       |
       v
validated GenerationResult.success()
```

Do not depend on image pixels, image resize, interpolation, raster filters, NumPy randomness, or third-party geometry frameworks.

All geometry operates directly in the requested logical width × height coordinate space.

## 6. RULES request integration

Production generator class should conceptually be:

`RuleShapeGenerator`

and implement:

`PixelGenerator`

Stable identity, for example:

- `generator_id = "rule-shape"`
- `generator_version = "1.0.0"`

Exact strings may differ if documented/stable.

### Mode

Accept only:

`GeneratorMode.RULES`

MASK/WFC/HYBRID requests must fail deterministically with `INVALID_REQUEST`.

### RNG

Use only project `DeterministicRNG`.

Apply the M03-validated top-level rule:

- supplied RNG must be exact project RNG type;
- supplied RNG domain must be `"root"`;
- supplied root stage seeds must match `DeterministicRNG(request.seed).stage_seeds()`;
- no supplied RNG means construct exactly `DeterministicRNG(request.seed)`.

No global `random`, Python `hash()`, time, UUID, process ID, or OS entropy.

### Stage/domain use

Use project stage separation deliberately:

- geometry stage: recipe/primitive/operation geometry;
- colorization stage: palette-to-region assignment;
- child domains for individual primitive instances and operation steps.

Unrelated stage output must not depend on call-order consumption in another stage.

### Dimensions / palette

Resolve only through existing M01/M02 request contracts:

- legal width/height;
- legal selected C-ID subset.

No clamp/resize.

### Result

Successful result must be built only through validated:

`GenerationResult.success(...)`

with:

- exact requested/resolved dimensions;
- full row-major C01..C16 grid;
- RULES mode;
- stable generator identity/version;
- exact master seed;
- project RNG identity;
- authenticated stage/retry provenance.

Failures use `GenerationResult.failure(...)` with stable code/reason and no partial grid.

## 7. Internal RuleCanvas / geometry model

Implement a clear immutable-or-controlled-mutable internal geometry model.

It must represent at least:

- width;
- height;
- occupancy/region membership;
- protected cell semantics;
- deterministic region IDs or semantic region labels;
- row-major indexing.

### Protected states

Composition must be able to distinguish at least:

- ordinary mutable cells;
- protected occupied cells;
- protected negative-space cells.

Protected semantics are internal geometry constraints only.

Final logical output still contains only canonical C01..C16 IDs.

Do not create BG01, transparency, `None`, or C17+ logical cells.

### Invariants

- all coordinates in bounds;
- exact width × height storage;
- region IDs deterministic and stable within one generation run;
- no unordered set/dict iteration may influence canonical geometry;
- external caller-owned collections must not mutate stored recipe/config state.

## 8. PAG-S04.1 — 12 core primitives

Implement tasks `PAG-0401..PAG-0412`.

Each primitive must:

- operate directly at target logical dimensions;
- use explicit project RNG when stochastic;
- have deterministic bounded behavior;
- support rectangular boards;
- expose testable geometry output;
- never resize another source grid;
- never rely on image libraries;
- respect protected cells when composed.

### PAG-0401 — BLOB

A compact connected organic filled region.

Required properties:

- connected 4-neighbor occupancy;
- bounded target area/radius;
- irregular but coherent contour;
- deterministic variation across seeds.

### PAG-0402 — ISLAND

A compact isolated region placed inside available negative space.

Required properties:

- connected;
- deterministic center/seed;
- configurable separation from protected occupied regions where requested;
- suitable for multi-island recipes.

### PAG-0403 — RING

Discrete annular/loop geometry.

Required properties:

- closed or nearly closed loop by explicit contract;
- configurable thickness;
- internal pocket/negative space remains visible;
- rectangular boards supported.

### PAG-0404 — CORRIDOR

Connected path/band between deterministic endpoints.

Required properties:

- in bounds;
- configurable width;
- 4-neighbor connected;
- no teleport gaps.

### PAG-0405 — POCKET

Carve a bounded negative-space pocket inside eligible occupied geometry.

Required properties:

- never remove protected occupied cells;
- bounded size;
- deterministic placement;
- retains surrounding structure where feasible.

### PAG-0406 — SNAKE / self-avoiding walk

A bounded self-avoiding logical walk.

Required:

- no repeated cell;
- deterministic neighbor choice;
- explicit max steps;
- explicit stop reason when trapped;
- no infinite retry.

### PAG-0407 — BRANCH

Connected trunk/branch geometry.

Required:

- one connected source structure;
- bounded branch count/depth;
- deterministic branching;
- no recursion without explicit depth cap.

### PAG-0408 — CHAMBER

Room/chamber geometry, optionally linked by corridors.

Required:

- bounded rectangle/organic chamber regions;
- protected overwrite rules;
- deterministic placement.

### PAG-0409 — SPIRAL

Discrete logical spiral/path/band.

Required:

- integer-grid algorithm;
- bounded turns/steps;
- no floating-point rasterization dependency;
- supports rectangular clipping deterministically.

### PAG-0410 — WAVE

Structured repeated wave/ribbon.

Prefer integer/stair-step or rational periodic construction.

Required:

- deterministic period/amplitude parameters;
- no platform-sensitive trigonometric raster differences required for correctness;
- no checkerboard noise.

### PAG-0411 — RADIAL / BURST

Center/anchor with bounded spokes/rays/lobes.

Required:

- deterministic center;
- bounded ray count/length;
- no out-of-bounds writes.

### PAG-0412 — VORONOI-LIKE regions

Project-owned deterministic region partitioning.

Use logical seed points and deterministic distance/tie-break semantics, preferably Manhattan or squared integer distance.

Required:

- every eligible cell assigned to exactly one region;
- stable tie-breaking;
- no SciPy/sklearn dependency;
- no stochastic unordered iteration.

## 9. Primitive API and evidence

Do not hide primitives only inside one monolithic generator.

Expose a narrow internal/testable API that can render/apply each primitive to a RuleCanvas.

Tests must prove every primitive individually.

For each primitive include at least:

- same seed/config -> same geometry digest;
- fixed seed variation set -> at least two distinct valid outputs where stochastic;
- rectangle support;
- protected-cell respect;
- step/size bounds;
- no out-of-bounds cells;
- nontrivial structure.

Create one fixed M04 golden geometry hash per primitive.

## 10. PAG-S04.2 — growth / morphology / rewrite operations

Implement tasks `PAG-0413..PAG-0422`.

Operations must work on logical region/occupancy state, not RGB pixels.

### PAG-0413 — seeded frontier growth

- seed from valid eligible cell(s);
- deterministic frontier ordering plus project RNG domain;
- explicit target cell count / max steps;
- connected output.

### PAG-0414 — constrained connected growth

Support constraints such as:

- allowed region;
- forbidden/protected region;
- target min/max size;
- edge-touch policy.

Must fail boundedly if target cannot be reached.

### PAG-0415 — erosion

Deterministically remove boundary cells according to project neighborhood rules.

Must:

- preserve protected occupied cells;
- support explicit iterations;
- stop at explicit iteration limit;
- not accidentally erase required structure when protection forbids it.

### PAG-0416 — dilation

Deterministically expand eligible region by neighborhood.

Must:

- respect protected negative space;
- remain bounded by iterations/board.

### PAG-0417 — hole carving

Create one or more coherent negative-space holes.

Must:

- preserve protected occupied cells;
- use minimum hole size;
- avoid default singleton holes.

### PAG-0418 — contour / outline extraction

Return or mark occupied boundary cells using explicit 4-neighbor semantics.

Deterministic and independently testable.

### PAG-0419 — nested-region creation

Create coherent child region(s) inside a parent region.

Must:

- remain inside parent geometry;
- preserve minimum region size;
- deterministic child placement/count.

### PAG-0420 — controlled fragmentation

Split a region deliberately into bounded coherent fragments.

Must:

- accept explicit max fragments/min fragment size;
- never devolve into salt-and-pepper pixels;
- preserve protected cells.

### PAG-0421 — local rewrite-rule operation

Implement a small **project-owned** local rewrite abstraction.

Conceptual shape:

```text
neighborhood predicate + deterministic replacement + bounded passes
```

Requirements:

- no MarkovJunior runtime;
- explicit local neighborhood;
- deterministic scan/tie-break order;
- project RNG only when rule intentionally selects among eligible matches;
- no self-modifying unbounded loop;
- rule cannot write protected cells illegally.

At least three original rewrite fixtures should demonstrate:

- fill a one-cell notch;
- bridge a bounded small gap;
- remove a small protrusion or equivalent project-authored rules.

Do not copy MarkovJunior XML/models/rules.

### PAG-0422 — global boundedness

Every iterative operation must expose:

- max steps/passes/iterations/attempts;
- deterministic stop condition;
- deterministic failure/partial-policy contract.

No `while True` without a proven internal finite bound.

Static/source tests should scan for accidental unbounded production loops where practical.

## 11. PAG-S04.3 — composition recipe model

Implement tasks `PAG-0423..PAG-0432`.

### Versioned recipe format

Define immutable, versioned project-owned recipes.

A recipe must describe a sequence/layers of:

- primitive application;
- operation/transformation;
- target/protected region semantics;
- deterministic parameters;
- child RNG domain.

Do not use arbitrary executable callbacks loaded from JSON.

Do not use eval/exec.

Production recipes may be Python-defined immutable data for V1.

### Layer composition

Each layer must apply to the same fixed logical width/height.

Never resize/interpolate between layers.

### Protected semantic regions

Recipe composition must support regions that later layers cannot accidentally overwrite.

At minimum test:

- protected occupied region survives erosion/pocket/fragmentation;
- protected negative-space opening survives dilation/growth;
- invalid overwrite fails closed or is explicitly skipped according to deterministic documented policy.

### Required recipe families

Implement:

#### PAG-0426 — SYMMETRY recipe

Uses one or more primitives/operations with intentional left-right, top-bottom, or combined logical symmetry.

#### PAG-0427 — ORGANIC / ASYMMETRIC recipe

Connected organic structure with controlled irregularity.

#### PAG-0428 — CENTRAL_SUBJECT recipe

Clear central occupied subject surrounded by negative-space classification.

#### PAG-0429 — MULTI_ISLAND recipe

Several coherent separated structures, each above minimum region size.

#### PAG-0430 — BORDER / FRAME_EMBLEM recipe

Structured border/frame plus emblem/interior geometry.

#### PAG-0431 — DENSE_FULL_BOARD recipe

High occupancy structured board without becoming uniform/random fill.

Must retain multiple coherent regions/negative-space or structural boundaries as configured.

#### PAG-0432 — SPARSE_NEGATIVE_SPACE recipe

Sparse subject/paths/islands with substantial base/negative-space region.

### Recipe selection

M04 may use `GenerationRequest.style` as recipe selector.

Recommended exact style names:

- `SYMMETRY`
- `ORGANIC`
- `CENTRAL_SUBJECT`
- `MULTI_ISLAND`
- `BORDER_FRAME_EMBLEM`
- `DENSE_FULL_BOARD`
- `SPARSE_NEGATIVE_SPACE`

Requirements:

- known style -> exact recipe;
- unknown style -> `INVALID_REQUEST`;
- `style=None` -> deterministic recipe selection via named geometry child stream;
- do not silently use M03 family names as RULES recipes.

Theme remains unsupported unless a narrowly documented M04 rule is added. Preferred V1 behavior: reject non-None theme.

## 12. Generator options

Keep RULES options strict and bounded.

Suggested namespace/version:

- namespace `"rules"`
- version `1`

Potential option keys may include:

- primitive density / target occupancy;
- symmetry mode;
- operation intensity;
- min color-region size;
- max region dominance percentage;
- accent count.

Do not expose every internal knob.

Requirements:

- unknown option -> fail closed;
- wrong type -> fail closed;
- bounds validated;
- all options immutable through GenerationRequest;
- all options influence deterministic output only through documented domains.

## 13. PAG-S04.4 — region color assignment

Implement tasks `PAG-0433..PAG-0438`.

M04 coloring is **region-driven**, not random per-cell coloring.

You may reuse generic non-MASK utilities only if they do not create a dependency on M03 template semantics. Prefer an independent rules colorizer or a genuinely generic helper extracted without regressing M03.

### PAG-0433 — canonical palette subset

Use only:

`request.resolve_palette_subset()`

No extra colors.

### PAG-0434 — exact legal used-color count

Every selected palette C-ID must actually appear at least once, and all M01 difficulty color-band rules remain satisfied.

### PAG-0435 — no pathological checkerboard

Default coloring must never assign colors independently per cell.

Use coherent region groups/connected components.

### PAG-0436 — minimum region size

Default final same-color components must have a configured/project-owned minimum.

Recommended:

- minimum 2 cells for every component;
- larger defaults allowed on larger boards.

If exact palette cardinality cannot fit coherent regions, boundedly regenerate/fail.

Do not use singleton dots to force palette completion.

### PAG-0437 — maximum region dominance

Add deterministic maximum same-color dominance control.

Recommended project default:

- no single color may exceed a configurable percentage such as 75–85% unless the selected recipe explicitly documents a denser base behavior.

Do not hardcode an arbitrary value without documenting it in the model/tests.

The base/negative-space color counts as a logical color and may be dominant in sparse recipes, but still must obey the recipe-specific configured cap.

### PAG-0438 — deliberate accent regions

Support coherent accent regions:

- minimum region size;
- deterministic location;
- not singleton salt;
- actual selected canonical IDs only.

## 14. Final logical-grid contract

As with M03:

- every board cell is a gameplay logical cell;
- every final cell is exactly C01..C16;
- BG01 never appears;
- no transparency/None/background sentinel;
- negative-space/base is represented by one selected canonical logical color and counts as used.

Final logical grid length = width × height.

No image generation is needed in production M04.

## 15. Deterministic retries

Rule recipes may fail because constraints conflict.

Use an explicit small `MAX_ATTEMPTS`.

Attempt N must derive from project retry machinery.

Same request must reproduce:

- identical attempt sequence;
- identical accepted output, or
- identical bounded failure.

Include authenticated retry provenance for successful attempt sequences where retries occur.

Do not catch broad exceptions and silently mutate defaults.

## 16. Production failure semantics

Use stable M02 failure codes.

Examples:

- wrong mode/style/theme/options -> `INVALID_REQUEST`;
- impossible protected-region/recipe contract -> `CONTRACT_VIOLATION` or bounded internal retry;
- exhausted deterministic attempts -> `RETRY_EXHAUSTED`.

Failure reason strings must be deterministic and free of paths/memory addresses.

## 17. Primitive golden evidence — PAG-0439

Create reviewable deterministic primitive fixtures for all 12 primitives.

Suggested review/golden artifact:

`tests/golden/m04_primitive_fixtures.json`

For each primitive record compact evidence:

- primitive ID;
- fixed dimensions;
- seed;
- parameters;
- occupied/region geometry SHA-256;
- occupied cell count;
- component count;
- optional operation-specific invariant summary.

Do not store huge duplicate full grids if hashes + focused fixtures are enough.

Tests must regenerate and compare every primitive.

## 18. Recipe golden evidence — PAG-0440

Create at least one deterministic fixture for each 7 composition recipe families.

Suggested:

`tests/golden/m04_recipe_fixtures.json`

Record:

- recipe ID/version;
- request/difficulty/seed;
- dimensions;
- palette;
- geometry/region digest;
- final grid SHA-256;
- canonical GenerationResult SHA-256;
- occupancy;
- color-component summary.

## 19. Review-only evidence

Create:

`review/m04/m04_review_manifest.json`

and:

`review/m04/M04_RULES_CONTACT_SHEET.html`

These are review-only, not M08 production artifacts.

Minimum review set:

- all 12 primitives represented;
- all 7 recipes represented;
- all 4 difficulties represented across recipe examples;
- rectangular examples;
- multiple seeds.

Contact sheet should show at least:

1. geometry/region preview;
2. final colored logical grid.

Self-contained:

- no network/CDN;
- integer block rendering;
- canonical palette;
- presentation only.

Include review diagnostics:

- occupancy;
- occupied component count;
- color component sizes;
- singleton count;
- max color dominance;
- recipe/primitive/seed/dimensions.

Do not create M07 production quality scoring APIs.

## 20. “More structure than uniform random” acceptance — PAG-0442

M04 must prove its outputs are structurally generated, not disguised random fill.

Automated evidence should include deterministic structural invariants such as:

- primitive-specific connectivity/topology;
- recipe-specific component/occupancy constraints;
- coherent color components;
- no checkerboard/salt;
- stable protected regions.

Also create explicit deliberately uniform/random-like test fixtures and show M04 recipes are not equivalent to them under simple deterministic diagnostics.

Do not claim that a heuristic is a universal visual-quality metric. M07 owns general quality scoring later.

ChatGPT will manually review the M04 contact sheet.

## 21. Acceptance batch

Run at least **140 deterministic RULES candidates**.

Recommended matrix:

- 7 recipes
- 4 difficulties
- 5 fixed seeds

= 140.

Use representative rectangles.

For every successful candidate assert:

- exact dimensions;
- width×height grid;
- C01..C16 only;
- no BG01;
- exact selected palette fully used;
- zero singleton same-color components under default settings;
- max dominance policy satisfied for that recipe;
- deterministic rerun equality;
- root RNG/provenance coherence.

Target:

- >=120 accepted;
- preferably 140/140 if recipe constraints permit.

If deterministic candidates fail, log them honestly and add fixed candidates to keep >=120 accepted.

## 22. 59×59 performance dependency — PAG-0441

Task text says:

`59×59 generation completes within the V1 performance budget established in M10.`

M10 has not yet established that budget.

Therefore:

- **do not invent a V1 performance budget in M04**;
- benchmark representative 59×59 RULES generation now;
- record machine, sample count, median, p95/worst observed time;
- prove all algorithms are bounded;
- do not mark PAG-0441 complete yourself.

ChatGPT will record PAG-0441 as an explicit **forward dependency on M10 performance-budget establishment** unless a valid owner-approved budget already exists by audit time.

This forward dependency must not be hidden or “passed” against an invented number.

M04 algorithmic acceptance may proceed with PAG-0441 carried as deferred performance confirmation.

## 23. Required tests — primitives

For every primitive:

- exact dimensions;
- deterministic same seed;
- bounded variation;
- rectangular support;
- protected-cell respect;
- no out-of-bounds;
- expected connectivity/topology;
- explicit max-step behavior.

Specific tests:

- BLOB connected;
- ISLAND isolated/connected;
- RING contains bounded interior pocket;
- CORRIDOR connects endpoints;
- POCKET carves negative-space region without protected overwrite;
- SNAKE self-avoiding and max-step bounded;
- BRANCH connected and branch-depth bounded;
- CHAMBER bounded and valid;
- SPIRAL follows discrete connected path/band;
- WAVE deterministic period/amplitude structure;
- RADIAL spokes bounded;
- VORONOI every eligible cell exactly one region and deterministic ties.

## 24. Required tests — operations

At minimum:

- frontier growth connected;
- constrained growth fails boundedly when impossible;
- erosion protects required cells;
- dilation protects forbidden cells;
- hole carving minimum size/no singleton;
- contour exact against fixture;
- nested region contained;
- fragmentation respects min fragment size/max fragments;
- rewrite deterministic scan/order;
- rewrite cannot mutate protected cells;
- every iterative operation obeys explicit cap.

## 25. Required tests — recipes

For all 7 recipes:

- deterministic same request;
- variation across fixed seeds;
- all four difficulty bands collectively;
- rectangles;
- no resize/interpolation;
- protected semantics;
- coherent structure;
- exact palette use after colorization.

Add recipe-specific invariants, e.g.:

- CENTRAL_SUBJECT has clear central occupied region;
- MULTI_ISLAND has >=2 coherent occupied components;
- BORDER_FRAME_EMBLEM touches intended border/frame structure;
- SPARSE_NEGATIVE_SPACE occupancy below documented cap;
- DENSE_FULL_BOARD occupancy above documented floor but not uniform fill.

## 26. Required tests — color regions

At minimum:

- exact palette set equality;
- no BG01;
- no singleton components default;
- min region size;
- max dominance;
- accents connected;
- deterministic recoloring;
- changing colorization domain does not mutate geometry;
- 10..12-color VERY_HARD case remains coherent.

## 27. Offline/security/source-policy regression

All M00-M03 tests must remain green.

M04 production code must:

- run inside `offline_runtime()`;
- import no networking modules;
- add no runtime network dependency;
- use no global random;
- use no Python `hash()` for canonical behavior;
- run no subprocess/shell;
- use no eval/exec;
- deserialize no executable object;
- load no external art/model;
- require no C#/MarkovJunior runtime.

Run source-policy scans against all new production modules.

## 28. Prohibited shortcuts

Do not:

- implement RULES by calling MASK and relabeling the result;
- make primitives wrappers around random board filling;
- copy MarkovJunior rules/models/source;
- use cellular noise/checkerboard as default art;
- generate a small grid then resize;
- interpolate;
- use BG01/None/transparency logical cells;
- drop selected palette IDs;
- add singleton pixels to force color count;
- ignore protected regions;
- add an unsafe/unbounded rewrite loop;
- start WFC;
- start HYBRID/AUTO;
- create M08 production export schema;
- create CLI;
- edit ChatGPT-owned task/tracker/audit state;
- self-audit.

## 29. Required verification before handoff

Run and log:

- all primitive unit tests;
- all operation unit tests;
- all recipe unit tests;
- color-region tests;
- RULES production integration tests;
- primitive golden tests;
- recipe golden tests;
- >=140 deterministic acceptance batch or equivalent >=120 accepted;
- review manifest/contact-sheet validation;
- representative 59×59 benchmark;
- M00-M03 full regression;
- standalone import;
- `pip check`;
- no-network/no-global-random/no-hash/no-subprocess/no-eval source scans;
- `git diff --check`;
- source scan proving no M05+ production implementation.

Record exact totals, deterministic failures/retries, benchmark environment/results, and corrections.

## 30. Builder exit criteria

Builder may stop as **implementation complete / pending independent audit** only when:

- PAG-0401..PAG-0440 and PAG-0442 have implementation/test evidence;
- all 12 primitives have deterministic golden evidence;
- all 7 recipes have deterministic golden evidence;
- RULES production generator is integrated with M02 contracts;
- >=120 deterministic acceptance candidates succeed with zero logical-contract violations;
- default color-region singleton count is zero;
- selected palette is fully used;
- max dominance policy passes;
- review-only M04 evidence is committed;
- 59×59 benchmark evidence is recorded without inventing the future M10 budget;
- M00-M03 regressions remain green;
- no M05+ implementation exists;
- matching builder log is published;
- implementation commit(s), push result, and equality checkpoint are recorded.

Do not mark PAG-0441 complete yourself.

Do not close M04 or begin M05. ChatGPT will perform the independent strict audit, manual review, and tracker update.
