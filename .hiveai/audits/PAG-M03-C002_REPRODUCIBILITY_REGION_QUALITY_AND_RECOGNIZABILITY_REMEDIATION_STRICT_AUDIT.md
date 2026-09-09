# PAG-M03-C002 — Reproducibility, Region Quality & Recognizability Remediation

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-09-09  
Auditor: ChatGPT  
Cycle: `PAG-M03-C002`  
Repository: `Sekiph82/ScrubBots-Level-Factory`

Audited builder implementation commit:
`dcb5a7e — Remediate M03 reproducibility and sprite quality`

## 1. VERDICT

**FAIL**

C002 closes two of the four C001 findings:

- `F-PAG-M03-C001-001` — root RNG coherence: **CLOSED**
- `F-PAG-M03-C001-002` — singleton/fragmented default coloring: **CLOSED**

Two MAJOR findings remain:

- **F-PAG-M03-C002-001 — MAJOR — semantic color roles exist as labels, but selected colors are not actually bound to semantic roles.**
- **F-PAG-M03-C002-002 — MAJOR — manual family recognizability/distinctness still fails for several families.**

PAG-M04 remains blocked.

A final bounded `PAG-M03-C003` remediation is required.

## 2. CONTRACT RECOVERY

C002 was required to fix:

1. canonical request-root RNG coherence;
2. zero default single-pixel color salt and coherent regions;
3. real semantic color roles;
4. recognizable/distinct family silhouettes and colored review output.

The semantic-role requirement was not merely to attach role labels to cells. It explicitly required:

- deterministic role-to-palette mapping;
- outline/body/detail roles derived from geometry;
- each selected palette color to map to a coherent semantic role region;
- final colored output to communicate structure rather than arbitrary partitions.

PAG-0336 remained a human/manual visual-review gate owned by ChatGPT.

## 3. BRANCH / HEAD / DIFF SCOPE

The remediation remains bounded to M03:

- mask templates;
- mask colorizer;
- mask generator;
- M03 tests;
- regenerated M03 golden fixtures;
- review-only manifest/contact sheet;
- matching C002 builder log.

No M04+ implementation was introduced.

No M00-M02 product contract was rewritten.

Scope result: **PASS**

## 4. ACCEPTANCE CRITERIA MATRIX

| Criterion | Result | Independent conclusion |
| --- | --- | --- |
| Non-root same-seed RNG rejected | PASS | Generator now requires `stream.domain == "root"`. |
| Wrong seed root RNG rejected | PASS | Existing stage-seed coherence remains. |
| Default/no-RNG equals canonical root RNG | PASS | Source/tests implement this equality. |
| Review singleton count = 0 | PASS | Independently recomputed from committed manifest: 40/40 candidates have zero single-cell same-color components. |
| Minimum connected region behavior | PASS | Colorizer seeds regions as pairs and rejects singleton final components. |
| Exact selected palette still used | PASS | Result/review evidence retains exact set equality. |
| Semantic role enum exists | PASS | NEGATIVE_SPACE, OUTLINE, BODY_PRIMARY, SECONDARY, DETAIL_ACCENT exist. |
| Base role corresponds to negative space | PASS | Non-foreground cells are NEGATIVE_SPACE. |
| Outline role derives from foreground boundary | PASS | `_role_for_index` identifies mask boundary cells. |
| Selected colors are semantically bound to roles | **FAIL** | Color propagation ignores role boundaries; every review candidate contains foreground colors spanning multiple semantic role classes. |
| Role-to-color mapping covers all selected colors | **FAIL** | `role_colors` records at most five mappings and does not represent palettes with 6..12 selected IDs. |
| Colored result communicates outline/body/detail structure | **FAIL** | Color regions are connected but remain spatial partitions rather than semantic structural coloring. |
| Universal hidden four-way mirror removed | PASS | `_finish` no longer mirrors every REQUIRED cell across both axes. |
| Family-specific preferred symmetry | PASS | Explicit preferred symmetry table exists. |
| FISH directional cue | PASS | Review silhouette now reads much more clearly as a directional fish. |
| CORAL directional/organic improvement | PASS | Review silhouette is materially improved. |
| All ten families sufficiently recognizable/distinct | **FAIL** | INSECT/TREE_PLANT remain highly similar dense silhouettes; FACE_EMBLEM still lacks convincing facial/emblem feature separation. |
| >=120 acceptance batch | PASS / REVALIDATE | Builder reports 120/120; rerun required after final visual/semantic remediation. |
| Zero dimension/palette violations | PASS / REVALIDATE | Current batch passes; final C003 must rerun. |
| PAG-0336 manual contact-sheet acceptance | **FAIL** | Human review gate not met. |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

### Claim: canonical supplied RNG root is enforced

Current `MaskSpriteGenerator.generate_candidate()` explicitly rejects:

`stream.domain != "root"`

and still verifies stage-seed equality to the request-derived root stream.

Tests include:

- wrong seed;
- `"evil"` domain;
- `"geometry"` domain;
- child stream;
- retry stream.

Disposition: **VERIFIED / CLOSED**

### Claim: singleton color salt is eliminated

Independent audit parsed the committed C002 review manifest and recomputed 4-neighbor same-color connected components.

Result:

- review candidates: **40**
- candidates with singleton color components: **0**
- background-classification color count per candidate: exactly one.

This materially corrects the C001 state of 39/40 candidates containing singleton components.

Disposition: **VERIFIED / CLOSED**

### Claim: semantic roles now map palette colors to base/outline/body/secondary/detail

This is not supported by repository behavior.

Current algorithm:

1. chooses connected two-cell seeds for each foreground color;
2. assigns each seed pair a color;
3. stores each seeded cell's role from `_role_for_index`;
4. propagates **color** through adjacent foreground cells;
5. for every propagated cell, recomputes its role independently from geometry.

Propagation does not constrain a color to its intended semantic role.

Independent audit reconstructed the same geometry-role function on the committed review manifest.

Result:

- candidates with at least one foreground color spanning multiple semantic roles: **40 / 40**
- ROBOT EASY: all four foreground colors span multiple role classes;
- CREATURE EASY: all three foreground colors span multiple role classes;
- FISH EASY: both foreground colors span multiple role classes;
- INSECT EASY: both foreground colors span multiple role classes.

Example ROBOT EASY:

- C14 → BODY_PRIMARY + OUTLINE + SECONDARY
- C11 → BODY_PRIMARY + DETAIL_ACCENT + OUTLINE + SECONDARY
- C03 → BODY_PRIMARY + OUTLINE + SECONDARY
- C04 → BODY_PRIMARY + OUTLINE

This is connected coloring plus geometry role annotation, not semantic role-bound coloring.

Additionally, `ColorizedMask.role_colors` is built with a zip over only five role slots:

- NEGATIVE_SPACE
- OUTLINE
- BODY_PRIMARY
- SECONDARY
- DETAIL_ACCENT

against:

- base color
- first four foreground colors.

For 6..12-color palettes, remaining selected colors have no entry in `role_colors`.

Disposition: **REJECTED**

### Claim: recognizability is sufficiently remediated

There is real improvement, especially FISH and CORAL.

However manual review still does not satisfy PAG-0336.

Independent silhouette review of EASY representatives found:

- ROBOT: reasonably readable;
- FISH: materially improved and directional;
- CORAL: materially improved;
- ABSTRACT_SYMBOL: acceptable as an abstract emblem;
- INSECT: large dense tapering mass;
- TREE_PLANT: large dense tapering mass, visually close to INSECT;
- FACE_EMBLEM: mostly a filled symmetric mass without clear eye/mouth feature separation.

Committed review diagnostics still report:

- maximum top pairwise Jaccard: **0.844937**
- INSECT vs TREE_PLANT remains the dominant near-overlap pair.

Colored-grid inspection does not cure this because semantic detail colors are not actually bound to facial/body/outline features.

Disposition: **PARTIAL / NOT ACCEPTED**

## 6. FILE / SYMBOL EVIDENCE

### `mask/generator.py`

Positive:

- root-domain check added;
- canonical root/no-RNG behavior preserved;
- preferred family symmetry applied when user did not explicitly specify symmetry;
- bounded retries preserved.

Result: **PASS**

### `mask/colorize.py`

Positive:

- deterministic 4-neighbor component logic;
- paired region seeds;
- zero-singleton final validation;
- role enum and geometry-role classification.

Remaining defect:

`labels[index]` stores a color and the local geometric role independently.

During propagation, color selection is based on neighboring **color counts**, not target semantic role.

Therefore color identity is not controlled by semantic role.

`role_colors` also cannot describe all colors in 6..12-color palettes.

Result: **FAIL for PAG-0330**

### `mask/templates.py`

Positive:

- hidden universal four-way mirror removed;
- preferred symmetry is now family-specific;
- FISH directional cue improved;
- organic/asymmetric families are no longer universally mirrored.

Remaining quality issue:

Several core family builders still create very large filled central masses. Random contour resolution then changes edges but not the family-level structural silhouette enough.

INSECT and TREE_PLANT remain particularly close.

FACE_EMBLEM still creates a filled face-shaped mass; its “eye” and “mouth” rectangles are REQUIRED foreground rather than actual structural feature zones/negative spaces, so silhouette review cannot read them as facial features.

Result: **PARTIAL**

## 7. FOCUSED TEST EVIDENCE

Builder reports:

- focused C002/M03 suite: `42 passed`;
- full repository: `166 passed`;
- acceptance batch: `120 accepted`;
- review manifest: 40 candidates;
- maximum singleton count: 0.

Independent audit additionally verified:

- 0 singleton components across all 40 committed review candidates;
- exact one negative-space/background color per candidate;
- semantic role/color crossover across all 40 candidates;
- representative silhouette rendering;
- current top Jaccard value 0.844937.

Passing tests currently do not assert role-color purity or complete role/color mapping for 6..12-color palettes.

## 8. REGRESSION EVIDENCE

No M00-M02 source regression was found in C002 scope.

No M04 production work exists.

Result: **PASS**

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Root RNG provenance hole is closed.

No new:

- network dependency;
- global random;
- shell execution;
- cloud/API;
- third-party artwork

was introduced.

Result: **PASS**

## 10. ARCHITECTURE CONSISTENCY

Architecture is now much closer to the intended M03 boundary:

- generic mask engine;
- family templates;
- deterministic coloring;
- M02 result/provenance integration;
- review-only evidence.

The remaining semantic-color problem is architectural rather than cosmetic: roles must drive color assignment, not merely be annotated after color regions grow.

Result: **FAIL at semantic coloring layer only**

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Positive:

- matching C002 log was created before edits;
- previous process-ordering defect did not repeat;
- no self-audit;
- no task/H!veAI acceptance mutation;
- failures/corrections recorded;
- implementation publication checkpoint recorded.

Result: **PASS**

## 12. FINAL REPOSITORY STATE

C002 remediation is published.

The repository contains improved M03 behavior but M03 is not accepted due two remaining MAJOR findings.

## 13. OPEN CROSS-MILESTONE FINDINGS

### F-PAG-M03-C002-001 — MAJOR

**Semantic color roles are annotations, not actual role-to-color bindings.**

Required target:

- semantic roles must drive color allocation;
- outline color(s) should remain on outline regions;
- body-primary color(s) should remain body/interior;
- detail/accent colors should occupy deterministic detail/accent regions;
- secondary colors should occupy coherent secondary regions;
- palettes with >5 colors must explicitly map every selected color into a semantic role family/sub-role;
- every selected palette color must appear in at least one coherent region belonging to its assigned semantic role.

### F-PAG-M03-C002-002 — MAJOR

**Family recognizability/distinctness still fails manual review.**

Required target:

Focus only weak families:

- INSECT
- TREE_PLANT
- FACE_EMBLEM

and any directly coupled template logic required to distinguish them.

Targets:

- INSECT: clear central segmented body with discrete paired wing lobes / leg cues, not a tapered solid blob;
- TREE_PLANT: narrow trunk/stem clearly separated from a crown/canopy/branch structure;
- FACE_EMBLEM: structural feature zones for eyes/mouth/emblem, preferably negative-space/detail geometry rather than just painting over one solid mass.

Maintain improvements already achieved for FISH/CORAL/other families.

## 14. DEFECTS BY SEVERITY

### BLOCKER

None.

### MAJOR

- F-PAG-M03-C002-001
- F-PAG-M03-C002-002

### MINOR

None.

### NOTE

Exact builder Windows test commands were not independently rerun. The remaining findings derive directly from committed source and review evidence.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Non-blocking after closure:

- formalize semantic roles as role regions before palette assignment;
- allow multiple deterministic sub-regions per broad role for 10..12-color palettes;
- M07 can later add general near-duplicate metrics, but M03 should leave recognizability in a healthy baseline state.

## 16. UNVERIFIED ITEMS

Exact owner-machine `166 passed` execution remains builder evidence.

No current review-manifest singleton metric is unverified.

## 17. REGRESSION RISK

**MEDIUM**

Final semantic/template changes will intentionally alter M03 golden hashes/review evidence again.

M00-M02 goldens must remain unchanged.

## 18. AUDIT CONFIDENCE

**HIGH**

Evidence includes:

- current GitHub source;
- current committed review manifest;
- independent connected-component recomputation;
- independent semantic color-role crossover analysis;
- manual silhouette and colored-grid review.

## 19. FINAL VERDICT

**FAIL**

`PAG-M03-C002` is not accepted.

Closed:

- C001 RNG coherence finding;
- C001 singleton/fragmentation finding.

Still open:

- true semantic role/color binding;
- manual family recognizability.

PAG-M04 remains blocked.

## 20. REQUIRED REMEDIATION

Create final bounded cycle:

`PAG-M03-C003 — Semantic Role Binding & Weak-Family Recognizability Remediation`

Required work only:

1. make semantic roles control color allocation;
2. support every selected palette color, including 10..12-color palettes, through explicit semantic role/sub-role mapping;
3. keep zero-singleton connected-region guarantee;
4. redesign only weak family silhouettes: INSECT, TREE_PLANT, FACE_EMBLEM;
5. preserve FISH/CORAL and other improved families unless a shared fix is required;
6. regenerate M03 goldens/review evidence;
7. rerun >=120 acceptance batch;
8. rerun manual-review diagnostics;
9. rerun full M00-M03 regression;
10. do not begin M04.
