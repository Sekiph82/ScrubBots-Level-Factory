# ScrubBots Semantic Pixel Studio — Canonical GitHub Task State

This root `TASKS.md` is the **only current project-status tracker**. Historical cycle detail remains in Git history, `.hiveai/audits/`, `.hiveai/codex-logs/`, review evidence and published project documents.

Only ChatGPT, acting as independent auditor/tracker owner, may mark tasks or milestones accepted/closed. Codex builder logs are implementation evidence, never acceptance.

## Project Status

- Current Milestone: **PAG-SP04 — Semantic Provider / Model / Workflow Qualification**
- Current Phase: **LIVE QUALIFICATION EVIDENCE**
- Current Task Status: **READY_FOR_LIVE_EVIDENCE**
- Required Actor: **CHATGPT / OWNER**
- Closing Offline Cycle: `PAG-SP04-C004` → **PASS / CLOSED**
- Closing C004 Audit: `.hiveai/audits/PAG-SP04-C004_REVIEW_ENTRY_PROOF_AND_PROVIDER_CAPTURE_EVIDENCE_CLOSURE_STRICT_AUDIT.md`
- Previous Milestone: `PAG-SP03 — Semantic Normalization Pipeline` → **PASS / CLOSED FOR CURRENT TECHNICAL FOUNDATION**
- Existing Live Smoke Evidence: `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`
- Owner Decision: **Magnific wizard visual direction accepted; 24x24 px accepted as first ASSET_ART baseline target**
- Next Task/Action: **Recover/capture the exact existing Magnific smoke raw bytes without generating a new image if possible; prove local SP03 import/decoder compatibility; normalize locally to 24x24; present result metadata-blind for owner review.**
- Credit Policy: **Do not spend additional provider credits unless owner explicitly authorizes a new paid generation. Prefer the existing Magnific smoke creation first.**
- Blockers/Waits: **SP05 and M11 remain blocked** until live SP04 qualification evidence is accepted. PixelLab live qualification remains pending authorized secret/credit conditions.
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
- Owner accepted the visual direction and exact 24x24 provider-produced derivative.
- Exact private raw Magnific PNG local strict-decoder/import proof is the current qualification task.
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
- [~] PAG-SP04 — Semantic Provider / Model / Workflow Qualification — **offline contract foundation PASS; live evidence active**
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

# PAG-SP04 — Offline Qualification Cycle History

## C001 — Semantic Qualification Harness, Benchmark Corpus & Cost-Safe Provider Matrix

State: **FAIL / REMEDIATED**

Strict audit:
`.hiveai/audits/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_STRICT_AUDIT.md`

Retained foundation:

- [x] versioned 15-subject benchmark corpus;
- [x] 24x24 ASSET_ART baseline;
- [x] explicit Magnific / PIXFLUX / BITFORGE qualification matrix;
- [x] finite bounded offline plan;
- [x] cost/usage separation;
- [x] metadata-blind review concept;
- [x] public positive/negative evidence references.

## C002 — Qualification Provenance, Capability & Blind-Review Binding Remediation

State: **FAIL / REMEDIATED**

Strict audit:
`.hiveai/audits/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_STRICT_AUDIT.md`

Accepted closure retained:

- [x] provider capability gating;
- [x] Cartesian plan-entry integrity;
- [x] typed/sealed SP03 raw and normalization evidence;
- [x] raw/normalized provenance binding;
- [x] stable review identity and cost separation.

## C003 — Request-to-Case Binding, Attempt Seal & Review Attribution Closure

State: **FAIL / REMEDIATED IN C004**

Strict audit:
`.hiveai/audits/PAG-SP04-C003_REQUEST_TO_CASE_BINDING_ATTEMPT_SEAL_AND_REVIEW_ATTRIBUTION_CLOSURE_STRICT_AUDIT.md`

Accepted closure retained:

- [x] exact `QualificationRequestBinding` from benchmark case/provider cell to typed request;
- [x] exact request provider/model/workflow/config/description/category/target binding;
- [x] trusted attempt construction seal and monotonic lifecycle;
- [x] non-terminal pending owner disposition;
- [x] exact plan-bound summary;
- [x] visible review subject/target/sequence attribution.

## C004 — Review Entry Proof & Provider Capture Evidence Closure

State: **PASS / CLOSED**

Strict audit:
`.hiveai/audits/PAG-SP04-C004_REVIEW_ENTRY_PROOF_AND_PROVIDER_CAPTURE_EVIDENCE_CLOSURE_STRICT_AUDIT.md`

Builder reported:

- 26 SP04 focused tests passed;
- 107 SP01-SP04 focused tests passed;
- 488 full repository tests passed;
- compile/import/CLI/diff/offline checks passed;
- no provider calls or credit spend.

Independent technical acceptance:

- [x] SP04-C004-001 Free-form review strings cannot mint terminal owner proof.
- [x] SP04-C004-002 Sealed `QualificationReviewBinding` binds exact pre-review attempt, plan/case, normalized artifact/hash, request binding, typed review seed and expected review ID.
- [x] SP04-C004-003 Review pack emits hidden attempts carrying sealed review-entry evidence.
- [x] SP04-C004-004 Review IDs remain deterministic/idempotent and cost-independent.
- [x] SP04-C004-005 Sealed `ProviderCaptureEvidence` derives from accepted typed successful candidate or accepted raw-import provenance.
- [x] SP04-C004-006 Provider capture binds non-null model, provider/version/workflow/request/result identity, returned dimensions, raw SHA and input provenance.
- [x] SP04-C004-007 `RAW_PROVIDER_CAPTURED` and every later lifecycle require checked provider-capture evidence.
- [x] SP04-C004-008 Capture evidence is cross-bound to local raw import on exact provider result/request/model/SHA/dimensions.
- [x] SP04-C004-009 C003 request/case binding, attempt seal, lifecycle, summary and review attribution remain intact.
- [x] SP04-C004-010 No provider execution or credit spend occurred.
- [~] MINOR process debt: C004 builder read legacy hidden `.hiveai` control-plane files despite explicit instruction not to use/read them for current task authority. No technical acceptance impact; future builders must avoid this.

No C005 offline remediation cycle is authorized.

---

# PAG-SP04 — Live Qualification Gates

Current sequence:

- [ ] **SP04-Q01** Recover/capture the exact existing Magnific smoke raw bytes locally and compute immutable SHA-256. Prefer reuse of existing creation; no new paid generation unless owner authorizes it.
- [ ] **SP04-Q02** Prove exact live Magnific raw media/chunk profile is accepted by the current SP03 strict decoder/import boundary. If it fails, open evidence-driven compatibility remediation only.
- [ ] **SP04-Q03** Normalize the exact real Magnific raw candidate locally to **24x24** using accepted deterministic normalization and record full provenance.
- [ ] **SP04-Q04** Present the local normalized 24x24 result metadata-blind for owner review and compare it with the already accepted provider-produced 24x24 derivative.
- [ ] **SP04-Q05** Run PixelLab exact-size 24x24 qualification only when owner authorizes live API use and `PIXELLAB_SECRET` is available.
- [ ] **SP04-Q06** Compare eligible PIXFLUX / BITFORGE paths against Magnific using the same benchmark/review protocol.
- [ ] **SP04-Q07** Select any default provider/model/workflow only from technical evidence plus owner visual acceptance.

No default production provider/model/workflow is selected yet.

---

## Current Stop / Action Rule

**Do not start another Codex remediation cycle.**

Next action belongs to ChatGPT/owner live-evidence workflow. First attempt to reuse the existing Magnific smoke creation without spending additional credits. SP05, SP06 production gating and M11 remain blocked until SP04 live evidence is reviewed and accepted.
