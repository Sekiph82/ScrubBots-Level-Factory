# PAG-M07-C001 — Artwork Quality & Diversity Filters

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-09-10  
Auditor: ChatGPT  
Cycle: `PAG-M07-C001`  
Repository: `Sekiph82/ScrubBots-Level-Factory`  
Branch: `main`

Audited builder boundary:
- cycle base / M07-ready state: `2fe708cd4bd559907ae83ce422d541cf9f064996`
- implementation/review commit: `81059b10e34c1cdedab9d1fc2152306dd87b5ae4`
- first builder-log publication commit: `e8725a62e23f693adfd66b715ea2207158f6d1d7`
- equality-recording log commit / terminal builder-era HEAD independently observed: `6eba2c153014b1191aeda895ca19954e58920afc`

Previous independent audit:
- `.hiveai/audits/PAG-M06-C004_WFC_EVIDENCE_BINDING_CLOSURE_STRICT_AUDIT.md`

Authoritative prompt:
- `.hiveai/prompts/PAG-M07-C001_ARTWORK_QUALITY_AND_DIVERSITY_FILTERS_PROMPT.md`

## 1. VERDICT

**FAIL**

M07-C001 establishes a substantial dedicated quality layer, deterministic grid-only negative-space inference, immutable/canonical reports, exact-grid hashing, non-resizing similarity analysis, review artifacts, and broad regression coverage. Those parts are useful and should be preserved.

However, four MAJOR acceptance defects remain:

- `F-PAG-M07-C001-001` — `isolated_occupied_count` and tiny occupied-region metrics are computed from per-color components instead of occupied-mask components, changing the contract semantics and creating false fragmentation on connected multicolor subjects.
- `F-PAG-M07-C001-002` — `largest_color_dominance` measures the largest connected component of any occupied color, not total occupied usage by color; the rejection gate also suppresses configured dominance when there is only one occupied color.
- `F-PAG-M07-C001-003` — mandatory acceptance fixtures/tests are incomplete or mislabeled: the committed “multi-island” fixture has the same single connected subject geometry as other good fixtures, required symmetry/component edge cases are not directly tested, and representative M03-M06 compatibility tests prove analyzability but not conservative acceptance/non-systematic rejection.
- `F-PAG-M07-C001-004` — the human-review contact sheet omits mandatory exact grid-hash and diversity/duplicate evidence and does not fully expose the required review-card evidence contract.

M07 is not accepted. M08+ remains blocked pending bounded M07 remediation.

## 2. CONTRACT RECOVERY

M07-C001 was required to implement `PAG-0701` through `PAG-0738` as an independent deterministic structural-quality/diversity layer.

Relevant mandatory contract points recovered from the prompt:

1. core metrics must be derived only from width, height and row-major logical C-ID cells;
2. negative space must be inferred deterministically and explicitly heuristically;
3. `isolated occupied single-cell count` and `tiny occupied-region count` are occupied-structure metrics, distinct from per-color connected-component statistics;
4. largest-region and color-dominance concepts must remain distinct;
5. configured rejection thresholds must be real policy controls, not bypassed by hidden structural conditions;
6. acceptance evidence must include real connected, sparse, multi-island, symmetric, asymmetric and rectangular good fixtures plus deliberate bad fixtures;
7. explicit edge-case tests include horizontal-only symmetry, vertical-only symmetry, asymmetric grids and multiple equal-size components;
8. representative accepted M03-M06 outputs must not be systematically classified as garbage;
9. each review card/entry must expose identity, generator metadata when applicable, difficulty, dimensions, used-color count, inferred negative space, core metrics, decision/rejection codes, exact grid hash and diversity evidence where applicable;
10. no resize/interpolation/network/cloud/GPU/gameplay-solver behavior may be introduced.

## 3. BRANCH / HEAD / DIFF SCOPE

Independent GitHub comparison from `2fe708cd...` to `6eba2c15...` shows three commits and twelve changed paths:

- matching C001 builder log;
- `src/scrubbots_pixel_factory/quality/{core.py,review.py,__init__.py,README.md}`;
- public quality exports in `src/scrubbots_pixel_factory/__init__.py`;
- M07 unit/integration tests;
- `review/m07/build_review.py`;
- committed M07 manifest/contact sheet.

No M08+ implementation is present in the builder boundary. Existing MASK/RULES/WFC/HYBRID production implementations were not modified.

Result: **PASS for scope discipline**

## 4. ACCEPTANCE CRITERIA MATRIX

| Criterion | Result | Independent conclusion |
| --- | --- | --- |
| Dedicated quality package | PASS | M07 logic is isolated under `quality/`. |
| Grid-only negative-space inference | PASS | Boundary-majority, whole-grid count and ascending C-ID tie-break are explicit. |
| Canonical/off-palette input validation | PASS | Invalid dimensions/cell counts and illegal palette IDs fail closed. |
| Occupied count/ratio | PASS | Derived from inferred-negative-space exclusion. |
| Occupied connected components | PASS | Occupied mask is traversed deterministically. |
| Per-color component evidence | PASS with semantic note | Deterministic occupied-color components exist. |
| Isolated occupied cells | **FAIL** | Implemented as size-1 per-color components instead of isolated occupied-mask cells/components. |
| Tiny occupied regions | **FAIL** | Implemented as tiny per-color components instead of tiny occupied-mask regions. |
| Largest occupied-region dominance | PASS | Largest occupied component / occupied count is coherent. |
| Color dominance | **FAIL** | Uses largest same-color component rather than total occupied color usage. |
| Edge touch | PASS | Deterministic occupied boundary count/ratio. |
| Symmetry metrics | PARTIAL | Functions exist, but mandatory directional/asymmetric edge-case evidence is incomplete. |
| Entropy / adjacency | PASS structurally | Deterministic calculations and canonical serialization exist. |
| Bounding box / center of mass | PASS | Grid-only occupied geometry. |
| Rejection codes | PARTIAL | Required enum/policy exists, but semantics/evidence for fragmentation/dominance are not acceptable. |
| Exact grid hash | PASS | Framed canonical SHA-256 includes dimensions and cells. |
| Exact duplicate detection | PASS | Hash plus equality verification path exists. |
| Near-duplicate metrics | PASS | Equal-dimension occupancy Jaccard and exact-cell agreement are separate. |
| Unequal dimensions | PASS | Non-comparable; no resize. |
| Review manifest | PASS with gaps | Machine-readable, deterministic and contains grid/diversity fields. |
| Contact sheet evidence contract | **FAIL** | Does not render exact grid hash or duplicate/diversity evidence. |
| Deliberate bad fixtures | PARTIAL | Fixtures exist, but some required code assertions are not locked directly. |
| Diverse good fixtures | **FAIL** | “multi-island” and some labeled structural counterexamples are not genuinely distinct geometries. |
| M03-M06 conservative compatibility | PARTIAL | Tests show analysis succeeds but do not assert representative quality acceptance/non-systematic rejection. |
| Builder focused/regression | BUILDER PASS | Builder reports `266 passed, 1 warning`. |
| Independent CI/runtime rerun | UNVERIFIED | No GitHub Actions status/run attached to implementation commit; audit relied on direct static inspection plus builder runtime evidence. |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

### “Isolated/tiny metrics”

Builder log states the implementation “aligned tiny/isolated metrics with per-color connected regions.”

Repository truth: that alignment contradicts the prompt's distinct occupied-structure metric contract. `analyze_grid()` computes `isolated_occupied_count` by counting `ColorComponent.size == 1`, and computes tiny regions from per-color components. A one-cell accent touching occupied cells of another color is therefore labeled isolated/tiny even though it belongs to a larger occupied connected component.

The unit test cements this semantic mismatch: the center `C03` cell of the 3×3 occupied subject is surrounded by occupied `C02`, yet the test expects `isolated_occupied_count == 1` and `tiny_region_count == 1`.

Disposition: **FAIL**

### “Color dominance”

Builder claims a configured dominance gate exists.

Repository truth: `largest_color_dominance` is calculated as `max(component.size for component in color_components) / occupied_count`. This is largest same-color connected-region dominance, not total color-use dominance. A dominant color split into multiple connected regions can evade the configured color-dominance threshold. In addition, `_quality_codes()` only emits `DOMINANCE_VIOLATION` when `len(occupied_colors) > 1`, so a deliberately configured color-dominance threshold is silently suppressed for one occupied color.

Disposition: **FAIL**

### “Diverse structured counterexamples”

Builder claims the review pack contains the required good counterexamples.

Repository truth: `good-05-multi-island` is built with the same `_subject()` helper used for the central, asymmetric, sparse and near-duplicate-labelled cases. `_subject()` creates one continuous rectangular occupied subject; it does not create multiple occupied islands. The evidence label therefore overstates what the fixture proves. The test suite also lacks direct assertions for several prompt-mandated metric edge cases.

Disposition: **FAIL**

### “Representative compatibility”

Builder claims M03-M06 compatibility is covered.

Repository truth: compatibility tests assert generator results are successful and that M07 returns `analysis is not None`; they do not assert that a documented conservative policy accepts representative outputs or that the sample is not systematically rejected. That is weaker than the explicit M07 acceptance gate.

Disposition: **PARTIAL / FAIL as acceptance evidence**

### “Self-contained review evidence”

Builder produced both manifest and contact sheet.

Repository truth: the manifest carries hashes/diversity fields, but `build_contact_sheet()` renders only candidate ID, mode, seed, difficulty, dimensions, the grid, a short occupied/components/background/colors summary and decision/rejection codes. It omits the exact grid hash and duplicate/near-duplicate evidence required on review cards, and does not expose enough of the requested evidence to independently inspect diversity from the human artifact.

Disposition: **FAIL**

## 6. FILE / SYMBOL EVIDENCE

### `quality/core.py::analyze_grid`

Accepted:
- strict canonical cell validation;
- deterministic boundary-majority negative-space inference;
- deterministic occupied-mask component traversal;
- canonical adjacency and entropy evidence;
- non-mutating analysis.

Defect:
- `isolated_count = sum(1 for component in color_components if component.size == 1)` uses per-color components;
- `tiny_components = ... color_components ...` uses per-color components;
- `largest_color = max(component.size for component in color_components)` uses largest component rather than aggregate color counts.

Result: **FAIL on metric semantics**

### `quality/core.py::_quality_codes`

Accepted:
- stable enum ordering;
- conservative policy object;
- multiple codes can be emitted;
- checkerboard and difficulty validation are explicit.

Defect:
- dominance is conditioned on `len(occupied_colors) > 1`, making configured dominance controls ineffective for one occupied color;
- fragmentation gates consume the semantically wrong isolated/tiny metrics above.

Result: **FAIL**

### `tests/unit/test_m07_quality.py`

Accepted:
- negative-space tie-breaking;
- rectangular input;
- invalid input codes;
- checkerboard/salt/tiny/full-slab behavior;
- framed grid hash;
- duplicate/near-duplicate behavior;
- cross-process canonical serialization;
- no-resize/network-symbol checks.

Defects/gaps:
- the hand-computable subject test explicitly expects a surrounded one-cell accent to be an isolated occupied cell/tiny occupied region;
- no direct `EMPTY_ARTWORK` expected-code assertion;
- no direct `DOMINANCE_VIOLATION` expected-code assertion;
- no direct horizontal-only symmetry test;
- no direct vertical-only symmetry test;
- no true asymmetric-grid score test;
- no multiple-equal-size occupied-component test;
- no direct one-occupied-cell metric test.

Result: **FAIL for mandatory acceptance completeness**

### `review/m07/build_review.py`

Accepted:
- deterministic committed review builder;
- deliberate bad fixtures;
- generated MASK/RULES/HYBRID and synthetic-test-only WFC evidence;
- no owner artwork fabrication.

Defect:
- `good-05-multi-island` is built by `_subject()` and therefore is not a multi-island occupied composition;
- several “good” fixtures are largely color swaps of the same geometry, weakening diversity evidence;
- fixture difficulty metadata is mostly absent even though the review-card contract asks to show difficulty.

Result: **FAIL for acceptance evidence quality**

### `quality/review.py::build_contact_sheet`

Defect:
- exact `grid_hash` is not rendered;
- exact/near duplicate evidence is not rendered;
- only a small summary of metrics is shown.

Result: **FAIL**

### `tests/integration/test_m07_generator_compatibility.py`

Defect:
- assertions prove that representative generator outputs can be analyzed, not that the conservative M07 policy avoids systematically rejecting them.

Result: **PARTIAL**

## 7. FOCUSED TEST EVIDENCE

Builder reports:

- first M07 unit iterations exposed and corrected multiple failures;
- final M07 unit suite: `11 passed, 1 warning`;
- focused M07/review/compatibility suite: `16 passed, 1 warning`;
- post-refinement focused suite: `16 passed, 1 warning`.

The existence of green focused tests is confirmed structurally, but some tests encode the wrong occupied-fragmentation semantics and mandatory edge cases/rejection-code assertions are absent.

Result: **FAIL despite builder-green focused suite**

## 8. REGRESSION EVIDENCE

Builder reports:

- M07 + M01-M06 representative regression: `176 passed, 1 warning`;
- full repository regression: `266 passed, 1 warning` before and after refinement;
- standalone import: PASS;
- cross-process/hash-seed test: PASS;
- offline/no-resize/built-in-hash/M08+ scans: PASS;
- `git diff --check`: PASS;
- unchanged pytest/pytest-asyncio `pip check` mismatch.

No GitHub Actions workflow run or combined status is attached to the implementation commit. Independent runtime execution is therefore not promoted beyond builder evidence.

Result: **BUILDER PASS / acceptance still FAIL due contract defects**

## 9. SECURITY / SAFETY / OFFLINE REVIEW

No runtime HTTP/cloud/AI/GPU dependency is introduced. The quality layer is pure Python and grid-only. No resize/resampling or perceptual-image library is introduced. No secrets or owner-private data are embedded.

Result: **PASS**

## 10. ARCHITECTURE CONSISTENCY

The dedicated `quality/` package is the correct architectural boundary. Existing generators are not modified to auto-reject or repair output, M02 result contracts remain untouched, and quality/diversity evidence is separate from generator success/failure state.

Result: **PASS**

The remediation must preserve this architecture rather than moving quality logic into individual generators.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

The builder log is detailed and records failed tests/corrections, changed files, test counts, known `pip check` mismatch, implementation commit and publication sequence.

The log records equality for `e8725a6...`, then a later log-only commit `6eba2c15...` records that statement. GitHub confirms `6eba2c15...` is the terminal builder-era commit on `main`, but the log cannot simultaneously record a post-push local equality check for the commit that contains the equality statement itself. Treat this as a non-blocking process note, not a product defect.

More importantly, the claim that required fixture/metric coverage is complete is not supported by the source/tests as described above.

Result: **FAIL on acceptance claims; publication itself confirmed**

## 12. FINAL REPOSITORY STATE

Terminal builder-era HEAD observed: `6eba2c153014b1191aeda895ca19954e58920afc`.

Builder diff is bounded to M07. No M08+ implementation exists in the audited boundary. M06 remains unchanged and previously accepted.

Result: **PASS for repository scope / FAIL for M07 acceptance**

## 13. OPEN CROSS-MILESTONE FINDINGS

- `PAG-0441` remains blocked until M10 establishes the V1 performance budget.
- The local pytest/pytest-asyncio mismatch remains a known environment issue and was not changed by M07.
- M08+ must remain blocked until M07 receives unconditional independent PASS.

## 14. DEFECTS BY SEVERITY

### BLOCKER

None.

### MAJOR

- `F-PAG-M07-C001-001`: occupied isolated/tiny metrics use per-color components instead of occupied-mask components.
- `F-PAG-M07-C001-002`: color-dominance metric/gate does not represent total occupied color dominance and can ignore an explicit configured threshold.
- `F-PAG-M07-C001-003`: required good-fixture/edge-case/representative-acceptance evidence is incomplete or mislabeled.
- `F-PAG-M07-C001-004`: contact-sheet cards omit mandatory grid-hash/diversity evidence and do not expose the full required review-card contract.

### MINOR

None.

### NOTE

- `N-PAG-M07-C001-001`: no GitHub Actions runtime status is attached to the implementation commit; builder test results remain runtime evidence supplied by Codex.
- `N-PAG-M07-C001-002`: the final equality statement is recorded by a later log-only commit, so equality of that later terminal commit is not itself recorded inside the same immutable log.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

- Consider keeping per-color singleton/tiny-component statistics as separate explicitly named metrics if they are useful for color-fragmentation analysis, but do not substitute them for occupied-mask fragmentation metrics.
- Consider exact integer numerator/denominator evidence for ratios in a future schema revision if downstream persisted numeric comparisons become important.
- Keep review fixture builders factored by structural intent rather than reusing one geometry helper under multiple semantic labels.

None of these suggestions authorizes M08 work.

## 16. UNVERIFIED ITEMS

- Independent runtime execution of the `266 passed` full suite.
- Builder-local equality after the final `6eba2c15...` log-only commit.

Direct GitHub source/diff evidence is sufficient to establish the four acceptance defects regardless of these unverified runtime items.

## 17. REGRESSION RISK

**MEDIUM.**

The architecture is clean and regression tests are broad, but the affected metrics feed policy decisions. Correcting occupied fragmentation and color dominance may alter acceptance/rejection outcomes and require deterministic regeneration of the M07 review manifest/contact sheet. Remediation must therefore rerun M03-M06 compatibility and full regression.

## 18. AUDIT CONFIDENCE

**HIGH.**

The findings are based on direct GitHub inspection of the authoritative prompt, builder diff, production quality source, unit/integration tests, review builder and committed evidence. The strongest defects are semantic and visible directly in the implementation, not inferred from missing runtime logs.

## 19. FINAL VERDICT

**FAIL**

`PAG-M07-C001 — Artwork Quality & Diversity Filters` is not accepted.

Preserve the accepted architecture, negative-space inference, hashing/similarity design, offline boundary and M00-M06 behavior. Remediate only the structural-metric semantics, policy evidence and review/acceptance proof identified above.

M08+ remains blocked.

## 20. REQUIRED REMEDIATION

Issue bounded cycle:

`PAG-M07-C002 — Structural Metric Semantics & Acceptance Evidence Remediation`

C002 must at minimum:

1. compute isolated occupied cells and tiny occupied regions from occupied-mask connected structure;
2. keep per-color component statistics separate and explicitly named;
3. compute total occupied color-use dominance independently from largest connected-region dominance;
4. make explicit dominance thresholds enforceable rather than silently disabled by occupied-color count;
5. add direct known-answer tests for all prompt-mandated structural edge cases and every required rejection code;
6. replace mislabeled good fixtures with structurally real multi-island/symmetric/asymmetric/sparse/rectangular counterexamples;
7. directly prove representative M03-M06 outputs are not systematically rejected under the documented conservative policy;
8. render exact grid hash and duplicate/diversity evidence in the human contact sheet and strengthen review tests;
9. regenerate deterministic M07 review evidence as required;
10. rerun focused, cross-process, M03-M06 regression and full repository tests;
11. do not begin M08+ or rewrite accepted M00-M06 generator behavior.