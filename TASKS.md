# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the only current project-status tracker for active Semantic Pixel Studio / Level Factory work. Historical implementation detail belongs in Git history, `.hiveai/prompts/`, `.hiveai/codex-logs/`, `.hiveai/audits/`, `review/` evidence and published owner-decision documents.

Only ChatGPT, acting as independent auditor/tracker owner, may promote task state or mark a cycle/milestone accepted or closed. Builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: PAG-SP07 — Reference / Style Generation
- Current Sprint: PAG-SP07-C001 — Reference / Style Generation Contract & Deterministic Plan Foundation
- Current Task: PAG-SP07-C001 — Reference / Style Generation Contract & Deterministic Plan Foundation
- Current Task Status: READY_FOR_IMPLEMENTATION
- Next Task/Action: Codex executes only PAG-SP07-C001 from the published GitHub prompt, pushes implementation/tests/finalized builder log to `main`, then stops for ChatGPT strict audit.
- Required Actor: CODEX
- Current Phase: REFERENCE_STYLE_PLANNING_FOUNDATION
- Current Prompt: `.hiveai/prompts/PAG-SP07-C001_REFERENCE_STYLE_GENERATION_CONTRACT_AND_DETERMINISTIC_PLAN_FOUNDATION_PROMPT.md`
- Previous Strict Audit: `.hiveai/audits/PAG-SP06-C002_DURABLE_REVIEW_EVIDENCE_AND_ACCEPTANCE_GATE_STRICT_AUDIT.md`
- SP06 Final Disposition: PASS / CLOSED
- SP06-C002 Implementation: `3c91bd93faf860b85f195ded421900a11be8dd7a`
- SP06-C002 Builder Log Publication: `a2b9f4ef344a5346acf89f4a3f53abc206820ddf`
- SP06-C002 Audit Commit: `fd50942bf155f9c00c1e7a7d5ca736efbfc6cd0f`
- SP05 Final Disposition: PASS / CLOSED
- Credit Policy: No Magnific or PixelLab call is authorized in SP07-C001. Spend zero provider credits.
- Blockers/Waits: Live provider execution, SP08+, Studio expansion, weekly batching, M08/LevelData bridge, solver integration and M11 remain blocked until their own explicitly authorized cycles.
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

SP05 is independently accepted and closed.

- production width and height: 20..59 inclusive, independently validated;
- rectangular boards legal;
- one logical artwork pixel = one gameplay cell;
- logical palette: C01..C16 only; BG01 remains presentation-only;
- used-color envelope: 3..12 independent of difficulty lane;
- <3 fails closed;
- >12 reduces deterministically to exactly 12 using the accepted weighted subset/remap policy;
- no new C-ID may be introduced by envelope reduction;
- reduction policy: `CELL_MAJORITY_V1`;
- palette policy: `PALETTE_SNAP_V1`;
- exact deterministic provenance required;
- trusted invariant: `report.raw_sha256 == artifact.raw_sha256 == source_provenance.raw_sha256`;
- public historical `from_compilation()` remains non-minting and recomputes canonically;
- ASSET_ART remains a separate contract.

## Accepted SP06 Quality / Recognizability Contract

SP06 is independently accepted and closed for the authorized offline scope.

Accepted flow:

`trusted LEVEL_ART artifact → deterministic structural diagnostics → explicit UNREVIEWED/ACCEPT/REJECT review → deterministic durable evidence → strict reload/recomputation → ACCEPT-only gate`

Accepted rules:

- structural diagnostics are objective grid facts, not semantic-recognition scores;
- transition density, connected components, singleton counts and color-region structure never auto-accept recognizability;
- diagnostics are recomputed from the exact trusted artifact when durable evidence is reloaded;
- imported diagnostics/identity strings are comparison evidence only, never trusted directly;
- durable evidence cross-binds artifact digest, final-grid digest, dimensions, used IDs/count, diagnostic policy, diagnostics identity, structural assessment identity, review identity and full assessment identity;
- semantic-request digest remains intent identity only, not proof of semantic understanding;
- only explicit `ACCEPT` passes the downstream gate;
- `UNREVIEWED` and `REJECT` never pass;
- no provider or external vision model is called by the SP06 gate.

## SP07 Contract Direction

SP07 begins before provider execution.

C001 must create a provider-neutral deterministic plan from one canonical `SemanticGenerationRequest` and its content-addressed REFERENCE / STYLE / INIT / COLOR_REFERENCE descriptors.

Planning rules:

- request digest is source truth;
- image content SHA/digest and role are canonical identity;
- local filesystem paths are not canonical generation identity;
- multiple inputs and variants have deterministic order/identity;
- candidate identities/seeds are deterministic;
- provider/model/workflow/config choice is bound explicitly with no silent fallback;
- C001 performs no provider call and generates no image;
- accepted SP05 compilation and SP06 review/evidence gates remain unchanged downstream.

## Milestone Overview

- [x] PAG-SP00 — Owner Rejection & Semantic Pivot Record
- [x] PAG-SP01 — Semantic Contracts & Provider Boundary
- [x] PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion
- [x] PAG-SP03 — Semantic Normalization Pipeline technical foundation
- [~] PAG-SP04 — Provider / Model / Workflow Qualification; Magnific live path qualified through accepted owner disposition, remaining comparative qualification deferred until useful/authorized
- [x] PAG-SP05 — LEVEL_ART Semantic Integration — PASS / CLOSED
- [x] PAG-SP06 — Semantic Quality / Recognizability Gate — PASS / CLOSED
- [~] PAG-SP07 — Reference / Style Generation — C001 READY_FOR_IMPLEMENTATION
- [ ] PAG-SP08 — Edit / Inpaint
- [ ] PAG-SP09 — Pixel Studio Create / Gallery UI
- [ ] PAG-SP10 — Automated Weekly Semantic Batch
- [ ] PAG-SP11 — ASSET_ART Production
- [ ] PAG-SP12 — Direction / Rotation Variants
- [ ] PAG-SP13 — Animation
- [ ] PAG-SP14 — ScrubBots Level Factory Bridge

M00–M10 remain historical accepted technical foundation except the M10 visual pack, which remains OWNER REJECTED 100/100. M11 remains blocked pending explicitly authorized semantic replacement integration.

---

# PAG-SP06 Closure Record

## PAG-SP06-C001 — Semantic Recognizability Gate Contract & Offline Review Foundation

State: PASS / CLOSED

Implementation commit: `fe77b4a36c6fc7b3b60e608f6e8d6991f0c088ec`

Final builder-log commit: `0b27ba953aee45a2ca52a91d2a16645d50c23757`

Strict audit:

`.hiveai/audits/PAG-SP06-C001_SEMANTIC_RECOGNIZABILITY_GATE_CONTRACT_AND_OFFLINE_REVIEW_FOUNDATION_STRICT_AUDIT.md`

Accepted closure:

- [x] dedicated `semantic/quality` boundary outside SP05;
- [x] deterministic transition/component/count diagnostics;
- [x] diagnostics derived from trusted artifact cells;
- [x] explicit UNREVIEWED / ACCEPT / REJECT review;
- [x] ACCEPT/REJECT require reviewer + reason;
- [x] structural diagnostics never auto-accept;
- [x] stable structural identity and review-specific full identity;
- [x] SP05 behavior preserved;
- [x] zero provider calls / zero credits;
- [x] ChatGPT strict audit PASS.

## PAG-SP06-C002 — Durable Review Evidence & Acceptance Gate

State: PASS / CLOSED

Implementation commit: `3c91bd93faf860b85f195ded421900a11be8dd7a`

Builder-log publication commit: `a2b9f4ef344a5346acf89f4a3f53abc206820ddf`

Strict audit:

`.hiveai/audits/PAG-SP06-C002_DURABLE_REVIEW_EVIDENCE_AND_ACCEPTANCE_GATE_STRICT_AUDIT.md`

Accepted closure:

- [x] deterministic versioned durable evidence;
- [x] export only from intact trusted C001 assessment;
- [x] strict canonical JSON parser and fail-closed schema handling;
- [x] reload validates exact trusted LEVEL_ART artifact;
- [x] reload recomputes C001 diagnostics rather than trusting serialized facts;
- [x] artifact/grid/dimensions/used IDs/policy/diagnostic/structural identities cross-bound;
- [x] review identity reconstructed against recomputed structural identity;
- [x] full assessment identity reverified;
- [x] artifact-A evidence rejected against artifact-B;
- [x] optional semantic-request identity preserved/checked;
- [x] only explicit ACCEPT passes;
- [x] UNREVIEWED and REJECT fail the gate;
- [x] no heuristic recognizability threshold added;
- [x] no unsafe deserialization path;
- [x] SP05/SP06-C001 regressions retained green by builder evidence;
- [x] zero provider calls / zero credits;
- [x] no root `TASKS.md` builder edit;
- [x] ChatGPT strict audit PASS.

SP06 final state: **PASS / CLOSED**.

---

# PAG-SP07-C001 — Reference / Style Generation Contract & Deterministic Plan Foundation

State: READY_FOR_IMPLEMENTATION

Prompt:

`.hiveai/prompts/PAG-SP07-C001_REFERENCE_STYLE_GENERATION_CONTRACT_AND_DETERMINISTIC_PLAN_FOUNDATION_PROMPT.md`

Required closure:

- [ ] add isolated SP07 reference/style planning boundary;
- [ ] bind exact canonical `SemanticGenerationRequest` digest;
- [ ] preserve content-addressed REFERENCE / STYLE / INIT / COLOR_REFERENCE identities;
- [ ] keep local filesystem paths out of canonical plan identity;
- [ ] deterministic input ordering and duplicate handling;
- [ ] deterministic candidate count, variant order, IDs and seeds;
- [ ] explicit provider/model/workflow/config identity with no fallback;
- [ ] immutable versioned canonical plan;
- [ ] caller assertions cannot mint trusted derived plan facts;
- [ ] preserve LEVEL_ART / ASSET_ART separation;
- [ ] no provider call or image generation;
- [ ] accepted SP05 and SP06 tests remain green;
- [ ] zero provider credits;
- [ ] no root `TASKS.md` builder edit;
- [ ] no main-game writes;
- [ ] ChatGPT strict audit required before C001 closure.

---

## Current Stop / Action Rule

Execute only `PAG-SP07-C001` from the published prompt.

Do not call Magnific or PixelLab. Do not execute provider generation. Do not reopen accepted SP05/SP06 architecture. Do not begin SP08+, Studio UI, weekly batching, M08/LevelData, solver or M11.

After Codex pushes C001 implementation + finalized builder log, stop for ChatGPT strict audit.
