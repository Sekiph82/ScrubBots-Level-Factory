# PAG-M05-C002 — Exemplar Contract, Diagnostics & Acceptance Evidence Remediation

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M05-C001_WAVE_FUNCTION_COLLAPSE_GENERATOR_STRICT_AUDIT.md`

Previous implementation prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M05-C001_WAVE_FUNCTION_COLLAPSE_GENERATOR_PROMPT.md`

Primary reference remains:
`https://github.com/ikarth/wfc_2019f/tree/3a937fed13934722377dd7fb6dd238518fa644dd`

Secondary reference remains:
`https://github.com/mxgmn/WaveFunctionCollapse/tree/de7d22e705e816b62b4d613199d0463820fcaef3`

## 1. Scope

This is a bounded M05 remediation for exactly four findings:

- `F-PAG-M05-C001-001` — **MAJOR** — PRODUCTION_ARTIFACT exemplars do not validate dimensions against their declared production difficulty.
- `F-PAG-M05-C001-002` — **MAJOR** — terminal contradiction/rejection history is discarded and adversarial contradiction/retry evidence is missing.
- `F-PAG-M05-C001-003` — **MAJOR** — `extracted_pattern_count` metadata is transform-expanded rather than raw extraction-window count.
- `F-PAG-M05-C001-004` — **MAJOR** — review/golden/rectangle acceptance evidence is incomplete.

Do not rewrite the validated WFC architecture.

Preserve:

- project-owned overlapping pattern extraction;
- exact adjacency semantics;
- deterministic transforms;
- bounded WFC solver;
- periodic/non-periodic reconstruction;
- exact source→target palette mapping;
- exact target palette gate;
- offline/network isolation;
- canonical root RNG behavior;
- N=2/N=3 and experimental N=4 support.

Do not begin PAG-M06+.

## 2. GitHub authority

GitHub is the sole task/prompt/audit authority.

Implementation repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Do not modify the main ScrubBots repository.

Do not copy/adapt upstream WFC source or sample artwork.

No new runtime dependency is expected.

## 3. Mandatory reads

Before the first source/test/golden/review/docs edit, read completely:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. C001 builder log
9. C001 strict audit
10. current WFC model/exemplar/patterns/solver/generator
11. current M05 tests/goldens/review/benchmark
12. existing M01 difficulty contract module
13. this prompt

## 4. Matching builder log

Create **before the first source, test, fixture, golden, review, benchmark, or documentation edit**:

`.hiveai/codex-logs/PAG-M05-C002_EXEMPLAR_CONTRACT_DIAGNOSTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M05-C002 — Exemplar Contract, Diagnostics & Acceptance Evidence Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- authority/prompt/audit URLs;
- starting branch/HEAD/origin/ahead-behind/status;
- synchronization;
- mandatory reads;
- exact remediation design per finding;
- files changed;
- commands;
- failed tests/corrections;
- production exemplar dimension evidence;
- contradiction/retry evidence;
- raw/transformed pattern-count evidence;
- rectangle evidence;
- golden evidence;
- >=12 review evidence;
- >=120 acceptance matrix;
- 59×59 benchmark;
- full regression;
- implementation commit SHA(s);
- push/equality checkpoint;
- final changed-file summary.

Do not self-audit.

Do not edit ChatGPT-owned task/tracker/audit state.

## 5. Finding F-PAG-M05-C001-001 — production exemplar dimension legality

### Current defect

Current `Exemplar` validation requires a legal `production_difficulty` name for:

`role == "PRODUCTION_ARTIFACT"`

but does not validate `width` and `height` against the corresponding M01 difficulty band.

Therefore an invalid production artifact such as:

```text
role = PRODUCTION_ARTIFACT
production_difficulty = EASY
width = 3
height = 3
```

currently passes the WFC Exemplar constructor.

### Required target behavior

Reuse the existing M01 contract.

Import/call:

`validate_dimensions(production_difficulty, width, height)`

or the exact existing equivalent.

Do not duplicate difficulty ranges inside WFC.

Required behavior:

- TRAINING_MOTIF:
  - may remain smaller than production difficulty dimensions;
  - still must satisfy general logical/minimum requirements and configured N.
- PRODUCTION_ARTIFACT:
  - requires `production_difficulty`;
  - width and height must each be legal for that difficulty;
  - rectangles are allowed;
  - illegal dimension fails closed as `WFCContractError`.

### Required tests

Add at minimum:

- EASY 20×20 production exemplar accepted;
- EASY 29×23 accepted;
- EASY 19×20 rejected;
- EASY 20×30 rejected;
- MEDIUM 30×39 accepted;
- HARD 48×41 accepted;
- VERY_HARD 59×50 accepted;
- small 6×6 TRAINING_MOTIF remains accepted;
- production difficulty missing rejected.

## 6. Finding F-PAG-M05-C001-002 — contradiction/rejection diagnostics

### Current positive behavior

Retain:

- stable `WFCContradiction.code`;
- stable placement tuple;
- stable detail;
- successful candidate metadata containing prior failed-attempt records;
- retry attempt N derived from `root.retry_rng(N)`.

### Current defect

After all attempts fail, the accumulated contradiction history is discarded.

Current terminal failure exposes only:

`bounded WFC generation attempts exhausted`

This does not satisfy PAG-0530's requirement to record contradiction/rejection reasons.

### Required target behavior

Do not widen the M02 canonical success schema.

Introduce a project-owned immutable diagnostic model or equivalent internal representation, for example:

```text
WFCAttemptRecord
  attempt
  code
  placement
  detail
```

Then:

- successful `WFCCandidate` stores all prior attempt records;
- terminal exhausted generation must expose a deterministic stable diagnostic summary;
- the terminal `GenerationResult.failure.reason` may contain a compact stable canonical summary if that is the cleanest M02-compatible surface.

Recommended stable format concept:

```text
bounded WFC generation attempts exhausted [0:EMPTY_WAVE@3,5;1:MISSING_TARGET_COLOR@0,0;...]
```

Exact format may differ but must be:

- deterministic;
- bounded in length;
- no exception repr;
- no file paths;
- machine-parseable enough for tests;
- complete enough to identify each failed attempt code.

If a richer sidecar helper is created, it must not leak mutable global state between requests.

### Required adversarial tests

Add explicit tests for:

1. deterministic EMPTY_WAVE contradiction;
2. deterministic forced reconstruction conflict or another direct solver contract contradiction;
3. missing target color rejection;
4. all-attempt exhaustion includes stable attempt codes;
5. same failing request reproduces byte-identical failure result/reason;
6. attempt N retry stream is independent from previous attempt random consumption;
7. max_attempts = 1 and >1 paths;
8. successful later attempt records earlier contradiction history.

Do not merely test that one happy-path solve is deterministic.

## 7. Finding F-PAG-M05-C001-003 — truthful pattern-count metadata

### Current defect

Current metadata uses:

`sum(pattern.frequency for pattern in table.patterns)`

as:

`extracted_pattern_count`.

Because transform variants increment frequencies, this becomes a transform-expanded observation count.

C001 audit examples:

- 8×8 periodic N=3 with rotations:
  - raw extracted windows = 64;
  - current metadata = 246.

- 12×12 periodic N=3 with rotations/reflections:
  - raw extracted windows = 144;
  - current metadata = 566.

### Required target behavior

Track separate deterministic counts.

At minimum PatternTable/WFC metadata must expose:

- `raw_extracted_window_count`;
- `transformed_observation_count` or equivalently clear name;
- `unique_pattern_count`.

You may retain `extracted_pattern_count` only if it is redefined to mean the raw extraction count.

Preferred metadata fields:

```text
raw_extracted_window_count
transformed_observation_count
unique_pattern_count
```

### Exact count rules

For input_periodic = true:

`raw_extracted_window_count = exemplar.width * exemplar.height`

For input_periodic = false:

`raw_extracted_window_count = (width - N + 1) * (height - N + 1)`

`transformed_observation_count` is the sum of post-dedup transform variants added across raw windows.

### Required tests

Add exact fixtures proving:

- 6×6 periodic N=2 => raw 36;
- 8×8 periodic N=3 rotations => raw 64;
- 12×12 periodic N=3 rotations+reflections => raw 144;
- non-periodic formula;
- transformed observation count >= raw count;
- metadata stable across process/hash seed;
- golden/review metadata matches recomputation.

## 8. Finding F-PAG-M05-C001-004 — review/golden/rectangle evidence

This is an acceptance evidence remediation, not a solver redesign.

### Review pack

Current pack has 4 candidates.

Required pack:

**at least 12 accepted candidates**.

Recommended 16:

- 4 synthetic cardinality exemplars;
- 4 configurations/seeds each.

At minimum cover:

- all 4 synthetic exemplar IDs;
- N=2;
- N=3;
- input periodic true/false;
- output periodic true/false where legal;
- rotations;
- reflections;
- multiple seeds;
- at least 4 rectangular outputs.

Suggested legal rectangles:

- EASY: 29×23
- MEDIUM: 30×39
- HARD: 48×41
- VERY_HARD: 59×50

Use only configurations that naturally solve.

Do not fake a rectangular preview by resizing a square output.

### Exemplar preview evidence

Each review manifest candidate must include the source exemplar motif:

- exemplar width;
- exemplar height;
- exemplar logical pixels;
- source palette;
- synthetic ownership/provenance.

Contact sheet must render **two canvases per candidate**:

1. exemplar motif;
2. generated WFC output.

The visual relationship should be reviewable without opening fixture JSON.

### Review metadata

Each candidate should display:

- exemplar ID;
- seed;
- difficulty;
- output dimensions;
- N;
- input periodic;
- output periodic;
- transforms;
- raw extracted window count;
- transformed observation count;
- unique pattern count;
- target palette;
- mapping;
- attempt;
- contradiction history.

Keep review artifact self-contained and offline.

### Golden expansion

Current golden set has 3 square entries.

Expand it to at least **5** entries and include:

- N=2 non-periodic;
- N=2 periodic;
- N=3;
- at least one rectangular output;
- at least one 10-color VERY_HARD output.

Prefer one 59×50 or 50×59 10-color golden if it solves reliably.

Record:

- exemplar ID;
- exemplar digest;
- dimensions;
- config;
- mapping;
- raw window count;
- transformed observation count;
- unique pattern count;
- pattern-table digest;
- output-grid digest;
- GenerationResult digest;
- attempt/history.

### Generator-level rectangle tests

Add WFCGenerator integration tests, not only solver tests.

At minimum:

- EASY 29×23;
- MEDIUM 30×39;
- HARD 48×41;
- VERY_HARD 59×50

across legal exemplar/palette combinations.

Not every periodic configuration must solve every rectangle.

### Acceptance batch

Rerun at least 120 candidates.

This time the acceptance matrix must include rectangles.

Recommended matrix:

- all 4 synthetic exemplar/difficulty pairs;
- mix square + rectangular legal dimensions;
- N=2/N=3;
- periodic/non-periodic;
- multiple seeds.

Required:

- >=100 accepted;
- record contradictions honestly;
- exact dimensions;
- exact requested palette;
- no BG01;
- deterministic rerun;
- bounded attempts;
- correct metadata counts.

## 9. Review documentation corrections

Update `exemplars/README.md` to state explicitly:

- inbox items are not auto-approved;
- provenance and logical-contract validation are mandatory;
- upstream/external WFC sample images are forbidden as SCRUBBOTS owner exemplars;
- no owner-approved exemplar ships in M05.

Update `tests/fixtures/wfc/README.md` so the fixture count is truthful, including the benchmark fixture.

## 10. Keep validated WFC core unchanged where possible

Do not rewrite unless required:

- Pattern exact tuple representation;
- transform algorithms;
- adjacency compatibility;
- weighted integer pattern choice;
- deterministic queue propagation;
- periodic/non-periodic reconstruction;
- operation bounds;
- palette mapping;
- root RNG validation;
- no post-solve color repair;
- default empty registry;
- offline boundary.

Changes to `PatternTable` for truthful counters are expected.

Changes to solver should be minimal and test-driven.

## 11. Optional tie-selection improvement

Non-blocking:

Current observation chooses the first row-major placement among equal minimum cardinalities.

You may preserve this behavior.

If you choose to use deterministic RNG tie selection:

- use a named RNG child domain;
- add cross-process determinism tests;
- expect golden changes;
- document them.

Do not change this merely for novelty.

## 12. Golden and review regeneration

Regenerate M05 goldens/review only after the four findings are corrected.

Builder log must identify:

- old/new golden entries;
- why hashes changed;
- whether solver output changed or metadata-only changes occurred.

Do not modify M00-M04 goldens.

## 13. 59×59 benchmark

Refresh the benchmark after remediation.

At minimum:

- N=2 non-periodic;
- N=3 non-periodic;
- periodic case where legal.

Record:

- Python/platform;
- exemplar;
- pattern count;
- placement count;
- sample count;
- success/failure;
- median;
- p95;
- worst.

Do not invent an M10 performance budget.

## 14. Full regression

Run and log:

- exemplar dimension tests;
- contradiction/retry adversarial tests;
- metadata-count tests;
- WFC pattern/solver tests;
- palette mapping tests;
- WFC generator integration tests;
- rectangular integration tests;
- review evidence tests;
- golden tests;
- >=120 acceptance matrix;
- benchmark;
- cross-process determinism;
- offline/source-policy scan;
- M00-M04 regressions;
- full repository pytest;
- standalone import;
- `pip check`;
- no-network/no-random/no-hash/no-subprocess/no-eval scans;
- `git diff --check`;
- no M06+ source scan.

C001 builder baseline:

- focused/golden/acceptance: 14 PASS
- full repository: 222 PASS
- acceptance: 120/120

The new suite should grow materially.

## 15. Prohibited shortcuts

Do not:

- duplicate M01 difficulty bands;
- treat TRAINING_MOTIF as production artifact just to avoid dimension validation;
- drop contradiction history on terminal failure;
- call transform-expanded counts “raw extracted”;
- inflate review candidate count by duplicating identical candidate records;
- resize outputs to create rectangles;
- omit exemplar preview from review evidence;
- fake a 10-color golden with an unused color;
- inject missing colors after collapse;
- modify M02 canonical result schema unnecessarily;
- begin M06+;
- edit ChatGPT-owned task/tracker/audit state;
- self-audit.

## 16. Builder exit criteria

Builder may stop as implementation complete / pending independent audit only when:

- PRODUCTION_ARTIFACT dimensions use M01 validation;
- TRAINING_MOTIF small exemplars remain legal;
- terminal failures expose deterministic bounded attempt-code diagnostics;
- contradiction/retry adversarial tests pass;
- raw/transformed pattern counts are truthful;
- review pack contains >=12 accepted examples;
- exemplar and generated canvases both render in the contact sheet;
- review includes rectangles and multiple seeds;
- golden set includes rectangle + 10-color VERY_HARD;
- generator-level rectangles are tested;
- >=120 acceptance cases rerun with >=100 accepted;
- 59×59 benchmark refreshed;
- full M00-M05 regression passes;
- no M06+ implementation exists;
- matching C002 builder log is published;
- implementation commit(s), push result, and equality checkpoint are recorded.

Do not close M05. ChatGPT will independently re-audit.
