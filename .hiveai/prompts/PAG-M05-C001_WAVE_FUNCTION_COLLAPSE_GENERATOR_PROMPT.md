# PAG-M05-C001 — Wave Function Collapse Generator

Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M04-C002_GEOMETRY_FIDELITY_OPERATION_SEMANTICS_AND_RECIPE_DIVERSITY_REMEDIATION_STRICT_AUDIT.md`

Primary WFC implementation reference:
`https://github.com/ikarth/wfc_2019f/tree/3a937fed13934722377dd7fb6dd238518fa644dd`

Secondary canonical algorithm reference:
`https://github.com/mxgmn/WaveFunctionCollapse/tree/de7d22e705e816b62b4d613199d0463820fcaef3`

Verified provenance:
`THIRD_PARTY_NOTICES.md`

## 1. Objective

Implement and prove **PAG-M05 — Wave Function Collapse Generator** only.

M05 must provide a deterministic, offline, project-owned overlapping-pattern WFC engine that:

- learns local logical pattern language from approved/injected exemplars;
- operates entirely on logical C01..C16 cell arrays;
- generates exactly the requested logical width/height;
- supports rectangles;
- uses only the project deterministic RNG;
- handles contradiction/retry deterministically and with explicit bounds;
- supports N=2 and N=3;
- supports N=4 only as explicit experimental configuration;
- supports configurable input/output periodicity;
- supports controlled rotation/reflection transforms;
- never introduces unseen/off-palette colors;
- deterministically maps exemplar symbols to the request palette;
- rejects outputs that fail the exact logical palette contract;
- carries reproducible WFC/exemplar/config metadata outside the M02 canonical result schema where appropriate.

Do not begin M06 HYBRID/AUTO, M07 quality filters, M08 production export schema, M09 CLI, Godot integration, solver/gameplay logic, or cloud/network generation.

## 2. Authority and third-party boundary

GitHub is the sole task/prompt/audit authority.

Implementation repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

The pinned upstream WFC repositories are software references only.

### Preferred implementation policy

For M05, prefer a **project-owned conceptual reimplementation** of overlapping-pattern WFC in Python.

Do not vendor an upstream repository.

Do not copy:

- upstream sample images;
- sample tiles;
- demo assets;
- GUI code;
- logging/demo harnesses;
- project-specific exemplar artwork.

If substantial upstream source is adapted:

1. identify exact upstream repository/commit/file in the builder log;
2. add a provenance comment to every adapted production module;
3. update `THIRD_PARTY_NOTICES.md` with exact adaptation details;
4. preserve the applicable MIT notice;
5. keep all upstream sample artwork excluded.

If the implementation is original/conceptual, explicitly record that no upstream source was copied/adapted and leave the software references as reference-only.

## 3. Mandatory builder log

Create **before the first source, test, exemplar fixture, golden, manifest, contact-sheet, or documentation edit**:

`.hiveai/codex-logs/PAG-M05-C001_WAVE_FUNCTION_COLLAPSE_GENERATOR_CODEX_LOG.md`

Exact H1:

`# PAG-M05-C001 — Wave Function Collapse Generator`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- start timestamp;
- authority URLs;
- pinned upstream reference commits/licenses;
- starting branch/HEAD/origin/ahead-behind/status;
- safe synchronization;
- mandatory reads;
- source-copy/adaptation decision;
- exact WFC architecture;
- exemplar schema/ownership design;
- files changed;
- commands;
- failed tests/contradictions and corrections;
- pattern extraction evidence;
- adjacency/propagation evidence;
- palette mapping evidence;
- retry determinism;
- acceptance batch;
- golden/review evidence;
- 59×59 benchmark;
- full regression;
- provenance/license confirmation;
- implementation commit SHA(s);
- push/equality checkpoint;
- final changed-file summary.

Do not self-audit. Do not modify ChatGPT-owned task/tracker/audit acceptance state.

## 4. Mandatory read order

Before implementation, read completely:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. M04 C002 strict audit
9. `THIRD_PARTY_NOTICES.md`
10. M01 canonical contracts
11. M02 request/RNG/generator/result contracts
12. current M03/M04 generator integration patterns only as shared-contract examples
13. this prompt

Do not mutate M03/M04 behavior merely to implement WFC.

## 5. Production package shape

Create an independent WFC package, conceptually:

```text
src/scrubbots_pixel_factory/generators/wfc/
  __init__.py
  model.py
  exemplar.py
  patterns.py
  solver.py
  generator.py
```

Exact filenames may differ if architecture is clearer.

Expected conceptual flow:

```text
GenerationRequest(WFC)
        |
        v
canonical root DeterministicRNG
        |
        v
approved/injected Exemplar
        |
        v
explicit source->request palette mapping
        |
        v
N×N pattern extraction + transforms
        |
        v
adjacency compatibility table
        |
        v
bounded deterministic WFC solve
        |
        v
exact requested logical grid
        |
        v
palette/cardinality validation
        |
        v
validated GenerationResult.success()
```

## 6. PAG-S05.1 — WFC isolation

Implement tasks `PAG-0501..PAG-0510`.

### PAG-0501 — pinned upstream reference

The exact primary reference is already verified:

`ikarth/wfc_2019f@3a937fed13934722377dd7fb6dd238518fa644dd`

Do not replace it with a moving branch reference.

### PAG-0502 — minimum WFC modules

Implement only the concepts required for:

- pattern extraction;
- pattern frequency;
- pattern transforms;
- adjacency compatibility;
- wave state;
- observation;
- propagation;
- contradiction;
- reconstruction.

No GUI/demo/application framework.

### PAG-0503 — no irrelevant dependencies

M05 must not add:

- pygame;
- Qt;
- Pillow as a runtime WFC requirement;
- GUI/log viewer;
- Jupyter runtime;
- cloud SDK;
- network client.

Prefer zero new runtime dependencies.

### PAG-0504 — PixelGenerator integration

Production class:

`WFCGenerator`

or equivalently clear name.

Must implement `PixelGenerator`.

Stable identity, e.g.:

- `generator_id = "wfc-overlap"`
- `generator_version = "1.0.0"`

### PAG-0505 — in-memory logical arrays

WFC solver consumes exemplar logical C-ID arrays in memory.

The solver must not:

- open arbitrary image files;
- scrape network exemplars;
- load URLs;
- invoke external applications.

Production exemplar loading may use an explicitly approved local registry, but request data must never contain arbitrary filesystem paths.

### PAG-0506 — exact requested output dimensions

Final `GenerationResult` must be exactly:

`request.resolve_dimensions()`

No crop-as-fix.
No resize.
No scale.
No interpolation.

### PAG-0507 — no resampling

Static/source tests should prohibit resize/resample/interpolation calls in WFC production code.

### PAG-0508 — project RNG only

Use only `DeterministicRNG`.

Top-level supplied RNG must satisfy the now-established generator rule:

- exact project RNG type;
- domain = `"root"`;
- stage seeds equal `DeterministicRNG(request.seed).stage_seeds()`.

No RNG supplied -> construct exactly `DeterministicRNG(request.seed)`.

No `random`, `secrets`, UUID entropy, timestamps, or Python `hash()`.

### PAG-0509 — deterministic contradiction/retry

Contradictions must have stable machine-readable reasons.

A contradiction cannot trigger an uncontrolled ad hoc reset.

Attempt N must derive from:

`root.retry_rng(N)`

and must not depend on random consumption from previous failed attempts.

### PAG-0510 — retry bound

Default maximum attempts:

recommended 4.

If configurable, cap it at a small fixed upper bound such as 8.

No unbounded solve/restart loops.

## 7. Exemplar production/test ownership boundary

This boundary is critical.

### Production owner exemplars

Do **not** invent or fabricate SCRUBBOTS owner artwork for M05.

Create an intentionally empty owner exemplar path:

```text
exemplars/
  README.md
  inbox/
    .gitkeep
```

The README must state:

- inbox content is owner-supplied candidate material only;
- nothing becomes an approved production exemplar merely by being dropped there;
- exemplars require provenance/contract validation;
- external upstream WFC sample images are forbidden as SCRUBBOTS exemplars;
- no current owner exemplar ships in M05.

Do not commit third-party sample artwork to this path.

### Synthetic test exemplars

Create legal **test-only synthetic logical exemplars** under:

`tests/fixtures/wfc/`

They must be explicitly labeled:

- synthetic;
- unit/integration-test only;
- not SCRUBBOTS owner art;
- not production exemplar content.

These fixtures may be simple logical motifs generated/authored as test data.

They must use canonical C01..C16 IDs only.

## 8. PAG-S05.2 — exemplar contract

Implement tasks `PAG-0511..PAG-0517`.

### Exemplar metadata schema

Define an immutable/versioned exemplar model.

Required metadata:

- schema/version;
- exemplar_id;
- role;
- width;
- height;
- row-major logical pixels;
- source/provenance type;
- source/provenance description;
- ownership/use classification;
- optional approved-by metadata field reserved for future owner workflow.

Suggested roles:

- `TRAINING_MOTIF`
- `PRODUCTION_ARTIFACT`

Production approval status is independent from role.

### Allowed ownership/use classifications

At minimum distinguish:

- `SYNTHETIC_TEST_ONLY`
- `OWNER_SUPPLIED_UNAPPROVED`
- `OWNER_APPROVED`

Production generator default registry must not treat `SYNTHETIC_TEST_ONLY` as owner-approved production art.

Tests may inject a test registry containing synthetic exemplars.

### Explicit source/provenance

Every exemplar requires source/provenance metadata.

Reject missing provenance.

### Canonical logical pixels

M05 exemplar pixels must be exact logical C01..C16 IDs.

Do not accept antialiased RGB raster input directly in the WFC core.

Any input that is:

- unknown C-ID;
- BG01;
- transparency sentinel;
- RGB/HEX pixel array masquerading as logical IDs;
- interpolated/resampled source

must fail exemplar validation.

This exact logical-only policy satisfies PAG-0513/PAG-0514 for V1.

### Dimension semantics

For `PRODUCTION_ARTIFACT` role:

- if intended as a game artifact, enforce production difficulty dimension legality through explicit metadata/context.

For `TRAINING_MOTIF`:

- allow smaller motifs such as 4×4, 6×6, 8×8;
- require dimensions large enough for configured pattern N;
- clearly separate these from production artifact dimensions.

### No external sample ownership confusion

Never mark:

- ikarth samples;
- mxgmn samples;
- other GitHub images

as SCRUBBOTS-owned/approved exemplars.

### Empty inbox

Create the documentation/inbox path rather than fabricated production exemplars.

## 9. Exemplar registry

Implement an immutable/injected registry abstraction.

Suggested:

`ExemplarRegistry`

Responsibilities:

- lookup by exact exemplar_id;
- deterministic ordered listing;
- ownership/approval filtering;
- no arbitrary path traversal;
- no network lookup.

Production `WFCGenerator()` may default to an empty approved registry in M05.

Tests may instantiate:

`WFCGenerator(registry=test_registry)`

with synthetic exemplars.

Request `style` should select exemplar ID.

Rules:

- known allowed exemplar -> use it;
- unknown exemplar -> `INVALID_REQUEST`;
- no style when registry has exactly one eligible exemplar may optionally select it deterministically;
- otherwise require explicit exemplar selection.

Do not use M03/M04 style names as WFC exemplars.

## 10. PAG-S05.3 — WFC configuration

Implement tasks `PAG-0518..PAG-0525`.

Use strict:

- generator options namespace `"wfc"`
- version `1`.

Recommended supported keys:

- `pattern_size`
- `input_periodic`
- `output_periodic`
- `allow_rotations`
- `allow_reflections`
- `experimental_n4`
- `max_attempts`
- optional `palette_mapping`

Unknown keys fail closed.

### N=2

Fully supported.

### N=3

Fully supported.

### N=4

Allowed only when:

- `pattern_size == 4`
- `experimental_n4 == true`.

N=4 must not be default.

Benchmark it separately if used.

### Input periodicity

If true:

- extract N×N patterns at every exemplar cell;
- wrap exemplar coordinates.

If false:

- extract only fully in-bounds N×N windows.

### Output periodicity

If true:

- output pattern-placement adjacency wraps around output boundaries.

If false:

- no output wrap.

Both modes must still reconstruct exact requested dimensions.

### Rotation/reflection controls

Transforms must be deterministic integer matrix transforms only.

If rotations are enabled:

- include 0°, 90°, 180°, 270° transforms where dimensions/pattern square N×N permit.

If reflections are enabled:

- include mirror transforms in addition to selected rotations.

Deduplicate transformed patterns by exact tuple equality.

Pattern frequency accumulation must be deterministic.

### Config metadata

Record a canonical WFC metadata object in `WFCCandidate` and review/golden evidence.

At minimum include:

- schema/version;
- exemplar ID;
- exemplar provenance identity;
- pattern size;
- input periodic;
- output periodic;
- rotations/reflections flags;
- experimental N4 flag;
- max attempts;
- source palette;
- target palette;
- explicit resolved source->target mapping;
- extracted pattern count;
- unique transformed pattern count;
- attempt used;
- contradiction history/reasons.

Do not widen M02 result provenance arbitrarily.

The GenerationResult already embeds the canonical request, which records WFC options. Candidate metadata supplies WFC-specific sidecar evidence until M08 defines production artifact metadata.

### Reject impossible palette config

Before solve:

- source exemplar distinct symbol count must equal target requested palette subset count for V1 one-to-one mapping;
- explicit mapping must be one-to-one;
- target values must exactly equal request resolved palette;
- source values must exactly equal exemplar used C-IDs;
- duplicates/missing/extra mapping entries fail.

Do not silently merge two source symbols into one target color in M05 V1.

## 11. Explicit deterministic palette mapping

Implement PAG-0527 before pattern extraction.

### Default mapping

If no mapping option is supplied:

1. sort source exemplar C-IDs by numeric C index;
2. sort request resolved palette by numeric C index;
3. require equal cardinality;
4. pair positionally;
5. record the complete mapping.

Example:

```text
source: C01 C04 C11
target: C03 C09 C16

mapping:
C01 -> C03
C04 -> C09
C11 -> C16
```

### Explicit mapping

If supplied, require a complete immutable mapping.

No implicit nearest-color logic.
No RGB distance.
No palette guessing.

Apply mapping to the exemplar logical array **before** pattern extraction.

Consequences:

- solver patterns contain only requested target C-IDs;
- WFC can never introduce an off-request color through reconstruction.

## 12. Pattern extraction

Create immutable pattern representation.

For each unique N×N pattern record:

- exact tuple of mapped C-IDs;
- frequency/weight;
- stable integer pattern ID based on deterministic sorted canonical ordering, not hash randomization.

Pattern IDs must not depend on Python set iteration.

Preferred canonical sort:

lexicographic tuple of C-ID numeric indices.

### Minimum validation

Reject:

- exemplar width/height smaller than N in non-periodic extraction;
- no extracted patterns;
- invalid N;
- patterns containing any C-ID outside target palette.

## 13. Adjacency compatibility

Precompute exact 4-neighbor compatibility:

- LEFT
- RIGHT
- UP
- DOWN

Two patterns are compatible in a direction iff their N−1 overlapping columns/rows match exactly.

No fuzzy comparison.

No RGB comparison.

Compatibility tables must:

- be immutable/canonically ordered;
- contain only known pattern IDs;
- be deterministic across processes.

Add focused fixtures with manually obvious compatible/incompatible pattern pairs.

## 14. Solver architecture

Use a bounded overlapping-pattern WFC solver.

### Wave

Each pattern placement cell holds an allowed set/tuple of pattern IDs.

Do not expose mutable wave state outside solver internals.

### Observation

Select an unresolved placement with minimum allowed-pattern cardinality.

Avoid floating-point Shannon entropy for V1 unless there is a compelling reason.

Preferred deterministic selection:

1. find minimum allowed-count >1;
2. collect placement indices in ascending row-major order;
3. use project RNG child/stream to choose among tied cells.

### Weighted pattern choice

Use integer pattern frequencies.

Choose pattern with deterministic integer cumulative weights using `randbelow(total_weight)`.

No float probabilities required.

### Propagation

Use a deterministic queue.

For each changed placement:

- inspect four placement neighbors;
- apply output periodicity wrap only when configured;
- remove patterns lacking compatible support;
- enqueue changed neighbors deterministically.

Contradiction:

- any placement reaches zero allowed patterns.

### Bounds

Each attempt must have explicit upper bounds based on:

- number of placements;
- number of patterns;
- finite removals.

No infinite propagation loop.

Add internal counters if useful for audit metadata.

## 15. Placement grid and exact reconstruction

### Non-periodic output

For requested logical:

`W × H`

and pattern size N:

placement grid:

`(W - N + 1) × (H - N + 1)`

Require W,H >= N.

After complete collapse:

- reconstruct each output cell from every covering placement;
- all covering pattern values must agree;
- disagreement is a `CONTRACT_VIOLATION`;
- every output cell must be covered;
- final output is exactly W×H.

### Periodic output

Placement grid:

`W × H`

with wrapped adjacency.

Reconstruct output deterministically from the collapsed periodic pattern field.

A simple valid method is to use each placement pattern's top-left symbol for its corresponding output cell, provided overlap consistency has been enforced globally.

Tests must prove periodic seam consistency.

No post-solve resizing/cropping.

## 16. Contradiction and retry metadata

Define stable contradiction codes/reasons, conceptually:

- EMPTY_WAVE
- RECONSTRUCTION_CONFLICT
- PALETTE_CARDINALITY_MISMATCH
- EXHAUSTED_ATTEMPTS

Exact enums may differ.

Do not use exception repr as canonical reason.

For every failed attempt record deterministic metadata:

- attempt index;
- contradiction code;
- optional placement index;
- stable detail fields.

Final failure after max attempts:

`GenerationResult.failure(FailureCode.RETRY_EXHAUSTED, ...)`

No partial logical grid.

Successful result candidate records prior failed attempt metadata if any.

## 17. PAG-S05.4 — palette/output enforcement

Implement tasks `PAG-0526..PAG-0530`.

### No unseen colors

Because mapping happens before extraction, all patterns must use target requested palette only.

Final grid must satisfy:

`set(grid) <= set(request.resolve_palette_subset())`

### Exact distinct color count

M05 acceptance is stricter:

`set(grid) == set(request.resolve_palette_subset())`

If WFC collapses to a legal local pattern arrangement but omits one target color:

- reject that attempt;
- record stable rejection reason;
- retry deterministically.

Do not inject a missing color afterward.

### Reject rather than repair

Do not:

- recolor random cells;
- append accents;
- merge regions;
- resize;
- repair palette count after solve.

Only a naturally generated contract-valid output is accepted.

### Reasons

Record contradiction/rejection reason metadata in `WFCCandidate`/attempt history.

## 18. Synthetic/unit-test exemplars

Create at least **four** legal synthetic test exemplars so the WFC core is exercised across palette cardinalities.

Recommended:

1. EASY motif using 3 canonical source symbols;
2. MEDIUM motif using 6 symbols;
3. HARD motif using 8 symbols;
4. VERY_HARD motif using 10 symbols.

These are test-only.

Each should have enough local structure for N=2 and at least selected N=3 tests.

Use simple project-authored logical structures such as:

- stripes;
- bordered motifs;
- diagonals;
- repeating blocks;
- cross/ring-like local motifs.

Do not imitate upstream sample art.

At minimum three distinct exemplar IDs must produce accepted deterministic WFC output to satisfy PAG-0531.

## 19. Required exemplar tests

At minimum:

- metadata immutability;
- missing provenance rejected;
- unknown ownership classification rejected;
- BG01 rejected;
- C17 rejected;
- non-string logical pixel rejected;
- RGB/HEX raster-style pixel array rejected;
- wrong pixel count rejected;
- TRAINING_MOTIF small dimensions allowed;
- production-artifact illegal dimensions rejected when production dimension context says so;
- exemplar smaller than pattern N rejected;
- external/upstream sample ownership cannot be marked owner-approved through convenience defaults;
- empty production registry contains no fabricated exemplars;
- test registry can inject synthetic fixtures.

## 20. Required pattern/adjacency tests

At minimum:

- N=2 extraction non-periodic;
- N=2 input-periodic wrap;
- N=3 extraction;
- N=4 rejected without experimental flag;
- N=4 accepted with flag;
- rotation transforms exact;
- reflection transforms exact;
- transform dedup;
- pattern frequency deterministic;
- pattern ID ordering deterministic;
- adjacency LEFT/RIGHT fixture;
- adjacency UP/DOWN fixture;
- incompatible overlap rejected;
- cross-process pattern tables identical under different PYTHONHASHSEED.

## 21. Required solver tests

At minimum:

- trivial single-pattern collapse;
- deterministic same seed/config;
- weighted pattern selection known fixture;
- minimum-option observation;
- deterministic propagation;
- contradiction produces stable reason;
- max attempts respected;
- retry attempt N independent from previous attempt RNG consumption;
- non-periodic rectangle output;
- periodic rectangle output;
- periodic seam consistency;
- exact requested W×H;
- no reconstruction conflict on accepted result;
- explicit forced conflict fails closed.

## 22. Required palette tests

At minimum:

- default sorted source->target mapping;
- explicit valid mapping;
- incomplete mapping rejected;
- duplicate target mapping rejected;
- source/target cardinality mismatch rejected;
- mapping target outside request palette rejected;
- output contains only requested IDs;
- output omitting a requested color is rejected/retried;
- no after-the-fact color injection.

Include 10-color VERY_HARD synthetic test.

## 23. Production integration tests

For `WFCGenerator`:

- implements PixelGenerator;
- WFC mode only;
- wrong mode fails;
- canonical root RNG only;
- wrong seed root RNG fails;
- non-root RNG fails;
- unknown exemplar fails;
- unapproved production exemplar fails when production registry policy requires approval;
- synthetic injected test exemplar works in tests;
- strict options;
- explicit width/height preserved;
- rectangles;
- exact target palette;
- authenticated M02 stage/retry provenance;
- same request/exemplar/config/seed -> byte-identical GenerationResult;
- no runtime network;
- no arbitrary filesystem path from request.

## 24. Golden evidence

Create compact WFC golden fixtures.

Suggested:

`tests/golden/m05_wfc_fixtures.json`

At minimum include accepted fixed outputs for:

- N=2 non-periodic;
- N=2 output-periodic;
- N=3;
- at least three distinct synthetic exemplar IDs;
- at least one rectangular output;
- one high-cardinality palette case.

Record:

- exemplar ID;
- exemplar logical digest;
- WFC config;
- source->target mapping;
- pattern count;
- unique pattern-table digest;
- output dimensions;
- output grid SHA-256;
- canonical GenerationResult SHA-256;
- attempt index;
- contradiction history.

Do not store giant duplicate grids if stable hashes plus fixture requests are enough.

## 25. Review-only evidence

Create:

`review/m05/m05_review_manifest.json`

and:

`review/m05/M05_WFC_CONTACT_SHEET.html`

These are review-only, not M08 production artifacts.

Minimum review set:

- at least 12 accepted WFC examples;
- all synthetic exemplar IDs represented;
- N=2 and N=3 represented;
- periodic and non-periodic outputs represented;
- rectangles represented;
- multiple seeds.

Each review entry should include:

- synthetic exemplar motif preview;
- generated logical grid preview;
- exemplar ID;
- N;
- periodic flags;
- transform flags;
- source palette;
- target palette;
- mapping;
- pattern count;
- output dimensions;
- attempt;
- contradiction history;
- used palette.

Self-contained:

- no network/CDN;
- exact canonical palette;
- integer block rendering;
- presentation only.

## 26. Acceptance batch

Run at least **120 deterministic WFC candidates** across:

- >=3 synthetic exemplars;
- N=2 and N=3;
- periodic/non-periodic configurations;
- all four difficulties where exemplar cardinality permits;
- rectangles;
- multiple seeds.

Required accepted-output invariants:

- exact requested dimensions;
- C01..C16 only;
- exact requested palette fully used;
- no BG01;
- no resampling;
- deterministic rerun equality;
- root RNG provenance;
- WFC metadata reproducible;
- bounded attempts.

Target >=100 accepted.

If some configurations deterministically contradict, preserve them as failure evidence and add fixed valid candidates to maintain >=100 accepted.

Do not cherry-pick only successes without logging contradictions.

## 27. PAG-0534 — 59×59 benchmark

Benchmark representative 59×59 WFC workloads.

At minimum benchmark:

- N=2 non-periodic;
- N=3 non-periodic;
- one periodic configuration if accepted.

Record:

- machine;
- Python;
- exemplar;
- pattern count;
- placement count;
- sample count;
- accepted/failure count;
- median;
- p95;
- worst.

M05 only requires benchmark evidence.

Do not invent a global V1 performance budget.

M10 will establish final V1 performance acceptance.

## 28. PAG-0535 — offline guarantee

WFC production code must:

- run inside `offline_runtime()`;
- import no networking libraries;
- add no network runtime dependency;
- perform no telemetry;
- call no cloud/image API;
- execute no subprocess/shell;
- load no URL;
- load no arbitrary request-provided path.

Source-policy tests must include the new WFC package.

## 29. Security / determinism

Prohibit:

- eval/exec;
- pickle/untrusted object loading;
- dynamic import by exemplar metadata;
- arbitrary file paths;
- unordered set/dict iteration affecting output;
- Python hash as ID/seed;
- floating-point entropy required for correctness;
- implicit locale-dependent ordering.

Use:

- stable numeric C-ID ordering;
- row-major positions;
- sorted pattern tuples;
- deterministic queues;
- integer weights;
- project RNG.

## 30. Prohibited shortcuts

Do not:

- call MASK or RULES and label the result WFC;
- import an upstream WFC package at runtime;
- copy upstream sample images;
- fabricate owner-approved exemplars;
- treat synthetic test motifs as production art;
- accept arbitrary PNG/JPEG exemplar paths;
- resize/pixelate normal images into exemplars;
- introduce off-palette colors;
- inject missing colors after collapse;
- silently change N/periodicity after contradiction;
- retry without bounded attempt identity;
- begin HYBRID/AUTO;
- modify M02 canonical result schema merely to store WFC metadata;
- edit ChatGPT-owned tracker/audit state;
- self-audit.

## 31. Required verification before handoff

Run and log:

- exemplar contract tests;
- registry/ownership tests;
- pattern extraction tests;
- transform tests;
- adjacency tests;
- solver/contradiction tests;
- palette mapping tests;
- WFC integration tests;
- cross-process determinism tests;
- M05 golden tests;
- review manifest/contact-sheet validation;
- >=120 acceptance batch with >=100 accepted;
- 59×59 benchmarks;
- full M00-M04 regression;
- standalone import;
- `pip check`;
- no-network/no-random/no-hash/no-subprocess/no-eval source scans;
- `git diff --check`;
- source scan proving no M06+ implementation.

Record exact totals, contradictions/retries, benchmark values, and corrections.

## 32. Builder exit criteria

Builder may stop as **implementation complete / pending independent audit** only when:

- PAG-0501..PAG-0535 have implementation/test evidence;
- no external sample art is committed;
- owner exemplar inbox exists but contains no fabricated owner art;
- at least three distinct synthetic exemplar IDs produce accepted outputs;
- N=2/N=3 are supported;
- N=4 remains explicit experimental;
- input/output periodicity works;
- rotations/reflections are deterministic;
- exact requested dimensions are produced;
- source->target mapping is explicit and deterministic;
- accepted output uses exactly the requested palette;
- contradictions/retries are bounded and reproducible;
- rectangular outputs pass;
- >=100 acceptance candidates pass;
- 59×59 benchmark is recorded;
- no M06+ source exists;
- M00-M04 regression remains green;
- matching builder log is published;
- implementation commit(s), push result, and equality checkpoint are recorded.

Do not close M05 or begin M06. ChatGPT will perform the independent strict audit and review.
