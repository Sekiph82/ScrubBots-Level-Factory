# PAG-M03-C001 — Mask / Sprite Generator

Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M02-C003_RESULT_CONSTRUCTION_BOUNDARY_REMEDIATION_STRICT_AUDIT.md`

Primary conceptual reference:
`https://github.com/zfedoran/pixel-sprite-generator/tree/8c2cee790b0ae5885319181e56745ae45a0f8138`

Verified provenance record:
`THIRD_PARTY_NOTICES.md`

## 1. Objective

Implement and prove **PAG-M03 — Mask / Sprite Generator** only.

M03 must produce original, deterministic, recognizable pixel-art-like logical subjects from project-owned procedural mask/template definitions.

Implement:

- generic 2D mask engine;
- required / forbidden / random mask cells;
- deterministic mask resolution;
- horizontal symmetry;
- optional vertical symmetry;
- asymmetric mode;
- deterministic mutation;
- rectangular-board placement;
- foreground occupancy controls;
- ten SCRUBBOTS-owned template families;
- canonical deterministic region coloring;
- legal difficulty color counts;
- representative review/contact-sheet evidence;
- at least 100 deterministic acceptance candidates.

Do not begin PAG-M04+.

Do not implement RULES, WFC, HYBRID routing, AUTO routing, quality-scoring framework, production artifact/PNG exporter, CLI, Godot integration, solver/gameplay logic, or network/cloud generation.

## 2. Authority and third-party boundary

GitHub is the sole task/prompt/audit authority.

Implementation repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

The zfedoran repository is a **conceptual reference only** for M03:

- masks;
- symmetry;
- silhouette generation;
- seeded mutation concepts.

Do not copy upstream sprite artwork, example images, templates, or sample assets.

For this cycle, prefer an original conceptual reimplementation rather than copying/adapting upstream source code.

If any source is substantially adapted despite that preference:

- stop and identify it explicitly in the Codex log;
- add required immutable provenance/license notice;
- do not represent adapted code as original.

No main `Sekiph82/Scrubbots` repository mutation is allowed.

## 3. Mandatory control-plane read order

Before the first source/product edit, read completely:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. M02 C003 strict audit
9. `THIRD_PARTY_NOTICES.md`
10. current M01 contract modules
11. current M02 request/RNG/generator/result modules
12. M02 golden/determinism tests
13. this prompt

## 4. Mandatory builder log and process-ordering hard gate

Create the matching Codex log **before the first source/product/review-artifact edit**:

`.hiveai/codex-logs/PAG-M03-C001_MASK_SPRITE_GENERATOR_CODEX_LOG.md`

Exact H1:

`# PAG-M03-C001 — Mask / Sprite Generator`

Immediately below:

`Document role: CODEX BUILDER LOG`

The prior M02 audit recorded repeated process finding:

`F-PAG-M02-C003-PROC-001` — source edit occurred before matching log creation.

**Do not repeat it.**

Before any product edit, the builder log must already exist and contain:

- start timestamp;
- authority URLs;
- branch/start HEAD/origin/status;
- synchronization evidence;
- mandatory reads;
- intended M03 architecture.

Then append chronologically:

- exact source/data/review files changed;
- implementation decisions;
- material commands;
- failures and corrections;
- deterministic tests;
- candidate acceptance batch;
- review-manifest/contact-sheet generation;
- full regression;
- provenance confirmation;
- implementation commit SHA(s);
- push/equality checkpoint;
- final changed-file summary.

Do not attempt to write the builder-log commit's own terminal SHA into itself.

If the first source edit happens before the log exists again, record the violation immediately; do not hide it.

## 5. Builder-only boundary

Codex must not:

- independently audit M03;
- declare M03 PASS/CLOSED;
- edit task checkbox/state in `tasks.md`;
- edit `.hiveai/HANDOFF.md`;
- edit `.hiveai/CYCLE_INDEX.md`;
- edit `.hiveai/STATE.json`;
- append acceptance events to `.hiveai/EVENTS.jsonl`;
- create/edit `.hiveai/audits/**`;
- begin M04+ implementation.

ChatGPT owns acceptance and tracker transitions.

## 6. Core integration contract

M03 must use the existing M02 core rather than invent a parallel pipeline.

Production generator must implement:

`PixelGenerator`

Expected production class conceptually:

`MaskSpriteGenerator`

with stable identifiers, for example:

- `generator_id = "mask-sprite"`
- `generator_version = "1.0.0"`

Exact identifier strings may differ if documented and stable.

### Request mode

The production mask generator accepts only:

`GeneratorMode.MASK`

If passed RULES/WFC/HYBRID, fail explicitly and deterministically.

Do not silently route to another engine.

### Explicit RNG ownership

`generate(request, rng)` must use the project-owned `DeterministicRNG`.

Do not create module-global/random entropy.

The generator must verify or otherwise ensure that the supplied RNG corresponds to the request master seed.

A straightforward accepted check is:

`rng.stage_seeds() == DeterministicRNG(request.seed).stage_seeds()`

If the supplied RNG is not coherent with the request seed, fail closed rather than generating irreproducible output.

### Stage usage

Use named stage/domain separation deliberately:

- geometry stage for mask/template resolution;
- colorization stage for palette/region assignment;
- child domains under those stages for family selection, mutation, placement, region growth, etc.

Do not derive behavior from call-order coupling between unrelated stages.

### Result

Successful generation must return only:

`GenerationResult.success(...)`

with:

- resolved legal dimensions;
- full row-major C01..C16 logical grid;
- exact legal used palette;
- MASK mode;
- stable generator ID/version;
- project RNG algorithm;
- authenticated stage provenance.

Failures must return:

`GenerationResult.failure(...)`

with stable bounded reason/code and no partial production grid.

## 7. Critical negative-space contract

M03's internal mask may distinguish:

- foreground/occupied subject cells;
- negative-space/background-classification cells.

However, **final `GenerationResult.logical_grid` has no empty cell concept.**

Every final board cell is a gameplay cell and must contain exactly one canonical logical C-ID C01..C16.

Therefore:

- BG01 is never written to the logical grid;
- alpha/transparency is never written to the logical grid;
- `None` is never a logical cell;
- no special BACKGROUND logical ID may be invented;
- internal negative-space cells must be colored with one of the selected canonical C01..C16 palette IDs;
- that canonical negative-space color counts as an actually used gameplay color.

This internal mask distinction exists only to create visual negative space, not to create non-gameplay cells.

Do not conflate presentation BG01 with internal stylistic negative space.

## 8. PAG-S03.1 — Generic mask engine

Implement tasks `PAG-0301..PAG-0310`.

Suggested package shape:

```text
src/scrubbots_pixel_factory/generators/
  __init__.py
  mask/
    __init__.py
    model.py
    engine.py
    templates.py
    colorize.py
    generator.py
```

Exact filenames may differ if separation is cleaner.

### 2D logical mask representation

Create a deterministic target-board logical mask representation.

Required conceptual cell states:

- REQUIRED foreground;
- FORBIDDEN foreground;
- RANDOM/OPTIONAL.

Names may differ but semantics must be explicit.

The resolved mask should be immutable or treated as immutable after construction.

At minimum expose deterministic operations/tests for:

- get/index;
- dimensions;
- foreground boolean/classification;
- row-major representation.

### Required / forbidden / random semantics

- REQUIRED must remain foreground.
- FORBIDDEN must remain negative-space.
- RANDOM resolves only through project deterministic RNG.
- mutation must never violate hard REQUIRED/FORBIDDEN constraints.

### Seeded resolution

Same:

- request;
- template;
- config;
- RNG stage seed

must yield identical resolved mask.

No Python global `random`.
No `hash()`.
No time/UUID entropy.

### Symmetry semantics

Document exact geometry meaning.

For this project:

- **HORIZONTAL** means left/right mirror symmetry across the board/template vertical centerline;
- **VERTICAL** means top/bottom mirror symmetry across the horizontal centerline;
- **HORIZONTAL_VERTICAL** may combine both;
- **ASYMMETRIC** means no forced reflection.

Equivalent enum naming is allowed only if tests make semantics unambiguous.

Support:

- odd widths;
- even widths;
- odd heights;
- even heights;
- rectangular boards.

No interpolation or image resize.

### Deterministic mutation

Provide bounded mutation amount.

Mutation must:

- use project RNG;
- operate only on mutable/random-capable cells;
- be deterministic;
- preserve hard template constraints;
- preserve board dimensions;
- remain bounded by explicit count/rate;
- never loop without a deterministic bound.

Prefer integer mutation controls rather than floating behavior sensitive to platform details.

### Placement / centering

Template-family geometry must be placed inside requested dimensions using integer logical coordinates.

Requirements:

- subject remains in bounds;
- support rectangular boards;
- deterministic center/offset behavior;
- optional deterministic bounded offset is allowed;
- no resampling;
- no interpolation;
- no “generate at one size then scale image.”

### Foreground occupancy controls

Occupancy means:

`foreground-mask-cell-count / total-board-cell-count`

It does not mean “all non-BG01 cells,” because final grid contains no BG01.

Implement floor/ceiling controls that:

- fail/retry boundedly when impossible;
- do not silently violate hard template constraints;
- are deterministic;
- are independently testable.

## 9. PAG-S03.2 — SCRUBBOTS-owned template families

Implement tasks `PAG-0311..PAG-0325`.

Required families:

1. `ROBOT`
2. `CREATURE`
3. `FISH`
4. `SEA_CREATURE` covering octopus/sea-creature intent
5. `SPACE_SHIP`
6. `INSECT` covering butterfly/insect intent
7. `FACE_EMBLEM`
8. `TREE_PLANT`
9. `CORAL`
10. `ABSTRACT_SYMBOL`

Names may differ only slightly if mapped clearly to the ten task families.

### Ownership

Every template definition must be newly authored for SCRUBBOTS.

Do not trace or transcribe third-party sprites.

Do not convert upstream sample artwork into masks.

Do not use external image files as template source.

### Template representation

Templates should be procedural/parametric logical definitions, not source bitmaps requiring resizing.

Good approaches include combinations of original:

- integer anchors;
- boxes/zones;
- stems/limbs;
- lobes;
- appendages;
- chambers;
- outlines;
- center axes;
- deterministic rule functions.

Final mask is generated directly at target dimensions.

### Multiple seeds

Every family must vary deterministically across multiple seeds.

Tests must show a fixed multi-seed set produces more than one resolved mask per family.

Do not claim every pair of seeds must differ.

### All legal difficulty dimensions

Every family must work across all production difficulty bands and representative rectangles.

Minimum automated family matrix:

- EASY: at least 20×20 and 29×23
- MEDIUM: at least 30×39 and 37×32
- HARD: at least 40×49 and 48×41
- VERY_HARD: at least 50×59 and 59×50

No family may assume square boards.

### Logical scaling

A family may derive logical feature lengths from board dimensions using integer arithmetic.

It must not:

- rasterize a small source sprite and scale it;
- call an image resize;
- interpolate;
- antialias.

### Negative space

Every family must support nonzero internal negative-space area.

The subject cannot accidentally occupy the full board for all seeds/configurations.

### Non-empty subject

Every accepted mask must contain at least one foreground cell and satisfy its occupancy bounds.

## 10. Style/family selection

M03 may use `GenerationRequest.style` as the explicit family selector.

Recommended strict values are the ten family names above.

Requirements:

- exact known family name → select that family;
- unknown style → explicit failure;
- `style=None` → choose a family deterministically from the ten families using a named geometry child stream;
- same request/seed → same family;
- family selection must not depend on dictionary/set order.

Do not create the broad future art-style catalog in M03.

### Theme

M03 does not yet define thematic generation.

If `request.theme` is non-None, either:

- explicitly reject it as unsupported in MASK V1, preferred; or
- support a narrowly documented deterministic semantic that does not widen scope.

Do not silently ignore a supplied theme.

## 11. Generator options

Do not create an unbounded options jungle.

Accept either:

- default empty options; or
- a strict MASK namespace/version with a small documented field set.

Potential M03 options may include:

- symmetry mode;
- mutation amount;
- bounded placement offset;
- foreground occupancy floor/ceiling.

Requirements:

- unknown option keys fail closed;
- wrong option types fail closed;
- unsupported namespace/version fail closed;
- options remain deeply immutable through M02 request contract;
- all options participate deterministically in output.

Do not add M04/M05-specific options.

## 12. PAG-S03.3 — Region coloring

Implement tasks `PAG-0326..PAG-0333`.

### Palette source

Resolve the M03 palette only through:

`request.resolve_palette_subset()`

The final accepted result must actually use **every** ID in that resolved subset exactly at least once.

Do not choose an extra color outside the resolved subset.

### Negative-space color

Choose one canonical ID from the resolved subset as the internal negative-space/base color using deterministic colorization logic.

It:

- is still a gameplay color;
- counts in actual used palette;
- is not BG01;
- is not transparent.

### Foreground region coloring

Color foreground subject cells with the remaining palette using coherent regions.

Requirements:

- exactly the legal requested/resolved palette is actually used;
- avoid default checkerboard/salt noise;
- avoid isolated single-pixel color salt unless an explicit supported option requests accents;
- prefer connected or spatially coherent regions;
- deterministic region seeds/growth;
- no off-palette colors;
- no RGB operations required in the logical grid.

### Semantic color roles

Support logical roles such as:

- negative_space/base;
- outline;
- body/primary;
- secondary;
- detail/accent.

Roles map only to selected canonical C-IDs.

Do not encode semantic roles into gameplay cell values; logical cells remain C-IDs only.

### Requested palette cardinality

Difficulty legality is already enforced by M01.

M03 must additionally ensure every selected ID actually appears in the final grid.

If a generated geometry cannot support the selected palette coherently, fail/retry deterministically within a bounded M03 attempt policy rather than silently dropping a color.

### Deterministic recoloring

Given identical geometry + selected palette + colorization seed/config:

- recoloring is byte-identical.

Changing only the colorization domain may change color layout without changing foreground geometry.

Add a test proving geometry preservation under deterministic recoloring where architecturally appropriate.

## 13. Deterministic bounded generation / retry behavior

M03 must never loop indefinitely while chasing occupancy or coloring constraints.

Define a small explicit maximum internal attempt count.

Attempt `n` must derive from project retry/domain machinery deterministically.

Same request and same attempt policy must reproduce:

- same attempt sequence;
- same accepted candidate or same failure.

Do not make success depend on wall-clock timing.

When retries are used, include authenticated deterministic retry provenance in the final success result where applicable.

## 14. M03 production generator failure semantics

Return explicit `GenerationResult.failure` for bounded generation failures.

Use stable M02 failure codes.

Examples:

- invalid MASK-specific option/style/theme → `INVALID_REQUEST`;
- deterministic geometry cannot satisfy hard contract within bounded attempts → `RETRY_EXHAUSTED`;
- internal invariant violation → `CONTRACT_VIOLATION`.

Reasons must be deterministic strings without exception memory addresses or machine paths.

Do not leak partial grid as failure output.

## 15. Required unit tests — generic mask engine

At minimum prove:

- REQUIRED always foreground;
- FORBIDDEN always negative-space;
- RANDOM deterministic for same seed;
- random/mutation variation across selected seeds;
- mutation never violates required/forbidden;
- horizontal symmetry for odd/even widths;
- vertical symmetry for odd/even heights;
- combined symmetry;
- asymmetric mode does not forcibly mirror;
- rectangle support;
- in-bounds placement;
- deterministic centering/offset;
- occupancy floor;
- occupancy ceiling;
- impossible occupancy fails boundedly;
- zero-sized/illegal board state cannot enter engine through production request contract.

## 16. Required unit tests — template families

For each of the ten families:

- deterministic same-seed result;
- more than one mask across a fixed multi-seed set;
- non-empty foreground;
- nonzero negative space;
- required representative dimension matrix;
- no interpolation/resize dependency;
- no external artwork file dependency.

At least one automated test must iterate all ten families across all four difficulties.

## 17. Required unit tests — coloring

At minimum prove:

- final grid length = width × height;
- every cell C01..C16;
- no BG01;
- no `None`/alpha/background sentinel;
- actual used palette equals resolved palette exactly;
- all requested palette IDs appear;
- used-color count legal for difficulty;
- deterministic colorization;
- negative-space cells use canonical selected color;
- semantic roles introduce no extra colors;
- default coloring avoids pathological one-pixel salt on fixed fixtures;
- recoloring preserves geometry classification.

## 18. M03 production integration tests

Add integration tests for `MaskSpriteGenerator`.

Required:

- implements `PixelGenerator`;
- accepts only MASK request mode;
- mismatched supplied RNG fails closed;
- style selection explicit;
- style=None deterministic family selection;
- unsupported style fails;
- unsupported theme behavior explicit;
- legal rectangles across all difficulties;
- explicit width/height preserved exactly;
- explicit palette subset preserved exactly as actual used palette;
- auto palette subset legal and fully used;
- same request + same RNG = byte-identical `GenerationResult.canonical_bytes()`;
- different fixed seeds produce multiple logical grids;
- authenticated provenance accepted by M02 result contract;
- offline runtime compatibility.

## 19. Acceptance batch — PAG-0334 / PAG-0335

Run a fixed deterministic batch of **at least 120 candidates**, so the 100-candidate minimum has margin.

Recommended matrix:

- 10 families
- 4 difficulties
- 3 fixed seeds each

= 120 candidates.

The batch must include representative rectangles, not only squares.

For every accepted candidate assert:

- success;
- legal difficulty dimensions;
- exact width × height cells;
- only C01..C16;
- no BG01;
- legal actual used-color count;
- actual used palette equals resolved palette;
- non-empty foreground classification;
- nonzero negative-space classification;
- deterministic rerun equality.

Acceptance requirement:

**0 accepted candidates may violate dimension or palette contracts.**

If some fixed candidate deterministically fails generation, record it as failure and generate enough additional fixed candidates to maintain at least 100 accepted candidates. Do not hide failures.

## 20. Human review evidence — PAG-0336

M03 requires manual visual review evidence before independent audit closure.

Create review-only evidence under:

`review/m03/`

Required:

### `review/m03/m03_review_manifest.json`

A review-only, explicitly non-production manifest containing at least **40 representative accepted candidates**:

- all 10 families represented;
- all 4 difficulties represented;
- multiple seeds represented;
- candidate label;
- family;
- seed;
- difficulty;
- width;
- height;
- resolved palette;
- foreground mask/classification;
- final row-major C-ID grid.

This is **not** the M08 production artifact schema.

Label it clearly as:

`review-only / non-production / M03 manual audit evidence`.

### Self-contained contact sheet

Generate:

`review/m03/M03_MASK_CONTACT_SHEET.html`

Requirements:

- no CDN;
- no network;
- self-contained;
- visually renders the representative manifest candidates;
- uses exact canonical palette colors;
- nearest/integer block presentation only;
- labels family, seed, difficulty, dimensions, palette;
- no production PNG/export API;
- no claim that presentation rendering is the logical source artifact.

The contact sheet is audit/review evidence only.

The builder must not self-certify “recognizable.” ChatGPT will perform the independent/manual review from the committed manifest/contact-sheet evidence.

## 21. Review recognizability target

The ten families should be visually distinguishable by original structural cues, for example:

- ROBOT: body/head/limb structure;
- CREATURE: torso/head/appendage silhouette;
- FISH: body/tail/fin cues;
- SEA_CREATURE: central body + tentacle/appendage cues;
- SPACE_SHIP: hull/nose/wing or thruster cues;
- INSECT: body axis + paired wing/leg cues;
- FACE_EMBLEM: face/emblem symmetry and feature cues;
- TREE_PLANT: trunk/stem + crown/branch cues;
- CORAL: rooted branching organic structure;
- ABSTRACT_SYMBOL: deliberate emblem/symbol geometry rather than random noise.

These are structural targets, not copied sprite designs.

Do not hardcode one identical silhouette per family for every seed.

## 22. Determinism / golden evidence

Add compact M03 golden fixtures for at least one fixed candidate from each family.

Preferred fixture contents:

- request/config;
- family;
- dimensions;
- resolved palette;
- foreground-mask SHA-256;
- final logical-grid SHA-256;
- canonical `GenerationResult` SHA-256.

At least 10 family goldens total.

Do not commit giant duplicate full-grid golden files if review manifest already contains representative grids; hashes are enough for golden drift detection.

## 23. Performance sanity

M03 does not own the final M10 performance budget, but generation must be bounded.

Add a non-flaky sanity test or logged benchmark for representative 59×59 MASK generation.

Do not set an arbitrary hard acceptance millisecond budget yet.

Record:

- machine/environment;
- sample count;
- median/typical timing;
- worst observed timing in the builder run.

This is measurement only, not the final performance contract.

## 24. Offline/security regression

All M00/M01/M02 tests must remain green.

M03 production code must:

- operate within `offline_runtime()`;
- import no networking modules;
- introduce no runtime network dependency;
- use no global `random`;
- use no Python `hash()` for output;
- execute no shell/subprocess;
- load no remote asset;
- deserialize no executable object;
- use no copied third-party art.

Run existing source-policy tests against all new production modules.

## 25. Prohibited shortcuts

Do not:

- fill the board with uniform random C-IDs and call it sprite generation;
- generate normal-resolution images and pixelate/resize them;
- use image libraries to interpolate geometry;
- use BG01 or transparency as logical cells;
- invent C17+;
- count colors that do not actually appear;
- drop requested palette colors silently;
- copy zfedoran sprite/template artwork;
- add third-party exemplar art;
- start M04 rule primitives;
- start WFC;
- start HYBRID/AUTO router;
- create M08 production exporter/schema;
- create M09 CLI;
- edit ChatGPT-owned tracker/audit state;
- self-audit recognizability.

## 26. Required verification before handoff

Run and log:

- generic mask-engine focused tests;
- template-family focused tests;
- coloring focused tests;
- MASK production integration tests;
- at least 10 M03 golden tests;
- fixed >=120 acceptance batch with >=100 accepted;
- zero accepted palette/dimension violations;
- review manifest generation/validation;
- contact-sheet generation;
- full repository pytest regression;
- standalone package import;
- `pip check`;
- no-network/no-global-random/no-subprocess static scan;
- `git diff --check`;
- source scan proving no M04+ production modules.

Record exact totals, deterministic failures/retries, and corrections.

## 27. M03 builder exit criteria

The builder may stop as **implementation complete / pending independent audit** only if:

- `PAG-0301..PAG-0335` have implementation/test evidence;
- at least 100 accepted deterministic candidates exist in the acceptance run;
- zero accepted candidates violate dimension/palette contracts;
- all ten families are represented and deterministic;
- review-only manifest/contact sheet is committed for PAG-0336;
- every resolved/requested palette ID appears in accepted final grid;
- no BG01/transparency/off-palette cell exists;
- M00/M01/M02 regressions remain green;
- no M04+ implementation exists;
- matching builder log is published;
- implementation commit(s), push result, and equality checkpoint are recorded.

Do **not** mark PAG-0336 complete yourself. Recognizability/manual contact-sheet acceptance belongs to ChatGPT independent audit.

Do not close M03 or advance M04. ChatGPT will independently inspect source/tests, reproduce deterministic samples where possible, render/review the committed review manifest, and decide PASS/FAIL.
