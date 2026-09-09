# PAG-M05-C001 — Wave Function Collapse Generator

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-09-09  
Auditor: ChatGPT  
Cycle: `PAG-M05-C001`  
Repository: `Sekiph82/ScrubBots-Level-Factory`

Audited implementation boundary:
- cycle base: `b80cc778935b17411b3b388ffd3d5dd03009051b`
- implementation commit: `d72669b8dca385ba34c8e2dff873396749440eb9`
- builder-log publication commit / terminal builder-era HEAD: `f431b24b2c965e615898020d30d48dedbcbc6bde`

Primary reference:
`ikarth/wfc_2019f@3a937fed13934722377dd7fb6dd238518fa644dd`

Secondary reference:
`mxgmn/WaveFunctionCollapse@de7d22e705e816b62b4d613199d0463820fcaef3`

## 1. VERDICT

**FAIL**

The M05 implementation contains a real deterministic overlapping-pattern WFC engine and passes most core algorithmic contracts, but four acceptance/contract findings remain.

Findings:

- **F-PAG-M05-C001-001 — MAJOR — PRODUCTION_ARTIFACT exemplars do not validate width/height against their declared production difficulty band.**
- **F-PAG-M05-C001-002 — MAJOR — contradiction/rejection diagnostics are lost on terminal retry exhaustion and the required adversarial contradiction/retry evidence is absent.**
- **F-PAG-M05-C001-003 — MAJOR — WFC metadata field `extracted_pattern_count` is semantically incorrect when transforms are enabled.**
- **F-PAG-M05-C001-004 — MAJOR — committed M05 review/golden/rectangle evidence is materially below the authoritative acceptance prompt.**

M06 remains blocked.

A bounded `PAG-M05-C002` remediation is required.

## 2. CONTRACT RECOVERY

M05 was required to provide:

- project-owned overlapping-pattern WFC;
- exact in-memory logical C01..C16 exemplars;
- explicit exemplar ownership/provenance;
- PRODUCTION_ARTIFACT dimension legality while permitting small TRAINING_MOTIF exemplars;
- N=2/N=3 and opt-in experimental N=4;
- input/output periodicity;
- deterministic rotations/reflections;
- exact overlap adjacency;
- bounded deterministic contradiction/retry behavior;
- exact requested dimensions;
- one-to-one explicit source→request palette mapping;
- no post-solve palette repair;
- stable WFC metadata;
- contradiction/rejection reason recording;
- at least three synthetic exemplars producing deterministic output;
- rectangle evidence;
- at least 12 review examples with exemplar preview + generated output;
- goldens including rectangular and high-cardinality cases;
- >=120 acceptance candidates with >=100 accepted;
- 59×59 benchmark;
- offline-only operation.

## 3. BRANCH / HEAD / DIFF SCOPE

Independent GitHub comparison from `b80cc778...` to terminal builder-era HEAD shows two builder commits:

1. `d72669b8dca385ba34c8e2dff873396749440eb9`
   - WFC source package;
   - synthetic fixtures;
   - owner exemplar inbox/docs;
   - WFC tests/goldens;
   - review/benchmark evidence.

2. `f431b24b2c965e615898020d30d48dedbcbc6bde`
   - completed M05 builder log.

No M06+ implementation was found.

No main ScrubBots mutation was found.

No upstream WFC runtime/source/sample-art dependency was introduced.

Scope result: **PASS**

## 4. ACCEPTANCE CRITERIA MATRIX

| Criterion | Result | Independent conclusion |
| --- | --- | --- |
| PAG-0501 pinned upstream commit | PASS | Exact immutable ikarth SHA documented. |
| PAG-0502 minimum WFC modules | PASS | Project-owned model/exemplar/pattern/solver/generator modules. |
| PAG-0503 no GUI/demo dependency | PASS | No GUI/runtime upstream dependency. |
| PAG-0504 PixelGenerator integration | PASS | WFCGenerator integration exists and is tested. |
| PAG-0505 in-memory logical arrays | PASS | Core consumes Exemplar logical C-IDs; no request path loading. |
| PAG-0506 exact output dimensions | PASS | Solver reconstructs exact W×H. |
| PAG-0507 no resampling | PASS | No resize/interpolation production path found. |
| PAG-0508 project RNG | PASS | Canonical root RNG validation and retry_rng use. |
| PAG-0509 deterministic contradiction/retry | PASS / evidence gap | Retry identity is deterministic in source, but adversarial retry-independence tests are missing. |
| PAG-0510 bounded retries | PASS | WFCConfig max_attempts 1..8. |
| PAG-0511 exemplar metadata schema | PASS | Immutable versioned Exemplar exists. |
| PAG-0512 explicit provenance | PASS | Non-empty provenance required. |
| PAG-0513 canonical logical pixels | PASS | C01..C16 only. |
| PAG-0514 reject antialias/interpolation inputs | PASS | Core accepts logical IDs only, not RGB/HEX raster cells. |
| PAG-0515 production artifact dimension legality | **FAIL** | Declared difficulty is checked, dimensions are not validated against M01 band. |
| PAG-0516 external samples not treated as owner art | PASS | No upstream artwork committed. |
| PAG-0517 empty owner inbox | PASS / DOC NOTE | Inbox empty; README should be strengthened in remediation. |
| PAG-0518 N=2 | PASS | Implemented. |
| PAG-0519 N=3 | PASS | Implemented. |
| PAG-0520 N=4 experimental | PASS | Explicit flag required. |
| PAG-0521 input periodicity | PASS | Implemented. |
| PAG-0522 output periodicity | PASS | Implemented. |
| PAG-0523 rotations/reflections | PASS | Exact deterministic transforms/dedup. |
| PAG-0524 WFC config/metadata truth | **FAIL** | `extracted_pattern_count` counts transform-expanded observations rather than raw extracted windows. |
| PAG-0525 reject palette-illegal config | PASS | Source/target cardinality and complete one-to-one mapping enforced. |
| PAG-0526 no unseen/off-palette colors | PASS | Mapping before extraction. |
| PAG-0527 deterministic explicit remap | PASS | Stable numeric positional default and strict explicit mapping. |
| PAG-0528 exact distinct-color count | PASS | Missing target color rejects attempt. |
| PAG-0529 reject rather than fix | PASS | No color injection/repair found. |
| PAG-0530 contradiction/rejection reasons | **FAIL** | Success sidecar can retain prior contradictions, but terminal exhausted failure discards full attempt history. |
| PAG-0531 >=3 synthetic exemplar outputs | PASS | Four synthetic fixture families exercised. |
| PAG-0532 byte-identical replay | PASS | Integration/cross-process determinism evidence exists. |
| PAG-0533 rectangular WFC outputs | **PARTIAL / REVALIDATE** | Solver has a 9×7 rectangle test, but production integration/acceptance/review/goldens are square-only. |
| PAG-0534 59×59 benchmark | PASS | N=2/N=3 periodic/non-periodic benchmark recorded. |
| PAG-0535 no network/cloud runtime | PASS | Offline boundary preserved. |
| >=120 acceptance candidates | PASS / builder-supported | 120-case source matrix exists; builder reports 120/120 accepted. |
| >=12 review candidates | **FAIL** | Committed review manifest has 4 candidates. |
| exemplar motif + generated output review | **FAIL** | Contact sheet renders generated output only; exemplar motif preview is absent. |
| rectangular + high-cardinality golden coverage | **FAIL** | Current three goldens are square and stop at 8 colors. |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

### Claim: production artifact exemplar contract is complete

Current `Exemplar.__post_init__()` validates:

- role;
- width >=2;
- height >=2;
- production difficulty name for PRODUCTION_ARTIFACT.

It does **not** call the existing M01:

`validate_dimensions(production_difficulty, width, height)`

or equivalent.

Therefore a declared EASY production artifact with 3×3 dimensions passes the current Exemplar constructor even though EASY production dimensions are 20..29 independently per axis.

Disposition: **REJECTED for PAG-0515**

### Claim: contradiction/rejection reasons are recorded

Positive:

- `WFCContradiction` has stable `code`, `placement`, and `detail`;
- successful `WFCCandidate.metadata` records contradictions from earlier failed attempts.

Problem:

After all attempts fail, `WFCGenerator.generate_candidate()` returns only:

`GenerationResult.failure(RETRY_EXHAUSTED, "bounded WFC generation attempts exhausted", request)`

The accumulated `contradiction_history` is discarded.

No committed focused test forces:

- EMPTY_WAVE;
- reconstruction conflict;
- missing target color retry;
- all-attempt exhaustion with stable reason history;
- retry attempt N independence from previous attempt RNG consumption.

Disposition: **REJECTED for PAG-0530 / acceptance evidence**

### Claim: WFC metadata records extracted pattern count

Current metadata stores:

`"extracted_pattern_count": sum(pattern.frequency for pattern in table.patterns)`

But pattern frequencies are incremented **after rotations/reflections are expanded**.

Independent committed-manifest examples:

- EASY 6×6, N=2 periodic, no transforms:
  - raw windows = 36
  - metadata = 36
  - correct by coincidence.

- MEDIUM 8×8, N=3 periodic, rotations enabled:
  - raw extracted windows = **64**
  - metadata = **246**.

- VERY_HARD 12×12, N=3 periodic, rotations+reflections:
  - raw extracted windows = **144**
  - metadata = **566**.

The field is therefore not the raw extracted pattern/window count required by the prompt.

A separate transform-expanded observation count may be useful, but it must not be mislabeled.

Disposition: **REJECTED for metadata truth**

### Claim: review/golden evidence meets the M05 prompt

Current review builder defines exactly four CASES.

Manifest:

`candidate_count = 4`

The authoritative prompt required at least 12 accepted examples with:

- all synthetic exemplar IDs;
- N=2/N=3;
- periodic/non-periodic;
- rectangles;
- multiple seeds;
- synthetic exemplar motif preview;
- generated grid preview.

Current contact sheet displays only generated grids.

The current golden file has three entries:

- EASY 20×20, 3 colors;
- MEDIUM 30×30, 6 colors;
- HARD 40×40, 8 colors.

It lacks:

- a rectangular golden;
- a 10-color VERY_HARD golden.

Disposition: **REJECTED**

## 6. FILE / SYMBOL EVIDENCE

### `wfc/model.py::Exemplar`

Positive:

- frozen dataclass;
- logical C-ID validation;
- provenance required;
- ownership classification;
- owner approval explicit.

Defect:

- PRODUCTION_ARTIFACT does not validate dimensions against declared production difficulty.

Result: **FAIL only for PAG-0515**

### `wfc/model.py::ExemplarRegistry`

Positive:

- deterministic ordered immutable registry;
- default empty;
- no file/network lookup.

Result: **PASS**

### `wfc/patterns.py`

Positive:

- exact integer transforms;
- deterministic tuple dedup;
- stable pattern IDs;
- exact overlap adjacency;
- canonical SHA-256 pattern-table digest.

Metadata issue:

- PatternTable does not retain the raw extraction-window count separately from transformed frequency accumulation.

Result: **PASS algorithm / FAIL metadata accounting**

### `wfc/solver.py`

Positive:

- finite wave;
- weighted integer selection;
- deterministic queue;
- exact compatibility propagation;
- explicit operation limit;
- periodic/non-periodic placement;
- reconstruction conflict checks.

Result: **PASS**

### `wfc/generator.py`

Positive:

- WFC-only mode;
- canonical root RNG;
- bounded retry;
- exact palette set requirement;
- no post-solve repair;
- M02 validated GenerationResult;
- WFC sidecar metadata on success.

Defect:

- terminal exhausted failure drops contradiction history.

Result: **FAIL only for terminal diagnostic truth**

### `review/m05/build_review.py`

Defects:

- only four cases;
- no exemplar logical preview in manifest/contact sheet;
- no rectangular review example.

Result: **FAIL acceptance evidence**

## 7. FOCUSED TEST EVIDENCE

Builder reports:

- acceptance: **120/120 accepted**
- focused/golden/acceptance: **14 passed**
- full repository: **222 passed**
- benchmark: four accepted 59×59 WFC cases.

Independent audit additionally inspected:

- exemplar contracts;
- registry semantics;
- pattern transforms/adjacency;
- full solver source;
- generator retry logic;
- acceptance matrix source;
- golden fixtures;
- review builder/manifest;
- benchmark evidence.

Important missing adversarial tests:

1. production artifact dimensions rejected against M01 difficulty band;
2. stable EMPTY_WAVE contradiction code;
3. forced reconstruction conflict;
4. terminal retry exhaustion preserves/records reason sequence;
5. retry attempt N independent from previous attempt RNG consumption;
6. missing-target-color rejection/retry path;
7. production generator rectangular case;
8. periodic seam consistency at logical output level;
9. explicit invalid mapping coverage beyond the happy path;
10. metadata raw extracted-window count with transforms.

## 8. REGRESSION EVIDENCE

No M00-M04 source regression found in M05 scope.

No M06+ code exists.

No new runtime dependency was added.

Builder reports full repository 222 PASS.

Result: **PASS**

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive:

- no network/API/cloud;
- no arbitrary request-provided filesystem paths;
- no upstream runtime dependency;
- no subprocess in production WFC code;
- no global random;
- no Python hash as seed/ID;
- no unsafe deserialization;
- production registry defaults empty;
- owner-supplied unapproved exemplars rejected.

Result: **PASS**

## 10. ARCHITECTURE CONSISTENCY

The architecture is sound:

```text
Exemplar
 -> deterministic palette mapping
 -> transformed overlapping pattern table
 -> exact overlap adjacency
 -> bounded WFC wave
 -> exact W×H reconstruction
 -> exact target palette gate
 -> GenerationResult
```

The remaining issues are contract truth/evidence rather than a flawed solver architecture.

Result: **PASS with remediation required**

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Positive:

- matching builder log existed before M05 edits;
- no task/tracker/audit state mutated by builder;
- synthetic fixtures are clearly labeled test-only;
- production exemplar registry remains empty;
- no WFC upstream art/source is represented as project-owned;
- benchmark does not invent an M10 budget.

Documentation notes for remediation:

- `exemplars/README.md` should explicitly state provenance/contract validation and forbid upstream/external sample images as production exemplars.
- `tests/fixtures/wfc/README.md` says “four logical arrays” while the directory contains five JSON fixtures including the benchmark fixture.

Result: **PASS with documentation notes**

## 12. FINAL REPOSITORY STATE

Terminal builder-era HEAD:

`f431b24b2c965e615898020d30d48dedbcbc6bde`

Implementation commit:

`d72669b8dca385ba34c8e2dff873396749440eb9`

No unauthorized M06+ scope found.

Implementation is published but M05 is not accepted.

## 13. OPEN CROSS-MILESTONE FINDINGS

### F-PAG-M05-C001-001 — MAJOR

**PRODUCTION_ARTIFACT dimensions are not bound to M01 difficulty contracts.**

Required target:

- import/reuse existing M01 `validate_dimensions`;
- when role == PRODUCTION_ARTIFACT:
  - require production_difficulty;
  - validate width and height independently against that difficulty band;
- TRAINING_MOTIF retains small-motif allowance.

Do not duplicate difficulty ranges in WFC.

### F-PAG-M05-C001-002 — MAJOR

**Terminal contradiction/rejection history is discarded.**

Required target:

- preserve immutable stable attempt records internally;
- successful candidate continues to expose prior contradictions;
- terminal exhausted failure must surface a deterministic stable summary of attempt codes/rejections without widening M02 canonical success schema;
- add adversarial contradiction/retry tests.

### F-PAG-M05-C001-003 — MAJOR

**`extracted_pattern_count` is transform-expanded, not raw extraction count.**

Required target:

PatternTable/metadata should separately record:

- raw extracted window count;
- optional transform-expanded observation count;
- unique transformed pattern count.

For periodic input:
- raw count = exemplar.width × exemplar.height.

For non-periodic input:
- raw count = (width-N+1) × (height-N+1).

### F-PAG-M05-C001-004 — MAJOR

**Review/golden/rectangle acceptance evidence is incomplete.**

Required target:

- >=12 committed review candidates;
- multiple seeds;
- N=2/N=3;
- periodic/non-periodic;
- rectangular outputs;
- all four synthetic cardinality fixtures represented;
- manifest contains exemplar logical motif cells/dimensions;
- contact sheet renders exemplar motif beside generated output;
- golden set adds at least one rectangle and one 10-color VERY_HARD case;
- production integration test adds legal rectangular requests;
- acceptance matrix includes rectangles rather than squares only.

## 14. DEFECTS BY SEVERITY

### BLOCKER

None.

### MAJOR

- F-PAG-M05-C001-001
- F-PAG-M05-C001-002
- F-PAG-M05-C001-003
- F-PAG-M05-C001-004

### MINOR

None blocking.

### NOTE

The WFC solver itself is not rejected.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Non-blocking after remediation:

- optionally randomize tied minimum-option placement using a named deterministic RNG child stream for more seed diversity while preserving reproducibility;
- deep-freeze nested WFC metadata if it later becomes production artifact metadata in M08;
- general contradiction-rate reporting belongs naturally in M10.

## 16. UNVERIFIED ITEMS

Exact owner-machine 222-test and benchmark commands were not independently rerun.

No solver-algorithm finding depends on those builder-only totals.

## 17. REGRESSION RISK

**LOW to MEDIUM**

Required changes are localized to:

- exemplar validation;
- pattern metadata accounting;
- failure diagnostics;
- tests/review/goldens.

Core adjacency/solver algorithms should not need replacement.

## 18. AUDIT CONFIDENCE

**HIGH**

Evidence includes:

- direct GitHub source inspection;
- exact commit/diff scope;
- direct solver/pattern/generator review;
- direct fixture/golden/review inspection;
- independent raw-window-count comparison against committed metadata;
- direct comparison against authoritative M05 acceptance prompt.

## 19. FINAL VERDICT

**FAIL**

`PAG-M05-C001` is not accepted.

Validated WFC algorithmic work should be preserved.

PAG-M06 remains blocked.

## 20. REQUIRED REMEDIATION

Create bounded cycle:

`PAG-M05-C002 — Exemplar Contract, Diagnostics & Acceptance Evidence Remediation`

Required work only:

1. enforce production exemplar dimensions through existing M01 contracts;
2. preserve terminal contradiction/rejection diagnostic history;
3. correct raw/transformed WFC pattern-count metadata;
4. add missing adversarial contradiction/retry tests;
5. add generator-level rectangular coverage;
6. expand review pack to >=12 with exemplar+output paired visualization;
7. add rectangular and 10-color golden evidence;
8. rerun >=120 acceptance matrix with rectangular cases and >=100 accepted;
9. rerun 59×59 benchmarks;
10. rerun full M00-M05 regression;
11. do not begin M06.
