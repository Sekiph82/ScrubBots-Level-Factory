# PAG-SP04-C003 — Request-to-Case Binding, Attempt Seal & Review Attribution Closure
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. VERDICT

**FAIL**

PAG-SP04-C003 closes most of the C002 residual contract surface. Request-to-case/provider binding, attempt construction integrity, exact raw model matching once raw evidence exists, non-terminal owner-disposition coherence, plan-bound summaries, and visible review attribution are materially stronger. Two MAJOR gaps still prevent live/paid qualification: terminal owner disposition can be reached using an arbitrary caller-supplied review string rather than proof of deterministic metadata-blind review entry, and `RAW_PROVIDER_CAPTURED` can be represented without any typed provider-capture/raw-model evidence.

Severity summary:

- BLOCKER: 0
- MAJOR: 2
- MINOR: 1
- NOTE: 2

SP04 live Magnific/PixelLab qualification remains blocked. No provider credits are authorized from this audit.

## 2. CONTRACT RECOVERY

Audited against:

1. root `TASKS.md` as the only current project-status tracker;
2. `.hiveai/prompts/PAG-SP04-C003_REQUEST_TO_CASE_BINDING_ATTEMPT_SEAL_AND_REVIEW_ATTRIBUTION_CLOSURE_PROMPT.md`;
3. `.hiveai/codex-logs/PAG-SP04-C003_REQUEST_TO_CASE_BINDING_ATTEMPT_SEAL_AND_REVIEW_ATTRIBUTION_CLOSURE_CODEX_LOG.md`;
4. `.hiveai/audits/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_STRICT_AUDIT.md`;
5. accepted SP01 semantic request/provider contracts;
6. accepted SP02 provider bridge/result contracts;
7. accepted SP03 typed/sealed raw and normalization contracts;
8. current SP04 qualification source/tests on GitHub `main`;
9. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

C003 was an offline remediation cycle only. It was not authorized to call providers, spend credits, begin live qualification, SP05/SP06, Studio UI, weekly batches or M11.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder-reported starting repository checkpoint: `1f70de0fc62f4ac0d10af638b73fd01d86440279`.

Scoped implementation/test/log commit: `453a47ff5e95ae397163b564e1be9815a95c5799`.

Authority merge commit: `e9fdbf9514cd0204c500f715519b9afce68c24d4`.

Audited pre-audit `main` HEAD: `b60bc66481fe74e0b942398b89e21f6cd228d690` (`Publish SP04 C003 builder log`).

GitHub compare from the entering checkpoint to audited terminal HEAD is ahead by six commits and contains the expected concurrent ChatGPT authority files plus C003 changes. Product implementation scope is limited to:

- `src/scrubbots_pixel_factory/semantic/qualification/models.py`;
- `src/scrubbots_pixel_factory/semantic/qualification/__init__.py`;
- `tests/unit/test_sp04_qualification.py`;
- matching C003 builder log.

No provider execution code, SP03 normalization algorithm, root tracker edit by Codex, SP05/SP06/M11 implementation, or sibling game-repository edit was introduced by the C003 implementation.

Scope discipline: **PASS**.

## 4. ACCEPTANCE CRITERIA MATRIX

| Requirement | Result | Audit assessment |
|---|---|---|
| Exact request→benchmark case binding | PASS | sealed `QualificationRequestBinding` checks description, negative intent, category, target, provider, model, workflow/config and input requirements |
| Request digest→raw evidence binding | PASS | attempt requires raw request digest to equal sealed request binding digest |
| Explicit raw model binding once raw evidence exists | PASS | `raw_import.model_id` must exactly equal matrix model/engine; `None` no longer bypasses this check |
| Unsealed-attempt seal minting | PASS | helpers call `_assert_integrity()` and cannot promote ordinary direct records |
| Non-terminal disposition coherence | PASS | PLANNED through READY require pending owner review |
| Backward lifecycle transitions | PASS | public lifecycle helper rejects backward movement and terminal transitions |
| Terminal owner state requires review proof | **FAIL** | terminal state requires only a non-null free-form `review_item_id`; arbitrary strings pass |
| `RAW_PROVIDER_CAPTURED` model/provenance evidence | **FAIL** | state can be created with no capture/raw evidence, therefore no returned provider model identity is proven |
| Summary plan membership | PASS | summary checks seal, plan digest, exact entry/provider/case/request binding and unique entry use |
| Visible review attribution | PASS | deterministic ID/sequence/subject/target are cross-checked against hidden attempt |
| Review tuple reorder safety | PASS | hidden attribution is ID-based |
| Cost separation | PASS | operational cost stays outside deterministic attempt/review binding identity |
| C003 builder-log-before-edit requirement | **FAIL (process)** | log admits it was absent and recreated after prior product changes already existed in worktree |
| Offline/no-credit discipline | PASS | no provider call or credit spend reported or visible in scoped code |
| Full regression | BUILDER PASS / AUDITOR UNVERIFIED | builder reports 486 full tests; no GitHub CI status/workflow exists |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder reports:

- SP04 focused: 24 passed;
- SP01-SP04 focused: 105 passed;
- full repository: 486 passed;
- compileall/import/CLI/diff checks passed;
- no Magnific/PixelLab call or credit spend.

Repository source and focused tests substantiate the request-binding, attempt-seal, plan-summary and review-attribution improvements. The remaining MAJOR findings are also directly visible in current tests: terminal lifecycle tests deliberately use arbitrary strings such as `review-fixed`, `review-accepted`, and `review-rejected` as sufficient review proof.

No contradictory CI evidence exists because GitHub exposes no status checks/workflow runs for terminal C003 HEAD.

## 6. FILE / SYMBOL EVIDENCE

### Request binding

`QualificationRequestBinding.from_plan_entry()` now binds a typed `SemanticGenerationRequest` to the exact validated plan entry. It requires ASSET_ART, exact dimensions, provider ID, non-null exact model/engine, workflow/config version, description, negative description, semantic category and reference/style presence to agree with the benchmark case/provider cell.

This closes the C002 defect where a wizard request could be attached to another benchmark case.

### Attempt seal

`QualificationAttemptRecord._assert_integrity()` now rejects records without `_ATTEMPT_TOKEN`; all public mutation helpers assert integrity before copying. Direct public PLANNED records therefore cannot mint a valid seal through `with_lifecycle()` or `_copy_bound()` in ordinary API use.

### Raw model exactness

When `raw_import` exists, current code requires `raw_import.model_id == self.model_or_engine` exactly. The previous `model_id is not None` bypass is removed.

### Review attribution

`MetadataBlindReviewPack.__post_init__()` derives expected order and review ID from hidden attempts and review seed, then validates visible sequence, review ID, subject and target dimensions against the exact hidden record.

### Residual terminal-review defect

`with_review_binding(review_item_id)` accepts any non-empty string. `__post_init__()` for OWNER_ACCEPTED/OWNER_REJECTED checks only that `review_item_id is not None`. No sealed review-entry object, review seed, expected deterministic review ID or successful pack construction is required for terminal disposition.

The committed tests explicitly demonstrate the bypass by using arbitrary values such as `review-fixed`, `review-accepted`, and `review-rejected` before transitioning to terminal owner states.

### Residual RAW_PROVIDER_CAPTURED defect

`from_plan_entry(..., lifecycle=RAW_PROVIDER_CAPTURED)` does not require `raw_import` or another typed provider-capture evidence object. Raw evidence becomes mandatory only at `RAW_IMPORT_VERIFIED` and later. Therefore the state called RAW_PROVIDER_CAPTURED can exist with only intended request model identity, not returned/captured provider model/result identity.

## 7. FOCUSED TEST EVIDENCE

Positive C003 test coverage now includes:

1. exact request binding and wrong description/model refusal;
2. unsealed attempt promotion refusal;
3. backward lifecycle refusal;
4. non-terminal owner-disposition refusal;
5. foreign-plan summary refusal;
6. visible review subject/target tamper refusal;
7. coordinated hidden-ID/review-ID swap refusal.

Residual sensitivity gaps:

1. no test proves an arbitrary review string cannot authorize terminal OWNER_ACCEPTED/OWNER_REJECTED; current tests prove the opposite;
2. no test proves RAW_PROVIDER_CAPTURED requires typed capture evidence and a non-null returned provider model identity.

## 8. REGRESSION EVIDENCE

Builder reports 486 repository tests and 105 SP01-SP04 focused tests passing. The implementation diff is localized to SP04 qualification contracts/exports/tests and does not rewrite accepted provider/normalization algorithms.

Independent clean-checkout replay was attempted by the auditor but the audit container could not resolve `github.com`, so runtime replay could not start.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

No network execution, provider secret read, browser automation or paid provider call was added in C003.

Construction seals remain local invariant mechanisms, not security credentials. The residual review issue is an authorization/integrity problem inside the qualification state machine: an arbitrary caller string can currently stand in for proof of metadata-blind review entry.

## 10. ARCHITECTURE CONSISTENCY

Provider-neutral architecture is preserved. Request binding sits above accepted SP01/SP02 contracts and typed evidence continues to reuse SP03 rather than duplicating a weaker image-provenance system.

The remaining fixes can stay fully inside the SP04 qualification layer. No SP01-SP03 redesign is justified.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Codex did not edit root `TASKS.md` or self-mark SP04 accepted.

However the builder log states that the required C003 log was missing during the run and was recreated after product changes were already visible in the resumed worktree. This does not satisfy the explicit C003 requirement that the matching builder log exist before any C003 implementation edit.

The log also records reading legacy hidden tracker/control-plane files while saying they were not used as current authority. This did not alter product truth, but those files should not be part of the next cycle's authority pass.

The final log correctly identifies the pre-log-only source/test checkpoint and does not falsely call that SHA the current remote HEAD. Current GitHub `main` is the later log-only commit `b60bc66481fe74e0b942398b89e21f6cd228d690`.

## 12. FINAL REPOSITORY STATE

Audited pre-audit remote `main`: `b60bc66481fe74e0b942398b89e21f6cd228d690`.

GitHub exposes no combined statuses and no workflow runs for this SHA.

Remote publication is visible. Final builder-local equality after the final log-only commit is not independently observable from GitHub and remains unverified by this audit.

## 13. OPEN CROSS-MILESTONE FINDINGS

1. Exact owner-approved Magnific private raw PNG has still not been exercised through the local strict SP03 decoder/import path.
2. Owner has not yet reviewed the local deterministic 2048→24 SP03 normalized result against the accepted provider-produced 24x24 derivative.
3. PixelLab live qualification remains pending later authorization/credential conditions.
4. SP05 and M11 remain blocked.

These are expected later SP04 gates, not additional C003 code defects.

## 14. DEFECTS BY SEVERITY

### BLOCKER

None.

### MAJOR

**F-PAG-SP04-C003-001 — Terminal owner disposition accepts arbitrary review strings.**

`with_review_binding()` accepts any non-empty caller-supplied string and terminal lifecycle validation only requires the string to be non-null. Therefore OWNER_ACCEPTED/OWNER_REJECTED can be minted without deterministic review-seed binding or proof that a valid `MetadataBlindReviewPack` ever contained the candidate. This violates the explicit C003 terminal prerequisite that review binding prove entry into the metadata-blind review protocol.

Required closure: terminal attempts must carry checked/sealed deterministic review-entry evidence derived from the exact ready attempt plus review seed/protocol, not a free-form string.

**F-PAG-SP04-C003-002 — RAW_PROVIDER_CAPTURED does not prove captured provider model/result identity.**

A trusted attempt can be constructed directly at `RAW_PROVIDER_CAPTURED` with no raw/capture evidence. The plan/request binding proves intended model/engine, but not the model/result actually returned by the provider. C003 explicitly required raw provider model identity to be present and exact for RAW_PROVIDER_CAPTURED or later.

Required closure: introduce typed/sealed provider-capture evidence derived from a successful typed provider candidate/result, or fail closed on RAW_PROVIDER_CAPTURED until equivalent capture evidence exists. Bind provider/model/version/workflow/request/result identity and cross-bind later raw import when both exist.

### MINOR

**F-PAG-SP04-C003-003 — Required builder log did not precede C003 product edits.**

The builder log itself admits it was recreated after prior C003 product changes were already present. The next remediation cycle must create its log first and maintain chronology from the start.

### NOTE

**N-PAG-SP04-C003-001:** no GitHub CI/status evidence exists for terminal C003 HEAD.

**N-PAG-SP04-C003-002:** independent clean-checkout replay could not run because the audit container could not resolve `github.com`.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

A small sealed `QualificationReviewBinding`/`ReviewEntryEvidence` would make the owner-review state machine cleaner than treating `review_item_id` as both display identifier and proof. It can bind review seed, deterministic review ID, attempt pre-review digest, subject and target dimensions without coupling cost or owner disposition into image identity.

Likewise, a small `ProviderCaptureEvidence` derived from `SemanticImageCandidate` can distinguish `RAW_PROVIDER_CAPTURED` from `RAW_IMPORT_VERIFIED` truthfully. This avoids misusing `RawImportEvidence`, which correctly means local SP03 import compatibility has already been verified.

## 16. UNVERIFIED ITEMS

- Independent runtime test replay: UNVERIFIED due audit-container DNS failure.
- GitHub-hosted CI: unavailable/no runs.
- Builder-local HEAD equality after final log-only commit: not independently observable.
- Live Magnific raw-byte local import: not yet performed.
- PixelLab live execution: not performed.

## 17. REGRESSION RISK

**LOW-MEDIUM for the required C004 remediation.**

The remaining issues are localized state/evidence contracts. They should not require changes to provider adapters, SP03 normalization, benchmark corpus, cost separation, or existing procedural generation infrastructure.

## 18. AUDIT CONFIDENCE

**HIGH** for both MAJOR findings because they are directly visible in current source and tests rather than inferred from missing runtime evidence.

Confidence in the rest of C003 closure is also high from static contract inspection. Runtime regression confidence is lower because independent execution was unavailable.

## 19. FINAL VERDICT

**FAIL**

C003 materially improves SP04 but does not yet authorize live/paid qualification.

Closed from C002: request-to-case binding, unsealed-attempt promotion, exact model comparison once raw evidence exists, plan-bound summaries, non-terminal owner coherence, and visible review attribution.

Still open: deterministic review-entry proof for terminal owner disposition and truthful RAW_PROVIDER_CAPTURED evidence.

## 20. REQUIRED REMEDIATION

Open one narrow C004 cycle only.

C004 must:

1. replace free-form terminal review proof with checked/sealed deterministic review-entry evidence;
2. require truthful typed provider-capture evidence for RAW_PROVIDER_CAPTURED or otherwise disallow that state until such evidence exists;
3. cross-bind provider capture to later raw import when both are present;
4. add adversarial tests proving arbitrary review IDs and capture-without-model/result are rejected;
5. preserve C003 request/case binding, attempt seals, summary checks and review-card attribution;
6. create the builder log before any implementation edit;
7. remain fully offline with zero provider credit spend.

Do not begin live provider qualification, SP05/SP06 or M11 until C004 receives independent PASS.