# SB-LF09-001-C001-R01 — Evidence Availability and Cross-Candidate Identity Remediation

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## VERDICT

**CHANGES_REQUIRED**

The R01 implementation closes the unavailable/stale required-artifact evidence
finding and preserves the bounded, deterministic, opt-in, offline experimental
lane. It does not close the complete cross-candidate identity policy: optional
`preview_ref`/`preview_digest` identities are canonical `CandidateEvidence`
artifact identities and are verified by the M08 boundary, but they are absent
from the versioned policy and can be shared across candidates without rejection
or an explicit sharing exception.

## CONTRACT RECOVERY

- Repository: `Sekiph82/ScrubBots-Level-Factory`
- Branch: `main`
- Audited live head: `c2372997bd8a1fc10c280c6b0a9091e168c2d135`
- R01 prompt: [authoritative remediation prompt](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/c2372997bd8a1fc10c280c6b0a9091e168c2d135/.hiveai/prompts/SB-LF09-001-C001-R01_EVIDENCE_AVAILABILITY_AND_CROSS_CANDIDATE_REMEDIATION_PROMPT.md)
- R01 criteria: [strict audit criteria](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/c2372997bd8a1fc10c280c6b0a9091e168c2d135/.hiveai/audit-criteria/SB-LF09-001-C001-R01_EVIDENCE_AVAILABILITY_AND_CROSS_CANDIDATE_AUDIT_CRITERIA.md)
- Previous audit: [C001 strict audit](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/c2372997bd8a1fc10c280c6b0a9091e168c2d135/.hiveai/audits/SB-LF09-001-C001_STRICT_AUDIT.md)
- Implementation commit: [483eb5e2b0f348e167e3b4396cbff40ccc38e3c1](https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/483eb5e2b0f348e167e3b4396cbff40ccc38e3c1)
- Log publication commit: [dc7dd367334f2a8a80f27625170c21298310ed56](https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/dc7dd367334f2a8a80f27625170c21298310ed56)
- Final handoff append: [c2372997bd8a1fc10c280c6b0a9091e168c2d135](https://github.com/Sekiph82/ScrubBots-Level-Factory/commit/c2372997bd8a1fc10c280c6b0a9091e168c2d135)
- Builder log: [published R01 CODEX log](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/c2372997bd8a1fc10c280c6b0a9091e168c2d135/.hiveai/codex-logs/SB-LF09-001-C001-R01_EVIDENCE_AVAILABILITY_AND_CROSS_CANDIDATE_REMEDIATION_CODEX_LOG.md)

## BRANCH / HEAD / DIFF SCOPE

The canonical owner mirror at `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` was dirty and 39 commits behind fetched `origin/main`; it was not reset, cleaned, stashed, rebased, synchronized in place, or otherwise disturbed. Audit inspection used fetched `origin/main` and an existing clean same-repository isolated worktree at the audited head.

The R01 implementation range from `672c0340823b1eb25631f921be26c938908812bf` through `483eb5e2b0f348e167e3b4396cbff40ccc38e3c1` contains only:

- `src/scrubbots_pixel_factory/evolutionary_selection.py`
- package exports in `src/scrubbots_pixel_factory/__init__.py`
- `tests/unit/test_sb_lf09_001_evolutionary_selection.py`

The separate publication commits add only the matching CODEX log. The range
does not modify `TASKS.md`, prompts, or audits. `git diff --check` and protected
path checks passed for the published range.

## ACCEPTANCE CRITERIA MATRIX

| Criterion | Result | Evidence |
| --- | --- | --- |
| Required evidence is verified before ranking; missing/stale bytes fail closed | PASS | `run_experimental_evolutionary_selection()` requires `artifacts` and invokes `verify_artifact_set()` for every candidate before population/budget/ranking. Independent missing/stale probes and focused tests pass. |
| Complete versioned cross-candidate artifact identity policy | FAIL | The policy enumerates ten required reference/digest pairs, but omits optional `preview_ref`/`preview_digest` and `mutation_ref`/`mutation_digest`, despite those fields being verified artifacts. A valid shared preview identity was independently accepted as `SELECTED`. |
| Existing positive, deterministic replay, finite-budget, opt-in, duplicate, lineage, and no-production tests remain green | PASS | Independent focused/R01 plus retained M07/M08 run: `106 passed in 21.41s`. |
| Full pytest, compileall, Godot, diff/protected checks and truthful unavailable reporting | PASS | Independent full suite: `1086 passed, 2 skipped in 568.30s`; skips are the documented unavailable canonical ScrubBots bridge capabilities. Compileall and Godot 4.7.2 headless boot exited 0; diff/protected checks passed. |
| Offline and production isolation preserved | PASS | No runtime network/provider/API-key/telemetry/cloud generation/publication path was added; the module remains absent from the production router and CLI. |

## BUILDER CLAIMS VS REPOSITORY TRUTH

The R01 CODEX log truthfully records the authorized scope, separate
implementation/log publication, test totals, offline review, exact SHAs, and
`AWAITING_CHATGPT_AUDIT`. Its statement that optional artifacts are
candidate-specific is not enforced by the published identity-field list. The
log's retained-test command contains a documentation placeholder for the
explicit M07 file list, but the retained tests and full suite were independently
reproduced.

## FILE / SYMBOL EVIDENCE

- The versioned policy and field list are defined in [`evolutionary_selection.py`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/c2372997bd8a1fc10c280c6b0a9091e168c2d135/src/scrubbots_pixel_factory/evolutionary_selection.py#L20-L43).
- `_validate_candidates()` enforces only the fields in that list at [`L131-L168`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/c2372997bd8a1fc10c280c6b0a9091e168c2d135/src/scrubbots_pixel_factory/evolutionary_selection.py#L131-L168).
- `CandidateEvidence` defines optional preview and mutation identities at [`m08_batch.py#L173-L193`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/c2372997bd8a1fc10c280c6b0a9091e168c2d135/src/scrubbots_pixel_factory/m08_batch.py#L173-L193), and `verify_artifact_set()` verifies them when present at [`L480-L491`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/c2372997bd8a1fc10c280c6b0a9091e168c2d135/src/scrubbots_pixel_factory/m08_batch.py#L480-L491).
- The selector calls that verification boundary before ranking at [`evolutionary_selection.py#L300-L368`](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/c2372997bd8a1fc10c280c6b0a9091e168c2d135/src/scrubbots_pixel_factory/evolutionary_selection.py#L300-L368).

## FOCUSED TEST EVIDENCE

- Independent focused/R01 and retained M07/M08 command: `python -m pytest -q -p no:cacheprovider` over the R01, M08, and explicit M07 test files -> `106 passed in 21.41s`.
- Independent contract probe created two valid candidates with the same
  `preview_ref` and `preview_digest`, supplied the matching shared bytes, and
  called the live selector with the exact opt-in. Result: `SELECTED`; reason:
  `experimental selection completed over accepted evidence identities`.
- This directly reproduces the remaining policy defect before ranking, while
  the R01 missing/stale required-byte tests pass.

## REGRESSION EVIDENCE

- Independent full suite: `1086 passed, 2 skipped in 568.30s (0:09:28)`.
- Skips: `test_sb_lf03_002_compact_solver_state.py` and
  `test_sb_lf04_012_regression.py`; both report unavailable canonical ScrubBots
  checkout capability and no bridge was exercised.
- `python -m compileall -q src tests`: PASS.
- `godot_console.exe --headless --editor --path . --quit`: PASS,
  Godot `4.7.2.stable.official.ed1daf0bf`, exit 0.
- Published R01 range `git diff --check`: PASS; `TASKS.md`, audits, and active
  prompt protected-file checks: PASS.

## SECURITY / SAFETY / OFFLINE REVIEW

No network, provider, telemetry, API-key, runtime HTTP, cloud image-generation,
production-router, or publication integration was added. The remaining defect
is an evidence-identity fail-open condition, not a new network boundary.

## ARCHITECTURE CONSISTENCY

The M08 verification boundary is correctly reused and the experimental selector
remains isolated from generation/publication. The identity policy is not yet
complete for the full `CandidateEvidence` artifact surface: optional artifacts
can be verified individually while being implicitly shared across candidates.

## TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

The builder did not edit tracker or audit ownership files and ended with the
required independent-audit marker. This audit retains the product implementation
and advances only the authorized lifecycle state to a bounded R02 remediation.

## FINAL REPOSITORY STATE

Audited `origin/main` is `c2372997bd8a1fc10c280c6b0a9091e168c2d135`. The canonical
owner mirror remains untouched with its pre-existing dirty/behind work. This
audit publication adds only the audit, R02 prompt/criteria, and tracker lifecycle
update.

## OPEN CROSS-MILESTONE FINDINGS

No M10, Content Platform, main-game runtime, provider, native-device, physical,
owner-subjective, or unavailable-bridge acceptance was attempted or claimed.

## DEFECTS BY SEVERITY

### MAJOR — LF09-001-R01-AUD-001: optional artifact identities are implicitly shareable

Affected symbols: `CANDIDATE_ARTIFACT_IDENTITY_FIELDS`, `_validate_candidates()`,
and `run_experimental_evolutionary_selection()` in
`evolutionary_selection.py`; corresponding optional fields are in
`m08_batch.CandidateEvidence`.

Current behavior: two valid candidates may carry the same
`preview_ref`/`preview_digest` (and the same gap exists for mutation identity),
pass M08 byte verification, and be selected together. The versioned policy and
immutable selection provenance do not declare a shared-identity exception.

Required behavior: enumerate the complete artifact identity policy. Candidate-
specific optional identities must be rejected on collision; any intentionally
shareable identity must be named in the versioned policy and immutable
provenance and covered by a positive test.

## TECHNICAL DEBT / UPGRADE OPPORTUNITIES

The experimental lane remains a deterministic bounded selector rather than a
fitness-producing evolutionary engine; that is outside this remediation and
remains reserved for later authorized M09 work.

## UNVERIFIED ITEMS

- No owner-only, visual, physical, native-device, clean-machine, or external
  canonical-game bridge gate was available or converted to acceptance.
- No production publication was executed or required.

## REGRESSION RISK

R02 should remain narrow: complete the selector's artifact-identity policy and
tests only. The principal risk is accidentally introducing implicit sharing or
touching accepted M00-M08 contracts and production paths.

## AUDIT CONFIDENCE

High. The remaining defect was independently reproduced against the published
live head, and the required regression gates were independently executed.

## FINAL VERDICT

**CHANGES_REQUIRED** — R01 is not eligible for PASS/CLOSED until the complete
cross-candidate artifact identity policy is explicit, enforced, tested, and
independently re-audited.

## REQUIRED REMEDIATION

Proceed only with the bounded R02 prompt and criteria published alongside this
audit:

- [R02 remediation prompt](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/c2372997bd8a1fc10c280c6b0a9091e168c2d135/.hiveai/prompts/SB-LF09-001-C001-R02_COMPLETE_CROSS_CANDIDATE_ARTIFACT_IDENTITY_REMEDIATION_PROMPT.md)
- [R02 audit criteria](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/c2372997bd8a1fc10c280c6b0a9091e168c2d135/.hiveai/audit-criteria/SB-LF09-001-C001-R02_COMPLETE_CROSS_CANDIDATE_ARTIFACT_IDENTITY_AUDIT_CRITERIA.md)
