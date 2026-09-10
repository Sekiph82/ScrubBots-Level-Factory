# PAG-M07-C001 — Artwork Quality & Diversity Filters

Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

M06 closing audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M06-C004_WFC_EVIDENCE_BINDING_CLOSURE_STRICT_AUDIT.md`

Canonical task ledger:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/tasks.md`

## 1. Mission and scope

Implement **PAG-M07 — Artwork Quality & Diversity Filters** only.

M07 is a deterministic, offline, generator-independent analysis and rejection layer for logical SCRUBBOTS artwork. It must compute structural metrics, reject deliberately bad fixtures with stable machine-readable reasons, measure exact/near duplicate similarity, and generate self-contained human-review evidence.

M07 is **not** a gameplay solver and must not claim to measure puzzle solvability, player difficulty, fun, campaign suitability or semantic artistic quality.

Implement task IDs:

- `PAG-0701` through `PAG-0712` — structural metrics;
- `PAG-0713` through `PAG-0722` — obvious-garbage rejection and machine-readable rejection codes;
- `PAG-0723` through `PAG-0730` — exact/near duplicate metrics and deterministic diversity handling;
- `PAG-0731` through `PAG-0735` — human review artifacts;
- `PAG-0736` through `PAG-0738` — M07 acceptance evidence.

Do not begin M08, M09, M10 or M11 implementation.

Existing cross-milestone dependency `PAG-0441` remains blocked until M10 establishes the performance budget.

## 2. GitHub-first H!veAI authority

Before editing, read completely from GitHub `main`:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. v3 machine block in `.hiveai/TASKS.md`
4. `.hiveai/EVENTS.jsonl`
5. `tasks.md`
6. `.hiveai/CYCLE_INDEX.md`
7. `AGENTS.md`
8. `GOVERNANCE.md`
9. M06 C004 prompt, builder log and strict audit
10. current M01/M02 contracts
11. current MASK, RULES, WFC, HYBRID/AUTO result paths and representative tests
12. this M07 prompt

GitHub `main` is current-state authority. The local mirror is execution workspace only.

Canonical local mirror:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Never substitute `C:\Users\sekip\Desktop\ScrubBots` or another sibling repository.

Synchronize only with non-destructive Git operations. Do not reset, force-push, discard user changes or auto-rebase.

## 3. Matching builder log

Before the first M07 product/test/review edit create:

`.hiveai/codex-logs/PAG-M07-C001_ARTWORK_QUALITY_AND_DIVERSITY_FILTERS_CODEX_LOG.md`

Exact H1:

`# PAG-M07-C001 — Artwork Quality & Diversity Filters`

Immediately below:

`Document role: CODEX BUILDER LOG`

Log chronologically and truthfully:

- starting timestamp;
- repository/branch/origin/HEAD/status;
- synchronization and pre-existing local changes;
- mandatory GitHub reads;
- architecture decisions;
- every materially relevant command;
- failed tests/commands and corrections;
- files changed;
- focused tests;
- generator-family regression tests;
- full regression;
- offline/network checks;
- dependency/license changes;
- final diff/status;
- implementation commit SHA(s);
- push result;
- final post-log-publication local HEAD and `origin/main` equality.

Do not self-audit or edit ChatGPT-owned acceptance/tracker state.

## 4. Architecture boundary

Create a dedicated project-owned quality layer under a coherent package such as:

`src/scrubbots_pixel_factory/quality/`

The exact module split may differ if justified in the builder log, but keep concerns separated:

- immutable/versioned metric/result models;
- grid-only structural analysis;
- versioned rejection policy;
- duplicate/similarity analysis;
- review-manifest/contact-sheet support only where it belongs in M07.

Do not bury M07 logic inside MASK, RULES, WFC or HYBRID generators.

M07 must be independently testable using hand-authored logical-grid fixtures without invoking any generator.

Do not mutate a `GenerationResult` or generated logical grid in order to improve quality. Analysis is read-only. A rejection means reject/report, not recolor, resize, smooth, repair or silently regenerate.

Do not modify M02 result integrity contracts merely to store M07 data. M08 owns the future export artifact schema.

## 5. Canonical quality input and validation

Define one immutable/versioned analysis input or a strict analyzer API that accepts at minimum:

- exact `width`;
- exact `height`;
- row-major logical cells.

The core metrics must be reproducible from those logical-grid inputs alone.

Fail closed before analysis when:

- dimensions are non-positive or inconsistent with cell count;
- a cell is not a canonical `C01..C16` logical ID;
- BG01 or any off-palette value is supplied.

Do not require generator family, seed, style, topology metadata or provenance to compute structural metrics.

### 5.1 Negative-space / occupied-cell semantics

The current `GenerationResult.logical_grid` contains only canonical C-IDs and does not carry a separate universal empty-cell token. Therefore M07 must not secretly depend on MASK/RULES private topology metadata while claiming grid-only reproducibility.

Define and document a **deterministic grid-only negative-space inference rule** for generic M07 analysis. The inference must:

- use only width, height and logical cells;
- be deterministic and canonical across runs;
- work on rectangular grids;
- have explicit tie-breaking using canonical C-ID order;
- return both the inferred negative-space C-ID and the evidence/counts used to choose it;
- be clearly labeled a structural-analysis heuristic, not gameplay truth or semantic background truth.

A recommended rule is boundary-majority inference: choose the color with the greatest count on the outer board boundary; break ties by greater whole-grid count; break any remaining tie by ascending canonical C-ID. If Codex chooses another rule, it must be equally deterministic, grid-only, documented and strongly tested.

For M07 structural metrics:

- inferred negative-space cells are structural negative space;
- all other cells are structural occupied cells.

Do not use BG01 as a logical empty token.

## 6. Structural metrics: PAG-0701..PAG-0712

Implement deterministic metrics for:

1. occupied-cell count and ratio;
2. number of 4-neighbor connected occupied components;
3. connected-component count and sizes per color;
4. isolated occupied single-cell count;
5. tiny occupied-region count with the threshold explicitly versioned/configured;
6. largest occupied-region dominance;
7. occupied edge-touch count/ratio;
8. horizontal and vertical symmetry scores, plus one documented aggregate if exposed;
9. color-distribution entropy;
10. color-adjacency statistics using deterministic 4-neighbor edge counting without double-counting undirected pairs;
11. occupied bounding box and center-of-mass;
12. negative-space count and ratio.

Metric calculations must be independent of Python hash/set/dict iteration order. Canonically sort C-IDs and component traversal roots/neighbors where serialization or tie outcomes matter.

Prefer exact integer counts and deterministic rational/scaled representations for persisted evidence. If floats are exposed for usability, define rounding/serialization explicitly and test byte-stable canonical serialization.

Edge cases must be defined and tested, including:

- all one color;
- no occupied cells after negative-space inference;
- one occupied cell;
- full occupied interior with one inferred border/background color;
- square and rectangular grids;
- horizontal-only symmetry;
- vertical-only symmetry;
- asymmetric grid;
- multiple equal-size components;
- entropy zero case.

## 7. Rejection policy: PAG-0713..PAG-0722

Create an immutable/versioned `QualityPolicy` or equivalent. Separate raw metrics from policy decisions.

Policy thresholds must be explicit data, not scattered magic numbers.

Implement stable machine-readable rejection codes for at least:

- empty/effectively empty artwork;
- full single-shape slab when disallowed by configured style/policy;
- excessive isolated salt-and-pepper cells;
- excessive tiny fragmented regions;
- configured largest-region/color dominance violation;
- checkerboard/noise pathology;
- difficulty color-count violation when difficulty is explicitly supplied to the validation wrapper;
- off-palette cell;
- dimension/cell-count mismatch.

A single candidate may produce multiple deterministic rejection codes. Canonically order them.

Do not conflate structural rejection with generator failure codes from M02. Use an M07-owned enum/schema for quality findings/rejections.

Do not invent aggressive default thresholds that systematically reject currently accepted M03-M06 good fixtures. Defaults must be conservative and justified by fixtures/evidence. Threshold-specific tests should use explicit policy values whenever that makes intent clearer.

Checkerboard/noise detection must be structural and deterministic. It must not reject any two-color use merely because adjacency is high; construct deliberate pathological fixtures and good counterexamples.

## 8. Diversity and duplicate analysis: PAG-0723..PAG-0730

### 8.1 Exact logical-grid hash

Define a versioned canonical logical-grid hash that binds at least:

- width;
- height;
- row-major C-ID cells.

Do not hash only concatenated cell text without unambiguous framing. Use canonical serialization and SHA-256 or the repository's existing cryptographic digest convention.

Two identical grids with identical dimensions must hash identically. A dimension change or any cell change must change the canonical hash.

### 8.2 Exact duplicate detection

Provide deterministic exact duplicate detection over a batch/set of analyzed grids using the canonical logical-grid hash, with collision-safe equality verification if the API claims exact identity rather than hash identity.

### 8.3 Near-duplicate metrics

Define deterministic near-duplicate metrics that keep geometry and color layout separate:

- occupancy-mask similarity;
- color-layout similarity.

Use explicit, bounded scales and define identical/completely-different edge behavior. Metrics must support rectangular grids of equal dimensions. For unequal dimensions, fail closed or return a documented non-comparable result; do not resize/interpolate.

A simple exact-cell agreement ratio is acceptable for color-layout similarity if clearly defined. Occupancy similarity may use Jaccard/IoU or another documented deterministic metric over inferred occupied cells. Do not use image libraries, resampling, perceptual AI or online services.

### 8.4 Batch duplicate threshold

Allow an explicit batch-level near-duplicate threshold/policy. Keep:

- structural quality score/decision;
- exact duplicate state;
- diversity/near-duplicate score

as distinct concepts.

Never silently mutate an accepted candidate to make it different. Future regeneration must use a recorded seed; M07 itself only reports duplicate/diversity evidence.

## 9. Human-review artifacts: PAG-0731..PAG-0735

Create committed deterministic review evidence under a bounded path such as:

`review/m07/`

At minimum produce:

- a machine-readable review manifest;
- a self-contained HTML contact sheet or equivalent committed human-readable review artifact.

Each candidate card/entry must show at least:

- candidate/review ID;
- generator mode/family when generated evidence is used;
- seed when generated evidence is used;
- difficulty;
- exact dimensions;
- distinct used-color count;
- inferred negative-space color;
- core structural metrics;
- ACCEPT/REJECT quality decision;
- stable rejection codes;
- exact grid hash;
- diversity/duplicate evidence where applicable.

The review manifest should define a simple future-compatible human `ACCEPT` / `REJECT` field without pretending that M07 already implements an interactive UI.

Contact sheet requirements:

- no CDN;
- no runtime network access;
- no external fonts/scripts/assets;
- no JavaScript requirement;
- logical cells shown without interpolation/antialiasing;
- integer/CSS nearest-neighbor style enlargement only for presentation;
- no modification of the underlying logical grid.

M08 is not implemented yet, so do not build the M08 PNG/JSON export system merely to satisfy this review pack.

## 10. Acceptance fixture design: PAG-0736..PAG-0738

Create deliberate hand-authored fixtures that prove the quality layer is discriminating rather than ceremonial.

### 10.1 Bad fixtures

Include deterministic fixtures for at least:

- inferred-empty artwork;
- solid/full slab pathology under a policy that rejects it;
- salt-and-pepper isolated noise;
- excessive tiny fragments;
- checkerboard/noise pattern;
- dominance violation;
- off-palette input;
- dimension mismatch;
- exact duplicate pair;
- near-duplicate pair.

Each bad fixture must assert the expected stable code(s), not merely `accepted == false`.

### 10.2 Good fixtures

Include a diverse set of structured counterexamples that must not be systematically rejected, including:

- connected central subject;
- sparse negative-space composition;
- multi-island composition when policy permits it;
- symmetric subject;
- asymmetric organic subject;
- rectangular board.

Also run a representative sample of already accepted M03-M06 generator outputs through M07 using a documented conservative policy. M07 must not break their generation contracts or systematically classify all of them as garbage.

### 10.3 Reproducibility

Prove byte-stable/canonical metric and rejection serialization for identical width + height + logical grid inputs across repeated calls and at least one cross-process/hash-seed test.

Changing generator metadata while keeping the logical grid identical must not change core grid-only metrics or rejection reasons under the same policy.

## 11. Integration boundary

M07 may expose public analysis APIs through package `__init__` files as appropriate, but do not make existing generators automatically reject candidates through M07 unless `tasks.md` or this prompt explicitly requires that integration. M07's first responsibility is a proven independent quality layer.

Do not:

- alter M03/M04/M05/M06 outputs merely to improve scores;
- change deterministic generator seeds;
- add post-generation recoloring/repair;
- resize or interpolate logical art;
- add cloud/AI/perceptual-image dependencies;
- add GPU requirements;
- add runtime HTTP;
- create gameplay solver logic.

## 12. Required tests

Add focused unit/property/integration tests as appropriate. At minimum prove:

- every PAG-0701..PAG-0712 metric with known hand-computable fixtures;
- deterministic negative-space inference and tie-breaking;
- rectangular board correctness;
- stable component traversal and canonical ordering;
- stable entropy/adjacency/symmetry semantics;
- each required quality rejection code;
- multi-code canonical ordering;
- exact grid hash stability and sensitivity;
- exact duplicate detection;
- occupancy similarity;
- color-layout similarity;
- unequal-dimension non-resize behavior;
- conservative good-fixture acceptance;
- deliberate garbage-fixture rejection;
- repeated byte-identical metric/rejection output;
- cross-process determinism;
- review manifest/contact sheet self-containment;
- no runtime network;
- no resize/interpolation;
- M03-M06 regression and representative quality-analysis compatibility.

## 13. Required verification

At minimum run and log:

- all new M07 focused tests;
- M01/M02 contract tests affected by input validation assumptions;
- representative M03 MASK tests;
- representative M04 RULES tests;
- representative M05 WFC tests;
- M06 router/hybrid/replay/AUTO tests;
- full repository pytest;
- standalone import;
- cross-process determinism tests;
- offline/network source-policy scan;
- resize/resample/interpolation scan;
- forbidden non-project randomness / built-in `hash()` scan in M07 source;
- `git diff --check`;
- `python -m pip check`;
- M08+ implementation-scope scan.

M06 closing builder baseline before M07 is `250 passed, 1 warning`. The known local `pytest-asyncio 0.24.0` versus pytest `9.1.1` mismatch may remain documented as an unchanged environment issue. Do not change unrelated dependencies to hide it.

## 14. Review evidence minimum

Commit a deterministic M07 review pack with enough examples to inspect every major rejection family and several good counterexamples. Minimum suggested evidence set: **20 cases**, containing both deliberately bad synthetic fixtures and representative accepted generator outputs.

The review manifest must be reproducible from source fixtures/config and must not contain timestamps or machine-specific absolute paths that cause meaningless diffs.

## 15. Prohibited shortcuts

Do not:

- call every logical cell “occupied” merely because every cell has a C-ID;
- use generator-private topology metadata for core metrics while claiming grid-only reproducibility;
- treat one hard-coded C-ID as universal background without a deterministic documented inference contract;
- use BG01 as logical content;
- let set/dict/hash iteration choose components, ties or serialized order;
- use Python built-in `hash()` for persisted identity;
- use random thresholds or seed-dependent quality scoring;
- collapse quality and diversity into one opaque score;
- silently repair bad grids;
- resize unequal grids to compare them;
- use SSIM/CV/AI/perceptual libraries that are unnecessary for V1 logical-cell analysis;
- fabricate visual/manual acceptance;
- mark owner human review as already completed;
- edit ChatGPT-owned task/tracker/audit state;
- begin M08+.

## 16. Builder exit criteria

Builder may stop and return for independent audit only when:

- all PAG-0701..PAG-0735 implementation scope exists with focused tests;
- every structural metric is deterministic and documented;
- negative-space inference is grid-only, deterministic and explicitly heuristic;
- every required garbage class has a stable rejection code and a positive/negative counterexample;
- exact and near-duplicate analysis is deterministic and non-resizing;
- quality and diversity outputs remain separate;
- M07 review manifest/contact sheet is committed and self-contained;
- deliberate garbage fixtures are rejected for the expected reasons;
- good fixtures are not systematically rejected;
- metrics/reasons reproduce from logical grid under the same versioned policy;
- M03-M06 regression is green;
- full repository regression is green except the unchanged documented environment-only `pip check` mismatch;
- no cloud/network/GPU/resize requirement is introduced;
- no M08+ implementation exists;
- matching M07 C001 builder log is committed and pushed;
- final post-log-publication local HEAD equals `origin/main` and that result is recorded in the log;
- Codex does not declare M07 or any task finally accepted.

Return the builder log to ChatGPT for independent strict audit.
