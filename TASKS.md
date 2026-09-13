# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical cycle detail remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, review evidence and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP04 — Semantic Provider / Model / Workflow Qualification**
- Current Sprint: **PAG-SP04-C003**
- Current Task: **Request-to-Case Binding, Attempt Seal & Review Attribution Closure**
- Current Task Status: **READY_FOR_IMPLEMENTATION**
- Required Actor: **CODEX**
- Previous Cycle: `PAG-SP04-C002` → **FAIL / 5 MAJOR + 1 MINOR**
- Previous Strict Audit: `.hiveai/audits/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_STRICT_AUDIT.md`
- Current Prompt: `.hiveai/prompts/PAG-SP04-C003_REQUEST_TO_CASE_BINDING_ATTEMPT_SEAL_AND_REVIEW_ATTRIBUTION_CLOSURE_PROMPT.md`
- Previous Milestone: `PAG-SP03 — Semantic Normalization Pipeline` → **PASS / CLOSED FOR CURRENT TECHNICAL FOUNDATION**
- Live Smoke Evidence: `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`
- Owner Decision: **Magnific wizard visual direction accepted; 24x24 px accepted as first ASSET_ART baseline target**
- Next Task/Action: Execute SP04-C003 only, close the remaining qualification request/state/review binding defects, publish builder log/tests, commit/push `main`, then stop for independent ChatGPT audit.
- Blockers/Waits: **SP04 live provider generation, SP05 and M11 remain blocked** until C003 receives independent PASS. No provider credits are authorized in C003.
- Approved Semantic Providers: **MAGNIFIC**, **PIXELLAB**
- Provider Architecture: **provider-neutral; explicit provider/model/engine selection; no silent fallback**
- Tracking Repository: `Sekiph82/ScrubBots-Level-Factory`
- Tracking Branch: `main`
- Canonical Local Repository: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Owner-Locked Contracts

### LEVEL_ART

Unchanged:

- EASY: width/height independently 20–29
- MEDIUM: 30–39
- HARD: 40–49
- VERY_HARD: 50–59
- rectangular boards allowed
- one logical artwork pixel = one gameplay cell
- C01..C16 logical palette only
- EASY 3–5 distinct used colors
- MEDIUM 6–7
- HARD 8–9
- VERY_HARD 10–12
- BG01 `#202533` presentation/background only
- no interpolation/antialiasing inside logical cells
- deterministic provenance/export required
- final LEVEL_ART semantic normalization remains blocked until SP05 integration.

### ASSET_ART

- Separate from LevelData/difficulty legality.
- **24x24 px is the first owner-approved baseline target.**
- 24x24 is not the only future ASSET_ART size.
- C01..C16 is not automatically forced on ASSET_ART.
- Current normalization baseline palette policy: `PRESERVE_SOURCE_RGBA`.

## Provider Decisions

### MAGNIFIC

- Approved semantic provider while owner credits are available.
- External owner-authorized orchestration only.
- Live `recraft-v4-1` wizard smoke generated successfully.
- Owner accepted the visual direction and exact 24x24 derivative.
- Exact private raw Magnific PNG local strict-decoder/import proof is still a later SP04 live qualification gate.
- Local `AREA_AVERAGE_V1` 2048→24 visual result is not yet owner-qualified.

### PIXELLAB

- Official Developer API / Python SDK provider remains approved.
- Direct network execution is opt-in only.
- `PIXELLAB_SECRET` remains runtime-only and must never enter Git/logs/manifests.
- PixelLab exact-size 24x24 remains strategically important for later provider comparison.

---

# Milestone Overview

- [x] PAG-SP00 — Owner Rejection & Semantic Pivot Record
- [x] PAG-SP01 — Semantic Contracts & Provider Boundary
- [x] PAG-SP02 — Magnific + PixelLab Provider Bridges & Result Ingestion
- [x] PAG-SP03 — Semantic Normalization Pipeline technical foundation
- [~] PAG-SP04 — Semantic Provider / Model / Workflow Qualification — C003 active
- [ ] PAG-SP05 — LEVEL_ART Semantic Integration
- [ ] PAG-SP06 — Semantic Quality / Recognizability Gate
- [ ] PAG-SP07 — Reference / Style Generation
- [ ] PAG-SP08 — Edit / Inpaint
- [ ] PAG-SP09 — Pixel Studio Create / Gallery UI
- [ ] PAG-SP10 — Automated Weekly Semantic Batch
- [ ] PAG-SP11 — ASSET_ART Production
- [ ] PAG-SP12 — Direction / Rotation Variants
- [ ] PAG-SP13 — Animation
- [ ] PAG-SP14 — ScrubBots Level Factory Bridge

M00–M10 remain historical accepted technical foundation except the M10 visual pack, which remains **OWNER REJECTED 100/100**. M11 remains blocked pending semantic replacement acceptance.

---

# PAG-SP04 — Qualification Cycle History

## C001 — Semantic Qualification Harness, Benchmark Corpus & Cost-Safe Provider Matrix

State: **FAIL / REMEDIATED IN C002 WITH RESIDUALS**

Strict audit:
`.hiveai/audits/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_STRICT_AUDIT.md`

Retained foundation:

- [x] versioned 15-subject benchmark corpus;
- [x] 24x24 ASSET_ART baseline;
- [x] explicit Magnific / PIXFLUX / BITFORGE qualification matrix;
- [x] finite bounded offline plan;
- [x] cost/usage separation;
- [x] metadata-blind review concept;
- [x] public positive/negative evidence references;
- [x] no provider call / no credit spend.

## C002 — Qualification Provenance, Capability & Blind-Review Binding Remediation

State: **FAIL / C003 REQUIRED**

Strict audit:
`.hiveai/audits/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_STRICT_AUDIT.md`

Builder reported:

- 20 SP04 focused tests passed;
- 100 SP01-SP04 focused tests passed;
- 481 full repository tests passed;
- compile/import/CLI/offline checks passed;
- no provider calls or credit spend.

Accepted C002 closure:

- [x] case REFERENCE/STYLE capability gating against provider matrix;
- [x] exact Cartesian plan-entry integrity checks;
- [x] typed/sealed `RawImportEvidence.from_sp03()`;
- [x] typed/sealed `NormalizationEvidence.from_sp03()`;
- [x] raw SHA + raw artifact + normalization source/report/RGBA binding;
- [x] provider/workflow/version binding improvements;
- [x] stable review-ID concept independent of cost/owner/review link;
- [x] accepted/rejected summary labels no longer collapse automatically to NO_READY;
- [x] C002 builder log created before implementation edits.

C002 residual findings:

- [!] `F-PAG-SP04-C002-001` **MAJOR** — a directly constructed unsealed PLANNED attempt can use public helper methods to mint a sealed advanced record without validated plan-entry origin.
- [!] `F-PAG-SP04-C002-002` **MAJOR** — selected benchmark case is not exactly bound to the actual typed `SemanticGenerationRequest`; semantic subject misattribution is possible.
- [!] `F-PAG-SP04-C002-003` **MAJOR** — explicit matrix model/engine equality can be bypassed when raw evidence carries `model_id=None`.
- [!] `F-PAG-SP04-C002-004` **MAJOR** — lifecycle transitions and owner disposition are not fully monotonic/coherent.
- [!] `F-PAG-SP04-C002-005` **MAJOR** — summary and visible review metadata are not fully cross-bound to supplied plan/hidden attempt.
- [~] `F-PAG-SP04-C002-006` **MINOR process** — final log-only terminal SHA/equality is not self-recorded inside the log; product source scope remains published.

---

# PAG-SP04-C003 — Request-to-Case Binding, Attempt Seal & Review Attribution Closure

State: **READY_FOR_IMPLEMENTATION**

Authoritative prompt:
`.hiveai/prompts/PAG-SP04-C003_REQUEST_TO_CASE_BINDING_ATTEMPT_SEAL_AND_REVIEW_ATTRIBUTION_CLOSURE_PROMPT.md`

Required closure:

- [ ] SP04-C003-001 Add checked plan/case/provider-matrix ↔ typed `SemanticGenerationRequest` binding.
- [ ] SP04-C003-002 Bind request semantic intent, target, provider, model/engine, workflow/config and required reference/style roles exactly.
- [ ] SP04-C003-003 Require raw request digest to equal checked qualification request binding digest target.
- [ ] SP04-C003-004 Make trusted attempts checked-construction-only or otherwise prevent any unsealed record from minting a trusted seal.
- [ ] SP04-C003-005 Make `dataclasses.replace()` unable to mint/reset attempt seal.
- [ ] SP04-C003-006 Require non-null exact raw model/engine equality for advanced provider attempts.
- [ ] SP04-C003-007 Enforce monotonic lifecycle transitions; forbid backward/terminal escape transitions.
- [ ] SP04-C003-008 Require PENDING owner disposition for every non-terminal lifecycle state.
- [ ] SP04-C003-009 Require terminal owner state to derive from exact review-bound technically ready candidate.
- [ ] SP04-C003-010 Make summary reject unsealed, incoherent, wrong-plan and unknown-entry attempts.
- [ ] SP04-C003-011 Cross-bind visible review subject/target/sequence to exact hidden attempt and deterministic review ID.
- [ ] SP04-C003-012 Add coordinated review-misattribution sensitivity tests.
- [ ] SP04-C003-013 Preserve C002 typed SP03 evidence, capability gating, plan integrity and cost separation.
- [ ] SP04-C003-014 SP01-SP04 focused + full regression + compile/import/CLI/offline/security checks green.
- [ ] SP04-C003-015 No provider execution, credits, live qualification, SP05/SP06/UI/M11.

## Qualification gates blocked until C003 independent PASS

- [ ] SP04-Q01 Capture exact live Magnific raw bytes locally and compute immutable SHA-256.
- [ ] SP04-Q02 Prove exact live Magnific raw file is accepted by SP03 decoder/import boundary.
- [ ] SP04-Q03 Normalize real Magnific raw candidate locally to 24x24 and present metadata-blind for owner review.
- [ ] SP04-Q04 Compare local normalized Magnific result with accepted provider-produced 24x24 derivative.
- [ ] SP04-Q05 Run PixelLab exact-size 24x24 qualification only when authorized API secret/credit conditions are available.
- [ ] SP04-Q06 Compare PIXFLUX / eligible BITFORGE against Magnific using same benchmark/review protocol.
- [ ] SP04-Q07 Select default provider/model/workflow only from technical evidence + owner visual acceptance.

No default production provider/model/workflow is selected yet.

---

## Current Stop Rule

Execute **PAG-SP04-C003 only**.

Do not call Magnific or PixelLab. Do not spend credits. Do not begin live SP04 qualification, SP05, SP06, Studio UI or M11. Codex must not edit `TASKS.md`, must create the matching C003 builder log before any implementation edit, commit/push `main`, verify final local HEAD == origin/main divergence `0 0`, then stop for independent ChatGPT audit.
