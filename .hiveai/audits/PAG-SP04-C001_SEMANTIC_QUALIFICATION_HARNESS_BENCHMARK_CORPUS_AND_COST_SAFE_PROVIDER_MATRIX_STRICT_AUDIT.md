# PAG-SP04-C001 — Semantic Qualification Harness, Benchmark Corpus & Cost-Safe Provider Matrix
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. VERDICT

**FAIL**

PAG-SP04-C001 establishes a useful offline qualification skeleton, but the current contracts do not yet fail closed strongly enough for paid/live qualification. The benchmark corpus, explicit provider matrix, finite plan construction, cost separation and offline discipline are good. However four MAJOR contract defects remain in plan capability enforcement, SP03 evidence authenticity/binding, attempt lifecycle provenance, and metadata-blind review binding.

Severity summary:

- BLOCKER: 0
- MAJOR: 4
- MINOR: 2
- NOTE: 2

SP04 live qualification remains blocked. No Magnific/PixelLab credit spend is authorized from this audit.

## 2. CONTRACT RECOVERY

Audited against:

1. root `TASKS.md` as the only current project-status tracker;
2. `.hiveai/prompts/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_PROMPT.md`;
3. `.hiveai/codex-logs/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_CODEX_LOG.md`;
4. `.hiveai/audits/PAG-SP03-C003_PROVENANCE_SEAL_AND_CONSTRUCTION_INTEGRITY_CLOSURE_STRICT_AUDIT.md`;
5. accepted SP01 provider-neutral contracts;
6. accepted SP02 Magnific/PixelLab provider bridges;
7. accepted SP03 raw/normalization typed contracts and construction seals;
8. `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`;
9. `review/m10/M10_OWNER_REVIEW_DECISION.md`;
10. current GitHub `main` source and tests.

C001 was an infrastructure/evidence-schema-only cycle. It was not authorized to call providers, spend credits, select a default provider/model/workflow, begin SP05/SP06, build Studio UI or begin M11.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder start checkpoint: `2adf2b21671f3bcdb2733f03d61e894dd762c37a`.

Implementation commit: `9b644f77d2062500f0beaec55a63d1eaad0da747`.

Authority merge commit: `a87b5ee325432ea82fad8e283a3ed227b4ddcebb`.

Final builder-log commit and audited pre-audit `main` HEAD: `13fe4d5bccbd6ff37c1e067e16bc838ebe13676a`.

GitHub compare from builder start to audited terminal HEAD is ahead by six commits and contains the expected concurrent ChatGPT authority commits plus the SP04 implementation/log scope. The C001 implementation itself changes only:

- `.hiveai/codex-logs/PAG-SP04-C001_..._CODEX_LOG.md`;
- `src/scrubbots_pixel_factory/__init__.py`;
- `src/scrubbots_pixel_factory/semantic/__init__.py`;
- `src/scrubbots_pixel_factory/semantic/qualification/__init__.py`;
- `src/scrubbots_pixel_factory/semantic/qualification/models.py`;
- `tests/unit/test_sp04_qualification.py`.

No provider execution path, SP03 algorithm, M08/M09/M10 artifact, sibling ScrubBots repository, or root tracker edit was introduced by Codex.

Scope breadth: **PASS**.

## 4. ACCEPTANCE CRITERIA MATRIX

| Requirement | Result | Audit assessment |
|---|---|---|
| Versioned recognizable benchmark corpus | PASS | 15 required subject classes present with stable case IDs |
| 24x24 ASSET_ART baseline without LEVEL_ART rules | PASS | output class enforced as ASSET_ART; no C01..C16 coupling |
| Explicit MAGNIFIC / PIXELLAB matrix | PASS | Magnific `recraft-v4-1`, PixelLab PIXFLUX and BITFORGE represented |
| Unknown/unpinned provider/model fail closed | PARTIAL | spec construction is guarded, but plan construction ignores per-case capability requirements |
| Finite offline qualification plan | PASS | explicit bounded attempts, default 45 entries |
| No provider call during plan construction | PASS | implementation imports contracts only; focused test monkeypatches provider execution |
| Real-provider compatibility gate | **FAIL** | PASS evidence is self-asserted data rather than checked construction from SP03 typed artifacts |
| Exact raw/import → normalized provenance | **FAIL** | raw SHA is checked, but local raw-artifact digest/workflow/model chain is not fully cross-bound |
| Metadata-blind review package | PARTIAL | visible metadata is clean, but stable-ID one-to-one binding is not invariant-checked |
| Owner disposition separate from technical state | PARTIAL | fields are separate, but terminal owner states can bypass raw-import PASS prerequisite |
| Cost/usage separate from deterministic identity | PASS | cost changes do not change attempt digest |
| Missing cost remains unknown | PASS | nullable values remain null |
| Positive/negative evidence references | PASS | repository references only, no private raster/URL material |
| Technical summary/gate | **FAIL** | owner-accepted/rejected terminal attempts can summarize as `NO_READY_CANDIDATES` |
| Offline/security constraints | PASS | no provider/network/secret/browser execution added |
| Full regression evidence | BUILDER PASS / AUDITOR UNVERIFIED | builder reports 473 passed; no GitHub CI run/status exists |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder reports:

- focused SP04: 11 passed;
- SP01-SP04 focused: 92 passed;
- full repository: 473 passed in 232.72s;
- compileall/import/CLI/diff/offline scans passed;
- no provider calls or credits.

The repository supports those implementation claims at a structural level, but the focused suite does not test several adversarial states required by the prompt. In particular it proves the happy-path builder output rather than proving fail-closed behavior against incompatible case/spec cells, self-asserted PASS evidence, terminal lifecycle bypass, malformed direct review-pack construction, or terminal summary semantics.

GitHub exposes no combined statuses and no workflow runs for terminal HEAD `13fe4d5...`.

## 6. FILE / SYMBOL EVIDENCE

Primary audited implementation:

`src/scrubbots_pixel_factory/semantic/qualification/models.py`

Key observations:

- `BenchmarkCase` carries `requires_reference` and `requires_style`.
- `ProviderWorkflowSpec` carries `supports_reference` and `supports_style`.
- `build_qualification_plan()` creates the Cartesian product of every selected case and every selected provider spec without comparing those requirement/capability flags.
- `RawImportEvidence` and `NormalizationEvidence` are ordinary public dataclasses whose PASS/digest fields are caller-supplied.
- `QualificationAttemptRecord` checks provider ID and optionally provider version, but does not bind `raw_import.workflow_version` to `attempt.workflow_version`; raw evidence has no model field to bind against `model_or_engine`.
- normalization binding compares `normalization.raw_import_sha256` to `raw_import.raw_sha256`, but does not bind the normalization source raw-artifact digest to `raw_import.local_raw_artifact_digest`.
- raw-import PASS is enforced only for `READY_FOR_BLIND_REVIEW`, not for `RAW_IMPORT_VERIFIED`, `NORMALIZED`, `OWNER_ACCEPTED` or `OWNER_REJECTED`.
- `MetadataBlindReviewPack.__post_init__()` checks tuple lengths and uniqueness only. It does not prove that each `item.hidden_attempt_id` exists in `hidden_attempts`, nor that each review ID is bound to the corresponding hidden attempt.
- `build_metadata_blind_review_pack()` derives review IDs from the pre-binding attempt digest and then mutates hidden attempt identity by adding `review_item_id` through `replace()`.
- `summarize_qualification()` computes `NO_READY_CANDIDATES` whenever `READY_FOR_BLIND_REVIEW` count is zero before considering terminal owner-accepted/rejected states.

## 7. FOCUSED TEST EVIDENCE

The committed focused tests positively cover corpus completeness, default provider matrix, finite planning, offline planning, basic raw SHA binding, metadata hiding, cost separation and evidence references.

Missing sensitivity tests include at minimum:

1. style-required case + PIXFLUX must fail plan construction;
2. reference-required case + a matrix cell with `supports_reference=False` must fail plan construction;
3. fabricated arbitrary 64-hex PASS evidence must not be sufficient to reach review-ready state;
4. exact SP03 `SemanticRawArtifact.digest()` must bind to normalization source raw-artifact digest;
5. raw workflow mismatch must fail;
6. raw model/result provenance mismatch must fail where model identity is available;
7. `OWNER_ACCEPTED`/`OWNER_REJECTED` with raw compatibility FAIL/NOT_ATTEMPTED must fail;
8. malformed direct `MetadataBlindReviewPack` with mismatched stable IDs must fail;
9. review-pack reconstruction must preserve stable IDs without self-referential digest drift;
10. owner-accepted terminal records must not summarize as `NO_READY_CANDIDATES`.

## 8. REGRESSION EVIDENCE

Builder-reported regression:

- 92 SP01-SP04 focused tests passed;
- 473 full repository tests passed;
- post-merge focused SP04 rerun passed;
- compileall/import/CLI/diff checks passed.

Independent execution in the audit container could not be performed because the audit environment could not resolve `github.com`, and GitHub has no Actions run/status for the terminal SHA. Therefore runtime replay is marked UNVERIFIED rather than contradicted.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

**PASS for C001 execution safety.**

No Magnific/PixelLab provider execution, browser automation, private endpoint, credential read or credit spend was added. Cost/usage metadata is separated from deterministic attempt identity. No private signed URL or Magnific creation identifier appears in the new evidence references.

The remaining failures are contract-integrity failures, not secret/network-safety failures.

## 10. ARCHITECTURE CONSISTENCY

The broad architecture is directionally correct:

`BenchmarkCase -> ProviderWorkflowSpec -> QualificationPlan -> Raw/Normalization Evidence -> Blind Review -> Owner Disposition -> QualificationSummary`

The problem is that the current joins between those stages are not yet sealed strongly enough. Earlier SP01-SP03 work deliberately hardened exact provenance against coordinated mutation. C001 reintroduces a softer, caller-asserted evidence layer above those sealed artifacts. SP04 must consume the accepted SP03 typed artifacts rather than replacing their verified chain with untrusted strings.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Root `TASKS.md` remains the current tracker and was not edited by Codex.

Builder disclosed a chronology violation: SP04 source/test files were briefly created before the required builder log existed, then removed/restored before the log was created. Because the prompt explicitly required the log **before any C001 source/test/doc edit**, this remains a process MINOR even though it was disclosed and reverted.

The final builder log records `a87b5ee...` as its publication checkpoint; the repository then advanced to `13fe4d5...` solely to commit the finalized builder log. This is not a production-scope defect, but the audited terminal SHA is therefore `13fe4d5...`, not `a87b5ee...`.

## 12. FINAL REPOSITORY STATE

Audited pre-audit `main` HEAD: `13fe4d5bccbd6ff37c1e067e16bc838ebe13676a`.

Current C001 implementation is committed on `main`; no evidence of provider credit use exists in the diff/log. GitHub reports no CI statuses/workflow runs for that SHA.

Because this audit is FAIL, root `TASKS.md` must move to a bounded SP04-C002 remediation cycle. SP04 live generation remains blocked.

## 13. OPEN CROSS-MILESTONE FINDINGS

The following previously carried qualification inputs remain open and are **not** defects in C001 by themselves:

1. exact private Magnific raw PNG local decoder/import compatibility is still unverified;
2. local 2048→24 `AREA_AVERAGE_V1` visual quality is not owner-qualified;
3. PixelLab live smoke remains pending authorized secret/access conditions.

These live gates must not begin until the C001 contract defects are closed.

## 14. DEFECTS BY SEVERITY

### BLOCKER

None.

### MAJOR

#### F-PAG-SP04-C001-001 — Plan construction ignores case capability requirements

`BenchmarkCase.requires_reference/requires_style` and `ProviderWorkflowSpec.supports_reference/supports_style` exist, but `build_qualification_plan()` never compares them. A style-required case can therefore be paired with PIXFLUX, and a reference-required case can be paired with a matrix cell that explicitly says reference is unsupported.

This directly violates the C001 requirement that unsupported provider capability combinations fail closed **when constructing a qualification plan** and leaves the required BitForge STYLE plan test unproven.

#### F-PAG-SP04-C001-002 — Real-provider compatibility evidence is self-asserted instead of checked from SP03 typed artifacts

`RawImportEvidence` and `NormalizationEvidence` accept caller-supplied digests and `PASS` compatibility. The focused test itself constructs review-ready evidence from arbitrary repeated hex strings rather than from a real/synthetic `SemanticRawArtifact` and `SemanticNormalizedArtifact` produced by SP03.

Therefore the harness can claim `READY_FOR_BLIND_REVIEW` without proving that exact bytes were decoded/normalized by SP03. This violates the central C001 real-provider compatibility gate.

Remediation must construct or validate PASS evidence from the accepted SP03 typed/sealed objects, not from free-form digest strings alone.

#### F-PAG-SP04-C001-003 — Attempt lifecycle and exact cross-provenance binding are incomplete

The current attempt contract does not bind all replay-critical facts:

- `raw_import.workflow_version` is not compared with `attempt.workflow_version`;
- raw import evidence has no model identity to compare with `attempt.model_or_engine`;
- normalization binds only raw SHA, not `RawImportEvidence.local_raw_artifact_digest` to the normalization source raw-artifact digest;
- `RAW_IMPORT_VERIFIED`, `NORMALIZED`, `OWNER_ACCEPTED` and `OWNER_REJECTED` do not require raw-import compatibility PASS.

Consequently an `OWNER_ACCEPTED` record can be constructed with raw compatibility FAIL/NOT_ATTEMPTED so long as other fields are syntactically present. A same-byte/different-provenance raw artifact can also evade the intended local raw-artifact binding because raw SHA alone is insufficient to encode provider provenance.

#### F-PAG-SP04-C001-004 — Blind-review stable-ID binding is not enforced as an invariant

`MetadataBlindReviewPack.__post_init__()` verifies only equal tuple lengths and uniqueness. It does not assert that visible item `hidden_attempt_id` values exactly match hidden attempt IDs, or that review IDs are bound to the intended hidden records.

A directly constructed malformed pack can therefore pass validation while its visible-to-hidden mapping is false. That recreates the class of binding weakness previously closed in M10.

Additionally, review IDs are derived from the attempt digest before `review_item_id` is injected into the hidden attempt, while `review_item_id` itself participates in attempt identity. This makes the final hidden attempt digest differ from the digest used to derive the review ID. The binding source must be an immutable pre-review fingerprint that does not change when the review link is installed.

### MINOR

#### F-PAG-SP04-C001-005 — Qualification summary misclassifies terminal owner states

`summarize_qualification()` chooses `NO_READY_CANDIDATES` whenever the count of `READY_FOR_BLIND_REVIEW` records is zero before considering owner-accepted/rejected records. A set containing only `OWNER_ACCEPTED` records therefore reports an owner-accepted count while the gate status says `NO_READY_CANDIDATES`.

The summary/gate must represent terminal owner states coherently.

#### F-PAG-SP04-C001-006 — Builder log was not literally created before all C001 edits

The builder explicitly reports a preflight mistake that briefly created source/test files before the log was created. The changes were reverted and disclosed, so this is process-only and does not invalidate the code by itself.

### NOTE

- N-PAG-SP04-C001-001: GitHub exposes no CI statuses/workflow runs for terminal SHA `13fe4d5...`.
- N-PAG-SP04-C001-002: independent pytest replay was unavailable in the audit environment due external DNS resolution failure; builder-reported test counts remain uncontradicted but independently UNVERIFIED.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Prefer checked constructors/factories that accept `SemanticRawArtifact`, `SemanticNormalizationRequest` and `SemanticNormalizedArtifact` directly, deriving qualification evidence from their accepted sealed identity methods. This avoids building a second weaker provenance system from strings.

For review binding, define a stable immutable `pre_review_attempt_digest` or equivalent identity that explicitly excludes mutable review-link/cost/owner fields. Derive review IDs from that identity and enforce exact set/mapping equality in the pack constructor.

For plan integrity, validate every entry against its referenced case and provider matrix cell, including capability requirements and attempt index domain, rather than validating only the entry count.

## 16. UNVERIFIED ITEMS

- Independent execution of 473-test full suite: UNVERIFIED.
- GitHub-hosted CI: unavailable/no runs.
- Exact live Magnific raw PNG import: not performed by design.
- PixelLab live execution: not performed by design.
- Owner review of local Magnific normalization: not performed.

## 17. REGRESSION RISK

**MEDIUM-HIGH if C001 were used for live paid qualification now.**

The implementation is offline and does not itself spend credits, but the weak joins could cause future paid attempts to be planned against unsupported capabilities, allow fabricated/misbound normalization evidence into review, or break visible-to-hidden review attribution. Those are exactly the areas that need to be trustworthy before live provider comparison begins.

## 18. AUDIT CONFIDENCE

**HIGH for the static contract findings.**

The failures follow directly from current constructor/validation code and do not depend on provider behavior. Confidence is lower only for runtime regression counts because independent execution was unavailable and GitHub provides no CI run.

## 19. FINAL VERDICT

**FAIL**

C001 is not accepted as the live-qualification foundation yet.

Positive work retained:

- benchmark corpus;
- provider-neutral qualification domain model;
- explicit Magnific/PixelLab matrix baseline;
- finite offline plans;
- cost/usage separation;
- evidence references;
- no-credit/offline discipline.

Required next step is a bounded **PAG-SP04-C002** remediation focused only on capability fail-closed planning, typed SP03 evidence binding, lifecycle/cross-provenance integrity, blind-review stable binding and summary correctness.

## 20. REQUIRED REMEDIATION

Open `PAG-SP04-C002 — Qualification Provenance, Capability & Blind-Review Binding Remediation`.

C002 must, at minimum:

1. reject selected case/provider cells whose required reference/style capabilities are not supported;
2. add positive BitForge STYLE-plan coverage and negative PIXFLUX STYLE/reference capability sensitivity tests;
3. derive PASS raw/normalization qualification evidence from actual typed SP03 raw/normalized artifacts or an equivalently sealed checked-construction path;
4. bind local raw-artifact digest, raw SHA, provider id/version/workflow/model/request/result identity and normalization source/request/output chain exactly;
5. require raw-import PASS for `RAW_IMPORT_VERIFIED` and every later lifecycle state;
6. require normalization PASS for `NORMALIZED` and every later lifecycle state;
7. bind attempts to exact plan entry/case/provider matrix identity rather than free-form duplicate strings;
8. make blind-review item↔hidden-attempt mapping fail closed by stable ID under direct construction/replacement, not by tuple position;
9. derive review IDs from an identity that does not change when the review link is installed;
10. correct terminal qualification summary semantics;
11. add adversarial focused tests for every finding;
12. preserve offline/no-provider/no-credit scope and the accepted SP01-SP03 contracts.

Do not begin live Magnific/PixelLab qualification, SP05, SP06, Studio UI or M11 until C002 receives independent PASS.