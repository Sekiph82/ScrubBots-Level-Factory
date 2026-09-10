# PAG-M07-C002 — Structural Metric Semantics & Acceptance Evidence Remediation

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Authoritative C001 strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M07-C001_ARTWORK_QUALITY_AND_DIVERSITY_FILTERS_STRICT_AUDIT.md`

C001 builder log:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/PAG-M07-C001_ARTWORK_QUALITY_AND_DIVERSITY_FILTERS_CODEX_LOG.md`

C001 prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M07-C001_ARTWORK_QUALITY_AND_DIVERSITY_FILTERS_PROMPT.md`

## 1. Mission

Remediate only the four open C001 findings:

- `F-PAG-M07-C001-001` — occupied isolated/tiny metrics use per-color components instead of occupied-mask components;
- `F-PAG-M07-C001-002` — color dominance measures largest same-color component instead of total occupied color use and configured dominance can be suppressed;
- `F-PAG-M07-C001-003` — acceptance fixtures/edge cases/representative generator acceptance evidence are incomplete or mislabeled;
- `F-PAG-M07-C001-004` — the contact sheet omits mandatory grid-hash/diversity evidence.

Preserve accepted C001 work:

- dedicated `quality/` architecture;
- grid-only boundary-majority negative-space inference;
- canonical/off-palette validation;
- deterministic occupied component traversal;
- entropy, adjacency, edge-touch, bbox/center-of-mass calculations unless a new focused test proves a defect;
- framed SHA-256 logical-grid hash;
- collision-safe exact duplicate detection;
- equal-dimension occupancy/color-layout similarity with no resize;
- immutable/canonical report models;
- offline/no-cloud/no-GPU boundary;
- M00-M06 behavior.

Do not begin PAG-M08+.

## 2. GitHub-first authority

Before editing, read completely from GitHub `main`:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. v3 machine block in `.hiveai/TASKS.md`
4. `.hiveai/EVENTS.jsonl`
5. `tasks.md`
6. `.hiveai/CYCLE_INDEX.md`
7. `AGENTS.md`
8. `GOVERNANCE.md`
9. C001 prompt
10. C001 builder log
11. C001 strict audit
12. current `quality/` source
13. current M07 unit/integration tests
14. current `review/m07` builder/manifest/contact sheet
15. representative accepted M03-M06 tests/results used by C001
16. this C002 prompt

GitHub `main` is current-state authority. The only authorized local workspace is:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Never substitute or modify:

`C:\Users\sekip\Desktop\ScrubBots`

Use only non-destructive synchronization. No force-push, hard reset, blanket restore/clean, or stale tracker overwrite.

## 3. Matching builder log

Before the first C002 product/test/review edit create:

`.hiveai/codex-logs/PAG-M07-C002_STRUCTURAL_METRIC_SEMANTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M07-C002 — Structural Metric Semantics & Acceptance Evidence Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- authority URLs;
- starting branch/HEAD/origin/status;
- synchronization and preserved local changes;
- mandatory reads;
- each semantic correction;
- failed tests and corrections;
- review evidence regeneration;
- focused/cross-process/M03-M06/full regression results;
- static scans;
- `pip check` result;
- changed files and scope check;
- implementation commit SHA(s);
- push result;
- final publication/equality checkpoint.

Do not edit ChatGPT-owned tracker/audit/task acceptance state and do not self-audit.

## 4. Fix F-PAG-M07-C001-001: occupied fragmentation semantics

The C001 source currently derives `isolated_occupied_count`, `tiny_region_count`, and `tiny_region_cell_count` from per-color connected components. That is not the required occupied-structure semantics.

Correct the model so these concepts are distinct:

### 4.1 Occupied-mask metrics

Using the boolean occupied mask after deterministic negative-space inference:

- `occupied_component_count` = number of 4-neighbor occupied connected components;
- `occupied_component_sizes` = deterministic sizes of those components;
- `isolated_occupied_count` = number of occupied cells whose occupied connected component has size exactly 1;
- `tiny_region_count` = number of occupied-mask connected components whose size is `<= tiny_region_max_size`;
- `tiny_region_cell_count` = total occupied cells belonging to those tiny occupied-mask components.

A single-color accent cell embedded inside/touching another occupied color is **not** an isolated occupied cell merely because it forms a one-cell same-color component.

Mandatory regression fixture:

- reuse/adapt the C001 5×5 central subject where a single `C03` cell is surrounded by occupied `C02`;
- expected occupied component count remains `1`;
- expected `isolated_occupied_count == 0`;
- expected occupied `tiny_region_count == 0` for threshold 3 because the occupied component size is 9;
- per-color evidence may still show a one-cell `C03` component.

### 4.2 Preserve per-color evidence separately

Keep deterministic per-color component counts/sizes because PAG-0703 requires them.

If per-color singleton/tiny statistics are useful, expose them only under explicitly different names. Do not overload the occupied-fragmentation metric names.

Update rejection gates for salt-and-pepper/tiny occupied fragmentation so they consume the corrected occupied-mask metrics unless a separately named/color-fragmentation policy is intentionally added. Do not silently preserve the old semantics under the old names.

## 5. Fix F-PAG-M07-C001-002: total color dominance semantics

`largest_occupied_region_dominance` and color dominance are different metrics.

Implement:

- `largest_occupied_region_dominance` = largest occupied connected-component size / occupied cell count;
- `largest_color_dominance` = maximum **total occupied cell count for one occupied C-ID**, summing across all of that color's connected components, divided by occupied cell count.

Do not compute color dominance from the largest same-color component.

### 5.1 Configured threshold must be enforceable

A configured `max_color_dominance_ratio` must not be silently disabled merely because only one occupied color exists.

If enforcing the existing default would become too aggressive for good fixtures, make the default conservative, for example `1.0`, rather than ignoring an explicit configured threshold based on occupied-color count.

The same principle applies to explicitly configured largest-region dominance: policy values must represent real gates.

Mandatory tests:

1. a split-dominant-color fixture where one occupied C-ID has the dominant total cell count but is separated into multiple same-color components by another occupied color; assert total color dominance and `DOMINANCE_VIOLATION` correctly;
2. a one-occupied-color fixture with an explicitly strict color-dominance threshold; prove the explicit threshold is honored;
3. conservative default good subject remains accepted when appropriate;
4. largest-region and largest-color dominance are asserted independently on at least one fixture where their values differ.

## 6. Fix F-PAG-M07-C001-003: mandatory metric/rejection acceptance evidence

### 6.1 Direct known-answer metric edge cases

Add direct tests for all C001 prompt edge cases, including at minimum:

- all one color / inferred empty;
- exactly one occupied cell;
- full occupied interior with inferred border/background;
- rectangular grid;
- horizontal-only symmetry;
- vertical-only symmetry;
- deliberately asymmetric grid;
- multiple equal-size occupied components;
- entropy zero;
- negative-space tie by whole-grid count;
- negative-space remaining tie by ascending C-ID.

For horizontal/vertical symmetry, explicitly document which geometric reflection each field means and construct fixtures that distinguish the two axes. Do not use a fixture where both scores happen to match.

### 6.2 Every required rejection code must be asserted directly

Add explicit expected-code tests for:

- `EMPTY_ARTWORK`;
- `FULL_SINGLE_SHAPE_SLAB`;
- `EXCESSIVE_SALT_AND_PEPPER`;
- `EXCESSIVE_TINY_REGIONS`;
- `DOMINANCE_VIOLATION`;
- `CHECKERBOARD_NOISE`;
- `DIFFICULTY_COLOR_COUNT`;
- `OFF_PALETTE`;
- `DIMENSION_MISMATCH`.

For policy-driven rejections, include at least one nearby good/counterexample that must not receive the code. Keep canonical multi-code ordering tests.

### 6.3 Replace mislabeled good fixtures with structurally real fixtures

The committed review builder must contain genuinely different structural good cases.

At minimum create and test:

- connected central subject;
- sparse negative-space composition;
- **real multi-island occupied composition with at least two occupied-mask components**, under a policy that permits it;
- clearly symmetric subject with the expected axis score(s);
- deliberately asymmetric organic subject with nontrivial lower symmetry scores;
- rectangular subject.

Do not label the same `_subject()` geometry as multiple structural categories merely by recoloring it.

Review-evidence tests must assert the claimed structural property, for example:

- multi-island `occupied_component_count >= 2`;
- symmetric fixture expected symmetry score exactly/near the designed value;
- asymmetric fixture score below the chosen documented bound;
- sparse fixture occupied ratio below the documented bound;
- rectangular width != height.

### 6.4 Representative M03-M06 quality acceptance

Strengthen compatibility tests beyond `analysis is not None`.

Using a documented conservative policy:

- generate representative accepted outputs from MASK, RULES, HYBRID/AUTO and synthetic-test-only WFC where available;
- assert analysis succeeds;
- assert the sample is **not systematically rejected** by M07;
- preferably assert at least one accepted sample from every represented family and report any family-specific policy relaxation explicitly;
- do not weaken product contracts or mutate generator output to make it pass.

If WFC requires a deliberately permissive policy for salt/tiny/color dominance due its pattern characteristics, keep that policy explicit and prove the relaxation is bounded to quality evaluation, not generator behavior.

## 7. Fix F-PAG-M07-C001-004: complete review-card evidence

Preserve the deterministic manifest and self-contained HTML, but make each valid contact-sheet card inspectable without opening the JSON manifest.

For every valid card render at minimum:

- candidate/review ID;
- generator mode/family;
- seed;
- difficulty or an explicit fixture/test classification if canonical difficulty is genuinely not applicable;
- exact dimensions;
- distinct used-color count;
- inferred negative-space C-ID;
- core structural metrics sufficient to inspect quality, including occupied ratio/component count, isolated/tiny counts, dominance and symmetry;
- ACCEPT/REJECT quality decision;
- stable rejection codes;
- exact logical-grid SHA-256 hash;
- exact duplicate group if any;
- near-duplicate partner evidence if any, including occupancy/color-layout similarity.

For invalid-input fixtures where canonical logical-grid hash cannot be computed by design, render an explicit `UNAVAILABLE: INVALID_INPUT` style value rather than silently omitting the field.

Do not add JavaScript, CDN, external fonts/assets or runtime network access.

Preserve presentation-only integer/CSS pixel enlargement and the original logical grid.

Strengthen integration tests to parse/assert representative rendered card content, not merely search the whole HTML for generic tokens.

## 8. Review manifest and difficulty truthfulness

The machine-readable manifest may keep `human_review` blank until actual owner review.

Do not fabricate owner ACCEPT/REJECT decisions.

For deterministic hand-authored fixtures, make `difficulty` truthful and inspectable:

- when a fixture is intentionally mapped to a canonical difficulty band, record it;
- when canonical difficulty is not applicable because the fixture is an invalid-input test, record a clearly documented fixture classification rather than pretending it is generated accepted artwork.

Do not allow a displayed `difficulty` field to imply that difficulty validation occurred when the selected quality policy did not perform it. Keep metadata and validation policy semantics explicit.

## 9. Preserve exact/near duplicate design

Do not redesign the accepted C001 duplicate architecture unless a focused test proves a defect.

Preserve:

- framed SHA-256 width/height/cells identity;
- collision-safe exact equality check;
- occupancy-mask similarity separate from color-layout similarity;
- unequal dimensions non-comparable;
- no resizing/interpolation;
- quality decision separate from diversity evidence;
- no mutation/regeneration by M07.

You may exclude exact duplicates from the near-duplicate list only if you document and test that semantic change; otherwise preserve current behavior.

## 10. Canonical serialization and determinism

After semantic fixes:

- repeated same input/policy must produce byte-identical canonical quality report;
- cross-process/PYTHONHASHSEED evidence must remain identical;
- any new mapping/list fields must have canonical ordering;
- review manifest/contact sheet regeneration from the same fixtures/config must be byte-stable;
- no timestamps or local absolute paths may enter committed review evidence.

## 11. Required focused tests

At minimum run and pass:

- `tests/unit/test_m07_quality.py`;
- `tests/integration/test_m07_review_evidence.py`;
- `tests/integration/test_m07_generator_compatibility.py`;
- any new M07 tests added for metric semantics/review parsing;
- cross-process/hash-seed determinism test(s).

Focused tests must directly prove each C001 finding closed, not only produce a green aggregate count.

## 12. Required regression verification

At minimum run and log:

- all M07 focused tests;
- M01/M02 contract tests affected by validation assumptions;
- representative/full M03 MASK tests;
- representative/full M04 RULES tests;
- representative/full M05 WFC tests;
- M06 router/hybrid/replay/AUTO tests;
- full repository `pytest`;
- standalone package import;
- cross-process determinism;
- offline/network source scan;
- resize/resample/interpolation scan;
- forbidden built-in `hash()` / non-project randomness scan for M07 source;
- `git diff --check`;
- `python -m pip check`;
- M08+ source-scope scan.

C001 builder baseline before remediation:

- full repository: `266 passed, 1 warning`;
- M07 focused/review/compatibility: `16 passed, 1 warning`;
- representative M01-M06 + M07 regression: `176 passed, 1 warning`.

The unchanged pytest/pytest-asyncio environment mismatch may remain documented. Do not modify unrelated dependencies to hide it.

## 13. Scope limits

Allowed product changes are bounded to M07 quality/review source, M07 tests and deterministic `review/m07` evidence, plus public export adjustment only if the corrected M07 API requires it.

Do not modify:

- M03/M04/M05/M06 production generator behavior;
- M02 generation-result integrity semantics;
- owner-locked palette/dimension/color-band rules;
- M08/M09/M10/M11 product scope;
- third-party exemplars/assets;
- main ScrubBots repository.

Do not edit ChatGPT-owned:

- `.hiveai/TASKS.md`;
- `.hiveai/EVENTS.jsonl`;
- `tasks.md` state/checkboxes/current-cycle authority;
- `.hiveai/CYCLE_INDEX.md`;
- `.hiveai/audits/**`;
- used prompt history.

## 14. Prohibited shortcuts

Do not:

- rename wrong metrics without implementing the required occupied semantics;
- keep the old per-color singleton behavior under `isolated_occupied_count`;
- call largest same-color component “color dominance”;
- ignore an explicit threshold based on hidden color-count conditions;
- weaken thresholds merely so generated samples become green without evidence;
- classify all generator outputs as accepted by special-casing generator mode;
- use private generator topology in core M07 analysis;
- fabricate multi-island/symmetric/asymmetric fixture labels;
- remove grid-hash/diversity requirements from contact cards;
- make the HTML depend on the JSON file at runtime;
- add network/CDN/JavaScript/perceptual-image dependencies;
- resize/interpolate grids;
- begin M08+;
- self-audit.

## 15. Builder exit criteria

Builder may return for independent audit only when:

- `F-PAG-M07-C001-001` through `004` are directly closed by source + focused tests;
- central multicolor subject proves per-color singleton does not equal isolated occupied cell;
- occupied tiny-region semantics are independently proven;
- total color dominance and largest occupied-region dominance are independently proven;
- configured color dominance cannot be silently bypassed;
- every required quality rejection code has a direct expected-code test and counterexample where applicable;
- all mandatory structural edge cases are explicitly tested;
- review good fixtures are structurally genuine, especially multi-island and asymmetry;
- representative M03-M06 quality evaluation is proven non-systematically rejecting under documented conservative policy;
- contact-sheet cards expose grid hash and duplicate/diversity evidence plus required quality metadata;
- regenerated manifest/contact sheet are deterministic and self-contained;
- full regression is green except the unchanged documented environment-only `pip check` mismatch;
- no M08+ implementation exists;
- matching C002 builder log is committed and pushed;
- final publication is present on GitHub `main`;
- Codex does not declare M07 finally accepted.

Stop and return the C002 builder log to ChatGPT for independent strict re-audit.