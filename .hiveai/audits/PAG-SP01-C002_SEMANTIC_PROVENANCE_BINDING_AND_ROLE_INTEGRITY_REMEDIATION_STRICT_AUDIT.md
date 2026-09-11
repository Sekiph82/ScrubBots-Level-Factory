# PAG-SP01-C002 — Semantic Provenance Binding & Role Integrity Remediation
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. VERDICT

**FAIL**

SP01-C002 materially improves the provider boundary, request/result binding, role integrity, and direct candidate validation, but one MAJOR residual remains. The standard non-success constructor does not preserve the exact request provenance required by the C002 contract, so reference/model-bearing requests cannot produce a valid typed failure through `generate_checked()`.

Severity summary:

- BLOCKER: 0
- MAJOR: 1
- MINOR: 0
- NOTE: 2

## 2. CONTRACT RECOVERY

Authoritative C002 requirements were recovered from:

- `.hiveai/prompts/PAG-SP01-C002_SEMANTIC_PROVENANCE_BINDING_AND_ROLE_INTEGRITY_REMEDIATION_PROMPT.md`
- `.hiveai/audits/PAG-SP01-C001_SEMANTIC_CONTRACTS_AND_PROVIDER_BOUNDARY_STRICT_AUDIT.md`
- `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
- `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
- `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`

C002 was required to close three C001 findings without beginning SP02:

1. bind concrete request provider intent to the executing provider;
2. bind SUCCESS and non-success candidates to the exact request/provider provenance;
3. enforce request and direct-candidate image-slot role integrity and fail-closed candidate construction.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder-reported start:

- HEAD: `b760326fc51bd858ae0a838a5d23f8e02bf0ff57`
- origin/main: same
- divergence: `0 0`

C002 implementation commit:

- `56124d692dc400c86c784edf4d0b8956b7e09090` — `Harden SP01 provenance binding and role integrity`

Builder then merged auditor-owned remote authority records non-destructively:

- merge: `6dd954dbd4cbd61843b91901fcd6bf1d131d5c36`
- completed builder-log publication: `f98b97939d5ba605344ad94f78f9d5e2e7a16a49`

Independent compare from C002 builder start to terminal builder-log HEAD shows 6 commits ahead / 0 behind. Production code changes are scoped to semantic contracts/provider, public exports, and focused SP01 tests. Auditor-owned C001 audit/C002 prompt/authority files also appear in the compare because they were published remotely during the builder run and merged as required. No M00-M10 generator algorithm file was changed.

## 4. ACCEPTANCE CRITERIA MATRIX

| Requirement | Result | Evidence |
|---|---|---|
| concrete request provider binding | PASS | `validate_request()` rejects concrete provider mismatch and permits only explicit `UNSPECIFIED` neutrality |
| provider config binding | PASS | request `provider_config_version` must match provider instance |
| request digest binding | PASS | `generate_checked()` compares result digest to `request.digest()` |
| provider id/version binding | PASS | exact result/provider comparisons exist |
| workflow binding | PASS | exact result/request workflow comparison exists |
| explicit model binding | PARTIAL / FAIL OVERALL | check exists, but normal failure constructor drops the explicit requested model |
| seed binding | PASS | exact comparison exists |
| requested dimension binding | PASS | resolved width/height compared |
| reference/style/init/color echo binding | PARTIAL / FAIL OVERALL | checks exist, but normal failure constructor drops those request echoes |
| request image-role integrity | PASS | REFERENCE/STYLE/INIT/COLOR_REFERENCE slots are enforced |
| direct candidate role integrity | PASS | accepted mappings are converted then roles are enforced |
| malformed direct candidate fields | PASS | invalid status/model/seed/retry/failure values fail closed with semantic candidate errors |
| material request identity tests | PASS | prompt/seed/dimensions/provider/workflow/model/config/reference hash covered |
| coordinated foreign-result rejection | PASS in intent, but evidence sensitivity weakened | foreign result rejected; however the baseline failure helper itself is invalid for reference/model-bearing requests |
| full regression evidence | BUILDER PASS | 417 tests reported passing |
| SP02 / Magnific integration absent | PASS | no provider-specific runtime integration introduced |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

The builder correctly claims that `generate_checked()` now checks request digest, provider identity/version, workflow, seed, dimensions, all image echoes, and explicit model identity. Repository inspection confirms those comparisons exist.

However, the builder also claims the binding is correct for success and non-success candidates. Repository truth does not fully support that claim: `SemanticImageCandidate.failure()` constructs a failure with `model_id=None` and does not echo `reference_images`, `style_image`, `init_image`, or `color_reference` from the request. For a request that explicitly selects a model and/or carries image inputs, the ordinary failure constructor therefore creates a candidate that can never satisfy the newly added binding checks.

## 6. FILE / SYMBOL EVIDENCE

`src/scrubbots_pixel_factory/semantic/provider.py` now correctly checks:

- request provider id against executing provider unless request uses explicit `UNSPECIFIED`;
- provider config version;
- result request digest;
- result provider id/version;
- workflow version;
- seed;
- resolved dimensions;
- all reference/style/init/color echoes;
- explicit requested model.

`src/scrubbots_pixel_factory/semantic/contracts.py` correctly enforces image-slot roles in both request construction and direct candidate construction.

The residual is in `SemanticImageCandidate.failure()`. It passes `None` for `model_id` and constructs no request image provenance echoes. In contrast, `SemanticImageCandidate.success()` does echo request reference/style/init/color provenance.

## 7. FOCUSED TEST EVIDENCE

Builder-reported focused result:

- `python -m pytest -q tests/unit/test_sp01_semantic_contracts.py`: **36 passed**

The expanded tests are useful, but the central mismatch parameterization is not sensitivity-safe. `BindingProvider.generate()` creates its baseline through `SemanticImageCandidate.failure(request, ...)`, while `bound_request()` contains `provider_model="model-a"` plus reference/style/init/color inputs. That unmodified baseline already disagrees with the request before any one-field mutation is applied.

Therefore many `with pytest.raises(SemanticProvenanceError)` cases can pass because of the pre-existing missing model/input echoes instead of the field supposedly under test. A focused test must first prove the unmutated reference/model-bearing failure passes `generate_checked()`, then corrupt exactly one binding.

## 8. REGRESSION EVIDENCE

Builder-reported full suite:

- `python -m pytest -q`: **417 passed**
- `python -m compileall -q src tests`: PASS
- standalone package import: PASS
- module CLI help: PASS
- installed CLI help: PASS
- offline/provider-boundary scan: PASS
- `git diff --check`: PASS apart from normal line-ending warnings

No regression in accepted M00-M10 behavior was found by source scope review.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

PASS for C002 scope.

No Magnific SDK/tool call, ComfyUI integration, network runtime, browser automation, scraping, model weights, credentials, or new external dependency were introduced. Provider neutrality remains intact.

## 10. ARCHITECTURE CONSISTENCY

The architecture remains correct:

`SemanticGenerationRequest -> SemanticGeneratorProvider -> raw SemanticImageCandidate -> future SP03 normalization`

LEVEL_ART and ASSET_ART remain separated. Raw semantic images still cannot masquerade as M08 logical-art bundles. The residual is a provenance-construction defect, not an architectural pivot failure.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Builder log is candid about start state, unrelated dirty files, remote advancement, merge/push chronology, tests, and scope. Root `TASKS.md` was not modified by Codex, consistent with current governance.

The semantic authority currently points at C002. It must not advance to SP02 until the residual below is closed.

## 12. FINAL REPOSITORY STATE

Builder reports final local HEAD == origin/main and divergence `0 0` after log publication. GitHub terminal builder-log commit is `f98b97939d5ba605344ad94f78f9d5e2e7a16a49`.

GitHub combined commit status exposes no CI statuses for this terminal SHA.

## 13. OPEN CROSS-MILESTONE FINDINGS

- M10 owner visual pack remains rejected 100/100.
- M11 remains blocked.
- SP02 Magnific bridge remains blocked until SP01 provenance boundary is fully trustworthy.

## 14. DEFECTS BY SEVERITY

### MAJOR — F-PAG-SP01-C002-001: standard non-success construction drops replay-critical request provenance

`SemanticImageCandidate.failure()` does not echo:

- explicit requested `provider_model` into `model_id`;
- `request.reference_images`;
- `request.style_image`;
- `request.init_image`;
- `request.color_reference`.

Yet `generate_checked()` correctly requires those fields to match for non-success results too. Consequently a legitimate provider failure for an explicit-model/reference-guided request cannot traverse the checked boundary as a valid typed failure. The current one-field mismatch tests are also vulnerable to false-positive passing because their baseline failure is already mismatched.

Required closure:

1. make non-success construction preserve all request-known replay/provenance fields required by `generate_checked()`;
2. add a direct test proving an unmodified explicit-model + all-image-input failure passes `generate_checked()` as a non-success result;
3. rebuild one-field mismatch tests from that proven-valid baseline and make them sensitive to the intended field, preferably asserting the typed error identifies the mismatched binding;
4. retain the coordinated foreign-result negative test;
5. rerun focused and full regression suites.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

No additional redesign is requested. Once F-PAG-SP01-C002-001 is closed, SP01 is structurally ready for a Magnific bridge. Future SP02 should keep requested model identity distinct from actual provider model identity where a provider may auto-select, but that is a later provider-adapter design detail and not a new C002 failure.

## 16. UNVERIFIED ITEMS

- No GitHub CI status exists for terminal SHA.
- Independent clean-runtime replay was not available through GitHub status evidence; builder runtime results are therefore corroborating evidence, while verdict is based primarily on repository/source/test-contract inspection.

## 17. REGRESSION RISK

Low-to-moderate. The required fix is narrow and should touch only semantic candidate failure construction and focused tests. M00-M10 production engines should remain untouched.

## 18. AUDIT CONFIDENCE

**HIGH**

The residual is directly observable from the constructor and provider binding code and is independently demonstrated by the test setup itself.

## 19. FINAL VERDICT

**FAIL**

C002 closes the original provider mismatch and role-integrity holes in principle, but non-success provenance is not yet internally constructible for the exact Magnific-style requests SP02 will need. SP02 is not authorized.

## 20. REQUIRED REMEDIATION

Execute one bounded SP01-C003 cycle only:

- repair `SemanticImageCandidate.failure()` provenance echoes;
- prove a valid explicit-model/reference-guided non-success baseline passes checked binding;
- make mismatch tests sensitivity-safe;
- preserve all existing role/provider checks;
- run focused + full regression;
- do not begin Magnific integration until independent C003 PASS.
