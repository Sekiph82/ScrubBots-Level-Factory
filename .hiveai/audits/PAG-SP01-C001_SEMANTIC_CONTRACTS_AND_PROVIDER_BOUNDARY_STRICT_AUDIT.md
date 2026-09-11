# PAG-SP01-C001 — Semantic Contracts & Provider Boundary
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. VERDICT

**FAIL**

SP01 establishes the correct provider-neutral semantic layer and preserves the accepted M00-M10 core, but the provider/result boundary is not yet provenance-safe enough to authorize SP02 Magnific integration.

## 2. CONTRACT RECOVERY

Audited authority:

- `.hiveai/prompts/PAG-SP01-C001_SEMANTIC_CONTRACTS_AND_PROVIDER_BOUNDARY_PROMPT.md`
- `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`
- `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`
- `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md`
- `review/m10/M10_OWNER_REVIEW_DECISION.md`
- historical M00-M10 contracts in root `TASKS.md`

SP01 is contract-only. Magnific generation, normalization and Studio UI are intentionally out of scope.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder implementation commit: `a7185810c00b24078c953a6a725ff1eb4708907e`.

Builder merged the then-current GitHub authority tip `5ef07ae0a8f7f435f31faf3ec83b0b4f898de437` non-destructively in merge commit `1f84956a463e398e75a9d0e8a9996f58f0ffa380`.

Completed builder-log commit: `b760326fc51bd858ae0a838a5d23f8e02bf0ff57`.

Compare `5ef07ae..b760326`: 3 commits ahead, 0 behind. SP01 changed only:

- `.hiveai/codex-logs/PAG-SP01-C001_SEMANTIC_CONTRACTS_AND_PROVIDER_BOUNDARY_CODEX_LOG.md`
- `src/scrubbots_pixel_factory/__init__.py`
- `src/scrubbots_pixel_factory/semantic/README.md`
- `src/scrubbots_pixel_factory/semantic/__init__.py`
- `src/scrubbots_pixel_factory/semantic/contracts.py`
- `src/scrubbots_pixel_factory/semantic/provider.py`
- `tests/unit/test_sp01_semantic_contracts.py`

No accepted MASK/RULES/WFC/HYBRID/AUTO production algorithms were modified.

## 4. ACCEPTANCE CRITERIA MATRIX

PASS:

- LEVEL_ART and ASSET_ART are separate typed contracts.
- LEVEL_ART reuses existing ScrubBots difficulty/dimension resolution.
- ASSET_ART supports explicit small and rectangular dimensions without fake difficulty labels.
- Semantic requests are frozen dataclasses with canonical JSON/digest rules.
- local paths and audit metadata are excluded from canonical request identity.
- image inputs carry content hashes and typed roles.
- provider capabilities are versioned and fail closed when requested features are unsupported.
- raw semantic candidates cannot masquerade as M08 logical artwork.
- existing procedural engines remain untouched.

FAIL:

- provider result provenance is not rebound to the request/provider at `generate_checked()`.
- role-specific image slots are not fail-closed against contradictory descriptor roles.
- direct candidate construction does not fully validate all provenance descriptor fields.
- the explicit deterministic-identity proof matrix is incomplete.

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder claims 13 focused tests passed and 394 full-repository tests passed. Static source inspection confirms the intended SP01 files and general architecture exist.

However, passing tests do not cover the critical provenance-binding cases described below.

## 6. FILE / SYMBOL EVIDENCE

`SemanticGenerationRequest` includes provider id, workflow version, model, config version, seed, dimensions and source-image descriptors in canonical request identity.

`SemanticImageCandidate` separately carries request digest, provider id/version, workflow/model identity, seed, dimensions and source provenance echoes.

`SemanticGeneratorProvider.generate_checked()` only:

1. validates declared capabilities,
2. calls `generate()`,
3. checks that the return type is `SemanticImageCandidate`.

It does not verify that the returned candidate is actually bound to the exact request and exact provider that produced it.

The focused test makes the gap visible: `level_request()` has `provider_id="test-provider"`, while `TextOnlyProvider.provider_id` is `"text-only-test"`. `generate_checked(level_request())` still succeeds as a typed UNAVAILABLE result instead of rejecting the request/provider mismatch.

## 7. FOCUSED TEST EVIDENCE

Builder reported:

`python -m pytest -q tests/unit/test_sp01_semantic_contracts.py` -> **13 passed**.

Coverage exists for dimensions, ASSET_ART separation, control validation, path-independent image identity, changed reference hash, provider-model identity, unsupported capabilities, typed failure and M08 normalization blocking.

Missing direct negative evidence includes request/result/provider cross-binding and contradictory descriptor-role cases.

## 8. REGRESSION EVIDENCE

Builder reported:

`python -m pytest -q` -> **394 passed**.

`compileall`, standalone import, module CLI help, installed CLI help and `git diff --check` were also reported successful.

Independent clean-clone/runtime replay was attempted by ChatGPT but failed before checkout because the audit container could not resolve `github.com`. Independent runtime is therefore **UNVERIFIED** and is not the reason for FAIL.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

PASS for SP01 scope.

No Magnific SDK, ComfyUI integration, browser scraping, HTTP runtime or new dependency was introduced. The core remains provider-neutral.

## 10. ARCHITECTURE CONSISTENCY

The architecture direction is correct. Semantic generation ends at immutable raw bytes/provenance, with SP03 normalization kept separate. This correctly prevents raw Magnific/provider output from bypassing ScrubBots normalization and M08 contracts.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

The builder log explicitly records that the required log did not exist before some earlier SP01 edits and was created before further edits. This is a process-ordering defect, but it was disclosed rather than hidden.

Root `TASKS.md` remains the historical M00-M10 record; post-M10 active authority is currently resolved by `docs/SEMANTIC_PIVOT_AUTHORITY_V01.md` plus the versioned SP prompt.

## 12. FINAL REPOSITORY STATE

Terminal builder publication commit is `b760326fc51bd858ae0a838a5d23f8e02bf0ff57`.

GitHub combined commit status exposes no CI statuses for that commit.

## 13. OPEN CROSS-MILESTONE FINDINGS

M10 visual V1 remains owner-rejected 100/100.

M11 remains blocked until the semantic path produces an owner-accepted replacement visual pack.

SP02 Magnific bridge must not begin until the SP01 provenance boundary is fail-closed.

## 14. DEFECTS BY SEVERITY

### F-PAG-SP01-C001-001 — MAJOR — Provider results are not cryptographically/semantically rebound to the checked request and provider

`generate_checked()` accepts any typed `SemanticImageCandidate` returned by `generate()` after capability validation. It does not require:

- `result.request_digest == request.digest()`;
- `request.provider_id == provider.provider_id` when the request names a concrete provider;
- `result.provider_id == provider.provider_id`;
- `result.provider_version == provider.provider_version`;
- `result.workflow_version == request.provider_workflow_version`;
- `result.model_id == request.provider_model` when a model is explicitly requested;
- `result.seed == request.seed`;
- `result.requested_width/height == request.resolved_dimensions()`;
- result reference/style/init/color provenance echoes to equal the request inputs.

A buggy or malicious future provider can therefore return a valid typed SUCCESS object for a different request, provider, seed, workflow, model or input set and still pass `generate_checked()`. That would poison SP02 Magnific provenance and later reproduce/batch bookkeeping.

### F-PAG-SP01-C001-002 — MAJOR — Image-role and typed provenance fields are not fully fail-closed

The request has role-bearing `ImageInputDescriptor` values, but slot/role consistency is not enforced. Examples currently possible in principle:

- `style_image` carrying role `REFERENCE`;
- `init_image` carrying role `STYLE`;
- `color_reference` carrying another role;
- `reference_images` containing STYLE/INIT/COLOR_REFERENCE descriptors.

This matters because SP02 must map these slots to different Magnific reference semantics.

Additionally, `SemanticImageCandidate.__post_init__()` validates/converts `reference_images` but does not equivalently type-check and role-check `style_image`, `init_image` and `color_reference` on direct construction. A supposedly typed immutable boundary can therefore be created with contradictory or non-descriptor provenance fields and fail only later when canonicalization is attempted.

### F-PAG-SP01-C001-003 — MINOR — Deterministic identity acceptance matrix is incomplete

The prompt requires proof that material prompt, seed, dimensions, provider, workflow/model and reference-image changes alter request identity. Tests directly prove path independence, changed reference hash and changed provider model, but do not separately assert prompt, seed, dimension, provider-id and workflow-version changes.

### F-PAG-SP01-C001-004 — NOTE — Builder log chronology did not satisfy the requested pre-edit creation order

The builder disclosed that the required log was absent after some SP01 work had already occurred. This cannot be retroactively repaired. Future cycles must create and verify the matching builder log before the first implementation edit.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

The large alias-heavy public export list is functional but can be simplified later if it becomes confusing. This is not an SP01 acceptance blocker.

## 16. UNVERIFIED ITEMS

Independent pytest replay is UNVERIFIED due audit-container DNS failure.

No GitHub CI status is available for the terminal builder commit.

## 17. REGRESSION RISK

Current M00-M10 regression risk is low because existing generator production modules were not changed.

SP02 risk is high if C001 provenance binding remains open, because paid Magnific generations could be attributed to the wrong canonical request or provider configuration.

## 18. AUDIT CONFIDENCE

**HIGH** for the static contract verdict. The blocking findings are directly visible in committed provider/request/result code and focused tests.

## 19. FINAL VERDICT

**FAIL**

SP01 architecture is retained. Do not rewrite it. Close the provenance/result/role binding defects in a bounded SP01-C002 before Magnific integration.

## 20. REQUIRED REMEDIATION

SP01-C002 must only:

1. bind provider request identity to provider identity before generation;
2. bind every returned result to the exact request/provider/workflow/model/seed/dimensions/input provenance;
3. reject contradictory image descriptor roles in each request slot;
4. enforce the same descriptor typing/role rules inside direct `SemanticImageCandidate` construction;
5. add negative tests for coordinated request/result/provider mismatches;
6. complete the required deterministic-identity change matrix;
7. preserve all current SP01 API intent and all M00-M10 behavior;
8. create the C002 builder log before any implementation edit.

Do not begin SP02 until this remediation independently passes.