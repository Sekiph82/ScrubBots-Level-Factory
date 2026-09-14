# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the only current project-status tracker for active Semantic Pixel Studio / Level Factory work. Historical implementation detail belongs in Git history, `.hiveai/prompts/`, `.hiveai/codex-logs/`, `.hiveai/audits/`, `review/` evidence and published owner-decision documents.

Only ChatGPT, acting as independent auditor/tracker owner, may promote task state or mark a cycle/milestone accepted or closed. Builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: PAG-SP07 — Reference / Style Generation
- Current Sprint: PAG-SP07-C001-R01 — Required Identity-Mutation Evidence & Process Closure
- Current Task: PAG-SP07-C001-R01 — Required Identity-Mutation Evidence & Process Closure
- Current Task Status: READY_FOR_IMPLEMENTATION
- Next Task/Action: Codex executes only PAG-SP07-C001-R01 from the published remediation prompt, pushes the test/evidence implementation and finalized R01 builder log to `main`, then stops for ChatGPT strict audit.
- Required Actor: CODEX
- Current Phase: ACCEPTANCE_EVIDENCE_REMEDIATION
- Current Prompt: `.hiveai/prompts/PAG-SP07-C001-R01_REQUIRED_IDENTITY_MUTATION_EVIDENCE_AND_PROCESS_CLOSURE_PROMPT.md`
- Previous Strict Audit: `.hiveai/audits/PAG-SP07-C001_REFERENCE_STYLE_GENERATION_CONTRACT_AND_DETERMINISTIC_PLAN_FOUNDATION_STRICT_AUDIT.md`
- SP07-C001 Disposition: CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED
- SP07-C001 Implementation: `f55a1064fb8ccf24163cc8d3e815adb7e782674f`
- SP07-C001 Builder Log Publication: `8f7552e24f859550bbf21d9aaeb4f19b1e081077`
- SP07-C001 Audit Commit: `24f408d67253da740c4320cd562fe17d98c50173`
- SP06 Final Disposition: PASS / CLOSED
- SP05 Final Disposition: PASS / CLOSED
- Credit Policy: No Magnific or PixelLab call is authorized in SP07-C001-R01. Spend zero provider credits.
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
- diagnostics are recomputed from the exact trusted artifact when durable evidence is reloaded;
- imported diagnostics/identity strings are comparison evidence only, never trusted directly;
- semantic-request digest remains intent identity only, not proof of semantic understanding;
- only explicit `ACCEPT` passes the downstream gate;
- `UNREVIEWED` and `REJECT` never pass;
- no provider or external vision model is called by the SP06 gate.

## Retained SP07-C001 Planning Contract

The current C001 product implementation is retained pending R01 acceptance-evidence closure.

Retained behavior:

- isolated `semantic/generation` provider-neutral planning boundary;
- exact canonical `SemanticGenerationRequest` digest is source truth;
- REFERENCE / STYLE / INIT / COLOR_REFERENCE inputs remain content-addressed and role-correct;
- local filesystem paths are excluded from canonical image identity under the existing descriptor contract;
- REFERENCE request order is preserved, followed by explicit STYLE / INIT / COLOR_REFERENCE ordering;
- duplicate REFERENCE `(role, content_sha256)` is rejected explicitly;
- candidate count, order and candidate IDs are deterministic;
- variant seeds use the project `DeterministicRNG` convention;
- provider/model/workflow/config identity is explicit and no fallback is introduced;
- LEVEL_ART / ASSET_ART separation remains intact;
- C001 performs no provider call, image upload or image generation;
- accepted SP05 compilation and SP06 review/evidence gates remain unchanged downstream.

Important dependency distinction:

- candidate identity binds canonical request identity;
- variant seed values are derived from canonical request seed + ordinal;
- therefore changing reference content or init strength must change request/plan/candidate identity, but does not by itself require a seed-value change when the canonical seed is unchanged.

## Milestone Overview

- [x] PAG-SP00 — Owner Rejection & Semantic Pivot Record
- [x] PAG-SP01 — Semantic Contracts & Provider Boundary
- [x] PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion
- [x] PAG-SP03 — Semantic Normalization Pipeline technical foundation
- [~] PAG-SP04 — Provider / Model / Workflow Qualification; remaining comparative qualification deferred until useful/authorized
- [x] PAG-SP05 — LEVEL_ART Semantic Integration — PASS / CLOSED
- [x] PAG-SP06 — Semantic Quality / Recognizability Gate — PASS / CLOSED
- [~] PAG-SP07 — Reference / Style Generation — C001 CHANGES_REQUIRED / PRODUCT RETAINED; C001-R01 READY_FOR_IMPLEMENTATION
- [ ] PAG-SP08 — Edit / Inpaint
- [ ] PAG-SP09 — Pixel Studio Create / Gallery UI
- [ ] PAG-SP10 — Automated Weekly Semantic Batch
- [ ] PAG-SP11 — ASSET_ART Production
- [ ] PAG-SP12 — Direction / Rotation Variants
- [ ] PAG-SP13 — Animation
- [ ] PAG-SP14 — ScrubBots Level Factory Bridge

M00–M10 remain historical accepted technical foundation except the M10 visual pack, which remains OWNER REJECTED 100/100. M11 remains blocked pending explicitly authorized semantic replacement integration.

---

# PAG-SP07-C001 — Reference / Style Generation Contract & Deterministic Plan Foundation

State: **CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Implementation commit:

`f55a1064fb8ccf24163cc8d3e815adb7e782674f`

Builder-log publication commit:

`8f7552e24f859550bbf21d9aaeb4f19b1e081077`

Strict audit:

`.hiveai/audits/PAG-SP07-C001_REFERENCE_STYLE_GENERATION_CONTRACT_AND_DETERMINISTIC_PLAN_FOUNDATION_STRICT_AUDIT.md`

Retained technical work:

- [x] dedicated SP07 planning package outside SP05/SP06;
- [x] canonical request digest binding;
- [x] content-addressed role-correct input bindings;
- [x] local paths excluded from canonical identity;
- [x] deterministic input order and explicit duplicate-reference handling;
- [x] deterministic candidate count/order/IDs and project-RNG seeds;
- [x] provider/model/workflow/config identity without fallback;
- [x] immutable/versioned/sealed plan values;
- [x] public construction/replace cannot mint derived plan facts;
- [x] LEVEL_ART / ASSET_ART separation retained;
- [x] no provider execution / zero credits;
- [x] accepted SP05/SP06 source untouched by C001 diff.

Open acceptance-evidence defects:

- [ ] literal REFERENCE content-SHA mutation test must prove changed request + plan identity;
- [ ] literal INIT-strength-only mutation test must prove changed request + plan identity;
- [ ] R01 must create its builder log before any R01 edit, preserving the original C001 process-order incident as historical evidence.

---

# PAG-SP07-C001-R01 — Required Identity-Mutation Evidence & Process Closure

State: **READY_FOR_IMPLEMENTATION**

Prompt:

`.hiveai/prompts/PAG-SP07-C001-R01_REQUIRED_IDENTITY_MUTATION_EVIDENCE_AND_PROCESS_CLOSURE_PROMPT.md`

Required closure:

- [ ] R01 builder log exists before R01 edits;
- [ ] REFERENCE content-SHA mutation changes canonical request digest;
- [ ] REFERENCE content-SHA mutation changes plan digest/canonical bytes;
- [ ] changed REFERENCE binding identity is proven directly;
- [ ] INIT-strength-only mutation changes canonical request digest;
- [ ] INIT-strength-only mutation changes plan digest/canonical bytes;
- [ ] changed INIT strength is preserved exactly in plan;
- [ ] tests preserve the distinction between candidate identity and project-RNG seed derivation;
- [ ] no production redesign unless a literal new test exposes a genuine defect;
- [ ] focused/combined/full regressions green;
- [ ] zero Magnific/PixelLab calls and zero credits;
- [ ] no root `TASKS.md` builder edit;
- [ ] no main-game writes;
- [ ] finalized R01 log records implementation commit SHA and push result;
- [ ] ChatGPT strict audit required before C001 closure.

---

## Current Stop / Action Rule

Execute only `PAG-SP07-C001-R01` from the published remediation prompt.

Do not call Magnific or PixelLab. Do not execute provider generation. Do not redesign the retained SP07 planning architecture unless a literal remediation test proves a product defect. Do not reopen accepted SP05/SP06 architecture. Do not begin SP08+, Studio UI, weekly batching, M08/LevelData, solver or M11.

After Codex pushes C001-R01 test/evidence implementation + finalized builder log, stop for ChatGPT strict audit.
