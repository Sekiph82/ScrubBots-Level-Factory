# SB-LF09-001-C001 — Experimental Evolutionary Selection

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## VERDICT

**CHANGES_REQUIRED**

The implementation is bounded, deterministic, explicitly opt-in, offline, and
isolated from production generation/publication. The strict evidence boundary is
not yet closed: selection can accept an evidence record whose referenced bytes
are unavailable, and it does not reject all cross-candidate reuse of
per-candidate artifact identities.

## CONTRACT RECOVERY

- Repository: `Sekiph82/ScrubBots-Level-Factory`
- Branch: `main`
- Live audited head: `b1c304701a422bb5b02f096576b58db84e57264b`
- Prompt: [SB-LF09-001-C001 prompt](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/b1c304701a422bb5b02f096576b58db84e57264b/.hiveai/prompts/SB-LF09-001-C001_EXPERIMENTAL_EVOLUTIONARY_SELECTION_PROMPT.md)
- Criteria: [SB-LF09-001-C001 strict criteria](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/b1c304701a422bb5b02f096576b58db84e57264b/.hiveai/audit-criteria/SB-LF09-001-C001_EXPERIMENTAL_EVOLUTIONARY_SELECTION_AUDIT_CRITERIA.md)
- Implementation: `6e1097bfb49801c6e89fc54d6db7fa9e8d7ebb15`
- Builder log publication: `b0e312145fa0b752f130f7e05213f16b13c6a288`
- Final handoff: `b1c304701a422bb5b02f096576b58db84e57264b`
- Builder log: [published CODEX log](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/b1c304701a422bb5b02f096576b58db84e57264b/.hiveai/codex-logs/SB-LF09-001-C001_EXPERIMENTAL_EVOLUTIONARY_SELECTION_CODEX_LOG.md)
- Previous audit: [SB-LF08-C001-R01 strict audit summary](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/b1c304701a422bb5b02f096576b58db84e57264b/.hiveai/audits/SB-LF08-C001-R01_STRICT_AUDIT_SUMMARY.md)

## BRANCH / HEAD / DIFF SCOPE

The canonical owner mirror was dirty and 34 commits behind at audit start. It
was not reset, synchronized in place, cleaned, stashed, rebased, or otherwise
disturbed. Audit evidence was read from fetched live `origin/main`; controller
publication used an isolated worktree of the same canonical repository.

The authorized implementation diff from `4ee246a8391c97123ebfdde7c319b4500d864866`
contains only:

- `src/scrubbots_pixel_factory/evolutionary_selection.py`
- package exports in `src/scrubbots_pixel_factory/__init__.py`
- `tests/unit/test_sb_lf09_001_evolutionary_selection.py`

The implementation commit does not change `TASKS.md`, prompts, or audits.
`git diff --check` passed for the implementation through finalized handoff.

## ACCEPTANCE CRITERIA MATRIX

| Criterion | Result | Evidence |
| --- | --- | --- |
| Versioned evolutionary-selection prototype | PASS | `SELECTION_SCHEMA`, `SELECTION_VERSION`, and `SELECTION_POLICY_VERSION` in `evolutionary_selection.py`; focused positive test passes. |
| Explicit opt-in and production isolation | PASS | Exact `EXPERIMENTAL_EVOLUTIONARY_SELECTION_V1` gate; default invocation returns `OPT_IN_REQUIRED`; no router/CLI integration. |
| Deterministic replay for same input/policy/seed | PASS | Canonical input ordering, policy digest, deterministic SHA-256 ranking; focused replay test passes. |
| Finite population/generation/evaluation budgets | PASS | Positive integer policy bounds and pre-selection `len(candidates) * generations` budget check; focused budget test passes. |
| Immutable candidate/source lineage preservation | PASS | Selector consumes frozen `CandidateEvidence`; M08 constructor binds all lineage fields; selected provenance records lineage digests. |
| Missing/unavailable/invalid evidence fails closed | FAIL | `None` and malformed candidate objects fail closed, but no artifact map is accepted or verified. A valid `CandidateEvidence` with an unavailable referenced record is selected. |
| Duplicate and cross-candidate evidence fails closed | FAIL | Candidate, lineage, bundle, and generation-result collisions are rejected, but shared M03/M04/M05/source/request/metadata identities can be accepted after recomputing a valid lineage digest. |
| No source-art mutation, gate bypass, or production promotion | PASS | Module only ranks existing evidence; no mutation, generation-router, publication, or promotion path. Static isolation checks and focused test pass. |
| Required focused tests | PARTIAL | Builder added nine focused tests; all pass, but the missing-byte and complete cross-candidate identity cases are absent. |
| Retained regressions, compileall, Godot, diff/protected checks | PASS | Independent retained suite `85 passed`; full suite `1074 passed, 2 skipped`; compileall, Godot 4.7.2 headless editor boot, and diff-check pass. The two skips are pre-existing unavailable canonical ScrubBots bridge capabilities. |

## BUILDER CLAIMS VS REPOSITORY TRUTH

The builder log truthfully records the authorized scope, separate implementation
and log publication, focused/full results, offline review, and `AWAITING_CHATGPT_AUDIT`.
The claimed `1074 passed, 2 skipped` full result was independently reproduced.
The builder did not claim acceptance or modify tracker/audit ownership files.

## FILE / SYMBOL EVIDENCE

- `run_experimental_evolutionary_selection()` returns `OPT_IN_REQUIRED` unless
  the exact opt-in token is supplied, then validates typed `CandidateEvidence`.
- `_validate_candidates()` rejects duplicate candidate IDs, lineage digests,
  bundle digests, and generation-result digests.
- `m08_batch.verify_artifact_set()` is the existing canonical byte/reference
  verification boundary, but the new selector neither receives an artifact map
  nor invokes that boundary.
- `CandidateEvidence` validates hash shape and lineage digest recomputation, but
  its references are portable strings; reference existence and bytes are not
  proven by its constructor alone.

## FOCUSED TEST EVIDENCE

Independent reproduction:

- `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf09_001_evolutionary_selection.py`
  -> `9 passed in 1.30s`.
- Additional probe: valid candidates sharing each of
  `m03_digest`, `m04_digest`, `m05_digest`, `source_provenance_digest`,
  `generation_request_digest`, and `generation_metadata_digest` all returned
  `SELECTED` rather than `INVALID_INPUT`.
- Additional probe: a valid candidate whose `generation_result_ref` points to
  an unavailable `missing-record.json` returned `SELECTED`.

One initial retained-test command used a PowerShell wildcard that pytest treated
as a literal missing path; this was corrected by explicit file enumeration and
the corrected command passed `85 passed in 6.36s`.

## REGRESSION EVIDENCE

- Full independent suite: `1074 passed, 2 skipped in 522.34s`.
- Skips: unavailable canonical ScrubBots checkout capability in
  `test_sb_lf03_002_compact_solver_state.py` and
  `test_sb_lf04_012_regression.py`; no bridge was exercised.
- `python -m compileall -q src tests`: PASS.
- `godot_console.exe --headless --editor --path . --quit`: PASS,
  Godot `4.7.2.stable.official.ed1daf0bf`.
- `git diff --check`: PASS.

## SECURITY / SAFETY / OFFLINE REVIEW

No network, provider, telemetry, API-key, or runtime HTTP behavior was added.
The module uses only standard-library dataclass, JSON, and SHA-256 logic. The
missing-byte finding is an evidence-integrity fail-closed issue, not a network
dependency.

## ARCHITECTURE CONSISTENCY

The public package export is consistent with the experimental module and does
not make the path reachable from the production router or CLI. The selector is
appropriately separate from generation and publication, but the evidence
verification boundary must be explicit before this research result can be
trusted as a selection over accepted immutable artifacts.

## TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

The live tracker authorized the task as `READY_FOR_IMPLEMENTATION` and was not
updated by the builder. The matching log is complete through final publication
and ends with the independent audit pending. This audit changes the tracker to
the bounded R01 remediation state; no builder-owned file is rewritten.

## FINAL REPOSITORY STATE

Before controller publication, live `origin/main` was
`b1c304701a422bb5b02f096576b58db84e57264b`. The dirty canonical mirror remains
untouched, including its pre-existing product/control-plane changes and stashes.

## OPEN CROSS-MILESTONE FINDINGS

No M10, Content Platform, main-game runtime, provider, native-device, physical,
owner-subjective, or unavailable bridge acceptance was attempted or claimed.

## DEFECTS BY SEVERITY

### BLOCKER — LF09-001-AUD-001: unavailable referenced evidence is selectable

Affected symbol: `run_experimental_evolutionary_selection()` and its input
contract in `evolutionary_selection.py`.

Current behavior: a syntactically valid `CandidateEvidence` with a reference to
an unavailable artifact is accepted and can be selected because the selector
does not verify referenced bytes or receive a verified artifact-set result.

Required behavior: missing, unavailable, or stale required evidence must return a
closed non-selected disposition before ranking. The contract must use the
canonical `verify_artifact_set()` boundary or an equivalent typed verified
evidence input, with deterministic provenance for the verification result.

### MAJOR — LF09-001-AUD-002: incomplete cross-candidate identity rejection

Affected symbol: `_validate_candidates()`.

Current behavior: only candidate ID, lineage digest, bundle digest, and
generation-result digest collisions are rejected. Other per-candidate artifact
identities can be reused across distinct candidates while preserving a newly
recomputed lineage digest.

Required behavior: define and enforce the complete allowed identity-sharing
policy. For identities that are candidate-specific, reject collisions across all
required artifact digests/references; if a field is intentionally shareable,
encode that exception in the versioned policy and provenance rather than relying
on an implicit omission.

## TECHNICAL DEBT / UPGRADE OPPORTUNITIES

The current hash ranking is a deterministic bounded research selector rather than
a mutation-producing evolutionary engine. That remains within this prototype's
scope, but future fitness work must be separately authorized under SB-LF09-002
and must not be smuggled into this remediation.

## UNVERIFIED ITEMS

- No owner-only, visual, physical, native-device, clean-machine, or external
  canonical-game bridge gate was available or required for this task; none is
  converted to acceptance.
- The audit did not execute a production publication because the implementation
  is required to remain isolated from it.

## REGRESSION RISK

R01 should be narrow: changing only the experimental selector contract,
associated focused tests, and its matching builder evidence. The primary risk is
accidentally importing artifact publication or provider behavior into the
experimental lane.

## AUDIT CONFIDENCE

High for the source, commit scope, focused/full tests, offline isolation, and the
two directly reproduced evidence-boundary defects. Medium for the final policy
choice about intentionally shareable artifact identities; R01 must make that
choice explicit and test it.

## FINAL VERDICT

**CHANGES_REQUIRED** — product implementation is retained, but SB-LF09-001 is
not eligible for PASS/CLOSED until both evidence-boundary defects are remediated
and independently re-audited.

## REQUIRED REMEDIATION

Use the bounded prompt and criteria published with this audit:

- [R01 remediation prompt](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/57095e5edcd74c08abf268d5a029ef674ef41bbf/.hiveai/prompts/SB-LF09-001-C001-R01_EVIDENCE_AVAILABILITY_AND_CROSS_CANDIDATE_REMEDIATION_PROMPT.md)
- [R01 audit criteria](https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/57095e5edcd74c08abf268d5a029ef674ef41bbf/.hiveai/audit-criteria/SB-LF09-001-C001-R01_EVIDENCE_AVAILABILITY_AND_CROSS_CANDIDATE_AUDIT_CRITERIA.md)
