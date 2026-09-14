# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the only current project-status tracker for active Semantic Pixel Studio / Level Factory work. Historical implementation detail belongs in Git history, `.hiveai/prompts/`, `.hiveai/codex-logs/`, `.hiveai/audits/`, `review/` evidence and published owner-decision documents.

Only ChatGPT, acting as independent auditor/tracker owner, may promote task state or mark a cycle/milestone accepted or closed. Builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: PAG-SP06 — Semantic Quality / Recognizability Gate
- Current Sprint: PAG-SP06-C002 — Durable Review Evidence & Acceptance Gate
- Current Task: PAG-SP06-C002 — Durable Review Evidence & Acceptance Gate
- Current Task Status: READY_FOR_IMPLEMENTATION
- Next Task/Action: Codex executes only PAG-SP06-C002 from the published GitHub prompt, pushes implementation/tests/finalized builder log to `main`, then stops for ChatGPT strict audit.
- Required Actor: CODEX
- Current Phase: DURABLE_REVIEW_EVIDENCE_AND_GATE
- Current Prompt: `.hiveai/prompts/PAG-SP06-C002_DURABLE_REVIEW_EVIDENCE_AND_ACCEPTANCE_GATE_PROMPT.md`
- Previous Strict Audit: `.hiveai/audits/PAG-SP06-C001_SEMANTIC_RECOGNIZABILITY_GATE_CONTRACT_AND_OFFLINE_REVIEW_FOUNDATION_STRICT_AUDIT.md`
- SP06-C001 Disposition: PASS / CLOSED
- SP06-C001 Implementation: `fe77b4a36c6fc7b3b60e608f6e8d6991f0c088ec`
- SP06-C001 Final Builder Log: `0b27ba953aee45a2ca52a91d2a16645d50c23757`
- SP06-C001 Audit Commit: `57af8cafa83e20dd78317f6313f6a6db27e99b35`
- SP05 Final Disposition: PASS / CLOSED
- Credit Policy: No Magnific or PixelLab call is authorized in SP06-C002. Spend zero provider credits.
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

## Accepted SP06-C001 Contract

SP06-C001 is independently accepted.

Accepted flow:

`trusted LEVEL_ART artifact → deterministic structural diagnostics → UNREVIEWED assessment → explicit auditable ACCEPT/REJECT review`

Accepted rules:

- structural diagnostics are objective grid facts, not semantic-recognition scores;
- transition density, component counts, singleton counts and color-region sizes never auto-accept recognizability;
- diagnostics are derived from trusted row-major C-ID cells and are deterministic/canonical;
- assessments bind trusted artifact digest, final-grid digest, dimensions, used IDs/count, diagnostics policy and diagnostic identity;
- recognizability disposition is explicit `UNREVIEWED`, `ACCEPT`, or `REJECT`;
- ACCEPT/REJECT require non-empty reviewer and reason evidence;
- `passes`/`accepted` is true only for explicit ACCEPT bound to the same structural assessment identity;
- changing review disposition changes full assessment identity while structural diagnostics identity remains unchanged;
- no provider, vision model or external recognition service is called by this gate.

C002 must preserve this separation while adding durable/reloadable review evidence. Persisted evidence must be reverified against the exact trusted artifact rather than trusted as serialized assertions.

## Milestone Overview

- [x] PAG-SP00 — Owner Rejection & Semantic Pivot Record
- [x] PAG-SP01 — Semantic Contracts & Provider Boundary
- [x] PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion
- [x] PAG-SP03 — Semantic Normalization Pipeline technical foundation
- [~] PAG-SP04 — Provider / Model / Workflow Qualification; Magnific live path qualified through accepted owner disposition, remaining comparative qualification deferred until useful/authorized
- [x] PAG-SP05 — LEVEL_ART Semantic Integration — PASS / CLOSED
- [~] PAG-SP06 — Semantic Quality / Recognizability Gate — C001 PASS / CLOSED; C002 READY_FOR_IMPLEMENTATION
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

## PAG-SP05-C003 / C003-R01

State: PASS / CLOSED

Product implementation commit:

`e3605c263c495870766b6d841612b88194b35b66`

R01 implementation/test-evidence commit:

`fc008dce7887a1eefbc314eab449c57355f2a942`

R01 builder-log publication commit:

`009fb76ce9ced264212f6827fa16a66bc4b13083`

Final strict audit:

`.hiveai/audits/PAG-SP05-C003-R01_DIRECT_BINDING_PROOF_AND_PUBLICATION_EVIDENCE_CLOSURE_STRICT_AUDIT.md`

Accepted closure:

- [x] report/artifact/source raw SHA cross-binding;
- [x] private report/artifact sealing retained;
- [x] direct fingerprint-valid wrong-raw-SHA adversarial proof;
- [x] lane-non-transformative evidence;
- [x] deterministic 13/14/15/16 over-envelope reduction evidence;
- [x] no public trust-minting API;
- [x] zero provider calls / zero credits.

SP05 final state: **PASS / CLOSED**.

---

# PAG-SP06-C001 — Semantic Recognizability Gate Contract & Offline Review Foundation

State: PASS / CLOSED

Implementation commit:

`fe77b4a36c6fc7b3b60e608f6e8d6991f0c088ec`

Final builder-log commit:

`0b27ba953aee45a2ca52a91d2a16645d50c23757`

Strict audit:

`.hiveai/audits/PAG-SP06-C001_SEMANTIC_RECOGNIZABILITY_GATE_CONTRACT_AND_OFFLINE_REVIEW_FOUNDATION_STRICT_AUDIT.md`

Accepted closure:

- [x] dedicated `semantic/quality` package outside SP05 compiler;
- [x] exact trusted LEVEL_ART artifact integrity required;
- [x] canonical deterministic structural diagnostics from logical cells;
- [x] exact horizontal/vertical transitions and integer density evidence;
- [x] four-neighbour components per C-ID;
- [x] singleton components;
- [x] per-color counts and largest component sizes/shares;
- [x] unchecked public caller assertions cannot mint trusted diagnostics;
- [x] explicit UNREVIEWED / ACCEPT / REJECT review contract;
- [x] ACCEPT/REJECT require auditable reviewer + reason evidence;
- [x] UNREVIEWED never passes;
- [x] structural diagnostics remain distinct from semantic-recognition claims;
- [x] structural identity stable across review disposition while full review identity changes;
- [x] SP05 compiler files unchanged by C001 delta;
- [x] builder-reported focused/combined/full regressions green;
- [x] zero provider calls / zero credits;
- [x] no root `TASKS.md` builder edit;
- [x] ChatGPT strict audit PASS.

---

# PAG-SP06-C002 — Durable Review Evidence & Acceptance Gate

State: READY_FOR_IMPLEMENTATION

Prompt:

`.hiveai/prompts/PAG-SP06-C002_DURABLE_REVIEW_EVIDENCE_AND_ACCEPTANCE_GATE_PROMPT.md`

Required closure:

- [ ] add deterministic versioned durable SP06 review evidence;
- [ ] export only from an intact trusted C001 assessment;
- [ ] deterministic repeated export bytes/digest;
- [ ] strict checked reload against the exact trusted LEVEL_ART artifact;
- [ ] recompute C001 structural diagnostics during reload rather than trust serialized facts;
- [ ] cross-bind artifact digest, final-grid digest, dimensions, used IDs/count and diagnostic policy;
- [ ] cross-bind diagnostics facts/digest and structural assessment identity;
- [ ] reconstruct and reverify review identity against the recomputed structural identity;
- [ ] reverify full assessment identity;
- [ ] reject malformed/unsupported schemas and tampered fields;
- [ ] reject artifact A evidence against artifact B;
- [ ] preserve/check optional canonical semantic-request identity when present;
- [ ] add explicit acceptance gate where only ACCEPT succeeds;
- [ ] UNREVIEWED and REJECT never pass the gate;
- [ ] add no heuristic structural recognizability threshold;
- [ ] add no public trust-minting or unsafe deserialization shortcut;
- [ ] SP06-C001 focused tests remain green;
- [ ] SP05 focused tests remain green;
- [ ] zero Magnific/PixelLab calls and zero credits;
- [ ] no root `TASKS.md` builder edit;
- [ ] no main-game writes;
- [ ] ChatGPT strict audit required before C002 closure.

---

## Current Stop / Action Rule

Execute only `PAG-SP06-C002` from the published prompt.

Do not reopen accepted SP05 or SP06-C001 architecture. Do not call Magnific or PixelLab. Do not download or invoke external recognition models. Do not add heuristic semantic-recognition thresholds. Do not begin SP07+, Studio UI, weekly batching, M08/LevelData, solver or M11.

After Codex pushes C002 implementation + finalized evidence log, stop for ChatGPT strict audit.
