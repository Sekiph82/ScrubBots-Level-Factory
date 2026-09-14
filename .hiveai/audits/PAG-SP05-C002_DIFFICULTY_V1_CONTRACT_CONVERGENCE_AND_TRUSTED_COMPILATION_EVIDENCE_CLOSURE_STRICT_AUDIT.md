# PAG-SP05-C002 — Difficulty V1 Contract Convergence & Trusted Compilation Evidence Closure
Document role: CHATGPT STRICT AUDIT

## 1. VERDICT

**FAIL**

Severity summary:

- BLOCKER: 0
- MAJOR: 1
- MINOR: 3
- NOTE: 3

C002 materially fixes the central Difficulty V1 problem from C001. The current production compiler now uses independent 20..59 width/height legality, a global 3..12 C01..C16 used-color envelope, and preserves the accepted `CELL_MAJORITY_V1` and `PALETTE_SNAP_V1` algorithms. The public historical `from_compilation()` path also no longer seals caller assertions and instead recomputes through the canonical compiler.

However, C002 cannot receive unconditional PASS because the trusted-report binding remains incomplete: a sealed `SemanticLevelArtReport.raw_sha256` is not cross-bound to the artifact/source raw SHA in `SemanticLevelArtArtifact.__post_init__()`. The prompt explicitly required that binding. The focused test suite also omits several mandatory adversarial/equivalence probes that would have exposed this gap.

A narrow C003 remediation is required. No redesign of CELL_MAJORITY, palette snap, the production envelope, providers, M08, solver, SP06, Studio, publishing, or the main-game repository is authorized.

## 2. CONTRACT RECOVERY

Authoritative C002 prompt:

`.hiveai/prompts/PAG-SP05-C002_DIFFICULTY_V1_CONTRACT_CONVERGENCE_AND_TRUSTED_COMPILATION_EVIDENCE_CLOSURE_PROMPT.md`

Prior independent audit:

`.hiveai/audits/PAG-SP05-C001_LEVEL_ART_HARD_CELL_COMPILER_PALETTE_SNAP_AND_DIFFICULTY_BUDGET_STRICT_AUDIT.md`

Current LEVEL_ART convergence authority present on `main`:

`docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V02.md`

Relevant current source:

- `src/scrubbots_pixel_factory/contracts/production.py`
- `src/scrubbots_pixel_factory/semantic/normalization/level_art.py`
- `tests/unit/test_sp05_level_art.py`

The C002 contract requires, among other things:

- CELL_MAJORITY_V1 unchanged;
- PALETTE_SNAP_V1 unchanged;
- independent width/height 20..59 production legality;
- rectangles legal independent of lane/class;
- global 3..12 used-color legality independent of lane/class;
- <3 fail closed;
- >12 reduce deterministically to exactly 12 using the retained weighted subset optimizer;
- trusted report/artifact evidence bound to the actual raw/intermediate/budget/final stages;
- direct/replace/public checked-constructor forgery prevented;
- legacy compatibility preserved;
- explicit focused tests for the trust boundary and lane-independence invariants.

## 3. BRANCH / HEAD / DIFF SCOPE

C002 builder starting HEAD:

`a4d843d98357af4157377bf0736ec0a3685240d7`

C002 implementation commit:

`f9c0aaf9043f2f90c1a422e075aebcad9807ecbe`

C002 builder-log publication commit:

`1a2c29bec920abdf7f90cc914b18ba1ac18ca166`

Audit snapshot current `main` HEAD:

`319dcd3248ff49ab68de47775cf57e7dbea74e22`

The C002 implementation commit changed only the expected LEVEL_ART production-contract/export/compiler/test/log paths. Later commits after C002 altered governance/scaffold/tracker documents and removed premature Content Platform migration artifacts; the C002 product source remained present.

Independent clean-clone/test replay was attempted during this audit but the audit runtime could not resolve `github.com`. Therefore builder-reported test counts remain builder evidence, while code/contract inspection is independent.

## 4. ACCEPTANCE CRITERIA MATRIX

| Criterion | Audit result |
|---|---|
| CELL_MAJORITY_V1 unchanged | PASS |
| PALETTE_SNAP_V1 unchanged | PASS |
| production width/height independently 20..59 | PASS |
| rectangles legal | PASS |
| lane/class no longer controls dimensions | PASS |
| global production used-color envelope 3..12 | PASS |
| 3..12 preserved independent of lane | PASS in implementation; focused evidence PARTIAL |
| <3 fails closed without fabrication | PASS |
| >12 reduces deterministically to 12 | PASS |
| weighted subset optimizer retained | PASS |
| removed colors map only to nearest retained colors | PASS |
| no new C-ID introduced | PASS |
| current policy identity distinct from legacy class-band identity | PASS with compatibility-name NOTE |
| trusted report direct/replace construction blocked | PASS for tested public dataclass paths |
| trusted artifact direct/replace construction blocked | PASS for tested public dataclass paths |
| public `from_compilation()` cannot seal caller assertions | PASS |
| report raw SHA exactly bound to source raw SHA | **FAIL / MAJOR** |
| majority/snapped/final digests bound through canonical artifact path | PASS |
| original/retained/cost evidence built from canonical compiler stages | PASS on canonical compiler path; adversarial proof PARTIAL |
| legacy compatibility validators retained | PASS |
| ASSET_ART behavior retained | PASS by source scope + builder evidence |
| strict PNG behavior retained | PASS by source scope + builder evidence |
| zero provider calls / credits | PASS by builder evidence and source scope |
| builder did not edit root TASKS.md | PASS for C002 implementation |
| no main-game writes | PASS by repository diff evidence |
| focused/full regressions green | PASS as builder evidence; independent replay UNVERIFIED |
| builder publication evidence fully complete | PARTIAL |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder claims include:

- focused SP05: `21 passed, 1 warning`;
- combined semantic/contract regression: `187 passed, 1 warning`;
- full repository: `520 passed, 1 warning`;
- compileall/import/CLI/diff/offline scans passed;
- zero Magnific/PixelLab calls and zero credits;
- C002 changes limited to production contracts, LEVEL_ART implementation/exports, focused tests and log.

Repository truth supports the claimed product-scope changes and the substantive Difficulty V1 convergence. The current source contains the new production contract and uses it from `SemanticLevelArtRequest` and the color-envelope enforcement path.

The independent audit does not promote builder test claims to independent replay because the audit environment could not clone the repository.

## 6. FILE / SYMBOL EVIDENCE

### `src/scrubbots_pixel_factory/contracts/production.py`

Correctly introduces:

- `PRODUCTION_DIMENSION_MIN = 20`;
- `PRODUCTION_DIMENSION_MAX = 59`;
- `PRODUCTION_COLOR_MIN = 3`;
- `PRODUCTION_COLOR_MAX = 12`;
- independent width/height validation;
- rectangle legality;
- global used-color validation.

This is the correct separation from historical class-specific compatibility contracts.

### `src/scrubbots_pixel_factory/semantic/normalization/level_art.py`

Correct retained behavior:

- CELL_MAJORITY footprint math is unchanged from C001;
- lexicographic RGBA majority tie-break remains unchanged;
- no averaging/interpolation was introduced;
- PALETTE_SNAP remains C01..C16 only with squared-RGB distance + canonical-index tie-break;
- request dimensions now call `validate_production_dimensions()`;
- the color-envelope path uses 3..12 globally;
- >12 reduction retains the C001 exact weighted subset optimization;
- `PRODUCTION_COLOR_ENVELOPE_V1` is emitted as the current production policy identity;
- `SemanticLevelArtArtifact.from_compilation()` discards caller-supplied stage assertions and delegates to `compile_semantic_level_art()`.

### Trust-binding defect

`SemanticLevelArtReport` contains both:

- `source_raw_artifact_digest`;
- `raw_sha256`.

The report is fingerprint-sealed after construction.

`SemanticLevelArtArtifact.__post_init__()` correctly cross-checks:

- artifact source digest against source provenance;
- artifact raw SHA against source provenance;
- artifact request digest against report request digest;
- artifact source digest against report source digest;
- difficulty/target dimensions;
- majority digest;
- snapped digest;
- final digest;
- final used IDs;
- final cells against final-grid digest.

But it does **not** require:

`report.raw_sha256 == artifact.raw_sha256 == source_provenance.raw_sha256`

Therefore the explicit C002 requirement that the trusted report raw SHA exactly equal the source raw artifact SHA is not encoded as an invariant at the artifact/report binding boundary.

The canonical compiler currently passes the correct value into `_build_report()`, so ordinary compiler output is correct. That is not enough for a trusted-evidence contract: the seal must reject an internally inconsistent trusted report rather than merely trusting the factory inputs.

## 7. FOCUSED TEST EVIDENCE

Positive focused coverage includes:

- exact-size hard-cell behavior;
- 4x4→2x2 majority;
- non-divisible footprint determinism;
- majority tie-break;
- source-smaller fail closed;
- non-opaque winner fail closed;
- exact/nearest/tie palette snap;
- global >12 reduction;
- <3 fail closed;
- lane-independent 3/5/8/12 preservation examples;
- cell-by-cell removed-color nearest-retained mapping;
- weighted-subset fixture;
- equal-cost subset tie fixture;
- current production dimension boundaries;
- EASY 38x38 and VERY_HARD 24x24 legality;
- byte-distinct/raw-equivalent provenance behavior;
- direct report construction rejection;
- `replace(report, raw_sha256=...)` rejection;
- direct artifact construction rejection;
- `replace(artifact, ...)` rejection;
- public `from_compilation()` recomputation behavior;
- ASSET_ART separation.

Required C002 probes still missing or incomplete:

1. No explicit 14-color and 15-color >12 reduction fixtures; 13 and 16 are covered, but the prompt required 13 through 16.
2. Lane non-transformative test compares final logical cells/used IDs, but does not explicitly assert identical `majority_rgba_sha256`, `snapped_grid_digest`, and `final_logical_grid_digest` for the same raw+target under EASY vs VERY_HARD.
3. No focused adversarial probe attempts to present a trusted report with a wrong `raw_sha256` while all other artifact bindings remain coherent.
4. No explicit mutation probes cover forged report majority digest, snapped digest/used set, retained subset/weighted cost, and final-grid digest as separately required by the prompt.

The missing raw-SHA adversarial probe is material because it corresponds to an actual missing invariant in product code.

## 8. REGRESSION EVIDENCE

Builder reports:

- SP05 focused: 21 passed;
- combined semantic/contract suite: 187 passed;
- full repository: 520 passed;
- compileall and CLI/package smokes passed.

C002 did not edit historical class-specific difficulty/color contract files, provider adapters, strict PNG decoder implementation, or ASSET_ART normalization implementation.

Later current-main changes after C002 are governance/scaffold/tracker changes rather than C002 product-source changes.

Independent replay status: **UNVERIFIED** because the audit runtime could not resolve GitHub for a clean clone.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive findings:

- no network/runtime provider dependency added to LEVEL_ART core;
- no API key/credential/telemetry path added;
- no provider calls are required by C002;
- palette remains closed to canonical C01..C16;
- strict raw decode boundary remains reused.

Integrity finding:

- trusted report raw SHA is not cross-bound to the actual raw SHA by artifact validation. This is a provenance-integrity defect, not a code-execution vulnerability.

## 10. ARCHITECTURE CONSISTENCY

The corrected production compiler architecture is now aligned with Difficulty V1:

`RAW → CELL_MAJORITY_V1 → PALETTE_SNAP_V1 → C01..C16 → production 20..59 envelope → production 3..12 envelope → trusted logical art`

Difficulty lane metadata is retained for lineage but no longer drives dimension or color-count transforms.

This is the correct separation from downstream challenge/progression intelligence.

C002 should not be reopened architecturally. C003 must be a trust/evidence closure only.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

The current root `TASKS.md` is stale: it still shows SP05-C001 as `READY_FOR_IMPLEMENTATION` even though C001 was implemented, independently audited FAIL, and C002 was implemented afterward.

This audit therefore requires the ChatGPT-owned tracker to be updated after publication of this audit/remediation prompt.

Builder-log issues:

- the log says the separate `Sekiph82/Scrubbots` repository was “not accessed or modified”, while the authority section says the main-game owner decision was used as a read-only contract reference. “Not modified” is supported; “not accessed” conflicts with the stated authority read;
- the prompt requested exact changed-file enumeration, push result and terminal repository state. The committed log provides implementation SHA and scope summary but does not contain the final push result/terminal equality values, instead deferring them to the handoff.

These are documentation shortcomings, not evidence that product code was modified outside scope.

## 12. FINAL REPOSITORY STATE

Audit snapshot:

- repository: `Sekiph82/ScrubBots-Level-Factory`;
- branch: `main`;
- current HEAD observed: `319dcd3248ff49ab68de47775cf57e7dbea74e22`;
- C002 implementation remains present from `f9c0aaf9043f2f90c1a422e075aebcad9807ecbe`;
- C002 builder-log publication remains present from `1a2c29bec920abdf7f90cc914b18ba1ac18ca166`.

No C002 product-source rollback was observed in the later current-main governance/scaffold cleanup commits.

## 13. OPEN CROSS-MILESTONE FINDINGS

1. Root `TASKS.md` must be advanced from stale C001-ready state to the audited C002/C003 truth.
2. `AGENTS.md` currently contains contradictory tracker guidance: its opening section references a `.hiveai/TASKS.md` v3 control plane that is absent on current `main`, while its later H!veAI section says root `TASKS.md` is the only current project-status tracker. This governance inconsistency should be handled separately and must not be used to reopen C002 product scope.
3. M08/LevelData remains out of scope until SP05 compiler trust closure passes.
4. SP06 recognizability remains separate and must not begin inside C003.

## 14. DEFECTS BY SEVERITY

### MAJOR — F-PAG-SP05-C002-001 — Trusted report raw SHA is not bound to actual source raw SHA

**Affected:** `SemanticLevelArtArtifact.__post_init__()` / trusted report-artifact binding.

**Current behavior:** artifact validation checks artifact raw SHA against source provenance and source digest against report source digest, but omits report raw SHA equality.

**Required behavior:** every accepted trusted artifact must enforce:

`report.raw_sha256 == artifact.raw_sha256 == source_provenance.raw_sha256`

and reject any mismatch before the artifact can be considered valid or serialized/digested as trusted evidence.

**Required test:** create a legitimate compiler result, produce an adversarial trusted-report mutation/factory test fixture with only report raw SHA altered, and prove artifact/report trust validation fails. The test may use internal test-only access specifically to prove the invariant; production public APIs must remain unable to mint arbitrary trust.

### MINOR — F-PAG-SP05-C002-002 — Lane non-transformative digest evidence is incomplete

The implementation appears lane-independent for transformation output, but focused tests do not explicitly assert equality of majority digest, snapped-grid digest and final-grid digest across EASY vs VERY_HARD for identical raw+target.

Add those exact assertions.

### MINOR — F-PAG-SP05-C002-003 — 14/15-color envelope cases are not explicitly covered

The generic algorithm appears correct and 13/16 cases exist, but the prompt explicitly required 13 through 16.

Add 14 and 15 color fixtures proving deterministic reduction to exactly 12 with no introduced C-ID.

### MINOR — F-PAG-SP05-C002-004 — Required trust-failure probes are incomplete

Add explicit focused probes for tampered report majority digest, snapped digest/used IDs, retained subset/weighted cost, and final-grid digest. Each must fail trust validation and must not be sealable through a public compatibility constructor.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

- Consider renaming the public compatibility alias `DIFFICULTY_BUDGET_POLICY_VERSION`, or clearly documenting it as a deprecated compatibility name, because its value now points to `PRODUCTION_COLOR_ENVELOPE_V1` rather than the historical `DIFFICULTY_COLOR_BUDGET_V1` semantics.
- Consider making report serialization helpers such as `canonical_dict()` assert report integrity before returning trusted data, mirroring the artifact’s stronger behavior.
- Keep historical difficulty/color validators explicitly marked compatibility-only.

These are not all required for C003 PASS unless needed to close the trust tests.

## 16. UNVERIFIED ITEMS

- Builder-reported pytest counts were not independently replayed because the audit environment could not resolve `github.com` for a clean clone.
- Final local builder `HEAD == origin/main` values were not committed into the builder log; GitHub confirms the implementation and log-publication commits exist.
- No independent runtime benchmark of the exhaustive >12 subset optimizer was performed.

## 17. REGRESSION RISK

C003 risk should be **LOW** if strictly bounded.

Do not touch:

- CELL_MAJORITY algorithm;
- PALETTE_SNAP algorithm;
- production dimension envelope;
- production 3..12 envelope algorithm;
- provider code;
- strict PNG decoder;
- ASSET_ART behavior;
- M08/solver/SP06/Studio/publishing/main-game source.

The required code change is primarily a missing cross-binding invariant plus focused adversarial tests.

## 18. AUDIT CONFIDENCE

**HIGH** for the raw-SHA binding defect because it is visible directly in the current `SemanticLevelArtArtifact.__post_init__()` condition set and is explicitly required by the C002 prompt.

**HIGH** for the focused-test gaps because the current `tests/unit/test_sp05_level_art.py` can be inspected directly.

**MEDIUM** for full regression state because independent pytest replay was unavailable.

## 19. FINAL VERDICT

**FAIL**

C002 successfully fixes the large architectural error from C001 and should be retained. It does not need another Difficulty V1 redesign.

The remaining issue is narrower but acceptance-critical: trusted report raw SHA must be bound to the actual source raw SHA, and the missing adversarial/equivalence tests must be added.

## 20. REQUIRED REMEDIATION

Open `PAG-SP05-C003 — Trusted Report Binding & Acceptance Evidence Closure`.

C003 must:

1. enforce report/artifact/source raw-SHA equality;
2. add explicit lane-invariant majority/snapped/final digest assertions;
3. add explicit 14- and 15-color >12 reduction tests;
4. add adversarial trust probes for report raw SHA, majority digest, snapped digest/used set, retained subset/weighted cost and final-grid digest;
5. preserve C002 production semantics and all accepted C001 hard-cell/palette behavior unchanged;
6. run focused and full regressions;
7. make zero provider calls and spend zero credits;
8. not edit root `TASKS.md` as builder;
9. stop after push for ChatGPT strict audit.
