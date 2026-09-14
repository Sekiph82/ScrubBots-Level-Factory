# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the only current project-status tracker for active Semantic Pixel Studio / Level Factory work. Historical implementation detail belongs in Git history, `.hiveai/prompts/`, `.hiveai/codex-logs/`, `.hiveai/audits/`, `review/` evidence and published owner-decision documents.

Only ChatGPT, acting as independent auditor/tracker owner, may promote task state or mark a cycle/milestone accepted or closed. Builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: PAG-SP06 — Semantic Quality / Recognizability Gate
- Current Sprint: PAG-SP06-C001 — Semantic Recognizability Gate Contract & Offline Review Foundation
- Current Task: PAG-SP06-C001 — Semantic Recognizability Gate Contract & Offline Review Foundation
- Current Task Status: READY_FOR_IMPLEMENTATION
- Next Task/Action: Codex executes only PAG-SP06-C001 from the published GitHub prompt, pushes implementation/tests/finalized builder log to `main`, then stops for ChatGPT strict audit.
- Required Actor: CODEX
- Current Phase: CONTRACT_AND_OFFLINE_GATE_FOUNDATION
- Current Prompt: `.hiveai/prompts/PAG-SP06-C001_SEMANTIC_RECOGNIZABILITY_GATE_CONTRACT_AND_OFFLINE_REVIEW_FOUNDATION_PROMPT.md`
- Previous Strict Audit: `.hiveai/audits/PAG-SP05-C003-R01_DIRECT_BINDING_PROOF_AND_PUBLICATION_EVIDENCE_CLOSURE_STRICT_AUDIT.md`
- SP05 Final Disposition: PASS / CLOSED
- SP05 Closing Builder Implementation: `fc008dce7887a1eefbc314eab449c57355f2a942`
- SP05 Closing Builder Log Publication: `009fb76ce9ced264212f6827fa16a66bc4b13083`
- SP05 Closing Audit Commit: `5e789b7b753fca9156af8dd0081fa9d0a7f00b89`
- Credit Policy: No Magnific or PixelLab call is authorized in SP06-C001. Spend zero provider credits.
- Blockers/Waits: SP07+, Studio expansion, weekly batching, M08/LevelData bridge, solver integration and M11 remain blocked until their own authorized cycles.
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

Do not wrap those label names in Markdown bold markers and do not replace them with aliases.

## Accepted SP05 LEVEL_ART Production Contract

SP05 is independently accepted and must not be reopened by SP06 unless a new audited defect proves it necessary.

- production width: 20..59 inclusive;
- production height: 20..59 inclusive;
- width and height validated independently;
- rectangular boards legal;
- one logical artwork pixel = one gameplay cell;
- logical palette: C01..C16 only;
- BG01 `#202533` remains presentation/background only;
- used-color envelope: 3..12 distinct C01..C16 colors independent of difficulty lane;
- 3..12 snapped grids remain unchanged merely because EASY/MEDIUM/HARD/VERY_HARD metadata changes;
- fewer than 3 colors fail closed;
- more than 12 colors reduce deterministically to exactly 12 using the accepted exact weighted subset/remap policy;
- no new C-ID may be introduced by envelope reduction;
- high-resolution reduction policy: `CELL_MAJORITY_V1`;
- palette policy: `PALETTE_SNAP_V1`;
- no averaging/interpolation/antialiasing inside logical cells;
- exact deterministic provenance required;
- trusted report/artifact/source raw SHA binding is explicit;
- public historical `from_compilation()` remains non-minting and recomputes canonically;
- ASSET_ART remains a separate contract.

Trusted raw-SHA invariant:

`report.raw_sha256 == artifact.raw_sha256 == source_provenance.raw_sha256`

Historical class-specific dimension/color bands remain compatibility evidence only and must not become current production truth.

## SP06 Contract Direction

SP06 begins only after accepted trusted LEVEL_ART output exists.

C001 must distinguish two concepts that must not be blurred:

1. deterministic structural diagnostics computed from an accepted LEVEL_ART logical grid;
2. semantic recognizability disposition.

Structural metrics such as transition density, connected-component counts, singleton counts or color-region sizes are objective diagnostics. They are not proof that the depicted subject is recognizable.

C001 therefore establishes an offline, auditable quality/review foundation. It must not silently auto-accept semantic recognizability from heuristic structure alone.

No live provider call, downloaded vision model, CLIP/OCR service, or external semantic recognition API is authorized in C001.

## Milestone Overview

- [x] PAG-SP00 — Owner Rejection & Semantic Pivot Record
- [x] PAG-SP01 — Semantic Contracts & Provider Boundary
- [x] PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion
- [x] PAG-SP03 — Semantic Normalization Pipeline technical foundation
- [~] PAG-SP04 — Provider / Model / Workflow Qualification; Magnific live path qualified through accepted owner disposition, remaining comparative qualification deferred until useful/authorized
- [x] PAG-SP05 — LEVEL_ART Semantic Integration — PASS / CLOSED
- [~] PAG-SP06 — Semantic Quality / Recognizability Gate — C001 READY_FOR_IMPLEMENTATION
- [ ] PAG-SP07 — Reference / Style Generation
- [ ] PAG-SP08 — Edit / Inpaint
- [ ] PAG-SP09 — Pixel Studio Create / Gallery UI
- [ ] PAG-SP10 — Automated Weekly Semantic Batch
- [ ] PAG-SP11 — ASSET_ART Production
- [ ] PAG-SP12 — Direction / Rotation Variants
- [ ] PAG-SP13 — Animation
- [ ] PAG-SP14 — ScrubBots Level Factory Bridge

M00–M10 remain historical accepted technical foundation except the M10 visual pack, which remains OWNER REJECTED 100/100. M11 remains blocked pending explicitly authorized semantic replacement integration.

---

# PAG-SP05 Closure Record

## PAG-SP05-C001

State: FAIL / SUPERSEDED

Retained foundation:

- [x] CELL_MAJORITY_V1;
- [x] PALETTE_SNAP_V1;
- [x] weighted exact subset optimizer foundation;
- [x] raw-artifact/provenance foundation;
- [x] ASSET_ART separation.

## PAG-SP05-C002

State: FAIL / PARTIAL TECHNICAL ACCEPTANCE; REMEDIATED BY C003

Implementation commit:

`f9c0aaf9043f2f90c1a422e075aebcad9807ecbe`

Strict audit:

`.hiveai/audits/PAG-SP05-C002_DIFFICULTY_V1_CONTRACT_CONVERGENCE_AND_TRUSTED_COMPILATION_EVIDENCE_CLOSURE_STRICT_AUDIT.md`

Retained technical direction:

- [x] current 20..59 production dimensions;
- [x] rectangle legality independent of lane;
- [x] global 3..12 production used-color envelope;
- [x] <3 fail closed;
- [x] >12 deterministic exact weighted reduction to 12;
- [x] no new C-ID introduction;
- [x] non-minting public `from_compilation()` behavior.

## PAG-SP05-C003

State: PASS / CLOSED THROUGH C003-R01 EVIDENCE CLOSURE

Product implementation commit:

`e3605c263c495870766b6d841612b88194b35b66`

Original strict audit:

`.hiveai/audits/PAG-SP05-C003_TRUSTED_REPORT_BINDING_AND_ACCEPTANCE_EVIDENCE_CLOSURE_STRICT_AUDIT.md`

Retained product fix:

- [x] artifact/source raw SHA binding;
- [x] artifact/report raw SHA binding;
- [x] private report/artifact sealing model retained;
- [x] lane-non-transformative evidence strengthened;
- [x] explicit 13/14/15/16 over-envelope fixtures;
- [x] broad report-field tamper probes.

## PAG-SP05-C003-R01

State: PASS / CLOSED

Implementation/test-evidence commit:

`fc008dce7887a1eefbc314eab449c57355f2a942`

Builder-log publication commit:

`009fb76ce9ced264212f6827fa16a66bc4b13083`

Strict audit:

`.hiveai/audits/PAG-SP05-C003-R01_DIRECT_BINDING_PROOF_AND_PUBLICATION_EVIDENCE_CLOSURE_STRICT_AUDIT.md`

Accepted closure:

- [x] fingerprint-valid wrong-raw-SHA report constructed through private test-only helper;
- [x] forged report passes its own integrity check before artifact construction;
- [x] artifact boundary rejects the report/source raw-SHA mismatch with `INVALID_ARTIFACT`;
- [x] no public trust-minting API added;
- [x] same-lane 13/14/15/16 repeat determinism explicitly proven;
- [x] EASY/VERY_HARD lane-equivalence retained;
- [x] every 13..16 case finishes at exactly 12 used colors;
- [x] no new C-ID introduced in tested reductions;
- [x] production source unchanged by R01;
- [x] builder recorded focused/full green regressions;
- [x] zero provider calls / zero credits;
- [x] no main-game writes;
- [x] builder did not edit root `TASKS.md`;
- [x] publication evidence contains implementation SHA and push result;
- [x] ChatGPT strict audit PASS.

SP05 final state: **PASS / CLOSED**.

---

# PAG-SP06-C001 — Semantic Recognizability Gate Contract & Offline Review Foundation

State: READY_FOR_IMPLEMENTATION

Prompt:

`.hiveai/prompts/PAG-SP06-C001_SEMANTIC_RECOGNIZABILITY_GATE_CONTRACT_AND_OFFLINE_REVIEW_FOUNDATION_PROMPT.md`

Required closure:

- [ ] add a dedicated SP06 semantic-quality package outside the SP05 compiler;
- [ ] bind assessments to exact trusted LEVEL_ART artifact identity;
- [ ] compute canonical deterministic structural diagnostics from logical cells;
- [ ] cover horizontal/vertical transition counts and deterministic transition density;
- [ ] cover 4-neighbour connected components per color;
- [ ] cover singleton components;
- [ ] cover per-color cell counts and largest component sizes/shares;
- [ ] prevent unchecked caller assertions from minting trusted diagnostics;
- [ ] provide explicit UNREVIEWED / ACCEPT / REJECT recognizability disposition;
- [ ] require auditable review evidence for ACCEPT/REJECT;
- [ ] ensure UNREVIEWED never silently passes;
- [ ] keep structural diagnostics distinct from claims of semantic recognition;
- [ ] preserve accepted SP05 compiler behavior unchanged;
- [ ] keep provider execution offline and spend zero credits;
- [ ] focused and full regressions green;
- [ ] no root `TASKS.md` edit by builder;
- [ ] no main-game writes;
- [ ] ChatGPT strict audit required before C001 closure.

---

## Current Stop / Action Rule

Execute only `PAG-SP06-C001` from the published prompt.

Do not reopen accepted SP05 architecture. Do not call Magnific or PixelLab. Do not download or invoke external recognition models. Do not begin SP07+, Studio UI, weekly batching, M08/LevelData, solver or M11.

After Codex pushes C001 implementation + finalized evidence log, stop for ChatGPT strict audit.
