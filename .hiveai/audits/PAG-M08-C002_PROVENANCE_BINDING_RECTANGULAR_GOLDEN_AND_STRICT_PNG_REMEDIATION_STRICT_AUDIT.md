# PAG-M08-C002 — Provenance Binding, Rectangular Golden & Strict PNG Remediation
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. VERDICT

FAIL

C002 fully closes the rectangular-evidence and strict-IEND findings from C001, and it materially improves rich-mode provenance handling. One MAJOR residual provenance-binding defect remains, so PAG-M08 cannot close yet.

## 2. CONTRACT RECOVERY

Authoritative C002 prompt: `.hiveai/prompts/PAG-M08-C002_PROVENANCE_BINDING_RECTANGULAR_GOLDEN_AND_STRICT_PNG_REMEDIATION_PROMPT.md`.

Source findings:

- `F-PAG-M08-C001-001` rich WFC/HYBRID/AUTO provenance omission/cross-binding;
- `F-PAG-M08-C001-002` rectangular row-major/golden evidence;
- `F-PAG-M08-C001-003` non-empty IEND acceptance.

C002 was authorized only to close those findings while preserving accepted C001 architecture and all M00-M07 behavior.

## 3. BRANCH / HEAD / DIFF SCOPE

Repository: `Sekiph82/ScrubBots-Level-Factory`

Branch: `main`

Builder synchronized base: `760042785d81abf95c3d19ff422e514a3af46c65`

Implementation/evidence commit: `cddb738a71eda0dc614cbcc4d06b19cb9ac31c4a`

Completed builder-log commit: `53fdac71eef517f633f1e99fd7489e201be296db`

Terminal builder-era HEAD independently observed: `cca76e86f7690660c24f386f80b36a9091f8ca85`

Independent compare from the builder synchronized base to terminal HEAD reports exactly three commits ahead, zero behind. Changed paths are limited to the matching C002 builder log, `output/bundle.py`, `output/png.py`, `output/README.md`, the M08 unit/integration/golden tests, and the new rectangular golden JSON/PNG pair. No M09+ implementation or generator production rewrite is present.

## 4. ACCEPTANCE CRITERIA MATRIX

- Raw WFC/HYBRID/AUTO result cannot silently lose required metadata: PASS.
- Explicit authoritative generator metadata API: PASS.
- Rich namespace/mode binding: PASS.
- WFC/HYBRID/AUTO reconstructible semantic binding: PARTIAL / FAIL.
- Real rectangular row-major known-answer evidence: PASS.
- Committed rectangular JSON/PNG golden: PASS.
- Non-empty IEND with valid CRC rejected: PASS.
- Accepted C001 architecture preserved: PASS.
- Full runtime regression independently reproduced: UNVERIFIED due audit-environment DNS failure.

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

The builder accurately reports the broad C002 architecture and the existence of focused rich-mode validators. The repository confirms that raw rich-mode results fail closed without wrapper/explicit metadata, wrapper vs explicit metadata equivalence is tested, rectangular goldens exist, and the strict IEND gate exists.

The builder log overstates the completeness of deterministic rich-provenance cross-binding. Some fields described as bound to stage/attempt seeds remain only shape-checked rather than rederived from the authoritative outer seed/attempt contract.

## 6. FILE / SYMBOL EVIDENCE

`src/scrubbots_pixel_factory/output/bundle.py` now contains `_candidate_payload()`, `_validate_wfc_metadata()`, `_validate_hybrid_metadata()`, and `_validate_auto_metadata()`.

`_candidate_payload()` correctly rejects raw successful WFC/HYBRID/AUTO results with no candidate wrapper or explicit `generator_metadata`.

However:

- `_validate_wfc_metadata()` checks `0 <= attempt < max_attempts` and only requires each contradiction-history entry to precede the successful attempt. It does not bind the successful `attempt` to the successful GenerationResult's authoritative `rng.provenance.retry_seeds` keys/count, even though that evidence is present in the exported GenerationResult and directly reconstructible.
- `_validate_hybrid_metadata()` accepts any non-negative `outer_attempt`; it does not bind that attempt to the exported result's retry provenance.
- `_validate_hybrid_metadata()` checks each stage's `stage_index`, 64-hex `derived_seed`, child-request digest and child seed equality, but does not enforce the strategy-specific stage name/kind layout and does not rederive each stage seed from `outer master seed + strategy + outer_attempt + stage index + stage name`, despite the accepted M06 generator contract defining exactly that deterministic derivation.

Consequently, a metadata editor can construct internally self-consistent but historically false rich provenance without changing the artwork/result truth.

## 7. FOCUSED TEST EVIDENCE

Builder reports final focused M08 result: `16 passed, 1 warning`.

Repository tests prove:

- raw rich results fail without metadata;
- wrapper and explicit metadata exports are equivalent;
- wrong rich namespace fails;
- WFC unrelated `exemplar_id` tamper fails;
- HYBRID `final_result_digest` tamper fails;
- AUTO `selected_engine_id` tamper fails;
- rectangular row-major known-answer behavior;
- non-empty IEND rejection.

Missing false-green tests include at least:

- WFC successful attempt changed while contradicting `GenerationResult.rng.provenance.retry_seeds`;
- WFC contradiction-history attempt sequence inconsistent with successful attempt;
- HYBRID `outer_attempt` changed while result retry provenance remains unchanged;
- HYBRID stage name/kind layout corruption;
- HYBRID stage derived seed changed together with child-request seed/digest so the current internal-consistency checks still pass, while the seed no longer matches deterministic M06 derivation.

The C002 prompt also explicitly required a second WFC deterministic request/artwork binding tamper beyond `exemplar_id`; the committed focused test only uses `exemplar_id` for WFC.

## 8. REGRESSION EVIDENCE

Builder reports full repository result: `288 passed, 1 warning in 190.18s` and successful compile/import/static checks.

No GitHub combined status checks or workflow evidence exist for terminal HEAD.

Independent clean-checkout pytest could not start because the audit container could not resolve `github.com`. Runtime regression is therefore `UNVERIFIED`, not failed.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

PASS.

C002 adds no runtime dependency, HTTP/API/cloud/telemetry path, interpolation/resizing path, arbitrary RGB acceptance, or M09+ execution surface.

## 10. ARCHITECTURE CONSISTENCY

PARTIAL / FAIL only for rich-provenance trust semantics.

The overall M08 separation remains sound: immutable artwork truth, generation metadata, quality state, exact logical PNG, optional preview, and deterministic filesystem publication remain separate. C003 should not redesign these layers.

The missing fix belongs only in the M08 metadata verifier and focused tests. It must reuse accepted M05/M06 deterministic contracts rather than duplicate full replay engines.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Builder log has the exact shared H1 and `CODEX BUILDER LOG` role. It records starting authority, failures/corrections, test results, commits, pushes and terminal equality.

An intervening H!veAI control-plane migration made root `TASKS.md` the current project-status authority. Hidden legacy tracker files must not be revived as a competing current tracker.

## 12. FINAL REPOSITORY STATE

Terminal C002 builder-era HEAD: `cca76e86f7690660c24f386f80b36a9091f8ca85`.

C002 product diff is bounded to M08 remediation scope. M09+ remains untouched.

## 13. OPEN CROSS-MILESTONE FINDINGS

`PAG-0441` remains deferred to M10 performance-budget establishment.

No new M00-M07 regression finding was identified.

## 14. DEFECTS BY SEVERITY

### F-PAG-M08-C002-001 — MAJOR — Rich provenance accepts deterministic attempt/stage histories that contradict authoritative result provenance

Status: OPEN.

Affected subsystem: `src/scrubbots_pixel_factory/output/bundle.py`, primarily `_validate_wfc_metadata()` and `_validate_hybrid_metadata()`.

Current incorrect behavior:

1. WFC `attempt` is range-checked but not tied to result retry provenance.
2. WFC contradiction-history sequence is not required to correspond exactly to prior attempts.
3. HYBRID `outer_attempt` is not tied to result retry provenance.
4. HYBRID stage layout/name/kind is not validated against strategy.
5. HYBRID stage seeds are only checked for format and equality with the embedded child request; they are not rederived from the accepted deterministic M06 seed path.

Required target behavior:

- every directly reconstructible attempt/stage identity field must be bound to the exported GenerationResult/request and accepted M05/M06 deterministic seed/layout contract;
- internally self-consistent but deterministically false metadata must fail closed with `OutputContractError`;
- do not run/reimplement full WFC/HYBRID replay merely to validate non-reconstructible runtime details.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

NOTE only: Windows-specific candidate-ID hardening remains optional and is not part of this verdict.

## 16. UNVERIFIED ITEMS

Independent pytest execution: UNVERIFIED because audit-container DNS could not resolve GitHub for a clean checkout.

Builder-reported `288 passed` is retained as builder evidence only.

## 17. REGRESSION RISK

Low-to-moderate if remediation is limited to metadata validation and focused tests. The accepted JSON/PNG/preview/filesystem implementation should not be changed.

## 18. AUDIT CONFIDENCE

HIGH for the residual provenance finding because it follows directly from static control flow and accepted generator contracts. MEDIUM for runtime regression because independent execution was unavailable.

## 19. FINAL VERDICT

FAIL

`F-PAG-M08-C001-002` is CLOSED.

`F-PAG-M08-C001-003` is CLOSED.

`F-PAG-M08-C001-001` is PARTIALLY REMEDIATED and continues as `F-PAG-M08-C002-001`.

PAG-M08 remains OPEN. PAG-M09+ remains blocked.

## 20. REQUIRED REMEDIATION

Create bounded `PAG-M08-C003` only for `F-PAG-M08-C002-001`.

Required evidence must include deterministic negative tests for WFC attempt/retry provenance, WFC prior-attempt sequence, HYBRID outer-attempt/retry provenance, strategy-specific HYBRID stage layout, and HYBRID rederived stage seeds. Preserve all accepted C001/C002 artwork, PNG, rectangular golden, quality, filesystem and offline behavior.