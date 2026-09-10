# PAG-M07-C002 — Structural Metric Semantics & Acceptance Evidence Remediation

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-09-10  
Auditor: ChatGPT  
Cycle: `PAG-M07-C002`  
Repository: `Sekiph82/ScrubBots-Level-Factory`  
Branch: `main`

Audited builder boundary:
- cycle base / C002-ready state: `bd8384d851a9f70c299cfb728e90da5b1249cf63`
- implementation/evidence commit: `7c4ef89` as recorded by the builder log
- builder-log publication equality checkpoint: `5d3355c78f397b058d53fb03d1aa86f48d6d5c3a`
- equality-recording terminal builder-era HEAD independently observed: `4379400527bfd81061512840958f3e939b880e87`

Previous independent audit:
- `.hiveai/audits/PAG-M07-C001_ARTWORK_QUALITY_AND_DIVERSITY_FILTERS_STRICT_AUDIT.md`

Authoritative prompt:
- `.hiveai/prompts/PAG-M07-C002_STRUCTURAL_METRIC_SEMANTICS_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_PROMPT.md`

## 1. VERDICT

**FAIL**

C002 materially repairs the two C001 product-semantic defects and most of the missing acceptance/review evidence. The corrected occupied-fragmentation metrics now derive from occupied-mask connected components, total color dominance now sums all occupied cells per C-ID, explicit one-color dominance thresholds are enforceable, genuine structural fixtures were added, representative generator outputs are evaluated for acceptance, and the contact-sheet renderer now emits hash and diversity evidence.

Two residual acceptance defects remain:

- `F-PAG-M07-C002-001` - **MAJOR**: contact-sheet integration evidence still does not satisfy the C002 prompt's explicit card-local verification requirement. The test searches the whole HTML for generic `exact duplicate group:`, `near-duplicate partners:` and invalid-input tokens. A value rendered on an unrelated card can therefore satisfy the test. The prompt explicitly required representative rendered card content to be parsed/asserted rather than global-token searched.
- `F-PAG-M07-C002-002` - **MINOR**: the geometric meaning of `horizontal_symmetry_score` and `vertical_symmetry_score` remains undocumented in the quality contract/docs. The C002 prompt explicitly required the reflection represented by each field to be documented. Current implementation uses x-reflection for the `horizontal_symmetry_score` flag and y-reflection for `vertical_symmetry_score`, but that convention is not stated in `quality/README.md` or a public metric contract.

M07 is therefore not yet unconditionally accepted. M08+ remains blocked. C003 should be a bounded evidence/documentation closure, not a redesign of the corrected C002 metric mathematics.

## 2. CONTRACT RECOVERY

C002 was authorized to close exactly four C001 findings while preserving the accepted M07 architecture.

The relevant C002 requirements were:

1. occupied isolation/tiny metrics must use occupied-mask connected components;
2. color dominance must use total occupied usage per C-ID and explicit thresholds must remain real gates;
3. acceptance fixtures must be structurally genuine and mandatory metric/rejection edge cases must be directly tested;
4. representative M03-M06 outputs must prove conservative quality compatibility, not only analyzability;
5. every valid contact-sheet card must show exact hash and duplicate/near-duplicate evidence;
6. invalid-input cards must show an explicit unavailable hash state and stable failure evidence;
7. integration tests must parse/assert representative card content, not merely search the whole HTML for generic tokens;
8. horizontal/vertical symmetry fields must explicitly document which geometric reflection each represents;
9. no M08+ implementation or generator-output mutation is allowed.

## 3. BRANCH / HEAD / DIFF SCOPE

Independent GitHub comparison from `bd8384d851a9f70c299cfb728e90da5b1249cf63` to `4379400527bfd81061512840958f3e939b880e87` shows three commits limited to C002 M07 source, tests, review artifacts and the matching builder log.

No M03-M06 production generator implementation changed. No M08+ product implementation was introduced. ChatGPT-owned tracker/audit state was not modified by the builder.

Result: **PASS**

## 4. ACCEPTANCE CRITERIA MATRIX

| Criterion | Result | Independent conclusion |
| --- | --- | --- |
| Occupied isolation from occupied-mask components | PASS | `isolated_count` is derived from `occupied_components` of size 1. |
| Tiny occupied regions from occupied-mask components | PASS | tiny components and tiny cell totals use occupied-mask components. |
| Per-color components remain separate evidence | PASS | `color_components` remains separately calculated. |
| Total occupied color dominance | PASS | `occupied_color_counts` sums all occupied cells by C-ID and `largest_color` uses those totals. |
| One-color explicit dominance gate | PASS | hidden multi-color condition was removed and focused test proves strict one-color policy rejection. |
| Genuine structural good fixtures | PASS | sparse, multi-island, symmetric, asymmetric and rectangular cases are structurally distinct. |
| Mandatory known-answer metric tests | PASS | direct one-cell, full-interior, rectangular, directional symmetry, asymmetry and equal-component tests exist. |
| Required rejection codes | PASS | all required C001 rejection families are directly asserted. |
| Representative generator quality compatibility | PASS | MASK, RULES, HYBRID/AUTO and synthetic-test WFC paths are evaluated using explicit conservative quality policies. |
| Contact renderer includes exact grid hash | PASS | per-card renderer emits `grid SHA-256`. |
| Contact renderer includes exact duplicate evidence | PASS | per-card renderer emits exact duplicate group. |
| Contact renderer includes near-duplicate evidence | PASS | per-card renderer emits partner IDs and occupancy/color similarity. |
| Invalid-input contact evidence | PASS in renderer | invalid input emits `UNAVAILABLE: INVALID_INPUT` and rejection state. |
| Card-local acceptance test | **FAIL** | integration test uses whole-document generic token searches rather than representative card-local assertions. |
| Symmetry axis contract documentation | **FAIL** | directional tests exist, but public documentation does not state the exact geometric reflection represented by each field. |
| Review pack regenerated | PASS | committed manifest/contact sheet reflect C002 structures. |
| Offline/no-resize boundary | PASS by source/diff evidence | no relevant prohibited path was introduced. |
| M08+ scope discipline | PASS | no M08+ implementation in C002 diff. |
| Builder focused tests | BUILDER PASS | builder reports `20 passed, 1 warning`. |
| Builder full regression | BUILDER PASS | builder reports `270 passed, 1 warning`. |
| Independent CI/runtime | UNVERIFIED | no GitHub Actions workflow run is attached to terminal builder-era HEAD. |

## 5. C001 FINDING DISPOSITION

### F-PAG-M07-C001-001

**CLOSED FUNCTIONALLY.**

The old false-fragmentation behavior was removed. Occupied isolation and tiny occupied regions now come from occupied-mask connectivity, while per-color component statistics remain separate.

### F-PAG-M07-C001-002

**CLOSED FUNCTIONALLY.**

Color dominance now represents total occupied usage by C-ID, including split same-color components, and strict one-color policy thresholds are honored.

### F-PAG-M07-C001-003

**MOSTLY CLOSED, residual documentation gap remains.**

The structural fixtures and edge-case tests are substantially corrected. Representative generator compatibility now tests acceptance. However, the required public definition of the two directional symmetry field conventions is still missing.

### F-PAG-M07-C001-004

**IMPLEMENTATION CLOSED, acceptance-test closure incomplete.**

The renderer itself now displays hash, duplicate and near-duplicate evidence. The remaining defect is the explicit C002 verification requirement: the integration test must prove those values belong to the intended card rather than merely appearing somewhere in the HTML.

## 6. OCCUPIED FRAGMENTATION REVIEW

`analyze_grid()` now computes:

- `occupied_components` from the boolean occupied mask;
- `isolated_occupied_count` from occupied components with size 1;
- `tiny_region_count` from occupied components with size at or below the configured threshold;
- `tiny_region_cell_count` as the sum of those occupied component sizes.

The hand-computable multicolor subject test now correctly expects the surrounded one-cell accent color to produce zero occupied isolation and zero tiny occupied regions because it remains part of one connected occupied structure.

Result: **PASS**

## 7. COLOR DOMINANCE REVIEW

C002 adds canonical `occupied_color_counts`, aggregating occupied cells for every non-negative-space C-ID regardless of same-color component splitting.

`largest_color_dominance` is now `max(total occupied cells for one C-ID) / occupied_count`.

The focused split-component fixture proves that the dominant color's total can exceed the largest occupied-region share, and the strict one-color fixture proves a configured limit is no longer bypassed.

Result: **PASS**

## 8. METRIC / EDGE-CASE TEST REVIEW

The C002 test suite now includes direct fixtures for:

- inferred empty;
- one occupied cell;
- full occupied interior;
- rectangular geometry;
- horizontal-only score behavior;
- vertical-only score behavior;
- deliberate asymmetry;
- equal-size occupied components;
- entropy zero;
- negative-space tie handling;
- every required stable rejection code.

These tests materially improve C001 acceptance coverage.

Result: **PASS with documentation residue handled in Section 12**

## 9. REVIEW FIXTURE TRUTHFULNESS

The C002 review builder no longer aliases the same connected `_subject()` geometry under misleading structural labels. It defines genuinely distinct fixtures and the manifest test verifies properties such as:

- sparse occupied ratio below the chosen bound;
- multi-island occupied component count at least 2;
- designed symmetry score;
- asymmetric scores below 1;
- rectangular width not equal to height.

Result: **PASS**

## 10. GENERATOR COMPATIBILITY

C002 strengthens M03-M06 quality compatibility beyond `analysis is not None`. Representative generated results are evaluated under documented conservative policies and acceptance is asserted, including explicit quality-only relaxation for synthetic-test WFC where needed.

The generator outputs themselves are not modified to satisfy M07.

Result: **PASS**

## 11. CONTACT-SHEET RENDERER

`build_contact_sheet()` now derives per-entry evidence from the deterministic review manifest and renders for each card:

- identity and generator/fixture metadata;
- dimensions;
- occupied/component/isolation/tiny/dominance/symmetry summary;
- inferred negative-space and used-color count;
- exact grid SHA-256 or explicit invalid-input unavailability;
- exact duplicate group;
- near-duplicate partner IDs with occupancy and color-layout similarities;
- quality decision and rejection codes.

The renderer therefore materially closes the C001 presentation defect.

Result: **PASS for implementation**

## 12. FINDING F-PAG-M07-C002-001: CARD-LOCAL REVIEW ASSERTIONS

Severity: **MAJOR**

C002 explicitly required:

`Strengthen integration tests to parse/assert representative rendered card content, not merely search the whole HTML for generic tokens.`

The current contact-sheet test does verify that one generated grid hash occurs somewhere in the document, but the duplicate/near-duplicate/invalid-input assertions remain whole-document searches:

- `"exact duplicate group:" in contact`;
- `"near-duplicate partners:" in contact`;
- `"UNAVAILABLE: INVALID_INPUT" in contact`.

Those assertions do not prove that:

- the `bad-09-exact-duplicate-a` card contains `bad-10-exact-duplicate-b` in its own duplicate group;
- the near-duplicate fixture contains the expected partner ID and the exact occupancy/color similarities in its own card;
- a specific invalid dimension or off-palette card contains its own stable rejection code and `UNAVAILABLE: INVALID_INPUT` state;
- evidence from another card cannot accidentally satisfy the test.

A future renderer regression that moves or drops evidence from the intended card can therefore remain green if the generic label still appears elsewhere.

Disposition: **OPEN / MUST REMEDIATE**

## 13. FINDING F-PAG-M07-C002-002: SYMMETRY FIELD CONTRACT

Severity: **MINOR**

The C002 prompt required the geometric reflection convention for both directional scores to be explicitly documented.

Current implementation behavior is clear from `_symmetry()`:

- `horizontal_symmetry_score` is computed by comparing `(x, y)` with `(width - 1 - x, y)`, meaning left-right mirroring, geometrically reflection across the vertical centerline;
- `vertical_symmetry_score` compares `(x, y)` with `(x, height - 1 - y)`, meaning top-bottom mirroring, geometrically reflection across the horizontal centerline.

The directional tests distinguish the two, but `src/scrubbots_pixel_factory/quality/README.md` still documents only the quality layer, negative-space inference and hash/similarity design. It does not state these field conventions, and the public metric contract has no equivalent explicit definition.

Because the field names can be interpreted either by mirror direction or axis of reflection, leaving this convention implicit is an avoidable contract ambiguity.

Disposition: **OPEN / MUST REMEDIATE**

## 14. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder claims for the C001 product fixes are substantially confirmed by direct GitHub source/test inspection.

Builder claims the contact-card scan confirmed hash, invalid-input status and diversity evidence are rendered. Repository source confirms that rendering exists. The issue is not fabrication of the renderer claim; it is that the required card-specific automated acceptance proof was not implemented.

Builder did not claim a symmetry documentation file change, and the changed-file list omits `quality/README.md`. Direct inspection confirms that documentation remained unchanged.

Result: **MOSTLY ACCURATE BUILDER LOG / acceptance gaps remain**

## 15. REGRESSION / TEST EVIDENCE

Builder reports:

- M07 focused suite: `20 passed, 1 warning`;
- M01/M02 plus representative/full M03-M06 suite: `160 passed, 1 warning`;
- full repository: `270 passed, 1 warning`;
- standalone import: PASS;
- cross-process/hash-seed test: PASS;
- offline/network/resize/hash/M08+ scans: PASS;
- `git diff --check`: PASS apart from line-ending warnings;
- unchanged `pytest-asyncio 0.24.0` versus pytest `9.1.1` environment-only `pip check` mismatch.

No GitHub Actions workflow run is attached to terminal builder-era HEAD `4379400527...`, so runtime results remain builder-supplied rather than independently executed.

Result: **BUILDER PASS / independent runtime UNVERIFIED**

## 16. SECURITY / OFFLINE / SCOPE REVIEW

No runtime HTTP/API/cloud/AI/GPU dependency was introduced. No resizing/interpolation path was added. No M03-M06 generator was modified. No M08+ implementation appears in the C002 builder diff.

Result: **PASS**

## 17. DEFECTS BY SEVERITY

### BLOCKER

None.

### MAJOR

- `F-PAG-M07-C002-001`: review contact-sheet acceptance evidence is still whole-document/global for the most important duplicate/near-duplicate/invalid-input assertions, contrary to the explicit card-local C002 requirement.

### MINOR

- `F-PAG-M07-C002-002`: horizontal/vertical symmetry field geometric reflection semantics remain undocumented.

### NOTE

- No GitHub Actions run exists for terminal builder-era HEAD; builder runtime test results are not independently reproduced by CI.
- The equality-recording commit necessarily follows the equality checkpoint it records. GitHub independently confirms the final log record is published on `main`; this is not treated as a product defect.

## 18. REGRESSION RISK

**LOW to MEDIUM.**

The two original metric-mathematics defects are fixed with focused tests. Remaining risk is concentrated in evidence binding and contract clarity rather than core computation. C003 should avoid changing metric algorithms unless a new focused test proves an actual contradiction.

## 19. FINAL VERDICT

**FAIL**

C002 is a strong remediation and closes the substantive C001 computation defects, but it does not satisfy every explicit C002 exit gate. One MAJOR evidence-validation defect and one MINOR documentation defect remain.

M07 stays open. No PAG-0701..PAG-0738 checkbox is promoted until unconditional independent PASS. M08+ remains blocked.

## 20. REQUIRED REMEDIATION

Create bounded cycle:

`PAG-M07-C003 — Review Evidence & Symmetry Contract Closure`

C003 must:

1. preserve C002 metric/rejection mathematics and acceptance fixtures;
2. explicitly document the geometric convention for `horizontal_symmetry_score` and `vertical_symmetry_score` in the public quality contract/docs;
3. strengthen contact-sheet tests so assertions are card-local and tied to exact expected values from representative manifest entries;
4. directly prove at minimum an exact-duplicate card, a near-duplicate card, an invalid-input card and a normal generated card each contain their own expected evidence;
5. regenerate committed review HTML only if the deterministic card markup changes;
6. retain offline/no-resize/M00-M06 behavior;
7. run focused M07 and full regression verification;
8. do not begin M08+ or modify ChatGPT-owned tracker/audit state.