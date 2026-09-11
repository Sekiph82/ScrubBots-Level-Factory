# PAG-M10-C002 — Executed Property Corpus, Performance Methodology & Release Evidence Remediation
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. VERDICT

FAIL

PAG-M10-C002 materially closes the C001 execution, benchmark, metrics, release-matrix and log-start defects, but two MAJOR residual acceptance defects remain. M10 must not proceed to owner visual review yet.

Open findings:

- `F-PAG-M10-C002-001` — owner-review HTML canvas-to-candidate binding is wrong for MEDIUM/HARD after regrouping;
- `F-PAG-M10-C002-002` — the executed 2,018-case property corpus does not replay every successful request as required by the C002 acceptance contract.

No M00-M09 production algorithm redesign is required. Remediation is bounded to the M10 evidence/review layer.

## 2. CONTRACT RECOVERY

Authoritative remediation prompt:
`.hiveai/prompts/PAG-M10-C002_EXECUTED_PROPERTY_CORPUS_PERFORMANCE_METHODOLOGY_AND_RELEASE_EVIDENCE_REMEDIATION_PROMPT.md`

Previous strict audit:
`.hiveai/audits/PAG-M10-C001_VALIDATION_PERFORMANCE_AND_V1_REVIEW_PACK_PREPARATION_STRICT_AUDIT.md`

C002 was required to close five C001 findings while preserving the accepted M00-M09 production algorithms and reserving `PAG-1033`, `PAG-1034`, `PAG-1050`, `PAG-0441` and `PAG-1048` from builder self-acceptance.

## 3. BUILDER BOUNDARY / COMMITS / DIFF

Repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`

C002 authority tip after the ChatGPT reconciliation note:
`76a5375f1df0a96b6bcdbf720ac8d62a5eb4f88d`

Implementation/artifact commit:
`36c964008c174b2ec090647bda2176e926dfafca`

Completed-log commit:
`737a6da55c853fe29ec65574dab71cbea739cc4f`

Terminal builder-era checkpoint commit:
`4e11a3e62d3e3827cc654c4a9b0a9f7fbaf9edfe`

Independent compare is 3 commits ahead, 0 behind. Scope is limited to the matching C002 log, M10 tool/tests and `review/m10/**`. Root `TASKS.md`, M03-M09 production algorithms and M11 were not changed by the builder.

## 4. FINDING SUMMARY

- BLOCKER: 0
- MAJOR: 2
- MINOR: 0
- NOTE: 2

C001 disposition:

- `F-PAG-M10-C001-001` actual corpus execution: substantially closed, residual reproducibility completeness continues as C002-002;
- `F-PAG-M10-C001-002` distinct benchmark methodology: CLOSED;
- `F-PAG-M10-C001-003` review attempt/diversity/metrics evidence: CLOSED except the newly introduced owner-HTML binding defect C002-001;
- `F-PAG-M10-C001-004` PAG-1035..1049 gate matrix: CLOSED;
- `F-PAG-M10-C001-005` builder-log pre-edit chronology: CLOSED.

## 5. EXECUTED PROPERTY CORPUS

The corpus now contains 2,018 valid deterministic requests and the execution report records 2,018 executed cases. Builder evidence reports 1,988 successes, 30 bounded `RETRY_EXHAUSTED` outcomes, zero successful-result contract defects and 9/9 invalid cases rejected without uncontrolled traceback.

The corpus is honestly weighted toward MASK to keep the thousands-case validation practical while retaining RULES, HYBRID, AUTO, technical synthetic WFC, all four difficulty bands, square/rectangular/auto dimensions and explicit 59x59 cases. This weighting is permitted by the C002 prompt.

For every successful first execution, the tool validates dimensions, cell count, canonical logical palette, difficulty used-color count, ascending actual used palette and absence of BG01.

## 6. F-PAG-M10-C002-002 — FULL-CORPUS REPRODUCIBILITY IS NOT EXECUTED

Severity: MAJOR

The C002 prompt requires every successful result in the executed property corpus to directly validate same-request reproducibility.

`execute_property_corpus()` executes all 2,018 advertised requests once, but replay is explicitly bounded to only the first two successful cases in each mode/difficulty bucket:

`if bucket["reproducibility_checks"] < 2:`

Therefore the majority of the 1,988 successful corpus requests are never regenerated and compared during the advertised M10 property execution.

The report field `reproducibility_mismatch_count == 0` means only that the small replay-probe subset had zero mismatches. It must not be interpreted as proving repeatability for all successful executed corpus cases.

Required closure: replay every successful advertised case through the canonical generation surface and compare a deterministic canonical result identity (at minimum result digest plus grid hash and success state). The committed execution report must expose `successful_result_count`, `reproducibility_check_count`, and prove equality of those counts with zero mismatches.

## 7. INVALID-CORPUS ROBUSTNESS

PASS.

C002 executes nine invalid request/CLI cases including dimension boundaries, unsupported difficulty/mode, invalid seed type, malformed options, palette/difficulty conflict and malformed generate/batch CLI invocations. The report records all rejected without traceback.

## 8. DISTINCT PERFORMANCE METHODOLOGY

PASS for C001 remediation scope.

The new benchmark manifest contains 404 distinct request/config cases across 29 groups. MASK, RULES and both non-WFC HYBRID review strategies use 20 distinct cases per difficulty; technical WFC uses 10 per difficulty; both WFC-bearing HYBRID strategies are measured at all four difficulties with bounded distinct cases.

Warmups are separated from measured samples, request digests are unique within groups, failures/retry exhaustion remain in the denominator, and raw per-case timing/memory/status evidence is retained.

## 9. PAG-0441 / RULES 59x59 DATASET

PASS as measured evidence preparation, not final task acceptance.

The dedicated RULES 59x59 group contains 20 distinct requests. The committed report records approximately:

- median: 2.7465024 s;
- nearest-rank p95: 9.9004345 s;
- measured max: 11.2720329 s;
- peak Python tracemalloc memory: 806,102 bytes;
- proposed time budget: 14.85065175 s.

The proposed budget remains explicitly non-owner-approved and `PAG-1048` remains pending independent acceptance, as required.

## 10. PERFORMANCE-BUDGET SEMANTICS

PASS for C002 preparation.

The budget proposal is now based on a distinct deterministic request distribution rather than repeated timing of one request. Measured maximum remains visible. The 50% p95 headroom is identified as a proposal only, not a proof of acceptance.

## 11. REVIEW SELECTION / ATTEMPT LEDGER

PASS.

The 100-candidate pack remains exactly 25 per difficulty and all candidates remain `PENDING_OWNER_REVIEW`. The selector now uses the documented `m10-review-root-v2` deterministic namespace, bounded per-slot attempts, and records all attempts.

The committed metrics report records 122 total attempts, 100 accepts, 22 `RETRY_EXHAUSTED` rejections and zero exact duplicates. No grid mutation/resizing/interpolation is claimed or used.

## 12. DIVERSITY / STRUCTURAL METRICS

PASS for C001 remediation scope.

`M10_METRICS_REPORT.json` now includes structural metric summaries, occupancy-mask similarity and color-layout similarity separately, near-duplicate evidence, nearest-neighbor evidence, family/recipe/strategy counts, rejection-code distribution, duplicate relations and the full attempt ledger.

The Markdown report exposes 80 comparable pairs, occupancy median similarity about 0.2995 and color-layout median similarity about 0.04183.

## 13. F-PAG-M10-C002-001 — OWNER HTML DRAWS THE WRONG GRIDS FOR MEDIUM/HARD

Severity: MAJOR

The review entries are sorted lexicographically by `candidate_id` before HTML creation. That produces difficulty blocks in lexical candidate order:

`EASY`, `HARD`, `MEDIUM`, `VERY_HARD`.

The HTML builder then regroups the already-built cards using `DIFFICULTIES`, whose order is:

`EASY`, `MEDIUM`, `HARD`, `VERY_HARD`.

This changes DOM canvas order without changing the embedded `pack.entries` array order.

The JavaScript renders with positional binding:

`document.querySelectorAll('canvas').forEach((canvas,i) => { const e=pack.entries[i]; ... })`

Consequently:

- EASY cards receive EASY grids;
- MEDIUM cards are drawn from the HARD segment of `pack.entries`;
- HARD cards are drawn from the MEDIUM segment;
- VERY_HARD cards receive VERY_HARD grids.

The visible card text, candidate ID and printed grid hash remain the card's own values, while the canvas may show another candidate's logical grid. This is unacceptable for owner visual review because the owner could approve/reject the wrong artwork.

The current HTML test does not catch the defect because it checks candidate ID/hash/status text inside each card, not the actual JavaScript canvas data binding.

Required closure: bind every canvas by stable candidate identity, never by cross-group positional index. For example, give each canvas a `data-candidate` value and render from a `candidate_id -> entry` map. Add a machine test proving every rendered card/canvas resolves to the same candidate ID/grid hash as that card for all 100 entries, including MEDIUM and HARD.

## 14. OWNER-REVIEW STATUS BOUNDARY

PASS.

All 100 owner states remain `PENDING_OWNER_REVIEW`. No builder approval is recorded. WFC visuals remain explicitly skipped because no owner-approved production exemplar exists.

Owner review must still not begin until C002 residual findings are closed and a subsequent independent technical PASS is issued.

## 15. RELEASE-GATE MATRIX

PASS for C001 remediation scope.

The matrix now enumerates every machine release gate `PAG-1035` through `PAG-1049` individually and separates owner-only gates. `PAG-1044` is explicitly synthetic-fixture technical evidence only, and `PAG-1048` remains `PENDING_INDEPENDENT_ACCEPTANCE`.

## 16. THIRD-PARTY ATTRIBUTION REAUDIT

PASS for C001 remediation scope.

The report now records all four pinned reference projects individually, their pinned commit/source, notice status, copied/adapted-source status and stale/missing/extra findings. No new dependency or artwork is introduced.

## 17. TEST / RUNTIME EVIDENCE

Builder reports:

- focused C002/M10 evidence tests: 31 passed;
- full repository: 378 passed, 1 pre-existing pytest-cache warning;
- compileall: PASS;
- package import: PASS;
- module CLI help: PASS;
- installed CLI help: PASS;
- `git diff --check`: PASS;
- offline/source scan: PASS.

GitHub exposes no CI statuses or workflow runs for terminal builder HEAD.

Independent runtime replay could not be started because the audit container cannot resolve `github.com`. Runtime execution is therefore independently UNVERIFIED. This is not the reason for FAIL.

## 18. BUILDER-LOG / PUBLICATION PROCESS

C001 chronology finding is CLOSED. The C002 matching builder log records a real start timestamp, synchronized start HEAD/origin `2496e929...`, divergence `0 0`, local dirt and explicitly states the log was created and verified before C002 source/test/report edits.

NOTE: after completed-log publication at `737a6da...`, equality was checked and then recorded by a final log-only commit `4e11a3e...`. The repository log does not itself contain a post-`4e11a3e...` equality record. This is a small publication-recursion process limitation, not an M10 product acceptance defect.

## 19. REQUIRED REMEDIATION

Create bounded `PAG-M10-C003` only for the two residual findings:

1. replay every successful property-corpus case and prove full successful-case reproducibility coverage;
2. repair owner HTML canvas binding to stable candidate identity and add a direct 100-card visual-data binding test.

Preserve the accepted C002 distinct benchmark data, 20-case RULES 59x59 dataset, metrics ledger/diversity reports, gate matrix, attribution evidence and current 100 immutable logical review grids unless the HTML binding repair itself requires no logical-grid changes.

Do not begin M11. Do not start owner visual acceptance yet.

## 20. FINAL DISPOSITION

PAG-M10-C002: FAIL / FIX_REQUIRED.

M10 remains open. `PAG-1033`, `PAG-1034`, `PAG-1050`, `PAG-0441` and `PAG-1048` remain unaccepted. M11 remains blocked.

Next authorized cycle must be a narrowly bounded M10 C003 remediation. No accepted M00-M09 production algorithm is reopened by this verdict.
