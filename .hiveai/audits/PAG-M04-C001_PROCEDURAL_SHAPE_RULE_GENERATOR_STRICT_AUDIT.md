# PAG-M04-C001 — Procedural Shape / Rule Generator

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-09-09  
Auditor: ChatGPT  
Cycle: `PAG-M04-C001`  
Repository: `Sekiph82/ScrubBots-Level-Factory`

Audited implementation boundary:
- cycle base: `134f350d4b0500fe4ae362f24b724232d627086e`
- implementation commit: `6d75900c583c565702467f65f3e79ac3129ef132`
- builder-log publication commit / terminal builder-era HEAD: `315233b77211d4771832b1732d9f9e52af66364a`

Primary conceptual reference:
`mxgmn/MarkovJunior@42aaf24bcf54ae164fba49c0a59348297904a676`

## 1. VERDICT

**FAIL**

M04 contains substantial valid work, but the final RULES contract is not yet accepted.

Open findings:

- **F-PAG-M04-C001-001 — BLOCKER — final colorization is not bound to procedural occupied/negative-space geometry, so the logical output can visually diverge from the rule-generated structure.**
- **F-PAG-M04-C001-002 — MAJOR — POCKET primitive has the opposite primitive-level behavior: `apply_primitive(..., "POCKET")` marks the pocket cells occupied instead of carving negative space.**
- **F-PAG-M04-C001-003 — MAJOR — `BRIDGE_GAP` is not a distinct local rewrite rule; it uses the same predicate as `FILL_NOTCH`.**
- **F-PAG-M04-C001-004 — MAJOR — protected occupied semantic labels are not protected from later relabeling/operations.**
- **F-PAG-M04-C001-005 — MAJOR — four required composition recipes are seed-invariant at fixed dimensions despite the M04 requirement for variation across fixed seeds.**
- **F-PAG-M04-C001-PROC-001 — MINOR — primitive review `singleton_count` is hardcoded to zero rather than computed from evidence.**

`PAG-0441` is not failed. It remains an explicit forward dependency on the M10 performance budget, as designed.

PAG-M05+ remains blocked.

A bounded `PAG-M04-C002` remediation is required.

## 2. CONTRACT RECOVERY

M04 was required to provide:

- 12 independently testable target-grid primitives;
- 10 bounded growth/morphology/rewrite operations;
- immutable/versioned layered recipes;
- protected occupied and protected negative semantics;
- seven composition recipes with deterministic seed variation;
- region-driven canonical color assignment;
- exact legal palette use;
- minimum color component size;
- maximum dominance control;
- deliberate coherent accent regions;
- final RULES logical art reflecting the generated geometry;
- deterministic goldens and review evidence;
- >=120 accepted candidates;
- structural output substantially different from uniform random board fill.

A particularly important M04 prompt invariant was:

> negative-space/base is represented by one selected canonical logical color

and M04 colorization was explicitly required to be **region-driven**, not a separate arbitrary board partition.

## 3. BRANCH / HEAD / DIFF SCOPE

Independent GitHub history confirms two builder-era M04 commits:

1. `6d75900c583c565702467f65f3e79ac3129ef132`
   - independent `generators.rules` package;
   - M04 tests;
   - primitive/recipe goldens;
   - review manifest/contact sheet.

2. `315233b77211d4771832b1732d9f9e52af66364a`
   - matching M04 builder log.

No M05+ production/test implementation was found.

No main ScrubBots mutation was found.

No MarkovJunior runtime/source/model/asset was added.

Scope result: **PASS**

## 4. ACCEPTANCE CRITERIA MATRIX

| Task / criterion | Result | Independent conclusion |
| --- | --- | --- |
| PAG-0401 BLOB | PASS | Connected target-grid growth primitive exists. |
| PAG-0402 ISLAND | PASS | Connected deterministic island primitive exists. |
| PAG-0403 RING | PASS | Connected ring with visible interior pocket exists. |
| PAG-0404 CORRIDOR | PASS | Bounded connected endpoint path exists. |
| PAG-0405 POCKET | **FAIL** | Pure helper identifies a pocket set, but generic primitive application marks those cells occupied. |
| PAG-0406 SNAKE | PASS | Self-avoiding bounded walk. |
| PAG-0407 BRANCH | PASS | Connected bounded branch structure. |
| PAG-0408 CHAMBER | PASS | Bounded chamber region. |
| PAG-0409 SPIRAL | PASS | Connected discrete spiral/band. |
| PAG-0410 WAVE | PASS | Integer-grid deterministic wave/ribbon. |
| PAG-0411 RADIAL | PASS | Bounded radial/spoke geometry. |
| PAG-0412 VORONOI-LIKE | PASS | Full deterministic partition with stable tie break. |
| PAG-0413 seeded frontier growth | PASS | Explicit target and bounded loop. |
| PAG-0414 constrained connected growth | PASS | Bounded and fail-closed minimum target. |
| PAG-0415 erosion | PASS | Iteration bound + protected occupied preservation. |
| PAG-0416 dilation | PASS | Iteration bound + protected negative preservation. |
| PAG-0417 hole carving | PASS | Coherent explicit holes with min-size/protection. |
| PAG-0418 contour extraction | PASS / NOTE | Logical contour helper exists; board-edge semantics should remain documented. |
| PAG-0419 nested region | PASS | Bounded contained child growth. |
| PAG-0420 controlled fragmentation | PASS | Deterministic labeled coherent fragments exist for accepted fixtures. |
| PAG-0421 local rewrite rule | **FAIL** | FILL_NOTCH and BRIDGE_GAP are behaviorally the same condition. |
| PAG-0422 deterministic operation bounds | PASS | Iteration/pass bounds are explicit. |
| PAG-0423 recipe format | PASS | Immutable/versioned recipe/step model. |
| PAG-0424 no resize composition | PASS | Fixed target RuleCanvas used throughout. |
| PAG-0425 protect semantic regions | **FAIL** | Occupancy is protected, but protected occupied labels can be overwritten. |
| PAG-0426 SYMMETRY | **PARTIAL** | Structural recipe exists, but fixed-dimension geometry does not vary with seed. |
| PAG-0427 ORGANIC | PASS | Structured and seed-varying. |
| PAG-0428 CENTRAL_SUBJECT | **PARTIAL** | Structural recipe exists, but fixed-dimension geometry is seed-invariant. |
| PAG-0429 MULTI_ISLAND | PASS | Multiple coherent islands and seed variation. |
| PAG-0430 BORDER_FRAME_EMBLEM | **PARTIAL** | Structural recipe exists, but fixed-dimension geometry is seed-invariant. |
| PAG-0431 DENSE_FULL_BOARD | **PARTIAL** | Structured dense recipe exists, but fixed-dimension geometry is seed-invariant. |
| PAG-0432 SPARSE_NEGATIVE_SPACE | PASS | Sparse structured seed-varying recipe. |
| PAG-0433 color generated regions | **FAIL** | Palette legality passes, but final color patches cross occupied/negative geometry. |
| PAG-0434 exact legal color count | PASS | Exact selected palette set is used. |
| PAG-0435 avoid checkerboard | PASS | Connected patches rather than per-cell noise. |
| PAG-0436 minimum region size | PASS | Default minimum 2, fail-closed final check. |
| PAG-0437 max dominance | PASS / REMEDIATION IMPACT | Global cap exists; recipe-specific behavior must be reconciled with geometry-bound base color. |
| PAG-0438 deliberate accents | **FAIL / PARTIAL** | Non-base patches exist, but there is no explicit coherent accent semantic tied to rule geometry. |
| PAG-0439 primitive deterministic evidence | **PARTIAL / REVALIDATE** | 12 fixtures exist, but POCKET semantics must change. |
| PAG-0440 recipe deterministic evidence | **PARTIAL / REVALIDATE** | 7 fixtures exist, but static recipe variation must be fixed. |
| PAG-0441 59×59 within M10 budget | **DEFERRED** | Benchmark exists; M10 has not established budget. |
| PAG-0442 structured vs uniform random | **FAIL / REVALIDATE** | Geometry itself is structured, but final color output is insufficiently coupled to it. |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

### Claim: 12 required primitives are implemented

Eleven primitive semantics are materially aligned.

POCKET is not.

Current `pocket()` returns a centered set of cells. Generic `apply_primitive()` then executes:

`canvas.mark_many(safe, primitive)`

for every non-dict primitive, including POCKET.

Therefore an empty canvas receives an **occupied 3×3 POCKET block** in the committed review evidence.

The CENTRAL_SUBJECT recipe manually compensates by calling the primitive, then carving the returned cells immediately afterward.

That recipe workaround does not make the primitive itself satisfy PAG-0405.

Disposition: **PARTIAL / POCKET REJECTED**

### Claim: local rewrite rules include notch, gap bridge, protrusion removal

Current source:

```python
if rule.name in {"FILL_NOTCH", "BRIDGE_GAP"} \
        and index not in current \
        and occupied_neighbors >= 3:
    additions.add(index)
```

FILL_NOTCH and BRIDGE_GAP therefore have the exact same eligibility behavior.

There is no test proving a bounded two-sided gap is bridged while a notch fixture behaves differently.

Disposition: **REJECTED for BRIDGE_GAP**

### Claim: protected composition semantics prevent accidental semantic overwrite

`RuleCanvas.mark()` rejects protected negative-space writes, and protected occupied cells cannot be carved.

However, a protected occupied cell can be marked again with another label:

```python
self._occupied.add(index)
self._regions[index] = label
```

There is no check for `index in _protected_occupied` before replacing the region label.

Operations such as dilation/fragmentation and later primitive marking can therefore preserve occupancy while destroying the protected semantic label.

The BORDER_FRAME_EMBLEM recipe also runs global contour/body relabeling after frame protection.

Disposition: **REJECTED for semantic protection**

### Claim: final coloring is region-driven

Current `colorize_canvas()` does not constrain color patches to:

- `canvas.occupied`;
- `canvas.negative`;
- `canvas.regions`.

It starts with:

`available = set(range(total))`

and grows each non-base patch through arbitrary available board cells.

Occupied cells are only preferred when selecting a seed.

After seeding, color patches can cross freely between occupied and negative-space classification.

Independent committed-review analysis over 28 recipe candidates found:

- average negative-space cells painted with non-base colors: **34.1%**
- examples exceed **42%**
- occupied cells can also remain the base color.

Examples:

- SPARSE / VERY_HARD: negative-space non-base = **42.3%**
- MULTI_ISLAND / VERY_HARD: **41.5%**
- SYMMETRY / VERY_HARD: **41.2%**

Therefore the final logical grid is a connected palette partition influenced by geometry seed locations, but it is not a faithful coloring of the procedural region structure.

Disposition: **REJECTED**

### Claim: seven recipes provide deterministic variation

The prompt required each recipe to demonstrate variation across fixed seeds.

At fixed dimensions, four recipes use only seed-independent primitive parameters:

- SYMMETRY
  - RING + RADIAL, both fixed geometry for fixed dimensions/params.
- CENTRAL_SUBJECT
  - CHAMBER + RING + centered POCKET, all fixed geometry.
- BORDER_FRAME_EMBLEM
  - FRAME + CHAMBER + RING, fixed geometry.
- DENSE_FULL_BOARD
  - WAVE + fixed DILATE + RADIAL, all fixed geometry.

The RNG objects are passed but those primitive implementations do not consume them for these parameters.

Changing request seed changes palette/retry metadata, but not those recipe geometry masks.

Existing recipe tests verify repeatability, not per-recipe multi-seed variation.

Disposition: **REJECTED for required recipe diversity**

## 6. FILE / SYMBOL EVIDENCE

### `rules/model.py::RuleCanvas`

Positive:

- bounded dimensions/indexing;
- controlled mutation API;
- protected occupied/negative sets;
- deterministic geometry/region digests.

Defect:

- protected occupied region labels are mutable through ordinary `mark` / `set_region`.

Result: **FAIL only for semantic-label protection**

### `rules/primitives.py`

Positive:

- project-owned integer-grid algorithms;
- no image dependency;
- no runtime MarkovJunior;
- all primitives bounded.

Defect:

- generic `apply_primitive` treats POCKET as an occupied primitive.

Result: **FAIL for PAG-0405**

### `rules/operations.py::local_rewrite`

Positive:

- bounded passes;
- deterministic row-major scan;
- protected occupied removal prevention.

Defect:

- FILL_NOTCH and BRIDGE_GAP share one predicate and are not distinct rewrite behaviors.

Result: **FAIL for PAG-0421**

### `rules/recipes.py`

Positive:

- immutable catalog;
- seven requested families;
- no resizing;
- geometry visibly structured;
- multi-island/organic/sparse variation.

Defects:

- four recipes have no fixed-dimension seed-driven geometry variation;
- protected semantic labels can be overwritten after protection.

Result: **PARTIAL**

### `rules/colorize.py`

Positive:

- canonical C-ID validation;
- exact palette use;
- min connected component size;
- max dominance;
- deterministic connected color patches;
- no checkerboard/singleton defaults.

Blocking defect:

- patches are generated on all board cells rather than procedural region classes.
- base color is not an exact representation of negative space.
- no explicit rule-geometry accent semantic exists.

Result: **FAIL**

### `rules/generator.py`

Positive:

- RULES-only;
- canonical root RNG;
- bounded retry;
- M02 validated success/failure path;
- authenticated provenance;
- strict options.

Result: **PASS**

## 7. FOCUSED TEST EVIDENCE

Builder reports:

- M04 focused: `28 passed`
- acceptance/offline subset: `2 passed, 3 deselected`
- full repository: `201 passed`
- acceptance: `140 / 140`

Independent audit did not treat these totals as proof.

Source/test review found important missing adversarial behavior tests:

1. POCKET applied to occupied geometry actually decreases occupancy.
2. POCKET refuses/remains clear of protected occupied cells.
3. BRIDGE_GAP bridges an opposite-neighbor gap and differs from FILL_NOTCH.
4. protected occupied region label survives later mark/dilation/fragmentation.
5. base color exactly maps procedural negative-space classification.
6. non-base colors remain inside occupied geometry.
7. every recipe produces >1 geometry digest across fixed seeds.

These omissions correspond directly to the findings.

## 8. REGRESSION EVIDENCE

M00-M03 code is not materially rewritten by M04.

RULES package is independent from MASK.

No runtime dependency added.

No M05+ source found.

Builder reports 201 full regression PASS.

Result: **PASS**

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive:

- offline-only;
- no HTTP/network;
- no global random;
- no Python hash determinism;
- no subprocess/eval/exec;
- no external art;
- no MarkovJunior/C# runtime.

No safety/security blocker found.

Result: **PASS**

## 10. ARCHITECTURE CONSISTENCY

The independent RULES architecture is appropriate.

The core architectural break is between:

```text
RuleCanvas geometry/regions
        X
final logical color grid
```

The current colorizer uses geometry only as a seed preference, not as the domain being colored.

This weakens the milestone's central idea: procedural region structure should drive the logical art.

Result: **FAIL**

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Positive:

- builder log existed before M04 edits;
- no task/H!veAI/audit acceptance mutation by builder;
- 59×59 budget was not invented;
- builder failures/corrections are documented;
- MarkovJunior remains conceptual reference only.

### F-PAG-M04-C001-PROC-001 — MINOR

`review/m04/build_review.py::_primitive_entry` writes:

`"singleton_count": 0`

rather than computing it.

Independent review-mask recomputation happened to show the current 12 fixed primitive masks contain no one-cell occupied components, so the displayed value is accidentally true for this snapshot.

However review evidence must be derived, not hardcoded.

Disposition: **MINOR / remediation required with review rebuild**

## 12. FINAL REPOSITORY STATE

Terminal builder-era HEAD:

`315233b77211d4771832b1732d9f9e52af66364a`

M04 implementation:

`6d75900c583c565702467f65f3e79ac3129ef132`

No unauthorized M05+ scope was found.

Implementation is published but not accepted.

## 13. OPEN CROSS-MILESTONE FINDINGS

### F-PAG-M04-C001-001 — BLOCKER

**Final colors do not preserve RuleCanvas occupied/negative/region semantics.**

Required target:

- choose one selected canonical base C-ID for procedural negative space;
- that base C-ID must occur **only** on negative-space cells;
- occupied cells must be colored only with the remaining selected IDs;
- every remaining selected ID must occur;
- occupied coloring must remain coherent and min-size compliant;
- deliberate accent color/region must be explicit and coherent;
- recipe-specific max dominance must account for sparse negative-space-heavy recipes;
- final geometry classification must be reconstructable from base-vs-non-base logical cells.

### F-PAG-M04-C001-002 — MAJOR

**POCKET primitive must carve, not paint.**

Required target:

- apply POCKET to eligible occupied geometry;
- remove a coherent bounded pocket;
- preserve protected occupied cells;
- fail boundedly when a valid pocket cannot be carved;
- primitive golden/review must demonstrate before/after carve semantics.

### F-PAG-M04-C001-003 — MAJOR

**BRIDGE_GAP must be a distinct rewrite rule.**

Required target:

- define a bounded small-gap predicate, e.g. empty cell with occupied opposite horizontal or vertical neighbors;
- bridge behavior must differ from FILL_NOTCH;
- add behavior fixtures for both rules.

### F-PAG-M04-C001-004 — MAJOR

**Protected semantic labels must survive later operations.**

Required target:

- protected occupied cells cannot be relabeled by ordinary mark/set-region paths;
- operations preserve both occupancy and protected semantic identity;
- tests cover primitive overlap, dilation, fragmentation/rewrite and recipe composition.

### F-PAG-M04-C001-005 — MAJOR

**Four recipes require real seed-driven geometry variation.**

Affected:

- SYMMETRY
- CENTRAL_SUBJECT
- BORDER_FRAME_EMBLEM
- DENSE_FULL_BOARD

Required target:

- same dimensions + different fixed seeds produce at least two valid geometry digests;
- preserve each recipe's structural signature;
- same seed remains byte/digest identical.

## 14. DEFECTS BY SEVERITY

### BLOCKER

- F-PAG-M04-C001-001

### MAJOR

- F-PAG-M04-C001-002
- F-PAG-M04-C001-003
- F-PAG-M04-C001-004
- F-PAG-M04-C001-005

### MINOR

- F-PAG-M04-C001-PROC-001

### NOTE

`PAG-0441` remains deferred to M10. Builder benchmark evidence:

- 59×59 samples: 20
- median: 110.491 ms
- p95: 164.504 ms
- worst: 166.015 ms
- Python 3.12.10 / Windows 11

No acceptance budget exists yet, so no PASS/FAIL performance claim is made.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Non-blocking after remediation:

- extract generic region partition helpers later if M03/M04 truly share semantics, but do not couple RULES to MASK templates;
- explicitly type rule-color role assignments for review provenance;
- improve recipe review diagnostics with geometry-to-color fidelity metrics;
- M07 can later generalize these diagnostics into production quality filters.

## 16. UNVERIFIED ITEMS

Exact owner-machine test and benchmark executions remain builder evidence.

The reported 140-case source test was inspected and does check logical legality/repeatability, but not the semantic findings above.

## 17. REGRESSION RISK

**MEDIUM**

Geometry-aware coloring and recipe variation will intentionally change M04 recipe golden hashes and review artifacts.

M00-M03 goldens/contracts must remain unchanged.

## 18. AUDIT CONFIDENCE

**HIGH**

Evidence includes:

- direct GitHub source inspection;
- exact builder commit/history inspection;
- direct test-source inspection;
- independent parsing of 28 committed recipe review candidates;
- independent occupied/negative-vs-color analysis;
- independent primitive connected-component recomputation;
- manual recipe silhouette review.

## 19. FINAL VERDICT

**FAIL**

`PAG-M04-C001` is not accepted.

Validated M04 primitives/operations/recipes should be preserved.

PAG-M05+ remains blocked.

`PAG-0441` remains deferred rather than failed.

## 20. REQUIRED REMEDIATION

Create bounded cycle:

`PAG-M04-C002 — Geometry Fidelity, Operation Semantics & Recipe Diversity Remediation`

Required work only:

1. bind final base/non-base coloring to RuleCanvas negative/occupied geometry;
2. add explicit coherent accent semantics;
3. make POCKET an actual carving primitive;
4. make BRIDGE_GAP a distinct rewrite behavior;
5. preserve protected occupied semantic labels across operations;
6. add fixed-seed variation to the four static recipes;
7. compute review diagnostics rather than hardcoding them;
8. regenerate affected primitive/recipe goldens;
9. regenerate M04 review evidence;
10. rerun >=140 acceptance batch and prove geometry/color fidelity;
11. rerun M00-M04 regression;
12. retain 59×59 measurement while keeping PAG-0441 deferred to M10;
13. do not begin M05.
