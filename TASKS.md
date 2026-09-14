# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the only current project-status tracker for the active Semantic Pixel Studio / Level Factory work. Historical cycle detail remains in Git history, `.hiveai/prompts/`, `.hiveai/codex-logs/`, `.hiveai/audits/`, `review/` evidence and published owner-decision documents.

Only ChatGPT, acting as independent auditor/tracker owner, may promote task state or mark a cycle/milestone accepted or closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: PAG-SP05 — LEVEL_ART Semantic Integration
- Current Sprint: PAG-SP05-C003-R01 — Direct Binding Proof & Publication Evidence Closure
- Current Task: PAG-SP05-C003-R01 — Direct Binding Proof & Publication Evidence Closure
- Current Task Status: READY_FOR_IMPLEMENTATION
- Next Task/Action: Codex executes only PAG-SP05-C003-R01 from the published remediation prompt, pushes the test/evidence implementation and finalized builder log to `main`, then stops for ChatGPT strict audit.
- Required Actor: CODEX
- Current Phase: ACCEPTANCE EVIDENCE REMEDIATION
- Current Prompt: `.hiveai/prompts/PAG-SP05-C003-R01_DIRECT_BINDING_PROOF_AND_PUBLICATION_EVIDENCE_CLOSURE_PROMPT.md`
- Current Owner Decision Authority: `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V02.md`
- C003 Builder Log: `.hiveai/codex-logs/PAG-SP05-C003_TRUSTED_REPORT_BINDING_AND_ACCEPTANCE_EVIDENCE_CLOSURE_CODEX_LOG.md`
- C003 Strict Audit: `.hiveai/audits/PAG-SP05-C003_TRUSTED_REPORT_BINDING_AND_ACCEPTANCE_EVIDENCE_CLOSURE_STRICT_AUDIT.md`
- SP05-C001: FAIL / SUPERSEDED BY C002 REMEDIATION
- SP05-C002: FAIL / CORE DIFFICULTY V1 CONVERGENCE RETAINED
- SP05-C003: CHANGES_REQUIRED / PRODUCT FIX RETAINED; DIRECT BINDING PROOF + PUBLICATION EVIDENCE REMAIN
- Credit Policy: No Magnific or PixelLab call is authorized in C003-R01. Spend zero provider credits.
- Blockers/Waits: M08/LevelData bridge, solver integration, SP06 semantic recognizability, Studio feature expansion, publishing, weekly batching and M11 remain blocked until SP05 receives independent PASS.
- Approved Semantic Providers: MAGNIFIC, PIXELLAB
- Provider Architecture: provider-neutral; explicit provider/model/engine selection; no silent fallback
- Tracking Repository: `Sekiph82/ScrubBots-Level-Factory`
- Tracking Branch: `main`
- Canonical Local Repository: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## H!veAI Parser Contract

The six live status labels above are literal parser fields and must remain exactly:

- `Current Milestone:`
- `Current Sprint:`
- `Current Task:`
- `Current Task Status:`
- `Next Task/Action:`
- `Required Actor:`

Do not wrap those label names in Markdown bold markers and do not replace them with aliases such as `Next Action:` or `Current Phase:`.

## Current Owner-Locked LEVEL_ART Contract

Current Difficulty V1 production legality is independent of EASY/MEDIUM/HARD/VERY_HARD class bands.

- width: 20..59 inclusive;
- height: 20..59 inclusive;
- width and height validated independently;
- rectangular boards legal;
- one logical artwork pixel = one gameplay cell;
- logical palette: C01..C16 only;
- BG01 `#202533` remains presentation/background only;
- production used-color envelope: 3..12 distinct C01..C16 colors, independent of lane/class;
- 3..12 snapped grids remain unchanged merely because lane/class metadata changes;
- fewer than 3 colors fail closed; no fabricated accents/colors;
- more than 12 colors reduce deterministically to exactly 12 using the retained exact weighted subset/remap policy;
- envelope reduction may not introduce a C-ID absent from the snapped used set;
- high-resolution semantic-image reduction policy: `CELL_MAJORITY_V1`;
- palette stage: `PALETTE_SNAP_V1`;
- no averaging/interpolation/antialiasing inside logical cells;
- deterministic exact provenance/export required;
- lane/class metadata may remain for lineage but must be non-transformative;
- Challenge Score / Session Load / Frustration / solver / campaign fit remain downstream concerns, not hard-cell compiler legality.

Historical class-specific rules remain compatibility evidence only:

- EASY 20–29 / 3–5 colors;
- MEDIUM 30–39 / 6–7 colors;
- HARD 40–49 / 8–9 colors;
- VERY_HARD 50–59 / 10–12 colors.

They must not be reintroduced as current production semantic-compiler truth.

Canonical workflow authority:

`docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V02.md`

## Trusted Evidence Contract

A trusted LEVEL_ART artifact/report must bind the actual canonical stages, not caller assertions.

Required invariant chain:

`SemanticRawArtifact → CELL_MAJORITY_V1 → PALETTE_SNAP_V1 → PRODUCTION_COLOR_ENVELOPE_V1 → final logical cells`

Trusted evidence must bind:

- exact source raw-artifact digest;
- exact source raw SHA-256;
- request digest and target dimensions;
- majority RGBA digest;
- snapped-grid digest and original used IDs/count;
- retained subset and weighted subset cost when >12 reduction occurs;
- final used IDs/count;
- final logical-grid digest;
- exact source provenance.

C003 product code now explicitly encodes:

`report.raw_sha256 == artifact.raw_sha256 == source_provenance.raw_sha256`

C003-R01 exists only to prove that cross-binding directly with a fingerprint-valid adversarial report and to close the missing builder-publication evidence. It must not reopen the production architecture.

## ASSET_ART Contract

- Separate from LevelData/difficulty legality.
- 24x24 px is the first owner-approved ASSET_ART baseline target.
- 24x24 is not the only future ASSET_ART size.
- C01..C16 is not automatically forced on ASSET_ART.
- ASSET_ART may retain separate normalization/palette policies when explicitly specified.
- ASSET_ART policy must never override the owner-locked LEVEL_ART workflow.

## Magnific Live Evidence

Accepted source facts remain:

- provider/model direction: Magnific `recraft-v4-1` wizard smoke;
- owner accepted semantic/readability direction;
- provider creation metadata previously reported 2048x2048;
- owner-downloaded exact file used for local qualification is 1024x1024, 265479 bytes;
- source SHA-256: `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`;
- source profile: 8-bit RGB, non-interlaced;
- chunk sequence: `IHDR -> caBX -> fdEC -> IDAT -> IEND`;
- metadata-vs-downloaded-file dimension mismatch remains visible and unresolved, not silently reconciled;
- Q03 `AREA_AVERAGE_V1` result was technically reproducible but OWNER REJECTED for LEVEL_ART visual behavior;
- CELL_MAJORITY diagnostic was OWNER ACCEPTED as the LEVEL_ART logical-cell reduction direction.

No live provider call is needed or authorized for C003-R01.

## Milestone Overview

- [x] PAG-SP00 — Owner Rejection & Semantic Pivot Record
- [x] PAG-SP01 — Semantic Contracts & Provider Boundary
- [x] PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion
- [x] PAG-SP03 — Semantic Normalization Pipeline technical foundation
- [~] PAG-SP04 — Semantic Provider / Model / Workflow Qualification — Magnific live path technically qualified through Q04 owner disposition; PixelLab/comparative qualification deferred until useful/authorized
- [~] PAG-SP05 — LEVEL_ART Semantic Integration — C001 FAIL → C002 core convergence retained → C003 product fix retained → C003-R01 acceptance evidence closure active
- [ ] PAG-SP06 — Semantic Quality / Recognizability Gate
- [ ] PAG-SP07 — Reference / Style Generation
- [ ] PAG-SP08 — Edit / Inpaint
- [ ] PAG-SP09 — Pixel Studio Create / Gallery UI
- [ ] PAG-SP10 — Automated Weekly Semantic Batch
- [ ] PAG-SP11 — ASSET_ART Production
- [ ] PAG-SP12 — Direction / Rotation Variants
- [ ] PAG-SP13 — Animation
- [ ] PAG-SP14 — ScrubBots Level Factory Bridge

M00–M10 remain historical accepted technical foundation except the M10 visual pack, which remains OWNER REJECTED 100/100. M11 remains blocked pending semantic replacement acceptance.

---

# PAG-SP04 — Accepted Live Qualification State

- C004 — PASS / CLOSED offline qualification foundation.
- C005 — FAIL / remediated by C006.
- C006 — PASS / CLOSED PNG ancillary + IDAT structural compatibility.
- Q01 — local owner-supplied artifact byte identity captured; provider-metadata 2048 vs downloaded-file 1024 mismatch remains recorded.
- Q02 — PASS, real owner-supplied Magnific PNG accepted by strict decoder without rewriting bytes.
- Q03 — deterministic `AREA_AVERAGE_V1` execution technically passed but its blended LEVEL_ART visual policy was owner rejected.
- Q04 — OWNER DISPOSITION RECORDED: CELL_MAJORITY selected; AREA_AVERAGE rejected for LEVEL_ART.
- Q05/Q06/Q07 — PixelLab/comparative/default-provider selection remains deferred and must not reopen the local LEVEL_ART compiler contract.

---

# PAG-SP05-C001 — LEVEL_ART Hard-Cell Compiler, Palette Snap & Difficulty Budget

State: FAIL / REMEDIATED BY C002 DIRECTION

Strict audit:

`.hiveai/audits/PAG-SP05-C001_LEVEL_ART_HARD_CELL_COMPILER_PALETTE_SNAP_AND_DIFFICULTY_BUDGET_STRICT_AUDIT.md`

Retained technical evidence:

- [x] CELL_MAJORITY_V1 deterministic hard-cell reduction;
- [x] PALETTE_SNAP_V1 to canonical C01..C16;
- [x] weighted exact subset optimizer foundation;
- [x] raw-artifact/provenance foundation;
- [x] ASSET_ART separation.

Rejected/superseded C001 behavior:

- [x] class-specific dimension/color legality identified as stale for current production;
- [x] public trusted-construction gap identified.

C001 is historical implementation evidence, not accepted final SP05 closure.

---

# PAG-SP05-C002 — Difficulty V1 Contract Convergence & Trusted Compilation Evidence Closure

State: FAIL / PARTIAL TECHNICAL ACCEPTANCE; REMEDIATED BY C003 PRODUCT FIX

Implementation commit:

`f9c0aaf9043f2f90c1a422e075aebcad9807ecbe`

Builder-log publication commit:

`1a2c29bec920abdf7f90cc914b18ba1ac18ca166`

Builder log:

`.hiveai/codex-logs/PAG-SP05-C002_DIFFICULTY_V1_CONTRACT_CONVERGENCE_AND_TRUSTED_COMPILATION_EVIDENCE_CLOSURE_CODEX_LOG.md`

Strict audit:

`.hiveai/audits/PAG-SP05-C002_DIFFICULTY_V1_CONTRACT_CONVERGENCE_AND_TRUSTED_COMPILATION_EVIDENCE_CLOSURE_STRICT_AUDIT.md`

Accepted/retained C002 technical work:

- [x] explicit current production 20..59 dimension contract;
- [x] rectangle legality independent of lane/class;
- [x] explicit current global 3..12 used-color envelope;
- [x] 3..12 preserved without class-specific recoloring;
- [x] <3 fail closed;
- [x] >12 exact weighted reduction to 12 retained;
- [x] removed colors map to nearest retained colors;
- [x] no new C-ID introduced by envelope reduction;
- [x] current `PRODUCTION_COLOR_ENVELOPE_V1` policy identity;
- [x] public historical `from_compilation()` changed to canonical recomputation rather than assertion-based sealing;
- [x] direct/replace report/artifact construction protections materially improved;
- [x] no provider execution/credits;
- [x] no M08/solver/SP06/main-game product expansion.

C002 defects were handed to C003; the product-code raw-SHA binding is now present on current `main`.

---

# PAG-SP05-C003 — Trusted Report Binding & Acceptance Evidence Closure

State: CHANGES_REQUIRED / PRODUCT FIX RETAINED; C003-R01 REQUIRED

Published implementation commit:

`e3605c263c495870766b6d841612b88194b35b66`

Builder log:

`.hiveai/codex-logs/PAG-SP05-C003_TRUSTED_REPORT_BINDING_AND_ACCEPTANCE_EVIDENCE_CLOSURE_CODEX_LOG.md`

Strict audit:

`.hiveai/audits/PAG-SP05-C003_TRUSTED_REPORT_BINDING_AND_ACCEPTANCE_EVIDENCE_CLOSURE_STRICT_AUDIT.md`

Independently retained C003 technical work:

- [x] explicit `artifact.raw_sha256 == source_provenance.raw_sha256` binding retained;
- [x] explicit `artifact.raw_sha256 == report.raw_sha256` binding added;
- [x] report/artifact token + fingerprint model retained;
- [x] public `from_compilation()` remains non-minting and recomputes canonically;
- [x] majority/snapped/final transformation evidence is lane-non-transformative for the tested same raw+target case;
- [x] 13 used colors reduce to exactly 12;
- [x] 14 used colors reduce to exactly 12;
- [x] 15 used colors reduce to exactly 12;
- [x] 16 used colors reduce to exactly 12;
- [x] envelope reduction introduces no new C-ID in the added fixtures;
- [x] field-level report fingerprint tamper probes cover raw SHA, majority, snapped, original-used, retained subset, weighted cost, final-used and final-grid evidence;
- [x] C003 diff scope is limited to one product line, focused tests and builder log;
- [x] root `TASKS.md` was not edited by the C003 builder commit;
- [x] no provider/product-scope expansion is visible in the C003 diff.

Open C003 acceptance-evidence defects:

- [ ] directly prove the new raw-SHA cross-binding with a fingerprint-valid but wrong-raw-SHA report so the artifact equality check, not the report fingerprint, is the rejecting boundary;
- [ ] make same-lane repeated 13/14/15/16 determinism explicit while retaining EASY/VERY_HARD equivalence;
- [ ] publish a complete superseding builder log with implementation commit SHA and implementation push result;
- [ ] use internally consistent wording for read-only main-game authority access versus no main-game writes.

---

# PAG-SP05-C003-R01 — Direct Binding Proof & Publication Evidence Closure

State: READY_FOR_IMPLEMENTATION

Prompt:

`.hiveai/prompts/PAG-SP05-C003-R01_DIRECT_BINDING_PROOF_AND_PUBLICATION_EVIDENCE_CLOSURE_PROMPT.md`

Required closure:

- [ ] construct a fingerprint-valid wrong-raw-SHA report through test-only/internal access;
- [ ] prove that forged report passes its own seal/integrity validation before artifact construction;
- [ ] prove canonical internal artifact construction rejects the report/source raw-SHA mismatch with `INVALID_ARTIFACT`;
- [ ] add no public trust-minting API;
- [ ] assert same-lane repeated 13/14/15/16 reductions are identical;
- [ ] retain EASY/VERY_HARD lane-equivalent 13/14/15/16 output/details;
- [ ] preserve exactly 12 final used colors for every over-envelope case;
- [ ] preserve no-new-C-ID property;
- [ ] preserve C003 product architecture;
- [ ] focused and full regressions green;
- [ ] zero Magnific/PixelLab calls and zero provider credits;
- [ ] no main-game writes;
- [ ] Codex does not edit root `TASKS.md`;
- [ ] C003-R01 builder log records implementation commit SHA and implementation push result;
- [ ] ChatGPT strict audit required before SP05 closure.

---

## Current Stop / Action Rule

Execute only `PAG-SP05-C003-R01`.

Do not reopen Difficulty V1 architecture. Do not alter CELL_MAJORITY, PALETTE_SNAP, production dimensions, the 3..12 envelope or weighted subset/remap behavior unless the direct binding proof exposes a genuine defect. Do not call Magnific or PixelLab. Do not spend credits. Do not begin M08/LevelData, solver, SP06, Studio, publishing, weekly batching or M11.

After Codex pushes C003-R01 implementation + finalized evidence log, stop for ChatGPT strict audit.
