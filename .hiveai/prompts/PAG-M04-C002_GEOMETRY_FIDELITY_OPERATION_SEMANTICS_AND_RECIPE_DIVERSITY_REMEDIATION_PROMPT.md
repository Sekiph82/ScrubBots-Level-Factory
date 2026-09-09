# PAG-M04-C002 — Geometry Fidelity, Operation Semantics & Recipe Diversity Remediation

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M04-C001_PROCEDURAL_SHAPE_RULE_GENERATOR_STRICT_AUDIT.md`

Previous implementation prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M04-C001_PROCEDURAL_SHAPE_RULE_GENERATOR_PROMPT.md`

Primary conceptual reference remains reference-only:
`https://github.com/mxgmn/MarkovJunior/tree/42aaf24bcf54ae164fba49c0a59348297904a676`

## 1. Scope

This is a bounded M04 remediation for the audited C001 findings only.

Open findings:

- `F-PAG-M04-C001-001` — **BLOCKER** — final RULES coloring is not bound to RuleCanvas occupied/negative-space geometry.
- `F-PAG-M04-C001-002` — **MAJOR** — POCKET primitive marks occupancy instead of carving a negative-space pocket.
- `F-PAG-M04-C001-003` — **MAJOR** — BRIDGE_GAP is behaviorally identical to FILL_NOTCH.
- `F-PAG-M04-C001-004` — **MAJOR** — protected occupied semantic labels can be overwritten.
- `F-PAG-M04-C001-005` — **MAJOR** — SYMMETRY, CENTRAL_SUBJECT, BORDER_FRAME_EMBLEM, and DENSE_FULL_BOARD do not vary geometry across fixed seeds.
- `F-PAG-M04-C001-PROC-001` — **MINOR** — primitive review singleton diagnostics are hardcoded instead of computed.

Do not reimplement the already-validated M04 architecture.

Do not begin PAG-M05+.

`PAG-0441` remains a forward dependency on the M10 V1 performance budget. Re-benchmark after remediation, but do not invent a budget or mark the task complete.

## 2. GitHub authority

GitHub is the sole task/prompt/audit authority.

Implementation repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Do not modify the main ScrubBots repository.

Do not copy/adapt MarkovJunior source, rules, models, examples, or assets.

Do not add a .NET/C#/Mono runtime dependency.

## 3. Mandatory reads

Before the first source/test/golden/review edit, read completely:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. C001 builder log
9. C001 strict audit
10. current M04 model/primitives/operations/recipes/colorizer/generator
11. current M04 unit/integration/golden/review tests
12. current review builder/manifest
13. this prompt

Preserve all M00-M03 contracts.

## 4. Matching builder log

Create **before the first source, test, golden, manifest, contact-sheet, or review-builder edit**:

`.hiveai/codex-logs/PAG-M04-C002_GEOMETRY_FIDELITY_OPERATION_SEMANTICS_AND_RECIPE_DIVERSITY_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M04-C002 — Geometry Fidelity, Operation Semantics & Recipe Diversity Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- authority/prompt/audit URLs;
- starting branch/HEAD/origin/status/ahead-behind;
- synchronization;
- mandatory reads;
- exact remediation design for every finding;
- source/test/review files changed;
- commands;
- failed tests and corrections;
- geometry→color fidelity evidence;
- POCKET before/after evidence;
- distinct rewrite-rule evidence;
- protected semantic-label evidence;
- per-recipe fixed-seed diversity evidence;
- regenerated goldens;
- regenerated review evidence;
- >=140 acceptance batch;
- 59×59 benchmark;
- full regression;
- implementation commit SHA(s);
- push/equality checkpoint;
- final changed-file summary.

Do not self-audit or edit ChatGPT-owned task/tracker/audit state.

## 5. Finding F-PAG-M04-C001-001 — final geometry/color fidelity

### Current defect

Current `colorize_canvas()` initializes all cells to the base color, then grows every non-base color patch over:

`set(range(total))`

rather than within RuleCanvas geometry classes.

Occupied geometry is only preferred when choosing a seed.

As a result, non-base colors spread through negative-space cells and base color remains on occupied cells.

Independent C001 review analysis over 28 recipe candidates found:

- average negative-space cells using non-base colors: **34.1%**
- SPARSE VERY_HARD: **42.3%**
- MULTI_ISLAND VERY_HARD: **41.5%**
- SYMMETRY VERY_HARD: **41.2%**

This breaks the procedural geometry → logical art contract.

### Required target behavior

Use one selected canonical C-ID as the exact procedural negative-space/base color.

Required V1 invariant:

```text
cell == base_color  <=>  RuleCanvas cell is negative-space
```

Therefore:

- selected palette[0] after canonical ordering may be the base color;
- every `canvas.negative` cell must use exactly the base C-ID;
- no `canvas.occupied` cell may use the base C-ID;
- every other selected C-ID must occur only on occupied cells;
- final occupied-vs-negative geometry must be exactly reconstructable from base-vs-non-base logical cells.

No BG01 or transparency.

### Geometry-derived color roles

Create an independent RULES semantic color model, not an M03 template dependency.

Recommended broad roles:

- NEGATIVE_SPACE
- OUTLINE
- BODY
- SECONDARY
- ACCENT

Exact names may differ.

At minimum:

- NEGATIVE_SPACE maps to the base color only;
- OUTLINE uses occupied contour geometry;
- BODY uses occupied interior geometry;
- ACCENT is an explicit coherent occupied subregion;
- remaining selected colors for high-cardinality palettes are deterministic coherent subregions of occupied BODY/SECONDARY/ACCENT role families.

Every selected C-ID must have an explicit internal role assignment or equivalent deterministic region assignment.

### Deliberate accent contract

Close PAG-0438 explicitly.

At least one selected non-base color in palettes with sufficient cardinality must be designated as a deliberate accent role/subregion.

Accent requirements:

- occupied cells only;
- coherent connected region;
- component size >= configured minimum;
- deterministic location;
- no singleton dots;
- no off-palette cells.

For a 3-color palette, base + outline + body is acceptable and an explicit accent may be absent because palette cardinality is too small.

For 4+ colors, reserve at least one coherent accent/secondary role.

### Minimum color-region size

Preserve current default minimum >=2.

Every same-color component must satisfy the configured minimum.

If the occupied geometry cannot accommodate every non-base selected C-ID at the required minimum, retry deterministically or fail boundedly.

Do not spill colors into negative space to solve capacity.

### Dominance policy after fidelity fix

Because exact negative-space/base mapping may make the base color naturally dominant in sparse recipes, the current universal default 82% cannot be assumed valid.

Use the immutable recipe's `max_color_dominance_pct` as the default rule-specific cap.

Set/document recipe defaults so they are compatible with each recipe's occupancy contract.

At minimum:

`recipe.max_color_dominance_pct >= 100 - recipe.occupancy_floor_pct`

subject to integer rounding.

Examples:

- a recipe with 6% occupancy floor may legitimately require up to 94% base color;
- dense recipes may keep a much stricter cap.

If user `rules` options explicitly override max dominance:

- validate 50..100;
- apply the override deterministically;
- if the requested cap is impossible for the generated occupancy, boundedly retry/fail;
- do not recolor negative space with foreground colors to satisfy it.

### Required fidelity tests

Add tests proving:

1. base color occurs on every negative-space cell;
2. base color occurs on zero occupied cells;
3. every non-base color occurs only on occupied cells;
4. `tuple(cell != base for cell in logical_grid) == tuple(index in canvas.occupied ...)`;
5. every selected C-ID is used;
6. no singleton components;
7. max dominance satisfies the effective recipe/request cap;
8. explicit accent is coherent and occupied-only;
9. 10..12-color VERY_HARD palette remains legal/coherent;
10. same request repeats byte-identically.

Run this invariant across the full 140-candidate acceptance matrix.

## 6. Finding F-PAG-M04-C001-002 — real POCKET primitive

### Current defect

`pocket()` returns candidate cells, but generic `apply_primitive()` then marks them occupied like every other set-valued primitive.

The current primitive review therefore renders POCKET as an occupied 3×3 square.

The CENTRAL_SUBJECT recipe manually compensates by immediately carving the returned cells.

### Required target behavior

POCKET must be a true carving primitive at the `apply_primitive` level.

When applied:

- the canvas must already contain eligible occupied geometry;
- choose/derive a bounded coherent pocket inside occupied cells;
- carved cells must be disjoint from `protected_occupied`;
- carved cells become negative-space;
- occupancy must decrease by exactly the carved count;
- protected occupied cells must remain occupied and semantically protected;
- failure must be bounded if no valid pocket exists.

The pure helper may still compute a candidate set, but generic primitive application must implement POCKET's carve semantics rather than mark semantics.

### POCKET tests

Required:

1. fill/chamber geometry, then apply POCKET;
2. returned pocket cells were occupied before;
3. returned pocket cells are negative afterward;
4. occupancy decreases;
5. pocket is coherent;
6. pocket size bounded;
7. protected occupied overlap rejected/avoided;
8. empty canvas POCKET fails closed;
9. deterministic same-seed behavior;
10. primitive golden/review represents carve semantics, not an occupied square.

Update CENTRAL_SUBJECT recipe to use the corrected primitive without a duplicate manual carve workaround.

## 7. Finding F-PAG-M04-C001-003 — distinct BRIDGE_GAP rewrite

### Current defect

Current source treats both:

- FILL_NOTCH
- BRIDGE_GAP

as:

`empty cell with occupied_neighbors >= 3`

So BRIDGE_GAP is not actually implemented.

### Required behavior

Keep FILL_NOTCH as a notch-filling rule.

Implement BRIDGE_GAP as a distinct bounded gap rule.

Recommended one-cell bridge predicate:

An empty eligible cell may be filled when either:

- left and right in-bounds neighbors are occupied; or
- up and down in-bounds neighbors are occupied.

Optionally support a documented bounded two-cell gap in a future change, but C002 only requires a real one-cell bridge.

Protected negative cells must never be bridged.

### Required rewrite fixtures

Create explicit small fixtures proving:

- FILL_NOTCH fills a three-sided notch;
- BRIDGE_GAP fills a horizontal one-cell gap;
- BRIDGE_GAP fills a vertical one-cell gap;
- a notch-only cell does not necessarily satisfy BRIDGE_GAP;
- a two-sided bridge-only cell does not necessarily satisfy FILL_NOTCH;
- protected negative gap remains unchanged;
- REMOVE_PROTRUSION behavior remains unchanged;
- bounded passes remain deterministic.

Do not test only that two runs are equal.

## 8. Finding F-PAG-M04-C001-004 — protected semantic identity

### Current defect

Protected occupied cells cannot be carved, but ordinary marking can replace their region label:

`self._regions[index] = label`

This means protection preserves occupancy but not semantic identity.

Operations such as dilation/fragmentation/relabeling can therefore destroy protected semantic labels.

### Required target behavior

When an occupied cell is protected, later generic operations must not silently change its protected semantic label.

Choose one clear rule:

Preferred:

- `protect_occupied()` freezes the cell's current semantic label;
- subsequent `mark(..., different_label)` preserves the original protected label;
- `set_region(..., different_label)` on protected occupied cells fails closed;
- operations may include protected occupied cells geometrically but cannot relabel them.

Equivalent strict semantics are acceptable if documented.

### Required tests

Prove protected occupied label survives:

- overlapping primitive application;
- dilation;
- controlled fragmentation;
- local rewrite;
- final recipe contour/body relabeling;
- copy/region digest behavior.

Protected negative semantics must remain intact.

Do not solve this by removing region labels entirely.

## 9. Finding F-PAG-M04-C001-005 — recipe seed diversity

### Current defect

At fixed dimensions these four recipe geometries are seed-invariant:

- SYMMETRY
- CENTRAL_SUBJECT
- BORDER_FRAME_EMBLEM
- DENSE_FULL_BOARD

because the primitives/parameters used in those recipe paths do not consume RNG to alter geometry.

### Required target behavior

Every one of the seven recipe families must show deterministic fixed-dimension variation across a fixed seed set.

For each recipe:

- same seed + same dimensions => identical geometry digest;
- fixed set of at least five different seeds => at least **2 distinct geometry digests**;
- structural signature remains valid for every accepted geometry.

Do not randomize recipe identity away.

### Seed-varying recipe guidance

Preserve structural intent while varying bounded parameters.

Examples:

#### SYMMETRY
Vary deterministically:
- ring radius/thickness within legal bounds;
- radial ray count/length;
- still enforce intended symmetry.

#### CENTRAL_SUBJECT
Vary:
- chamber width/height within centered bounded range;
- pocket size/location within subject;
- emblem ring radius;
- retain central subject.

#### BORDER_FRAME_EMBLEM
Vary:
- inner emblem/chamber size;
- ring radius;
- optional frame thickness within bounded range;
- preserve frame.

#### DENSE_FULL_BOARD
Vary:
- wave period/amplitude;
- dilation iteration count within safe range;
- radial ray count/length;
- preserve dense occupancy floor and structure.

Use named child domains.

No output may depend on unordered collection iteration.

### Required tests

For all seven recipes:

- deterministic same seed;
- >=2 geometry digests across 5 fixed seeds;
- occupancy contract;
- structural signature;
- rectangle support;
- no protected-region regression.

## 10. Review evidence truthfulness

Fix `F-PAG-M04-C001-PROC-001`.

Primitive review diagnostics must be computed from the actual primitive evidence.

Do not write:

`"singleton_count": 0`

as a constant.

Compute:

- occupied component sizes;
- singleton occupied components;
- occupied component count;
- occupancy;
- relevant primitive topology diagnostics.

For POCKET review, show both a suitable pre-carve context and the final carved geometry, or otherwise make the carve semantics unambiguous in the manifest/contact sheet.

Recipe review diagnostics should add:

- geometry/color fidelity boolean;
- base color;
- negative-space count;
- occupied count;
- base-on-occupied count;
- non-base-on-negative count;
- accent component sizes;
- effective max dominance cap.

Acceptance target:

- base-on-occupied = 0;
- non-base-on-negative = 0;
- fidelity = true.

## 11. Golden regeneration

Expected changed evidence:

- POCKET primitive fixture;
- all recipe final grid hashes because color fidelity changes;
- static recipe geometry hashes where seed diversity changes.

Regenerate M04 goldens only after behavior is correct.

Builder log must record old/new hashes or at minimum identify every changed fixture and exact reason.

Do not modify M00-M03 golden fixtures.

Keep:

- all 12 primitive golden records;
- all 7 recipe golden records.

## 12. Acceptance batch

Rerun the exact or equivalent matrix:

- 7 recipes
- 4 difficulties
- 5 fixed seeds

= **140 candidates**

Required:

- target 140/140 accepted;
- minimum 120 accepted if bounded failures are honestly recorded;
- exact dimensions;
- exact width×height cells;
- C01..C16 only;
- no BG01;
- exact selected palette used;
- geometry/color fidelity exact;
- zero singleton same-color components;
- effective max dominance satisfied;
- deliberate accent contract where palette cardinality >=4;
- root RNG/provenance coherence;
- deterministic rerun equality;
- each recipe has >=2 geometry digests across the fixed seed set.

Do not count a failed candidate as accepted.

## 13. PAG-0442 structure acceptance

After fidelity remediation, prove final logical outputs carry recipe structure.

Add deterministic diagnostics comparing:

- RuleCanvas occupied mask;
- reconstructed logical foreground mask from base-vs-non-base colors.

They must be byte/tuple identical.

Manual review contact sheet must show:

1. geometry mask;
2. final logical colored grid.

The colored grid should visibly preserve the recipe silhouette/region structure.

Do not use uniform/random baselines as a universal quality metric; keep this bounded to M04 structure evidence.

## 14. 59×59 benchmark and PAG-0441

Re-benchmark representative 59×59 RULES generation after C002.

Record:

- machine;
- Python;
- sample count;
- median;
- p95;
- worst;
- success/failure count.

Do not invent a pass/fail budget.

Do not mark `PAG-0441` complete.

The task remains blocked until M10 establishes the V1 performance budget.

## 15. Full regression

Run and log:

- POCKET focused tests;
- local rewrite behavior tests;
- protected semantic identity tests;
- all primitive tests;
- all operation tests;
- all recipe tests;
- geometry-bound colorization tests;
- accent tests;
- 10/12-color tests;
- primitive goldens;
- recipe goldens;
- 140-candidate acceptance batch;
- review-evidence tests;
- M00-M03 tests;
- full repository pytest;
- standalone import;
- `pip check`;
- offline/source-policy scan;
- no-global-random/no-hash/no-subprocess/no-eval scan;
- `git diff --check`;
- source scan proving no M05+ implementation.

C001 builder baseline:

- focused M04: 28 PASS
- full repository: 201 PASS

The new suite should grow materially.

## 16. Preserve validated M04 work

Do not rewrite without necessity:

- BLOB
- ISLAND
- RING
- CORRIDOR
- SNAKE
- BRANCH
- CHAMBER
- SPIRAL
- WAVE
- RADIAL
- VORONOI
- seeded/constrained growth
- erosion/dilation bounds
- hole carving helper
- contour
- nested region
- bounded repeat
- ORGANIC/MULTI_ISLAND/SPARSE recipe architecture
- root RNG integration
- M02 GenerationResult integration

Changes may touch shared helpers only when required by the findings.

## 17. Offline/security/provenance

Preserve:

- offline-only runtime;
- no network imports;
- no global random;
- no Python hash determinism;
- no subprocess;
- no eval/exec;
- no executable deserialization;
- no third-party artwork;
- no MarkovJunior source/model/runtime.

No new dependency is expected.

## 18. Prohibited shortcuts

Do not:

- color negative-space cells with foreground colors to satisfy dominance;
- allow base color inside occupied geometry;
- drop palette IDs;
- use singleton dots for palette completion;
- simply rename POCKET without making it carve;
- keep BRIDGE_GAP as the notch predicate;
- protect occupancy while still silently destroying protected semantic labels;
- claim recipe diversity from palette changes only;
- compare full result hashes when the geometry mask itself stays unchanged and call that geometry diversity;
- hardcode review diagnostics;
- regenerate goldens merely to hide a defect;
- start M05+;
- edit ChatGPT-owned tracker/audit state;
- self-audit.

## 19. Builder exit criteria

Builder may stop as implementation complete / pending independent audit only when:

- POCKET genuinely carves;
- BRIDGE_GAP is behaviorally distinct;
- protected semantic labels survive later operations;
- final logical grid exactly preserves occupied-vs-negative RuleCanvas geometry;
- base/non-base fidelity is exact;
- explicit coherent accent semantics exist;
- every selected C-ID remains fully used;
- singleton count remains zero;
- effective dominance policy passes;
- all seven recipes vary across fixed seeds;
- primitive/recipe goldens are regenerated transparently;
- review diagnostics are computed;
- 140-candidate batch is rerun;
- 59×59 benchmark is refreshed without inventing a budget;
- M00-M04 regression passes;
- no M05+ code exists;
- matching C002 builder log is published;
- implementation commit(s), push result, and equality checkpoint are recorded.

Do not close M04. ChatGPT will independently re-audit.

Do not mark PAG-0441 complete; it remains blocked on M10.
