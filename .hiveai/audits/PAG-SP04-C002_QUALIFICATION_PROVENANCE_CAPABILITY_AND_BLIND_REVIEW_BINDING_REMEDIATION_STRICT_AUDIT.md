# PAG-SP04-C002 — Qualification Provenance, Capability & Blind-Review Binding Remediation
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. VERDICT

**FAIL**

PAG-SP04-C002 closes a large part of the C001 remediation surface: provider capability gating, Cartesian plan validation, typed/sealed SP03-derived evidence, basic raw/normalized cross-binding, stable review IDs, cost separation, and terminal summary labels are materially improved. However the qualification chain is still not safe enough to begin paid/live provider qualification.

Severity summary:

- BLOCKER: 0
- MAJOR: 5
- MINOR: 1
- NOTE: 2

SP04 live Magnific/PixelLab qualification remains blocked. No provider credits are authorized from this audit.

## 2. CONTRACT RECOVERY

Audited against:

1. root `TASKS.md` as the only current project-status tracker;
2. `.hiveai/prompts/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_PROMPT.md`;
3. `.hiveai/codex-logs/PAG-SP04-C002_QUALIFICATION_PROVENANCE_CAPABILITY_AND_BLIND_REVIEW_BINDING_REMEDIATION_CODEX_LOG.md`;
4. `.hiveai/audits/PAG-SP04-C001_SEMANTIC_QUALIFICATION_HARNESS_BENCHMARK_CORPUS_AND_COST_SAFE_PROVIDER_MATRIX_STRICT_AUDIT.md`;
5. accepted SP01 provider/request contracts;
6. accepted SP02 Magnific/PixelLab provider bridge contracts;
7. accepted SP03 typed/sealed raw and normalization contracts;
8. current `src/scrubbots_pixel_factory/semantic/qualification/models.py`;
9. current `tests/unit/test_sp04_qualification.py`;
10. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

C002 was authorized only to close the C001 qualification-integrity findings offline. It was not authorized to call providers, spend credits, start live qualification, SP05/SP06, Studio UI or M11.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder start checkpoint: `b96cf26b8777ca1893ac5fba552d535596b735bd` with local/origin divergence `0 0`.

Implementation commit: `293fc5a8fe1a8024425ddf3c3a1e30a49f7cfa44`.

Audited pre-audit `main` HEAD: `1f70de0fc62f4ac0d10af638b73fd01d86440279`.

GitHub compare from C002 start to audited terminal HEAD is ahead by four commits and changes only:

- the matching C002 builder log;
- `src/scrubbots_pixel_factory/semantic/qualification/models.py`;
- `tests/unit/test_sp04_qualification.py`.

No root tracker edit by Codex, no provider execution path, no SP01-SP03 production algorithm edit, no SP05/SP06/M11 work.

Scope discipline: **PASS**.

## 4. ACCEPTANCE CRITERIA MATRIX

| Requirement | Result | Audit assessment |
|---|---|---|
| Case REFERENCE/STYLE capability fail-closed | PASS | unsupported cells reject; BITFORGE STYLE path remains eligible |
| Exact Cartesian plan-entry validation | PASS | case/provider/attempt-domain/entry-id bindings are checked |
| Typed SP03 raw evidence | PASS | free-form constructor path is removed; checked `from_sp03()` derives from typed raw artifact |
| Typed SP03 normalization evidence | PASS | checked `from_sp03()` derives from sealed normalized artifact and report |
| Raw→normalized exact byte/source binding | PASS | raw SHA + raw artifact digest + normalization source digest are cross-checked |
| Plan-entry→attempt checked construction | PARTIAL | factory exists, but an unsealed direct PLANNED record can later mint a sealed advanced attempt through helper methods |
| Exact provider/model/workflow binding | PARTIAL | provider/workflow/version checks exist, but `model_id=None` bypasses exact model/engine equality |
| Exact case→semantic request binding | **FAIL** | plan case identity and raw semantic request are carried side-by-side but never proven to describe the same benchmark case |
| Lifecycle monotonicity | **FAIL** | helper permits backward/arbitrary lifecycle changes and non-terminal owner dispositions are not universally forbidden |
| Terminal owner-state prerequisites | **FAIL** | terminal owner status does not require a blind-review binding, and summary can consume incoherent/unsealed records |
| Blind-review stable ID join | PARTIAL | review ID↔hidden attempt join is checked, but visible subject/dimension fields are not cross-bound to that hidden attempt |
| Summary semantics | PARTIAL | accepted/rejected labels improved, but summary does not validate attempt seal/plan membership and can summarize unrelated or incoherent records |
| Cost separation | PASS | cost/usage remains outside deterministic attempt/review identity |
| Offline/security discipline | PASS | no provider/network/secret/browser execution added |
| Builder chronology start | PASS | C002 log was created before implementation edits |
| Terminal log publication truth | MINOR FAIL | log's last recorded equality is still the parent of the final log-only commit, not current terminal HEAD |
| Full regression | BUILDER PASS / AUDITOR UNVERIFIED | builder reports 481 passed; GitHub exposes no CI status/workflow run |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder reports:

- SP04 focused: 20 passed;
- SP01-SP04 focused: 100 passed;
- full repository: 481 passed;
- compileall/import/CLI/diff/offline checks passed;
- no provider calls or credit spend.

The repository supports those claims as builder evidence, and the implementation genuinely closes several C001 findings. The remaining failures are adversarial contract gaps not covered by the 20 focused tests.

One focused fixture itself exposes a key residual: `_ready_attempt(entry_index=3)` uses the same semantic request description (`wizard qualification fixture`) and same raw candidate as `_ready_attempt(entry_index=0)`, while entry index 3 belongs to the next benchmark case. The checked attempt construction accepts this because it never binds the actual `SemanticGenerationRequest` semantics to the selected `BenchmarkCase`.

## 6. FILE / SYMBOL EVIDENCE

### F-PAG-SP04-C002-001 — MAJOR — unsealed PLANNED attempt can mint a sealed advanced record

`QualificationAttemptRecord` is still publicly constructible. For `PLANNED`, `__post_init__()` does not require `_ATTEMPT_TOKEN`. `_assert_integrity()` only raises when the token *is* `_ATTEMPT_TOKEN` and the fingerprint mismatches; an unsealed record therefore passes `_assert_integrity()` silently.

`with_lifecycle()`, `with_cost_usage()` and `with_review_binding()` call `_assert_integrity()` and then `_copy_bound()`. `_copy_bound()` installs the private `_ATTEMPT_TOKEN`, validates, computes a fresh fingerprint and thereby mints a sealed record.

Consequently a caller can directly construct a syntactically populated PLANNED record with arbitrary plan/case/provider binding strings, then call `with_lifecycle(...)` and obtain a sealed advanced record without ever passing through `from_plan_entry(plan, entry, ...)`.

This violates the C002 contract that advanced lifecycle states cannot be assembled from duplicated free-form strings.

### F-PAG-SP04-C002-002 — MAJOR — benchmark case is not bound to the actual semantic request

`from_plan_entry()` binds `case_id`, `case_digest`, provider matrix and plan digest, but the request side is populated only by copying `raw_import.request_digest`.

Neither `RawImportEvidence` nor `QualificationAttemptRecord` carries the typed `SemanticGenerationRequest` or a checked qualification request binding that proves:

- request description/negative intent corresponds to the selected benchmark case;
- request output class/target dimensions correspond to the plan case;
- request provider/model/workflow corresponds to the selected provider matrix cell;
- case reference/style requirements are present in the actual request.

Therefore a raw candidate generated for one semantic subject can be attributed to a different benchmark case while all existing seals remain valid. The current test helper demonstrates this pattern by reusing a wizard request for multiple plan entries.

This invalidates provider/model comparison because the benchmark subject attribution can be wrong even when every hash is internally consistent.

### F-PAG-SP04-C002-003 — MAJOR — exact model/engine equality has a null bypass

Attempt validation performs:

`if self.raw_import.model_id is not None and self.raw_import.model_id != self.model_or_engine: reject`

If the SP03 raw artifact carries `model_id=None`, the selected qualification matrix still has an explicit model/engine, but the equality check is skipped. C002 required exact model/engine binding with no silent substitution/unknown model.

For an advanced qualification attempt, model identity must be non-null and exactly equal to the selected provider matrix model/engine unless a provider contract explicitly defines another typed identity mapping.

### F-PAG-SP04-C002-004 — MAJOR — lifecycle/owner state is not monotonic or universally coherent

`with_lifecycle()` accepts an arbitrary target lifecycle. There is no allowed-transition graph and no prohibition on moving a sealed terminal record backwards to a pre-review state.

`__post_init__()` only enforces disposition for `READY_FOR_BLIND_REVIEW`, `OWNER_ACCEPTED` and `OWNER_REJECTED`. PLANNED / RAW_PROVIDER_CAPTURED / RAW_IMPORT_VERIFIED / NORMALIZED records may carry `OWNER_ACCEPTED` or `OWNER_REJECTED` dispositions.

This violates the required monotonic lifecycle and makes owner disposition semantically inconsistent with technical state.

### F-PAG-SP04-C002-005 — MAJOR — summary/review attribution still has unchecked joins

`summarize_qualification(plan, attempts)` does not:

- call `_assert_integrity()` on every attempt;
- require `attempt.plan_digest == plan.digest()`;
- require the attempt's plan entry to exist in the supplied plan;
- reject non-terminal records carrying terminal owner dispositions.

A direct PLANNED record with `OWNER_ACCEPTED` disposition can therefore contribute an `OWNER_ACCEPTED` summary even though it has no checked raw/normalized/review chain. A valid sealed attempt from another plan can also be summarized under the supplied plan.

Separately, `MetadataBlindReviewPack.__post_init__()` binds `hidden_attempt_id` and `review_id`, but does not prove that visible `subject_label`, target dimensions or deterministic sequence correspond to the referenced hidden attempt. A coordinated reassignment of `hidden_attempt_id + review_id` can pass while stale visible metadata remains attached to the wrong hidden candidate.

This leaves owner-facing attribution weaker than the intended stable-ID contract.

## 7. FOCUSED TEST EVIDENCE

The new tests correctly cover:

- STYLE/REFERENCE capability failures;
- wrong/duplicate/missing plan cells;
- direct free-form raw/normalization evidence constructor rejection;
- several evidence-field tamper cases;
- raw workflow/model/provider-matrix tampering on sealed records;
- basic terminal lifecycle prerequisites;
- orphan/duplicate/mismatched review IDs;
- hidden-tuple reordering;
- cost-independent review identity;
- accepted/rejected terminal summary labels.

Missing adversarial sensitivity includes:

1. direct unsealed PLANNED → `with_lifecycle()` seal minting;
2. case A plan entry + case B `SemanticGenerationRequest`/raw candidate;
3. `model_id=None` against explicit provider matrix model;
4. backward lifecycle transitions;
5. terminal owner disposition on non-terminal lifecycle;
6. summary with unsealed record;
7. summary with a sealed attempt from another plan;
8. visible review metadata coordinated swap while hidden/review IDs remain internally valid.

## 8. REGRESSION EVIDENCE

Builder reports 481 total tests and 100 SP01-SP04 focused tests passing. The diff is limited to SP04 qualification code/tests/log and does not touch accepted SP01-SP03 implementations.

No GitHub-hosted CI status or workflow run exists for the audited terminal HEAD, so independent runtime replay remains unavailable from repository automation.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

No network client, browser automation, credential access, private provider endpoint or paid-provider call was introduced.

No Magnific or PixelLab credits were spent in C002.

The remaining defects are integrity/state-machine problems, not external security/credential defects.

## 10. ARCHITECTURE CONSISTENCY

Provider-neutral architecture remains intact. The correct high-level chain is still:

`BenchmarkCase / ProviderWorkflowSpec -> QualificationPlanEntry -> checked semantic request binding -> provider raw -> SP03 raw artifact -> SP03 normalized artifact -> qualification attempt -> metadata-blind review -> owner disposition`.

C002 now has strong typed evidence in the middle of that chain, but the **left-side request-to-case join** and **right-side state/review/summary joins** remain incomplete.

The next remediation should add those joins without redesigning SP01-SP03 or beginning live provider work.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Positive:

- root `TASKS.md` was not edited by Codex;
- the C002 log was created before implementation edits;
- no legacy hidden tracker was used as current authority;
- the log records failed focused-test iterations and corrections;
- provider/credit non-use is stated consistently.

Residual process MINOR:

Current GitHub `main` is `1f70de0fc62f4ac0d10af638b73fd01d86440279`, but the last equality explicitly recorded inside the committed builder log is `5e321fb76cea5b51a7205dac74d0a68cf3145e97` and the text says the final log-only commit will follow. The final commit exists, but the file does not self-record that final terminal SHA/equality. This is not a product-code blocker.

## 12. FINAL REPOSITORY STATE

Audited pre-audit `main` HEAD: `1f70de0fc62f4ac0d10af638b73fd01d86440279`.

GitHub combined status: no statuses.

GitHub workflow runs for terminal HEAD: none.

C002 code is published and the source/test diff is bounded.

## 13. OPEN CROSS-MILESTONE FINDINGS

1. Exact live private Magnific raw PNG local import/strict-decoder compatibility remains unverified.
2. Owner visual acceptance of local Magnific 2048→24 normalization remains unverified.
3. PixelLab live 24x24 qualification remains pending explicit API-secret/credit authorization.
4. SP05/M11 remain blocked.

These are not C002 defects and must not be used to broaden C003 beyond the residual qualification-contract closure.

## 14. DEFECTS BY SEVERITY

### BLOCKER

None.

### MAJOR

- `F-PAG-SP04-C002-001` — unsealed PLANNED attempt can mint a sealed advanced attempt through public helper methods.
- `F-PAG-SP04-C002-002` — benchmark case and actual semantic request are not cross-bound; semantic subject misattribution is possible.
- `F-PAG-SP04-C002-003` — explicit provider matrix model/engine can be bypassed by raw evidence with `model_id=None`.
- `F-PAG-SP04-C002-004` — lifecycle transitions and owner disposition are not monotonic/coherent.
- `F-PAG-SP04-C002-005` — summary and visible review metadata are not fully cross-bound to the supplied plan/hidden attempt.

### MINOR

- `F-PAG-SP04-C002-006` — builder log does not self-record the final log-only terminal HEAD/equality.

### NOTE

- `N-PAG-SP04-C002-001` — no GitHub CI/status evidence exists for terminal C002 HEAD.
- `N-PAG-SP04-C002-002` — `RawImportEvidence.from_sp03()` calls typed SP03 raw capture `PASS`; actual review readiness remains protected by required successful normalization, but raw-import naming/semantics should stay precise in future live qualification.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

A small sealed `QualificationRequestBinding` would simplify the remaining architecture. It should be constructed from the actual typed `SemanticGenerationRequest` plus exact plan/case/provider matrix entry and bind the request digest, semantic intent, target, provider/model/workflow and required input roles before any raw provider result is accepted into a qualification attempt.

Attempt records should preferably use checked construction for **all** states, including PLANNED, rather than maintaining an intentionally unsealed public PLANNED form that helper methods can accidentally promote.

Review visible metadata should be derived/validated from the hidden attempt's bound case and normalized target, not trusted as free-form display fields.

## 16. UNVERIFIED ITEMS

- Independent runtime replay outside builder environment: UNVERIFIED.
- GitHub-hosted CI: unavailable/no runs.
- Exact live Magnific raw PNG local decoder/import: UNVERIFIED.
- PixelLab live execution: not performed.
- Owner review of local 2048→24 Magnific normalization: not performed.

## 17. REGRESSION RISK

**MEDIUM.**

C002's typed evidence/seal work is strong and should be preserved. Risk is concentrated at cross-object joins and lifecycle state promotion. A narrow C003 can close these without touching accepted provider bridges or normalization algorithms.

## 18. AUDIT CONFIDENCE

**HIGH.**

The residual defects are visible directly in constructor/helper conditions and in the committed focused fixture behavior. They do not depend on an unavailable runtime environment or speculative provider behavior.

## 19. FINAL VERDICT

**FAIL**

C002 closes the original free-form PASS evidence weakness and several plan/review defects, but the qualification harness still permits semantic misattribution and unchecked state promotion paths that would contaminate a paid provider benchmark.

Do not begin live Magnific/PixelLab qualification yet.

## 20. REQUIRED REMEDIATION

Open one bounded C003 only.

C003 must:

1. add an exact checked benchmark-case/plan-entry ↔ typed `SemanticGenerationRequest` binding;
2. prevent any unsealed/direct PLANNED record from minting a sealed advanced attempt;
3. require explicit non-null exact model/engine identity for advanced provider qualification attempts;
4. enforce monotonic lifecycle transitions and PENDING owner disposition for all non-terminal states;
5. require terminal owner states to derive from a review-bound technically ready attempt;
6. make summary reject unsealed, incoherent, wrong-plan or unknown-entry attempts;
7. cross-bind visible review subject/target/sequence to its hidden attempt and deterministic review identity;
8. add exact adversarial sensitivity tests for each residual;
9. preserve all accepted C001/C002 corpus, provider matrix, typed SP03 evidence, cost separation and offline behavior;
10. make no provider calls, spend no credits, and do not begin SP05/SP06/M11.
