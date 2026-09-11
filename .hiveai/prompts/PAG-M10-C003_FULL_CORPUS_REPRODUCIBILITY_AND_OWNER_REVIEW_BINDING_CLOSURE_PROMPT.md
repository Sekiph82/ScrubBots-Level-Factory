# PAG-M10-C003 — Full Corpus Reproducibility & Owner Review Binding Closure
Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`

Previous strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M10-C002_EXECUTED_PROPERTY_CORPUS_PERFORMANCE_METHODOLOGY_AND_RELEASE_EVIDENCE_REMEDIATION_STRICT_AUDIT.md`

Previous builder log:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/PAG-M10-C002_EXECUTED_PROPERTY_CORPUS_PERFORMANCE_METHODOLOGY_AND_RELEASE_EVIDENCE_REMEDIATION_CODEX_LOG.md`

## 1. Mission

Close ONLY these two residual M10 findings:

- `F-PAG-M10-C002-001` — owner review HTML canvas rendering is positionally bound and currently draws HARD grids inside MEDIUM cards and MEDIUM grids inside HARD cards after difficulty regrouping;
- `F-PAG-M10-C002-002` — the >=2,000 property corpus is executed once, but same-request reproducibility is replayed only for the first two successes per mode/difficulty rather than every successful corpus case.

Preserve all accepted M00-M09 contracts and all C002 evidence that already passed strict audit.

Do not begin M11.
Do not begin owner visual acceptance.
Do not mark `PAG-1033`, `PAG-1034`, `PAG-1050`, `PAG-0441` or `PAG-1048` accepted.
Do not modify root `TASKS.md` acceptance/checkbox state.

## 2. Current authority and temporary tracker display

Root `TASKS.md` remains the canonical project-state tracker, but it may still display the older M10 C001 header because the independent auditor has deliberately avoided a risky whole-file replacement merely to update a few state lines.

The C002 strict audit `FAIL` plus this authoritative C003 prompt explicitly authorize this bounded C003 remediation. Codex MUST NOT edit root `TASKS.md` to reconcile that display lag.

## 3. Matching builder log is a hard pre-edit gate

Before the FIRST C003 source/test/report/review-artifact edit create:

`.hiveai/codex-logs/PAG-M10-C003_FULL_CORPUS_REPRODUCIBILITY_AND_OWNER_REVIEW_BINDING_CLOSURE_CODEX_LOG.md`

Exact H1:

`# PAG-M10-C003 — Full Corpus Reproducibility & Owner Review Binding Closure`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record actual current timestamp, GitHub/local HEAD, origin/main, divergence and local dirt. Verify this file exists before any C003 implementation edit.

## 4. Preserve the accepted C002 foundation

Do not rebuild or tune accepted production generators.

Preserve unless a purely evidence-layer serialization update is required:

- the deterministic >=2,000 property corpus definition;
- the C002 invalid corpus and 9/9 rejection evidence;
- the 404-case distinct benchmark manifest;
- all C002 raw benchmark measurements and summaries;
- the 20-distinct-case RULES 59x59 PAG-0441 dataset;
- the proposed-only performance budgets;
- the current 100 immutable logical review grids;
- exactly 25 EASY / 25 MEDIUM / 25 HARD / 25 VERY_HARD;
- the 122-attempt review selection ledger;
- 100 accepted / 22 rejection / zero exact-duplicate evidence;
- M07 structural/diversity metrics;
- `WFC_VISUAL_PACK_SKIPPED_NO_APPROVED_EXEMPLAR`;
- PAG-1035..1049 gate matrix;
- third-party attribution re-audit.

Do not change logical review grids merely to repair HTML rendering.

## 5. Close F-PAG-M10-C002-002: replay every successful corpus result

The committed property-validation execution must directly prove same-request reproducibility for EVERY successful advertised corpus case.

The current `reproducibility_checks < 2` per mode/difficulty sampling shortcut is not sufficient for this cycle.

For every corpus case whose first canonical execution succeeds:

1. regenerate the exact same canonical `GenerationRequest` through the accepted canonical generation surface;
2. require replay success;
3. compare the canonical `GenerationResult` identity using at minimum:
   - result digest;
   - logical-grid hash;
   - resolved dimensions;
   - generator ID/version where applicable;
4. fail the evidence-generation command immediately on any mismatch.

The committed `M10_PROPERTY_EXECUTION_REPORT.json` must expose unambiguously:

- `advertised_case_count`;
- `executed_case_count`;
- `successful_result_count`;
- `reproducibility_check_count`;
- `reproducibility_mismatch_count`;
- mode/difficulty replay counts;
- enough per-case replay binding to audit that every successful case, not merely a sample, was covered.

Required invariants:

`executed_case_count == advertised_case_count >= 2000`

`reproducibility_check_count == successful_result_count`

`reproducibility_mismatch_count == 0`

If valid first-run failures such as bounded `RETRY_EXHAUSTED` exist, keep them honestly recorded. They do not count as successful-case reproducibility checks unless you additionally choose to prove deterministic failure replay.

### Practical execution

You may parallelize the full replay to keep the run practical, but do not weaken correctness for speed.

Avoid unsafe shared mutable generator/router state across threads. Prefer a clearly isolated per-worker router/generator context if concurrency is used, or otherwise prove the chosen objects are safely stateless for concurrent execution.

Do not replace direct execution with a claim derived only from stored digests.

## 6. Close F-PAG-M10-C002-001: bind review canvases by candidate identity

The owner-facing HTML must never render a canvas from positional array index when cards can be reordered/grouped independently.

Repair `M10_REVIEW_INDEX.html` generation so every card/canvas carries a stable candidate identity and the drawing code retrieves the exact matching manifest entry by that identity.

Preferred pattern:

- each card and/or canvas has `data-candidate="<candidate_id>"`;
- JavaScript creates an explicit mapping such as `Map(candidate_id -> entry)`;
- for each canvas, read its own candidate ID and retrieve that exact entry;
- fail visibly or throw if the candidate ID is absent/duplicated rather than silently drawing a positional neighbor.

Do not rely on `querySelectorAll(...).forEach((canvas, i) => pack.entries[i])` or any equivalent cross-group positional binding.

Keep nearest-neighbor integer logical-cell rendering and `imageSmoothingEnabled=false`.

## 7. Direct owner-review binding tests

Add machine tests strong enough to catch the exact C002 defect.

At minimum prove for all 100 cards/canvases:

- exactly one stable candidate ID exists on the card/canvas;
- the 100 HTML candidate identities equal the 100 manifest candidate IDs exactly;
- every HTML candidate ID resolves to the same manifest entry/grid hash;
- the renderer uses candidate-ID lookup, not global positional index;
- MEDIUM canvas identities map to MEDIUM manifest entries;
- HARD canvas identities map to HARD manifest entries;
- rendered width/height comes from that exact candidate;
- card-local printed candidate ID/grid hash/status remain consistent with the exact bound entry;
- no external network/CDN/font/image/CSS dependency appears.

A test that only verifies card text/hash while ignoring the canvas data-binding mechanism is insufficient.

If practical, expose a small deterministic project-owned helper that returns the render payload for a candidate ID and unit-test it directly.

## 8. Deterministic regeneration

Regenerate the owner HTML from the unchanged logical manifest and prove deterministic byte stability for the HTML under the same C003 generator version/input.

Do not change the 100 immutable logical-grid hashes as part of this binding repair. Add a test comparing the C002 logical review manifest identity/grid-hash set before/after if a stable historical reference is already available in source; otherwise explicitly assert the current manifest remains unchanged by HTML-only regeneration within the C003 run.

## 9. C002 evidence regression

Rerun and preserve direct evidence that:

- 2,018 or later explicitly versioned >=2,000 corpus definitions are actually executed;
- invalid corpus remains rejected without traceback;
- distinct benchmark manifest remains distinct and complete;
- RULES 59x59 still has >=20 distinct measured cases;
- metrics remain 100 accepted and complete;
- release matrix still enumerates PAG-1035..1049;
- owner gates remain pending;
- attribution report remains complete.

Do NOT rerun expensive performance measurements solely to make timing numbers change if no benchmark code/evidence changed. If `tools/m10_prepare.py` necessarily re-executes the benchmark as part of a monolithic command, either retain truthful newly measured timing evidence or cleanly split deterministic review/property regeneration from performance measurement without fabricating cached measurements.

## 10. Required tests / verification

Run and record at minimum:

- full >=2,000 first-execution property corpus;
- full successful-case replay coverage with `reproducibility_check_count == successful_result_count`;
- zero reproducibility mismatches;
- invalid corpus regression;
- C002 distinct benchmark structure tests;
- C002 metrics/diversity tests;
- new all-100 candidate-ID/canvas binding tests;
- explicit MEDIUM/HARD binding regression test;
- owner HTML offline/self-contained scan;
- deterministic HTML regeneration/hash comparison;
- review manifest 100-grid hash preservation check;
- gate matrix and attribution regression;
- relevant M07/M08/M09 regressions;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- standalone package import;
- module CLI help;
- installed CLI help where practical;
- offline/dependency/source scan;
- `git diff --check`;
- final scoped diff/status.

## 11. Scope boundary

Expected C003 changes are limited to:

- `tools/m10_prepare.py` or a small focused M10 helper;
- M10 property/review tests;
- `review/m10/M10_PROPERTY_EXECUTION_REPORT.json` and deterministic review HTML/evidence where needed;
- matching C003 builder log.

Changes to M03-M09 production algorithms are NOT authorized.

Do not add runtime dependencies.
Do not add network access.
Do not begin M11.

## 12. Stop conditions

STOP and report rather than hiding the result if:

- full replay discovers any same-request mismatch;
- review logical grids would have to change to repair HTML binding;
- a M00-M09 production defect appears;
- owner HTML cannot be bound unambiguously by candidate ID;
- C002 benchmark/gate/attribution evidence regresses.

## 13. Completion / publication

Commit and push C003 normally to `main`.

Publish the completed matching builder log.

After publication fetch origin and record the latest equality checkpoint available before the final evidence-only log commit. If an additional final log-only commit records that equality, state the publication-recursion limitation truthfully rather than claiming an unrecorded post-final-commit check.

Do not edit root `TASKS.md`.
Do not self-audit.
Do not start owner review.

Stop after publication and return the C003 builder log for independent ChatGPT strict audit.
