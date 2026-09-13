# PAG-SP04-C004 — Review Entry Proof & Provider Capture Evidence Closure
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. VERDICT

**PASS**

PAG-SP04-C004 closes the two remaining technical blockers from C003. Terminal owner disposition now requires sealed deterministic review-entry evidence rather than a caller-supplied string, and `RAW_PROVIDER_CAPTURED` plus every later lifecycle state requires typed provider-capture evidence with exact request/provider/model/result/raw-byte provenance. No BLOCKER or MAJOR finding remains in the offline SP04 qualification contract foundation.

Severity summary:

- BLOCKER: 0
- MAJOR: 0
- MINOR: 1
- NOTE: 2

SP04 is now technically ready to proceed to bounded live qualification evidence. This PASS does **not** itself select a default provider/model/workflow and does not accept SP05/M11.

## 2. CONTRACT RECOVERY

Audited against:

1. root `TASKS.md` as the only current project-status tracker;
2. `.hiveai/prompts/PAG-SP04-C004_REVIEW_ENTRY_PROOF_AND_PROVIDER_CAPTURE_EVIDENCE_CLOSURE_PROMPT.md`;
3. `.hiveai/codex-logs/PAG-SP04-C004_REVIEW_ENTRY_PROOF_AND_PROVIDER_CAPTURE_EVIDENCE_CLOSURE_CODEX_LOG.md`;
4. `.hiveai/audits/PAG-SP04-C003_REQUEST_TO_CASE_BINDING_ATTEMPT_SEAL_AND_REVIEW_ATTRIBUTION_CLOSURE_STRICT_AUDIT.md`;
5. accepted SP01 request/provider contracts;
6. accepted SP02 provider result/candidate contracts;
7. accepted SP03 typed/sealed raw and normalization contracts;
8. current SP04 qualification implementation/tests on GitHub `main`;
9. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

C004 was strictly offline. It was not authorized to call Magnific/PixelLab, spend credits, execute live qualification, begin SP05/SP06, Studio UI, weekly batches or M11.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder start checkpoint: `e18819690b25635e61fa3abd6eff7d444d851f2d`, synchronized with `origin/main`, divergence `0 0`.

Implementation/test terminal commit: `5f1d189570506aad13c3d8c19ef9b9ef88004bd7`.

Audited pre-audit `main` HEAD: `fab2860e1e6c811e5ddd2a1291a88b5282503fb2` (`Publish SP04 C004 builder log`).

GitHub compare from C004 start to audited terminal HEAD is ahead by two commits and changes only:

- matching C004 builder log;
- `src/scrubbots_pixel_factory/semantic/qualification/__init__.py`;
- `src/scrubbots_pixel_factory/semantic/qualification/models.py`;
- `tests/unit/test_sp04_qualification.py`.

No root `TASKS.md` edit by Codex, no provider execution implementation, no SP01-SP03 algorithm change, no SP05/SP06/M11 work and no sibling repository edit.

Scope discipline: **PASS**.

## 4. ACCEPTANCE CRITERIA MATRIX

| Requirement | Result | Audit assessment |
|---|---|---|
| Checked/sealed review-entry evidence | PASS | `QualificationReviewBinding` is `init=False`, checked-factory constructed and fingerprint sealed |
| Free-form review string cannot mint terminal proof | PASS | `with_review_binding()` accepts only checked `QualificationReviewBinding` |
| Review ID deterministic from seed + stable pre-review identity | PASS | expected ID is recomputed and sealed |
| Review proof binds exact attempt/artifact/request | PASS | attempt ID, plan/case, normalized artifact/RGBA, request binding and pre-review digest are bound |
| Review pack emits sealed reviewed hidden attempts | PASS | factory constructs bindings then attaches them to hidden attempts |
| Direct review-pack attribution remains fail-closed | PASS | ID, sequence, subject, target and hidden-attempt attribution remain checked |
| Typed provider-capture evidence | PASS | `ProviderCaptureEvidence` derives from typed successful candidate or sealed raw import |
| Provider capture requires non-null exact model | PASS | missing model is rejected |
| Provider capture binds immutable bytes/result identity | PASS | candidate digest, request, provider/version/workflow/model, dimensions, SHA and input provenance are checked |
| `RAW_PROVIDER_CAPTURED` requires capture evidence | PASS | lifecycle validation rejects missing capture evidence |
| Capture→raw exact cross-binding | PASS | result identity, request, provider/version/workflow/model, SHA and dimensions are checked |
| Direct RAW_IMPORT_VERIFIED can derive equivalent capture proof | PASS | `from_raw_import()` preserves accepted SP03 provenance without weakening it |
| Terminal owner states require sealed review proof | PASS | OWNER_ACCEPTED/REJECTED reject missing review binding |
| Existing request/case/plan/lifecycle safeguards preserved | PASS | C003 bindings and monotonic state rules remain intact |
| Cost remains outside deterministic review identity | PASS | cost changes do not alter attempt/review binding identity |
| No provider/network/credit execution | PASS | scoped code/log show offline-only work |
| Builder log created before C004 product edits | PASS | log records synchronized start and pre-edit creation |
| Full regression | BUILDER PASS / AUDITOR RUNTIME UNVERIFIED | builder reports 488 passed; GitHub has no CI status/workflow run |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder reports:

- SP04 focused: **26 passed**;
- SP01-SP04 focused: **107 passed**;
- full repository: **488 passed**;
- compileall: PASS;
- package import including new evidence types: PASS;
- CLI help checks: PASS;
- `git diff --check`: PASS;
- no provider calls, credentials, credits or network generation.

Static repository inspection supports the claimed C004 design and scope. The builder's Python test execution was not independently replayed by this auditor, and current GitHub `main` exposes no CI status/workflow run. Therefore test execution remains builder evidence rather than independently reproduced runtime evidence.

## 6. FILE / SYMBOL EVIDENCE

Primary implementation evidence:

- `ProviderCaptureEvidence` is checked-construction-only and binds typed candidate/raw-import provenance;
- `QualificationReviewBinding` is checked-construction-only and binds one exact pre-review attempt plus typed review seed/protocol;
- `QualificationAttemptRecord` now carries both `provider_capture` and `review_binding`;
- lifecycle validation requires provider capture from `RAW_PROVIDER_CAPTURED` onward;
- terminal owner lifecycles require sealed review-entry evidence;
- capture/raw and review/attempt chains are cross-validated;
- `build_metadata_blind_review_pack()` creates sealed review bindings for hidden attempts.

Primary adversarial tests explicitly cover arbitrary review strings, direct constructors, `dataclasses.replace()`, missing/wrong capture model/provider, capture/raw mismatch, missing capture at RAW_PROVIDER_CAPTURED and valid terminal owner transitions.

## 7. FOCUSED TEST EVIDENCE

Builder-reported focused result:

`python -m pytest -q tests/unit/test_sp04_qualification.py` → **26 passed**.

Focused tests cover both remaining C003 findings and retain prior C001-C003 adversarial behavior.

Auditor status: **not independently replayed**.

## 8. REGRESSION EVIDENCE

Builder-reported:

- SP01-SP04 focused suite → **107 passed**;
- full repository → **488 passed**;
- compileall/import/CLI/diff checks → PASS.

No GitHub Actions status or workflow run is attached to audited HEAD.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

PASS.

C004 adds no network client, browser automation, secret read, telemetry path or provider execution. No live Magnific/PixelLab call or credit spend is reported. Provider evidence classes consume already accepted typed local objects.

## 10. ARCHITECTURE CONSISTENCY

PASS.

C004 stays inside the SP04 qualification layer. It does not weaken SP01 request/provider contracts, SP02 provider bridges or SP03 normalization seals. The evidence wrappers are provider-neutral and preserve the explicit MAGNIFIC/PIXELLAB matrix architecture.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Technical chronology requirement is satisfied: the C004 builder log records creation before C004 implementation edits and a synchronized start checkpoint.

**MINOR F-PAG-SP04-C004-001 — legacy control-plane files were read despite explicit C004 instruction not to read them for current authority.**

The builder log says it read `.hiveai/RULES.md`, `.hiveai/PROJECT.json`, `.hiveai/EVENTS.jsonl` and `.hiveai/CYCLE_INDEX.md`, while the C004 prompt explicitly stated not to use or read legacy hidden tracker/control-plane files to reconstruct current task state. The log also states they were not treated as current authority, so this did not contaminate the implementation result. Future builders must use root `TASKS.md` plus the explicitly named current prompt/audit/governance docs only.

This is process/governance debt, not a technical C004 blocker.

## 12. FINAL REPOSITORY STATE

Audited pre-audit HEAD: `fab2860e1e6c811e5ddd2a1291a88b5282503fb2`.

GitHub branch inspection confirms that HEAD is the final log-only publication commit whose parent is the implementation/test terminal commit `5f1d189570506aad13c3d8c19ef9b9ef88004bd7`.

No CI statuses or workflow runs exist for that HEAD.

## 13. OPEN CROSS-MILESTONE FINDINGS

The following are intentionally outside C004 and remain open qualification work:

1. exact accepted Magnific smoke raw bytes still need local SP03 import/decoder proof;
2. the real Magnific raw candidate must be locally normalized to 24x24;
3. the local normalized Magnific 24x24 result still needs owner visual review against the already accepted provider-produced 24x24 derivative;
4. PixelLab live 24x24 qualification remains pending authorized API-secret/credit conditions;
5. no default provider/model/workflow is selected yet;
6. SP05 and M11 remain blocked until live qualification evidence is accepted.

## 14. DEFECTS BY SEVERITY

### BLOCKER

None.

### MAJOR

None.

### MINOR

- `F-PAG-SP04-C004-001` — builder read legacy hidden control-plane files contrary to explicit current-authority instruction.

### NOTE

- `N-PAG-SP04-C004-001` — builder test results are strong but not independently replayed by this auditor.
- `N-PAG-SP04-C004-002` — GitHub `main` has no CI status/workflow run for audited HEAD.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

No additional C004 remediation cycle is justified.

For future qualification tooling, consider centralizing the current-authority file list in one builder-facing helper/document so legacy `.hiveai` control-plane artifacts are not repeatedly rediscovered by Codex. This should not reopen C004.

## 16. UNVERIFIED ITEMS

- independent local replay of the 26/107/488 test runs;
- exact live Magnific private raw-byte compatibility through SP03;
- owner visual acceptance of local AREA_AVERAGE_V1 2048→24 output;
- PixelLab live exact-size behavior in this qualification harness.

## 17. REGRESSION RISK

**LOW-MEDIUM** for the offline qualification foundation.

The main remaining risk is now integration with real provider bytes rather than local contract integrity. C004 has materially reduced the risk of false owner acceptance and false provider-capture states.

## 18. AUDIT CONFIDENCE

**HIGH** for static contract/scope review.

**MEDIUM-HIGH** overall because runtime regression evidence is builder-reported rather than independently replayed.

## 19. FINAL VERDICT

**PASS**

PAG-SP04-C004 is accepted. The offline SP04 qualification contract foundation is technically closed for the current scope. Live qualification may proceed in a bounded, owner-authorized evidence cycle.

## 20. REQUIRED REMEDIATION

No C005 offline remediation cycle is required.

Next work is live qualification evidence, not architecture repair:

1. recover/capture the exact existing Magnific smoke raw bytes without generating a new image if possible;
2. ingest them through the accepted SP02/SP03 typed chain and record immutable SHA/provenance;
3. prove strict local decoder/import compatibility;
4. normalize locally to the owner-approved 24x24 target;
5. present that local normalized result metadata-blind for owner visual review and compare it to the already accepted provider-produced 24x24 derivative;
6. only after that decide whether another Magnific generation or PixelLab live comparison is worth spending credits on.
