# PAG-SP05-C001 — LEVEL_ART Hard-Cell Compiler, Palette Snap & Difficulty Budget
Document role: CHATGPT STRICT AUDIT

## 1. VERDICT

**FAIL**

Severity summary:

- BLOCKER: 1
- MAJOR: 1
- MINOR: 1
- NOTE: 3

SP05-C001 faithfully implements the prompt it was given and the core hard-cell art work is valuable: `CELL_MAJORITY_V1`, deterministic C01..C16 palette snap, raw-byte preservation, and the weighted exact subset optimizer are technically useful retained evidence.

It cannot be accepted as the canonical production LEVEL_ART compiler on current `main` for two independent reasons:

1. **Current owner-locked Difficulty V1 supersedes the prompt's class=dimension and class=color-count legality model.** The compiler still enforces legacy EASY/MEDIUM/HARD/VERY_HARD dimension bands and class-specific color bands.
2. **Trusted construction is incomplete.** The exported checked-construction path can seal a `SemanticLevelArtReport` whose raw/intermediate/budget evidence was not actually derived from the supplied raw artifact and transformation stages.

C001 is therefore retained as partial implementation evidence, not discarded. A bounded C002 remediation must converge the compiler to current Difficulty V1 and close the report/artifact trust boundary.

## 2. CONTRACT RECOVERY

### Builder-start authority

C001 started at `77262a8550391d821b24082ebb8776d13744fdf7` and implemented the then-published prompt:

`.hiveai/prompts/PAG-SP05-C001_LEVEL_ART_HARD_CELL_COMPILER_PALETTE_SNAP_AND_DIFFICULTY_BUDGET_PROMPT.md`

That prompt required:

- `CELL_MAJORITY_V1`;
- C01..C16 palette snap;
- legacy difficulty dimension bands;
- legacy class-specific used-color bands;
- exact weighted subset reduction above class maximum;
- fail-closed behavior below class minimum;
- typed immutable provenance.

### Current-main authority

Current Content Platform governance now explicitly states that main-game owner-locked Difficulty V1 outranks stale legacy difficulty rules in this repository.

`coordination/OWNER_CONTENT_PLATFORM_CONSOLIDATION_DECISION_V01.md` says:

- dimensions are an engine/content envelope, not difficulty-class identity;
- production artwork uses C01..C16 and the current **3..12 used-color envelope**;
- legacy `EASY 20..29 / MEDIUM 30..39 / HARD 40..49 / VERY_HARD 50..59` and class-specific color bands are historical compatibility rules.

The canonical migrated root `TASKS.md` repeats the same program rules and explicitly records that SP05-C001 is a grandfathered builder cycle whose output must be audited against current Difficulty V1 before canonical task closure.

Main-game authority `coordination/OWNER_DIFFICULTY_PROGRESSION_DECISION_V01.md` is unambiguous:

- width/height production envelope remains `20..59`, rectangles legal;
- a 24x24 level may be VERY_HARD;
- a 38x38 level may be EASY;
- old class-specific color bands are superseded as difficulty-class legality;
- current production logical art may use **3..12** canonical C01..C16 colors regardless of class;
- Challenge Score / Session Load / Frustration Risk, not dimension/color count alone, define current Difficulty V1 behavior.

This current authority controls this audit.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder start:

`77262a8550391d821b24082ebb8776d13744fdf7`

Implementation commit:

`d7c405d2b4358180be2fc62d028f79c938909b4a`

Builder-log publication commit:

`68a4c0a46d4797e15994d364aff3dd7b0bb07792`

The technical C001 implementation changed only the expected compiler/export/test/log paths. The builder did not edit root `TASKS.md`.

After the builder publication, a separate concurrent Content Platform consolidation/migration workstream added governance, architecture, tracker, Studio, schema, publishing and lifecycle commits. These are not attributed to the C001 builder. At technical-audit snapshot, current `main` was:

`2f88913db1ce5a3691105583b31a057664f579cd`

The C001 compiler source itself was not modified by those later governance/scaffold commits.

## 4. ACCEPTANCE CRITERIA MATRIX

| Criterion | Audit result |
|---|---|
| CELL_MAJORITY exact footprints / no averaging | PASS |
| majority tie by lexicographic RGBA | PASS |
| source<target fail closed | PASS for C001 V1 |
| non-opaque majority fail closed | PASS |
| palette snap only to C01..C16 | PASS |
| BG01 excluded from logical cells | PASS |
| squared-RGB distance + canonical-index tie | PASS |
| weighted exact subset optimization | PASS under legacy C001 policy |
| deterministic row-major logical grid | PASS |
| raw bytes/SHA preserved through source artifact | PASS |
| existing ASSET_ART path not modified | PASS by scoped source diff + builder regression evidence |
| current Difficulty V1 dimension semantics | **FAIL / BLOCKER** |
| current 3..12 production color envelope independent of class | **FAIL / BLOCKER** |
| trusted report/intermediate provenance cannot be falsely minted | **FAIL / MAJOR** |
| every required C001 focused assertion present | PARTIAL / MINOR test gap |
| no provider call/credit spend | PASS by builder evidence and changed-source inspection |
| no M08/solver/SP06 expansion | PASS for builder scope |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder reports:

- final focused SP05 test run: `16 passed`;
- SP05/SP03/SP04 normalization boundary set: `45 passed`;
- combined contract + SP01-SP05 set: `182 passed`;
- full repository: `516 passed`;
- compileall/import/CLI/diff/network-credential checks passed;
- no provider call or credit spend.

Repository inspection supports the claimed algorithm structure and the scoped implementation. These test counts are builder-reported, not independently replayed by ChatGPT because the audit container could not resolve `github.com` for a clean clone.

Important: the builder did **not** cause the Difficulty V1 authority mismatch. The current Difficulty V1 consolidation landed after its implementation/log publication. The mismatch is a prompt/tracker authority error that must be corrected before acceptance.

## 6. FILE / SYMBOL EVIDENCE

`src/scrubbots_pixel_factory/semantic/normalization/level_art.py`:

### Correctly retained technical work

- `cell_majority_rgba_grid()` uses exact half-open integer footprints;
- selects highest frequency, then lexicographic RGBA tie;
- does not average channels or invoke resampling;
- rejects source dimensions smaller than requested target;
- rejects non-opaque winning cells;
- `palette_snap_grid()` selects only `CANONICAL_PALETTE.colors` using integer squared RGB distance and canonical palette index tie-break;
- `enforce_difficulty_color_budget()` uses exact combinations and frequency-weighted subset cost;
- final logical cells are C-ID strings and canonical artifact validates actual-used palette IDs.

### Current-contract mismatch

`SemanticLevelArtRequest.__post_init__()` calls legacy `validate_dimensions(selected_difficulty, width, height)`.

`enforce_difficulty_color_budget()` calls legacy `_color_count_band(difficulty)` and therefore preserves/reduces/fails according to old class-specific ranges.

This means the compiler currently rejects or rewrites candidates that current Difficulty V1 explicitly permits.

### Trust-boundary gap

`SemanticLevelArtArtifact.from_compilation(...)` is an exported/publicly reachable classmethod that accepts caller-supplied:

- `logical_cells`;
- `majority_rgba_sha256`;
- `snapped_grid_digest`;
- `SemanticLevelArtReport`.

The artifact validates several cross-links, but it does **not** prove that the supplied majority/snapped/budget report evidence was actually computed from the supplied raw artifact.

In particular, artifact validation does not require `report.raw_sha256 == source_provenance.raw_sha256`, and does not recompute/verify `report.original_used_palette_ids`, `retained_palette_ids`, or `weighted_subset_cost` from sealed stage evidence. A caller can therefore construct a syntactically valid report with fabricated intermediate/budget facts, make its final-grid digest match an arbitrary legal final grid, then pass it through `from_compilation()` and obtain a sealed artifact.

That violates the requirement that trusted artifacts carry exact immutable transformation evidence.

## 7. FOCUSED TEST EVIDENCE

Existing C001 tests positively cover:

- exact-size hard-cell behavior;
- 4x4→2x2 majority;
- non-divisible footprint determinism;
- majority tie-break;
- source-smaller and alpha failure;
- exact/nearest/tie palette snap;
- all four legacy class maxima;
- below-minimum legacy failure;
- weighted subset fixture;
- subset tie fixture;
- legacy rectangles;
- raw-byte provenance sensitivity;
- direct artifact construction / artifact replace tamper checks;
- ASSET_ART separation.

Missing/insufficient audit probes:

- no test proves the public checked `from_compilation()` path rejects a forged but internally self-consistent report;
- no test mutates `report.raw_sha256` / original-used / retained / weighted-cost evidence while keeping final-grid fields consistent;
- required removed-color→nearest-retained mapping is not independently asserted cell-by-cell;
- current Difficulty V1 examples such as VERY_HARD 24x24, EASY 38x38, or 8-color EASY are not tested because the original prompt encoded superseded rules.

## 8. REGRESSION EVIDENCE

Builder reports full suite `516 passed` before the later Content Platform migration commits.

No C001 product change touched provider adapters, the accepted C005/C006 PNG decoder, or ASSET_ART normalization algorithms.

Later governance/scaffold commits modify program authority and repository boundaries, not C001 compiler source.

Because current-main program rules changed, green legacy tests cannot by themselves establish production correctness.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive findings:

- no network/provider execution added to LEVEL_ART compiler;
- no credentials/telemetry path added;
- raw PNG decoding remains behind accepted strict decoder;
- no arbitrary executable content behavior;
- palette output remains closed to C01..C16.

Integrity concern:

- forged intermediate/report evidence can be sealed through the public checked-construction path. This is a provenance/integrity failure, not a code-execution vulnerability.

## 10. ARCHITECTURE CONSISTENCY

CELL_MAJORITY → C01..C16 remains aligned with the current Content Platform Art Intelligence architecture.

The class-specific dimension/color-budget layer is no longer architecturally correct under Difficulty V1. Difficulty class/lane belongs to current challenge/progression intelligence and must not be reintroduced as a dimension or distinct-color legality proxy.

The correct production compiler boundary is now:

`RAW SEMANTIC ART → CELL_MAJORITY → C01..C16 PALETTE SNAP → CURRENT PRODUCTION ENVELOPE (20..59, 3..12) → immutable trusted logical-art evidence`

Challenge class/score evaluation occurs downstream in Difficulty Intelligence / QA rather than by forcing class-specific board/color bands in this compiler.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

The migrated current root `TASKS.md` now correctly states:

- canonical program has 224 LF/CP tasks;
- Difficulty V1 overrides stale class=dimension/class=color-count semantics;
- production logical art uses C01..C16 with 3..12 colors;
- C001 is a grandfathered builder cycle whose evidence must be audited against current contracts;
- existing PAG/SP evidence is preserved but does not automatically close new canonical tasks.

Builder log truthfully records its original scope and test failures/fixes. It does not falsely claim ChatGPT acceptance.

## 12. FINAL REPOSITORY STATE

At the technical-audit snapshot, current `main` was:

`2f88913db1ce5a3691105583b31a057664f579cd`

C001 implementation remains present unchanged from `d7c405d...`.

No GitHub combined commit statuses were present for the audited current-main snapshot.

The repository was concurrently receiving Content Platform migration/scaffold commits during this audit; those commits are treated as independent governance/platform work, not C001 builder scope.

## 13. OPEN CROSS-MILESTONE FINDINGS

1. Difficulty V1 contract convergence is required before LF02/LF05 canonical task closure.
2. Existing legacy `contracts/difficulty.py` and `contracts/color_usage.py` still encode historical compatibility behavior used by older PAG generators. They should not be destructively rewritten without regression planning; current production validators should be added/separated explicitly.
3. C001 has not yet been bridged into M08/LevelData; that remains correctly out of scope.
4. Semantic recognizability/SP06 remains separate.
5. Current 224-task evidence mapping remains open.

## 14. DEFECTS BY SEVERITY

### BLOCKER — F-PAG-SP05-C001-001 — Canonical compiler enforces superseded difficulty semantics

**Evidence:** current compiler uses `validate_dimensions(difficulty, ...)` and `_color_count_band(difficulty)` from legacy contracts.

**Current owner authority:** production width/height are independently legal across 20..59 regardless of EASY/MEDIUM/HARD/VERY_HARD; current production logical art may use 3..12 canonical colors regardless of class.

**Concrete wrong behavior:**

- VERY_HARD 24x24 is rejected, though current owner decision explicitly permits it;
- EASY 38x38 is rejected, though current owner decision explicitly permits it;
- an EASY candidate with 8 legal C01..C16 colors is reduced to 5, though current Difficulty V1 permits 8 colors;
- a VERY_HARD candidate with 5 colors is rejected for being below 10, though current Difficulty V1 permits 5.

**Disposition:** retain CELL_MAJORITY and palette snap, replace legacy class-specific compiler legality with a current production envelope.

### MAJOR — F-PAG-SP05-C001-002 — Checked constructor can seal fabricated transformation/report evidence

**Evidence:** `SemanticLevelArtArtifact.from_compilation()` accepts externally supplied final cells, majority hash, snapped hash and report. Artifact cross-checking does not bind every report fact to the exact source/stages and does not require report raw SHA equality with source provenance.

**Impact:** a legal final grid plus fabricated but self-consistent report/intermediate hashes can be sealed as a trusted artifact.

**Disposition:** trusted report/artifact construction must be internal/token-gated or based on typed sealed stage evidence created only by the canonical compiler. Direct construction/replace/public checked-constructor misuse must fail.

### MINOR — F-PAG-SP05-C001-003 — Focused tests do not explicitly prove nearest-retained remap for every removed color

Implementation appears correct (`_nearest_retained`), but prompt test requirement #22 is not independently asserted in the focused test suite.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

- Stop importing private `_color_count_band` from `contracts.color_usage` in new production code.
- Add explicit current-production contract helpers rather than overloading legacy compatibility validators.
- Keep legacy PAG behavior available only where historical reproduction requires it; mark it clearly as legacy compatibility.
- Consider sealed typed stage evidence for majority/snap/envelope transforms so each stage is independently auditable.
- Add CI for current Content Platform core tests.

## 16. UNVERIFIED ITEMS

- Builder-reported Python test suite was not independently replayed because the audit container could not resolve `github.com` for a clean clone.
- The builder's terminal local `HEAD == origin/main` handoff values are not stored in the committed log by design; GitHub confirms both implementation and log publication commits exist.
- No independent performance benchmark of exhaustive palette-subset search was run in this audit; the state space is bounded to at most 16 colors.

## 17. REGRESSION RISK

C002 risk is **MEDIUM** because it changes current production legality while historical generators still depend on legacy contracts.

Safe strategy:

- preserve `CELL_MAJORITY_V1` unchanged;
- preserve `PALETTE_SNAP_V1` unchanged;
- preserve legacy dimension/color-band validators for historical compatibility;
- add explicit current-production envelope validators (20..59; 3..12 independent of class);
- make the new semantic production compiler depend only on current validators;
- close report/artifact construction trust without changing raw decoder/provider behavior.

## 18. AUDIT CONFIDENCE

**HIGH** for the authority mismatch because current migrated `TASKS.md`, Content Platform consolidation decision and main-game owner Difficulty V1 decision all agree.

**HIGH** for the checked-construction provenance gap because it follows directly from the exported constructor inputs and missing cross-checks in `SemanticLevelArtArtifact.__post_init__()` / `from_compilation()`.

**MEDIUM** for full regression state because independent test replay was unavailable.

## 19. FINAL VERDICT

**FAIL**

C001 is not wasted work. Its hard-cell reduction and C01..C16 palette snapping are the correct foundation and should be retained. Its legacy class-specific difficulty enforcement cannot be promoted to current production truth, and its trusted report/artifact construction must be hardened.

No provider regeneration, new credit spend, CELL_MAJORITY redesign, palette redesign, M08 integration, solver work or SP06 expansion is justified for this remediation.

## 20. REQUIRED REMEDIATION

Open exactly one bounded cycle:

**PAG-SP05-C002 — Difficulty V1 Contract Convergence & Trusted Compilation Evidence Closure**

C002 must:

1. preserve `CELL_MAJORITY_V1` behavior byte-for-byte;
2. preserve `PALETTE_SNAP_V1` behavior byte-for-byte;
3. stop using legacy class-specific dimension bands as production compiler legality;
4. use current independent production dimension envelope `20..59` on each axis, rectangles legal;
5. stop using class-specific color-count bands as production compiler legality;
6. use current global production C01..C16 used-color envelope `3..12`;
7. preserve in-envelope 3..12 grids unchanged;
8. fail closed below 3 without fabricating colors;
9. deterministically reduce above 12 to exactly 12 using the already-implemented exact weighted subset optimization;
10. keep any EASY/MEDIUM/HARD/VERY_HARD lane metadata from altering dimension/color legality;
11. preserve historical legacy validators for old reproduction paths rather than silently rewriting all PAG behavior;
12. seal report/stage/artifact construction so fabricated raw/intermediate/budget evidence cannot be minted through direct construction, `replace()`, or a public checked-constructor path;
13. add explicit tests for current Difficulty V1 examples (VERY_HARD 24x24, EASY 38x38, same 3..12 envelope across lanes/classes);
14. add explicit forged-report / forged-intermediate / report-raw-SHA mismatch tests;
15. add explicit removed-color→nearest-retained mapping test;
16. preserve accepted ASSET_ART and PNG-decoder behavior;
17. spend zero provider credits;
18. do not edit root `TASKS.md` as builder;
19. do not begin M08/LevelData bridge, solver, SP06, Studio feature work or publishing work in this remediation;
20. stop for ChatGPT strict audit after push.
