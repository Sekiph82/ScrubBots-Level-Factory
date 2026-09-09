# PAG-M03-C002 — Reproducibility, Region Quality & Recognizability Remediation

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M03-C001_MASK_SPRITE_GENERATOR_STRICT_AUDIT.md`

Previous implementation prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M03-C001_MASK_SPRITE_GENERATOR_PROMPT.md`

## 1. Scope

This is a bounded M03 remediation for exactly four findings:

- `F-PAG-M03-C001-001` — BLOCKER — non-root supplied RNG can pass coherence while driving different executable streams than recorded provenance.
- `F-PAG-M03-C001-002` — MAJOR — default colorization creates single-pixel salt / fragmented same-color regions.
- `F-PAG-M03-C001-003` — MAJOR — semantic outline/body/detail color roles are absent.
- `F-PAG-M03-C001-004` — MAJOR — manual review evidence does not yet demonstrate sufficiently recognizable/distinct families.

Do not reimplement already-validated generic mask-engine work.

Do not begin PAG-M04.

Open/revalidation task IDs:

- `PAG-0328`
- `PAG-0329`
- `PAG-0330`
- `PAG-0334`
- `PAG-0335`
- `PAG-0336`

The RNG coherence finding is a cross-cutting M03 integration finding and must close even though it is not a standalone task ID.

## 2. GitHub authority

GitHub is the sole task/prompt/audit authority.

Repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Do not modify the main `Sekiph82/Scrubbots` repository.

Do not discover work from sibling local folders.

If working from the owner's Windows mirror, synchronize only the authorized Level Factory checkout with safe fetch + fast-forward while preserving unrelated local control-plane changes.

## 3. Mandatory reads

Before the first product/review edit, read completely:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. C001 builder log
9. C001 strict audit
10. current M03 mask model/engine/templates/colorizer/generator
11. current M03 tests/goldens/review builder
12. current M02 RNG/result contracts
13. this prompt

## 4. Matching builder log: hard ordering gate

Create **before the first source, test, golden, manifest, contact-sheet, or review-builder edit**:

`.hiveai/codex-logs/PAG-M03-C002_REPRODUCIBILITY_REGION_QUALITY_AND_RECOGNIZABILITY_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M03-C002 — Reproducibility, Region Quality & Recognizability Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- authority/prompt/audit URLs;
- starting branch/HEAD/origin/status;
- synchronization;
- mandatory reads;
- exact remediation design per finding;
- files changed;
- material commands;
- failed tests/attempts and corrections;
- adversarial RNG-domain evidence;
- color-component quality evidence;
- semantic-role evidence;
- family recognizability/review evidence;
- regenerated golden evidence;
- >=120 acceptance batch;
- full regression;
- implementation commit SHA(s);
- push/equality checkpoint;
- final changed-file summary.

Do not self-audit or declare M03 PASS.

## 5. Finding F-PAG-M03-C001-001 — BLOCKER

### Problem

Current M03 verifies supplied RNG coherence with:

`stream.stage_seeds() == DeterministicRNG(request.seed).stage_seeds()`

But current M02 RNG semantics allow:

`DeterministicRNG(seed, "non-root").stage_seeds()`

to equal the canonical root stage seeds, while executable child/retry streams differ because their keys include `self.domain`.

This can produce art that is not reproducible from recorded root provenance.

### Required target behavior

For M03, a supplied external RNG must be the canonical request-root stream.

At minimum require:

- exact `DeterministicRNG` instance;
- `rng.domain == "root"`;
- `rng.stage_seeds() == DeterministicRNG(request.seed).stage_seeds()`.

If no RNG is supplied, construct exactly:

`DeterministicRNG(request.seed)`.

Do not change the M02 RNG algorithm/version in this remediation.

### Required adversarial tests

Prove:

1. canonical root RNG for request seed succeeds;
2. wrong seed root RNG fails;
3. same seed with domain `"evil"` fails;
4. same seed with domain `"geometry"` fails;
5. a child/retry RNG passed as top-level generator RNG fails;
6. failure is stable `INVALID_REQUEST`;
7. valid root RNG output remains byte-identical to no-RNG/default generation;
8. recorded provenance reproduces the actual accepted root-stream generation.

## 6. Finding F-PAG-M03-C001-002 — MAJOR

### Problem

The current random-anchor nearest-region colorizer produces widespread salt/fragmentation.

Independent audit of the 40 committed review candidates found singleton same-color connected components in **39/40** candidates, including examples with 20+ singleton components.

### Required target behavior

Default M03 coloring must produce coherent color regions.

For accepted default M03 candidates:

- **zero single-cell same-color connected components** in the final logical grid;
- no checkerboard/salt behavior;
- each non-base semantic color region must have a deterministic minimum connected size;
- selected palette must still be fully used;
- negative-space/base may be a large connected or multi-component background-classification color;
- no off-palette repair/mutation after result validation.

Use deterministic 4-neighbor connectivity unless a clearly documented alternative is justified.

### Minimum region-size policy

Implement a project-owned deterministic minimum.

Recommended default:

- minimum connected component size >= 2 for every final color component;
- stronger minimum 3+ may be used where board/palette cardinality allows.

If the selected palette has many colors, allocate/partition regions deliberately so each color receives a coherent region rather than a single anchor cell.

If geometry cannot support all selected colors at the minimum size, retry deterministically or fail. Do not emit salt merely to satisfy color count.

### Required tests

Add:

- connected-component utility/test helper for M03 quality;
- zero singleton components across fixed default candidates;
- exact palette still fully used;
- fixed EASY/MEDIUM/HARD/VERY_HARD cases;
- all ten families;
- deterministic rerun equality;
- deliberately constructed tiny-region candidate rejected/recolored by the M03 coloring layer as designed.

Do not defer obvious default salt to M07. M07 may score quality later, but M03 must satisfy its own PAG-0328/PAG-0329 contract.

## 7. Finding F-PAG-M03-C001-003 — MAJOR

### Problem

Current `colorize_mask()` has one base color and random foreground anchors.

There is no explicit semantic role system.

### Required target behavior

Implement deterministic semantic color roles.

Required conceptual roles:

- `NEGATIVE_SPACE` / `BASE`;
- `OUTLINE`;
- `BODY_PRIMARY`;
- `SECONDARY`;
- `DETAIL_ACCENT`.

The exact enum/class names may differ.

### Palette-cardinality behavior

Map roles deterministically to the selected canonical palette.

Examples:

- 3 colors: base + outline + body;
- 4 colors: base + outline + body + secondary/detail;
- 5+ colors: add secondary/detail/accent regions;
- 10–12 colors: use additional coherent secondary/detail regions, not singleton dots.

Every selected palette ID must still appear in the final logical grid.

### Role geometry

Roles must be derived from geometry, not arbitrary metadata labels.

At minimum:

- derive foreground boundary/outline from the resolved mask;
- derive body/interior from non-boundary foreground;
- derive secondary/detail regions deterministically from family geometry / mask coordinates / connected regions;
- preserve the internal negative-space class separately.

Do not encode role names into logical cells. Final cells remain C01..C16.

### Tests

Prove:

- outline cells are foreground boundary cells;
- body cells are foreground;
- base cells are negative-space classification;
- role assignment is deterministic;
- roles use no off-palette IDs;
- every selected palette color maps to at least one coherent role region;
- no role mapping creates singleton salt by default;
- recoloring changes colors/roles deterministically without changing the foreground mask.

## 8. Finding F-PAG-M03-C001-004 — MAJOR

### Problem

The current template finalizer mirrors every REQUIRED cell across **both axes** for every family:

`templates.py::_finish`

This forces four-way hard symmetry before the configured mask symmetry mode is applied.

The review evidence consequently makes several families look like dense centered emblems instead of recognizable directional/organic subjects.

Independent review examples:

- FISH lacks a clear directional fish body/tail read;
- FACE_EMBLEM loses obvious face-feature separation;
- TREE_PLANT becomes a top/bottom-symmetric dense slab;
- CORAL becomes strongly emblem-like;
- INSECT vs TREE_PLANT EASY mask Jaccard similarity = 0.843.

### Required target behavior

Redesign template finishing so family geometry is not universally forced through four-way mirroring.

Required:

1. hard template geometry remains family-authored;
2. configured symmetry is applied deliberately rather than hidden inside `_finish`;
3. per-family directional cues survive;
4. placement offsets shift intended geometry instead of creating a mirrored union;
5. organic/directional families may use appropriate preferred symmetry.

### Preferred family structural cues

Preserve/improve:

- ROBOT: head/body/limbs;
- CREATURE: body/head/appendages;
- FISH: clear head/body/tail + fin silhouette;
- SEA_CREATURE: central body + distinct tentacle/appendage structure;
- SPACE_SHIP: clear hull + wing/thruster/nose structure;
- INSECT: body axis + paired wings/legs;
- FACE_EMBLEM: outline + visible eye/mouth/emblem feature zones;
- TREE_PLANT: trunk/stem + crown/branches, not vertically mirrored tree;
- CORAL: rooted branching structure;
- ABSTRACT_SYMBOL: deliberate emblem geometry.

### Family-specific symmetry

It is acceptable and encouraged to define a preferred default symmetry per family when the request does not explicitly supply a symmetry option.

Examples:

- FISH may prefer top/bottom mirror symmetry across its horizontal body axis;
- ROBOT/FACE/TREE/INSECT may prefer left/right symmetry;
- CORAL/CREATURE may use asymmetry or lighter symmetry;
- ABSTRACT_SYMBOL may use combined symmetry.

Explicit user-supplied M03 symmetry option must remain authoritative.

Do not alter generic `SymmetryMode` meanings.

### Variation

Preserve deterministic multi-seed variation without randomizing the family into unrecognizable noise.

## 9. Review evidence remediation

Regenerate:

- `review/m03/m03_review_manifest.json`
- `review/m03/M03_MASK_CONTACT_SHEET.html`

Keep them review-only/non-production.

### Contact sheet upgrade

For each representative candidate, render **both**:

1. foreground silhouette mask;
2. final colored logical grid.

This lets the independent auditor distinguish geometry quality from coloring quality.

Still:

- self-contained;
- no CDN/network;
- integer nearest-block rendering;
- exact canonical palette;
- presentation only.

### Review matrix

Keep at least 40 candidates:

- all 10 families;
- all 4 difficulties;
- multiple seeds;
- rectangles represented.

### Review diagnostics

Add deterministic review-only summary metadata or a companion file containing:

- occupancy;
- singleton color-component count;
- total same-color component count;
- top pairwise same-dimension foreground-mask Jaccard similarities.

This diagnostic is review-only, not M07 production quality scoring.

Acceptance target for default review candidates:

- singleton component count = 0;
- no exact duplicate masks;
- family silhouettes visibly distinct;
- no obvious family pair collapsed into near-identical slabs.

Do not use a metric alone to self-certify recognizability. ChatGPT still performs manual acceptance.

## 10. Acceptance batch revalidation

Rerun at least **120 deterministic default candidates**.

Required:

- >=100 accepted;
- target 120/120 if feasible;
- zero accepted dimension violations;
- zero accepted palette violations;
- zero BG01/None/off-palette cells;
- zero singleton same-color components in accepted default candidates;
- exact selected palette fully used;
- deterministic rerun equality;
- root-RNG provenance coherence.

If deterministic failures occur, log them honestly and add fixed candidates to maintain >=100 accepted.

## 11. Golden remediation

Template/colorization changes are expected to change M03 golden hashes.

Regenerate M03 golden fixtures only after the new behavior is correct.

For every changed golden record:

- preserve same fixed request where practical;
- record old vs new hash in builder log;
- explain that the change is caused by C002 recognizability/region-quality remediation;
- do not modify M00-M02 golden vectors.

Keep at least one golden per family.

## 12. Provenance and third-party boundary

The conceptual zfedoran reference remains reference-only.

Do not copy source sprites/templates/assets while improving recognizability.

Do not add third-party artwork.

If implementation remains original, `THIRD_PARTY_NOTICES.md` does not need an adaptation notice.

## 13. Required focused tests

At minimum:

### RNG coherence
- canonical root pass;
- wrong root seed fail;
- non-root same-seed fail;
- child/retry top-level fail.

### Color quality
- zero singleton components;
- minimum region-size behavior;
- coherent deterministic regions;
- all selected colors used.

### Semantic roles
- base/outline/body/detail structure;
- boundary correctness;
- deterministic role-to-palette mapping;
- geometry preservation.

### Templates
- clear family-specific fixed silhouettes;
- no universal four-way hard symmetry;
- per-family preferred default symmetry;
- explicit symmetry override still works;
- offsets act as intended placement;
- multi-seed variation.

### Review
- 40-candidate review manifest;
- silhouette + colored contact sheet;
- review diagnostics.

## 14. Full regression

Run:

- all M03 focused tests;
- regenerated M03 golden tests;
- >=120 acceptance batch;
- review evidence tests;
- all M00-M02 tests;
- full repository pytest;
- standalone import;
- `pip check`;
- offline/source-policy scan;
- no-global-random/no-hash/no-subprocess scan;
- `git diff --check`;
- source scan proving no M04+ implementation.

Builder C001 baseline:

- focused M03: 40 PASS;
- full repository: 164 PASS.

New suite should grow.

## 15. Safety / prohibited shortcuts

Do not:

- add an `allow_bad_quality` or `skip_quality` production bypass;
- simply delete difficult colors from the requested palette;
- use single pixels merely to force palette completeness;
- treat review diagnostics as M07 production scoring;
- blur/resize/interpolate geometry;
- copy third-party sprite templates;
- begin M04;
- change M02 RNG algorithm/version;
- modify ChatGPT-owned tracker/audit state;
- self-certify manual recognizability.

## 16. Builder exit criteria

Builder may stop as implementation complete / pending independent audit only when:

- non-root supplied RNGs fail closed;
- accepted output provenance corresponds to actual executable root stream;
- default accepted candidates contain zero singleton color components;
- coherent semantic region coloring is implemented;
- PAG-0330 semantic roles are demonstrable;
- family templates/contact sheet are materially more recognizable/distinct;
- regenerated 40-candidate review evidence is committed;
- >=120 acceptance batch is rerun with >=100 accepted and zero contract violations;
- M03 goldens are regenerated transparently where behavior changed;
- M00-M02 regression remains green;
- no M04+ code exists;
- matching C002 builder log is published;
- implementation commit(s), push result, and equality checkpoint are recorded.

Do not close M03. ChatGPT will independently repeat source/manifest/visual analysis and decide PASS/FAIL.
