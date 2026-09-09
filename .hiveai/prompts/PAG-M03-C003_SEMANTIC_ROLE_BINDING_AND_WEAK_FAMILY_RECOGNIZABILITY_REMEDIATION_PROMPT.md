# PAG-M03-C003 — Semantic Role Binding & Weak-Family Recognizability Remediation

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M03-C002_REPRODUCIBILITY_REGION_QUALITY_AND_RECOGNIZABILITY_REMEDIATION_STRICT_AUDIT.md`

Previous remediation prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M03-C002_REPRODUCIBILITY_REGION_QUALITY_AND_RECOGNIZABILITY_REMEDIATION_PROMPT.md`

## 1. Scope

This is a final bounded M03 remediation for exactly two remaining MAJOR findings:

- `F-PAG-M03-C002-001` — semantic color roles are labels, not actual role-to-color bindings.
- `F-PAG-M03-C002-002` — weak-family manual recognizability remains insufficient for INSECT, TREE_PLANT, and FACE_EMBLEM.

Already closed and must remain closed:

- canonical root-RNG coherence;
- zero-singleton connected-region behavior.

Do not begin PAG-M04.

Open/revalidation task IDs:

- `PAG-0330`
- `PAG-0334`
- `PAG-0335`
- `PAG-0336`

PAG-0328 and PAG-0329 are independently accepted by C002 and must not be regressed.

## 2. GitHub authority

GitHub is the sole task/prompt/audit authority.

Repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Do not modify the main ScrubBots repository.

Do not discover work from sibling local folders.

If working from the owner's Windows checkout, synchronize only the authorized Level Factory checkout using safe fetch + fast-forward and preserve unrelated local control-plane edits.

## 3. Mandatory reads

Before the first source/test/golden/review edit, read completely:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. C002 builder log
9. C002 strict audit
10. current M03 colorizer/templates/generator
11. current M03 focused/review/golden tests
12. current review manifest/contact sheet builder
13. this prompt

## 4. Matching builder log

Create **before the first source, test, golden, manifest, contact-sheet, or review-builder edit**:

`.hiveai/codex-logs/PAG-M03-C003_SEMANTIC_ROLE_BINDING_AND_WEAK_FAMILY_RECOGNIZABILITY_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M03-C003 — Semantic Role Binding & Weak-Family Recognizability Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- authority/prompt/audit URLs;
- starting branch/HEAD/origin/status;
- synchronization;
- mandatory reads;
- exact role-binding design;
- exact weak-family geometry changes;
- material commands;
- failed tests/attempts and corrections;
- role/color purity evidence;
- 10..12-color palette evidence;
- zero-singleton regression;
- regenerated golden evidence;
- regenerated review evidence;
- >=120 acceptance batch;
- full regression;
- implementation commit SHA(s);
- push/equality checkpoint;
- final changed-file summary.

Do not self-audit or declare M03 PASS.

## 5. Finding F-PAG-M03-C002-001 — true semantic role binding

### Current problem

The C002 colorizer introduced:

- NEGATIVE_SPACE
- OUTLINE
- BODY_PRIMARY
- SECONDARY
- DETAIL_ACCENT

but color propagation still ignores role boundaries.

The same selected C-ID can spread through several role classes.

Independent C002 audit found **40/40** committed review candidates contain foreground colors spanning multiple semantic roles.

Also, `ColorizedMask.role_colors` records only a five-entry zip and cannot represent all selected colors in 6..12-color palettes.

### Required target behavior

Roles must drive color allocation.

A selected color must have an explicit semantic assignment before cells are painted.

At minimum:

- negative-space/base color -> negative-space cells only;
- outline color(s) -> outline cells only;
- body-primary color(s) -> body/interior cells only;
- secondary color(s) -> secondary subregions;
- detail/accent color(s) -> detail/accent subregions.

A color may share a **broad role family** with another color, especially for 6..12-color palettes, but it must not arbitrarily cross unrelated role families.

### Required model

Introduce an explicit immutable semantic mapping structure.

Examples:

```text
ColorRoleAssignment
  C04 -> NEGATIVE_SPACE
  C10 -> OUTLINE
  C12 -> BODY_PRIMARY
  C16 -> DETAIL_ACCENT
```

or equivalent.

For 10..12 colors, support deterministic sub-role slots such as:

- BODY_PRIMARY_1 / BODY_PRIMARY_2
- SECONDARY_1 / SECONDARY_2 / ...
- DETAIL_ACCENT_1 / ...

The broad semantic parent remains one of:

- NEGATIVE_SPACE
- OUTLINE
- BODY_PRIMARY
- SECONDARY
- DETAIL_ACCENT

Do not invent new logical C-IDs.

### Palette cardinality contract

Required behavior by selected palette size:

- 3 colors: base + outline + body
- 4 colors: base + outline + body + one secondary/detail
- 5 colors: all five broad roles may be represented where geometry supports them
- 6..12 colors: additional colors must be assigned as coherent subregions of BODY_PRIMARY, SECONDARY, or DETAIL_ACCENT

Every selected C-ID must:

- have an explicit role assignment;
- appear in the final grid;
- occupy at least one connected component of size >=2;
- never be used outside its assigned broad role family, except where a documented broad-role subdivision intentionally allows it.

### Geometry-derived role regions

Build role regions **before** final color propagation.

Required broad geometry:

- NEGATIVE_SPACE = non-foreground mask cells
- OUTLINE = foreground boundary cells
- BODY_PRIMARY = interior foreground cells not assigned to more specific structural subregions
- SECONDARY / DETAIL_ACCENT = deterministic coherent subsets of foreground geometry

Do not derive detail roles from pure coordinate hash modulo alone if that produces scattered speckle-like role cells.

Secondary/detail role regions should themselves be coherent connected regions.

### Role/color purity acceptance

Add automated diagnostics that compute, for each final selected C-ID:

- assigned semantic role;
- observed semantic roles across all cells with that C-ID.

Acceptance:

- observed broad-role set for each color must equal its assigned broad role;
- base color must occur only in NEGATIVE_SPACE;
- outline color(s) only in OUTLINE;
- no selected color lacks a role assignment;
- 10..12-color VERY_HARD fixtures satisfy the same rule.

### Required tests

At minimum add:

1. 3-color semantic mapping test;
2. 4-color mapping;
3. 5-color mapping;
4. 10-color mapping;
5. 12-color mapping;
6. all selected colors explicitly represented in role map;
7. role/color purity across final cells;
8. no singleton connected color components;
9. deterministic role assignment;
10. recoloring preserves foreground geometry;
11. role assignment changes deterministically with palette/seed but not via unordered iteration;
12. invalid/impossible role allocation fails boundedly.

## 6. Preserve zero-singleton guarantee

C002 independently closed PAG-0328/PAG-0329.

Do not regress it.

For all accepted default candidates:

- singleton same-color components = 0;
- connected components remain deterministic;
- every selected palette color still appears;
- no fallback to one-cell accent dots.

If semantic role partitioning cannot support the selected palette cardinality, deterministically retry/fail. Do not violate region-size contract.

## 7. Finding F-PAG-M03-C002-002 — weak-family recognizability

Only the weak families below require redesign unless a shared helper must change:

- INSECT
- TREE_PLANT
- FACE_EMBLEM

Preserve the improvements already achieved for:

- FISH
- CORAL
- ROBOT
- CREATURE
- SEA_CREATURE
- SPACE_SHIP
- ABSTRACT_SYMBOL

### INSECT target

Current issue:

The silhouette is a dense tapering slab and remains too similar to TREE_PLANT.

Required cues:

- narrow central segmented body axis;
- clearly separated paired wing lobes;
- visible negative-space gaps between body and wing masses where possible;
- optional leg/antenna cues that do not fill the entire board;
- left/right symmetry is acceptable;
- avoid large solid triangular/tapered fill.

### TREE_PLANT target

Current issue:

The silhouette remains a dense tapering mass similar to INSECT.

Required cues:

- narrow visible trunk/stem;
- clearly wider crown/canopy in upper region;
- branch/crown lobes separated by some negative-space gaps;
- lower trunk should remain visually distinct from crown;
- no insect-like paired continuous wings;
- prefer asymmetry or light branch variation while retaining tree readability.

### FACE_EMBLEM target

Current issue:

The silhouette is primarily a filled face-shaped mass; eye/mouth rectangles were foreground, so structural facial features do not read clearly.

Required cues:

- explicit face/emblem outer shape;
- eye feature zones visible as negative-space holes or deliberate detail geometry;
- mouth/emblem feature visible structurally;
- maintain enough foreground connectivity for color region contract;
- left/right symmetry acceptable;
- do not rely only on final arbitrary color paint to suggest a face.

### Distinctness target

For the fixed EASY review representatives:

- INSECT vs TREE_PLANT foreground-mask Jaccard must be materially below the current 0.844937.
- Hard acceptance target: **< 0.70** for that pair.
- No other same-dimension different-family pair should be >= 0.80 in the committed review pack.

This metric supports review but does not replace manual recognizability.

## 8. Contact-sheet and review evidence

Regenerate:

- `review/m03/m03_review_manifest.json`
- `review/m03/M03_MASK_CONTACT_SHEET.html`

Continue rendering both:

1. silhouette
2. colored logical grid

Add or preserve diagnostics:

- occupancy;
- singleton components;
- total color components;
- role counts;
- pairwise Jaccard;
- **role-to-color assignment map**;
- **observed role set per color**.

For every review candidate:

- assigned role per color must be visible in manifest diagnostics;
- observed broad-role set must match assigned role;
- singleton count = 0.

Keep review evidence review-only/non-production.

## 9. M03 golden regeneration

Semantic coloring and weak-family geometry changes will legitimately alter M03 goldens.

Regenerate M03 goldens after behavior is final.

Builder log must record:

- which family fixtures changed;
- old vs new result/grid/mask hashes;
- whether change came from semantic coloring, weak-family geometry, or both.

Do not modify M00-M02 golden fixtures.

Keep >=1 M03 golden per family.

## 10. Acceptance batch revalidation

Rerun at least:

- 10 families
- 4 difficulties
- 3 seeds

= 120 candidates.

Required:

- >=100 accepted;
- target 120/120;
- zero dimension violations;
- zero palette violations;
- zero BG01/off-palette/sentinel cells;
- zero singleton color components;
- every selected palette ID used;
- every selected color has semantic role assignment;
- role/color purity holds;
- deterministic rerun equality;
- root RNG coherence preserved.

PAG-0334 and PAG-0335 remain open until this final batch passes after C003 behavior.

## 11. Manual recognizability evidence

Builder must not self-declare PAG-0336 PASS.

However, prepare evidence so ChatGPT can review:

- all 10 families;
- all 4 difficulties;
- multiple seeds;
- both silhouette and colored grid;
- improved INSECT / TREE_PLANT / FACE_EMBLEM examples;
- pairwise similarity diagnostics.

The contact sheet should make these three families obviously structurally different without relying on labels.

## 12. Regression requirements

Run and log:

- semantic-role focused tests;
- 10/12-color VERY_HARD role-purity tests;
- weak-family geometry tests;
- Jaccard threshold tests for review fixtures;
- zero-singleton regression;
- M03 golden tests;
- 120-candidate batch;
- review-evidence tests;
- full repository pytest;
- standalone import;
- `pip check`;
- offline/source-policy scans;
- no-global-random/no-hash/no-subprocess scan;
- `git diff --check`;
- no M04+ production source scan.

C002 baseline:

- focused M03: 42 PASS
- full repository: 166 PASS

The new suite should grow.

## 13. Safety / prohibited shortcuts

Do not:

- assign semantic role labels after coloring and call that role binding;
- let a color roam across unrelated role families;
- omit role mappings for 6..12-color palettes;
- create singleton accent pixels;
- simply rename existing coordinate-hash labels;
- blur/resize/interpolate;
- copy third-party sprite art/templates;
- make every family artificially sparse just to reduce Jaccard;
- begin M04;
- change M02 RNG algorithm/version;
- edit ChatGPT-owned task/tracker/audit state;
- self-certify manual recognizability.

## 14. Builder exit criteria

Builder may stop as implementation complete / pending independent audit only when:

- each selected C-ID has explicit semantic role/sub-role assignment;
- observed cells of each color respect that broad semantic role;
- 10..12-color palettes are fully mapped;
- singleton count remains zero;
- INSECT/TREE_PLANT EASY Jaccard < 0.70;
- no review different-family pair >= 0.80;
- INSECT, TREE_PLANT, FACE_EMBLEM are structurally redesigned and review evidence regenerated;
- >=120 acceptance batch rerun with >=100 accepted and zero contract violations;
- M03 goldens regenerated transparently;
- full regression passes;
- no M04+ implementation exists;
- matching C003 builder log is published;
- implementation commit(s), push result, and equality checkpoint are recorded.

Do not close M03. ChatGPT performs the final M03 strict audit and manual contact-sheet acceptance.
