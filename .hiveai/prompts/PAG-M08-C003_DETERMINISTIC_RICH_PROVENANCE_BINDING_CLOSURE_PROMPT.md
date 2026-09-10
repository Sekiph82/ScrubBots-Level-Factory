# PAG-M08-C003 — Deterministic Rich Provenance Binding Closure
Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`

Previous strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M08-C002_PROVENANCE_BINDING_RECTANGULAR_GOLDEN_AND_STRICT_PNG_REMEDIATION_STRICT_AUDIT.md`

Previous builder log:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/PAG-M08-C002_PROVENANCE_BINDING_RECTANGULAR_GOLDEN_AND_STRICT_PNG_REMEDIATION_CODEX_LOG.md`

Canonical current task tracker:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/TASKS.md`

## 1. Mission

Close only `F-PAG-M08-C002-001 — Rich provenance accepts deterministic attempt/stage histories that contradict authoritative result provenance.`

C002 already closed the rectangular row-major/committed rectangular golden finding and the strict empty-IEND finding. Preserve those fixes and all accepted C001/C002 architecture. Do not redesign JSON, PNG, preview, filesystem, quality binding, candidate identity or generator production code. PAG-M09+ remains out of scope.

## 2. Current tracking authority

The repository has undergone the H!veAI tracker migration. Root `TASKS.md` is the only current project-status tracker. Do not revive hidden legacy tracker files as competing current state. Historical prompts, builder logs and independent audits under `.hiveai/prompts/`, `.hiveai/codex-logs/` and `.hiveai/audits/` remain valid evidence records.

Codex is builder only. Do not mark M08 accepted/complete and do not author an independent audit. ChatGPT will update root `TASKS.md` after audit.

## 3. GitHub-first start

Before edits read from GitHub `main`: root `TASKS.md`; `AGENTS.md`; `GOVERNANCE.md`; C001 prompt/audit/log; C002 prompt/audit/log; current `output/bundle.py`; M08 tests; M05 WFC retry contract; M06 HYBRID stage/seed/replay contract; M06 AUTO attempt/seed/fallback contract; and this prompt.

Authorized local mirror only: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
Never use or modify: `C:\Users\sekip\Desktop\ScrubBots`.
Synchronize non-destructively only.

## 4. Matching builder log

Before the first C003 source/test edit create:
`.hiveai/codex-logs/PAG-M08-C003_DETERMINISTIC_RICH_PROVENANCE_BINDING_CLOSURE_CODEX_LOG.md`

Exact H1:
`# PAG-M08-C003 — Deterministic Rich Provenance Binding Closure`

Immediately below:
`Document role: CODEX BUILDER LOG`

Record starting HEAD/origin/status, authority reads, preserved local changes, each focused failure/correction, exact tests, diff scope, implementation commit, push, completed-log publication and final local HEAD == origin/main verification.

## 5. WFC successful-attempt binding

Current `_validate_wfc_metadata()` range-checks `attempt` but does not bind it to exported `GenerationResult.rng.provenance.retry_seeds`.

For successful WFC metadata require the directly reconstructible relation:
- retry keys exactly `"0"..str(attempt)`;
- exactly `attempt + 1` retry seeds;
- successful metadata `attempt` equals the final retry attempt represented by result provenance;
- keep existing GenerationResult/request RNG semantics authoritative.

Strengthen contradiction history:
- attempt 0 => empty history;
- attempt N > 0 => exactly N prior contradiction records;
- record attempt indices exactly `0..N-1` in order;
- do not recompute non-reconstructible detail text.

## 6. HYBRID outer-attempt binding

Bind `outer_attempt` to successful result retry provenance:
- keys exactly `"0"..str(outer_attempt)`;
- count exactly `outer_attempt + 1`.

Do not invoke the full hybrid replay engine from M08.

## 7. HYBRID strategy-specific stage layout

Validate exact ordered `(stage_name, stage_kind)` by strategy:
- `MASK_GEOMETRY_RULE_COLOR_REGIONS` => `[(MASK_GEOMETRY, MASK), (RULE_COLOR_REGIONS, COMPOSITION)]`
- `RULE_GEOMETRY_MASK_SYMMETRY` => `[(RULE_GEOMETRY, RULES), (MASK_SYMMETRY_COLOR_REGIONS, COMPOSITION)]`
- `RULE_BASE_WFC_DETAIL` => `[(RULE_BASE, RULES), (WFC_DETAIL, WFC)]`
- `MASK_BASE_WFC_DETAIL` => `[(MASK_BASE, MASK), (WFC_DETAIL, WFC)]`

Reject unknown strategy/layout/name/kind combinations. Bind each child request generator mode to the accepted stage semantics, including the existing synthetic RULES child request used by COMPOSITION stages.

## 8. HYBRID deterministic stage-seed binding

Re-derive each stage seed using the exact accepted M06 path:
`hybrid/{strategy}/{outer_attempt}/{stage_index}/{stage_name}`
with the existing project `DeterministicRNG` / M06 derivation semantics.

For every stage require:
- recorded index equals ordered index;
- recorded `derived_seed` equals exact deterministic rederived seed;
- child request typed seed equals the same seed;
- existing child-request digest remains valid;
- width/height/palette checks remain valid.

Do not copy the full M06 replay algorithm. This is metadata identity validation only.

## 9. AUTO retry-provenance coherence

C002 already validates AUTO candidate order, initial selection, attempt order and deterministic stage seeds. Complete result-provenance binding:
- retry keys exactly contiguous `"0"..str(len(attempts)-1)`;
- retry count equals recorded attempt count;
- preserve early-success prefix semantics.

Do not add child-generator replay.

## 10. Required negative tests

Add focused tests that fail against C002 and pass after C003. At minimum reject:
1. WFC `attempt` changed while result retry provenance is unchanged;
2. WFC contradiction history missing a required prior attempt;
3. WFC contradiction history duplicate/out-of-order attempt indices;
4. WFC target palette or output dimensions tampered, satisfying the missing C002 mandatory second WFC binding evidence gate;
5. HYBRID `outer_attempt` changed while result retry provenance/stages remain unchanged;
6. HYBRID stage name illegal for strategy;
7. HYBRID stage kind illegal for strategy;
8. HYBRID `derived_seed` + child-request seed + child-request digest changed together to an internally self-consistent but non-deterministic value;
9. HYBRID child request generator mode contradictory to its stage contract;
10. AUTO attempt count inconsistent with result retry provenance.

Retain positive tests proving accepted WFC/HYBRID/AUTO wrappers and explicit rich metadata round-trip.

## 11. Preserve accepted C002 evidence

Do not weaken or redesign:
- 20x21 rectangular row-major known-answer;
- committed rectangular JSON/PNG golden pair;
- valid-CRC non-empty IEND rejection;
- raw rich-result fail-closed policy;
- wrapper vs explicit metadata equivalence;
- wrong namespace rejection;
- exact logical PNG/preview semantics;
- M07 quality binding;
- deterministic filesystem writes;
- 59x59 support;
- cross-process determinism.

## 12. Scope boundary

Production edits should be narrowly limited to the M08 metadata verifier/documentation unless a directly related focused failing test proves another helper change is necessary. Do not modify M03-M07 generator production code. Do not add dependencies. Do not begin M09+.

## 13. Verification

Run and record: all C003 provenance tests; all M08 unit/integration/golden tests; WFC/HYBRID/AUTO positive round trips; rectangular golden; IEND negative test; 59x59; cross-process/PYTHONHASHSEED determinism; M01-M07 regressions; full pytest; `python -m compileall -q src tests`; standalone import; `git diff --check`; offline/no-resize/dependency static checks.

Record exact commands/counts and materially relevant failures/corrections.

## 14. Publication gate

Exit only when focused/full suites pass, no M09+ or unrelated generator change exists, implementation and matching C003 log are committed/pushed to `main`, and after log publication `git fetch origin main` proves local HEAD == origin/main with divergence `0 0`, recorded explicitly in the log. Then stop and return the C003 builder log for independent ChatGPT strict audit.