# PAG-SP03-C002 — Bounded Decode, Deep Immutability & Raw-to-Normalized Provenance Closure
Document role: CHATGPT STRICT AUDIT

## 1. VERDICT

**FAIL**

SP03-C002 closes the decompression-bound defect, nested-report mutability defect, and LEVEL_ART request-legality defect from C001. One production-facing MAJOR provenance-integrity defect remains.

Severity summary:

- BLOCKER: 0
- MAJOR: 1
- MINOR: 1
- NOTE: 2

Do not begin SP04 or M11. No provider credit execution is required for the remediation.

## 2. CONTRACT RECOVERY

Audited against:

1. root `TASKS.md` as the only current status tracker;
2. `.hiveai/prompts/PAG-SP03-C002_BOUNDED_DECODE_DEEP_IMMUTABILITY_AND_RAW_TO_NORMALIZED_PROVENANCE_CLOSURE_PROMPT.md`;
3. `.hiveai/audits/PAG-SP03-C001_RAW_CAPTURE_AND_DETERMINISTIC_24X24_NORMALIZATION_FOUNDATION_STRICT_AUDIT.md`;
4. accepted SP01/SP02 contracts;
5. current SP03 code/tests/docs;
6. M07/M08/M09 provenance/export boundaries;
7. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

C002 was required to close exactly four C001 findings: bounded zlib output, deep immutability, exact raw-to-normalized provenance binding, and LEVEL_ART normalization-request legality.

## 3. BRANCH / HEAD / DIFF SCOPE

Current GitHub `main` terminal HEAD audited: `32a5d93d7f438da1a8dd0a524005c9eecf7de4c8`.

Builder log records implementation/merge publication commit `e0059176ec2a599a80c80d945de73ec2a2beec03`, log publication commit `ff7395e8e03db757e6eaf61838274dc61a4d7780`, and a later final log-only commit produced current terminal HEAD.

Compare canonical C002 authority checkpoint `b28b55bb04223574ecf9137d93d98963059cd169` to terminal HEAD changes only:

- C002 builder log;
- SP03 normalization exports/docs;
- `semantic/normalization/core.py`;
- focused SP03 tests.

No M00-M10 production algorithms, provider execution, SP04/M11 implementation, or root tracker edit by Codex is present in the C002 implementation diff.

Scope discipline: **PASS**, with a process note in section 11.

## 4. ACCEPTANCE CRITERIA MATRIX

| Area | Result | Audit assessment |
|---|---|---|
| Bounded zlib lifecycle | PASS | no unrestricted `flush()`; exact expected+1 sentinel budget is enforced across incremental decompression |
| Compact decompression bomb | PASS | focused test creates compressed high-expansion input without materializing the giant decoded payload |
| Truncated/trailing stream rejection | PASS | explicit tests and fail-closed checks exist |
| Deep `crop_pad` immutability | PASS | caller mapping copied and stored behind `MappingProxyType` |
| Repeated report identity | PASS | canonical serialization thaws immutable mapping deterministically |
| LEVEL_ART legality | PASS | all LEVEL_ART normalization requests fail at construction, which is the prompt-authorized minimal strategy |
| Exact 24x24 fast path | PASS | preserved |
| 2048→24 deterministic baseline | PASS | preserved |
| Raw/source hash preservation | PASS | preserved |
| Source provenance snapshot | PARTIAL | useful immutable snapshot exists and normal path derives it from raw artifact |
| Coordinated provenance tamper | **FAIL** | seal can be reset/reissued through public dataclass replacement, allowing a forged internally-consistent source snapshot to be accepted |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder reports:

- SP03 focused: 14 passed;
- SP01+SP02+SP03 focused: 78 passed;
- full repository: 459 passed;
- compile/import/CLI/diff/source-policy checks passed.

Those claims are consistent with the committed test surface. The escaped defect is not covered by the current tests: tests modify either an artifact convenience field alone, use a provenance snapshot from an actually different raw artifact, or tamper the report. They do not reset the construction fingerprint while replacing both the source snapshot and matching convenience fields.

## 6. FILE / SYMBOL EVIDENCE

Positive evidence:

- `_decode_png_rgba()` now uses incremental compressed-input processing and a hard `expected_length + 1` output budget.
- `SemanticNormalizationReport.__post_init__()` copies caller mapping and stores `MappingProxyType`.
- `SemanticNormalizationRequest.__post_init__()` rejects all `LEVEL_ART` requests until the canonical policy exists.
- `SemanticSourceProvenance.from_raw_artifact()` provides the intended normal-path source snapshot.
- `SemanticNormalizedArtifact.from_raw_artifact()` is the intended checked normal constructor.

Residual weakness:

- `SemanticSourceProvenance` remains a publicly constructible/replacable dataclass with no construction seal tying its fields to the raw artifact identified by `raw_artifact_digest`.
- `SemanticNormalizedArtifact._construction_token` and `_construction_fingerprint` are ordinary `init=True` dataclass fields.
- `__post_init__()` treats `_construction_fingerprint is None` as permission to mint a new fingerprint.

Therefore a caller starting from a valid artifact can create a modified source snapshot that retains source A's `raw_artifact_digest` while changing provider/request convenience provenance, then call `dataclasses.replace()` on the artifact with matching fields and `_construction_fingerprint=None`. `dataclasses.replace()` preserves the valid private token from the original instance; `__post_init__()` then recomputes and accepts a fresh fingerprint for the forged coordinated state.

This is not an `object.__setattr__` attack. It uses normal exported dataclass construction/replacement semantics.

## 7. FOCUSED TEST EVIDENCE

Current tests correctly prove:

- caller mapping mutation cannot alter report state;
- stored `crop_pad` mutation raises `TypeError`;
- compact zlib bomb rejects;
- expected+1, truncated and trailing streams reject;
- single-field provider/request tampering rejects;
- replacing source provenance with a real foreign raw artifact rejects;
- report/raw/request cross-pairing rejects;
- LEVEL_ART request construction rejects.

Missing sensitivity test:

1. start from a valid normalized artifact;
2. create a forged `SemanticSourceProvenance` retaining the same `raw_artifact_digest` but changing provider/version/workflow/model/request provenance;
3. replace the artifact's source snapshot and matching duplicated fields together;
4. reset or otherwise bypass the current caller-settable construction fingerprint;
5. expect fail-closed rejection.

Current implementation can accept that coordinated state.

## 8. REGRESSION EVIDENCE

Builder evidence: 459 repository tests passed and compile/import/CLI checks passed.

Independent audit clean-clone replay was attempted. The audit container could not resolve `github.com`, so independent runtime replay is **UNVERIFIED**, not failed.

GitHub terminal HEAD has no commit statuses and no associated workflow runs.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Bounded PNG decompression: **PASS**.

The previous unrestricted zlib `flush()` path is gone. Decoder memory is now bounded by explicit raw-input, decoded-pixel and scanline-output budgets.

Offline/provider isolation: **PASS**.

No provider network execution or secret read is introduced.

Provenance integrity: **FAIL** because the construction seal can be caller-reset during coordinated replacement.

## 10. ARCHITECTURE CONSISTENCY

Overall normalization architecture remains sound:

`raw bytes -> immutable raw artifact -> normalization request -> deterministic decode/resize -> report -> normalized ASSET_ART`.

No redesign is needed. The remaining issue is limited to making the source provenance and normalized construction seal non-forgeable through public dataclass init/replace surfaces.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

MINOR process finding:

The C002 prompt explicitly says hidden legacy `.hiveai` tracker/control-plane files are not current status authority. The builder log nevertheless lists `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl` and `.hiveai/CYCLE_INDEX.md` among authority read before implementation.

The same log also records a start checkpoint before the GitHub C002 prompt/audit/tracker commits were present locally, then a later non-destructive merge after the first push was rejected.

Final code scope aligns with the actual C002 prompt, so this is a process/documentation finding rather than a second technical acceptance blocker. Future cycles must use root `TASKS.md` plus the active prompt/audit/docs only.

## 12. FINAL REPOSITORY STATE

GitHub `main` is ahead of the canonical C002 authority checkpoint by C002 implementation/log commits only. Current terminal HEAD is published. No evidence of force-push/reset or unrelated product edits was found.

## 13. OPEN CROSS-MILESTONE FINDINGS

- Real owner-approved Magnific raw PNG byte ingestion into the local Factory remains a post-normalization verification task.
- Local downsampler visual quality is not yet owner-qualified.
- SP04 remains blocked until SP03 technical acceptance.
- M11 remains blocked.
- PixelLab live smoke remains optional/pending authorized secret/access.

## 14. DEFECTS BY SEVERITY

### MAJOR — F-PAG-SP03-C002-001 — Normalized provenance construction seal can be reset during coordinated dataclass replacement

`SemanticSourceProvenance` is publicly constructible/replacable and is not itself sealed as a snapshot derived only from `SemanticRawArtifact`.

`SemanticNormalizedArtifact` carries `_construction_token` and `_construction_fingerprint` as init fields. A valid artifact therefore carries a valid token into `dataclasses.replace()`. If the caller supplies a forged source snapshot with the same raw-artifact digest, changes matching duplicated provider/request fields, and passes `_construction_fingerprint=None`, `__post_init__()` mints a new fingerprint for the coordinated forged state.

Impact: the normalized artifact can claim provider/request provenance that was not derived from the raw artifact identified by its source digest, while all current checks remain internally consistent.

Required closure:

- make `SemanticSourceProvenance` creation fail-closed so arbitrary caller construction/replacement cannot mint a snapshot claiming an existing raw-artifact digest with changed provenance; and/or validate it against an immutable canonical raw identity carried in a non-resettable way;
- make construction token/fingerprint implementation details non-caller-settable through normal constructor/`dataclasses.replace()` paths (`init=False` or equivalent);
- never use `fingerprint=None` from caller input as permission to re-seal arbitrary coordinated state;
- add an integrity assertion that is exercised on deterministic serialization/digest if appropriate;
- add the exact coordinated-replacement sensitivity test described in section 7.

### MINOR — F-PAG-SP03-C002-002 — Builder authority chronology includes deprecated hidden tracker inputs

The builder log contradicts the active prompt's authority rule by listing legacy hidden tracker/control-plane files as authority and records a start checkpoint before current C002 authority reached the local checkout.

Required closure: C003 builder reads only root `TASKS.md`, active C003 prompt, C002 audit, accepted docs/contracts and governance files. No legacy hidden tracker authority.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

- Prefer `init=False` for internal seals/fingerprints and derive them unconditionally from accepted inputs.
- Consider making source provenance a private/internal sealed value with only a public read-only projection if external callers do not need direct construction.
- Add a reusable `_assert_integrity()` invoked by `identity_dict()`/`digest()` so impossible states fail closed even if a future refactor weakens construction.
- Keep the strict PNG profile until a real provider byte fixture proves which ancillary chunks must be accepted.

## 16. UNVERIFIED ITEMS

- Independent execution of the 459-test suite: UNVERIFIED due audit-container GitHub DNS failure.
- Real Magnific raw PNG local ingestion: NOT RUN.
- Visual equivalence between local area resampler and owner-approved provider resize: NOT CLAIMED.

## 17. REGRESSION RISK

Current risk if SP03 were accepted now: **MEDIUM**.

Pixel normalization behavior itself is stable, but provenance authenticity is a core production invariant. The remaining defect is narrow and can be closed without changing image output.

## 18. AUDIT CONFIDENCE

**HIGH** for the provenance defect because it follows directly from Python dataclass `replace()` semantics and the committed init fields/checks.

**MEDIUM-HIGH** overall because independent runtime replay is unavailable, while builder regression evidence is extensive.

## 19. FINAL VERDICT

**FAIL**

Disposition:

- `F-PAG-SP03-C001-001` decompression-bound bypass: CLOSED;
- `F-PAG-SP03-C001-002` mutable report state: CLOSED;
- `F-PAG-SP03-C001-004` LEVEL_ART request legality: CLOSED;
- `F-PAG-SP03-C001-003` raw-to-normalized provenance binding: PARTIALLY CLOSED, residual moved to `F-PAG-SP03-C002-001`;
- SP03 overall: **FAIL / ONE BOUNDED C003 REQUIRED**.

## 20. REQUIRED REMEDIATION

Create one bounded cycle:

`PAG-SP03-C003 — Provenance Seal & Construction Integrity Closure`

C003 must only:

1. make source-provenance snapshots non-forgeable through ordinary public construction/`dataclasses.replace()`;
2. make normalized-artifact internal seal/fingerprint non-caller-resettable;
3. fail closed on coordinated source-snapshot + provider/request-field replacement even when syntactically valid;
4. preserve all accepted C001/C002 image behavior byte-for-byte;
5. add exact sensitivity tests for the coordinated replacement attack;
6. correct builder authority discipline;
7. run focused + SP01/SP02/SP03 + full regression;
8. stop for independent audit.

Do not begin SP04, M11, provider execution, palette redesign, or visual algorithm changes.