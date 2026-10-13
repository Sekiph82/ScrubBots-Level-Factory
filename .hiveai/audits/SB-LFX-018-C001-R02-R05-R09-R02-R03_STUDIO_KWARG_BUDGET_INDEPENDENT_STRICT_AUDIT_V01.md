# R09-R02-R03 — Independent Strict Audit: Installed Python Keyword and Solver Budget Contract

Document role: CHATGPT INDEPENDENT AUDIT
Date: 2026-10-13. Repository: `Sekiph82/ScrubBots-Level-Factory` / `main`.
**Final verdict: CONDITIONAL.** The focused *source/installed-contract remediation* meets the requested technical gates on current GitHub source and detailed builder evidence. The actual owner's installed Studio native pipeline has **NOT** been run after this fix. Parent R05, CPX-002, Release Pool and R2 all remain OPEN.

## 1. VERDICT
**CONDITIONAL: API compatibility and bounded parameter wiring TECHNICAL PASS at code/focused-builder-evidence level; OWNER LIVE SOLVER/REPLAY/QA UNVERIFIED.** No new owner full native Studio run, and builder states 0 native solver and 0 shipping load-check invocations. Do not label task end-to-end PASS or Family APK readiness.

## 2. CONTRACT RECOVERY
Master `.hiveai/prompts/SB-LFX-018-C001-R02-R05-R09-R02-R03_STUDIO_REAL_TIMEOUT_AND_NATIVE_LIMIT_CONTRACT_REPAIR_MASTER_PROMPT.md` and matching `.hiveai/audit-criteria/...R03...md` require (a) diagnose screenshot `real_timeout` TypeError from ACTUAL installed Python imports, (b) update release code/keyword parity, (c) enforce 25,000 visit / 90s per-native limits in primary and independent load-check on selected original 002 with 3/4/5 columns, (d) true non-native bound-kwargs tests on installed code, (e) safe in-place Release update, and (f) no native solver or cloud write by Codex.

## 3. BRANCH / HEAD / DIFF SCOPE
GitHub product commit `17643de6756ba3d9552351eb237db19bd8d0c269` independently fetched and diff inspected. Changes: `factory_studio_exact_ui.gd`, `studio_extensions.py`, `supply_optimizer.py`, `scrubbots_solver.py`, `verify.py`, new `solver_budget.py`, plus one new Python and one new Godot focused suite. Builder-only R05 existing log commit `9233d95e1cee5beedbf7a80e89e552d296761fa3` fetched and inspected. Builder reports Desktop HEAD==origin/main, 0 ahead/behind after publication; ChatGPT did not access live Desktop Git or installed Release bytes.

## 4. ACCEPTANCE CRITERIA MATRIX
| Gate | Finding |
| --- | --- |
| Trace installed live module signatures and hashes | PASS via detailed builder command evidence, not independently executed on owner's Windows |
| Prove exact original screenshot `real_timeout` spelling provenance | UNVERIFIED: screenshot and correlated JSONL differ; builder reports no full traceback |
| Identify functional API mismatch causing pipeline TypeError | PASS: stale Release optimizer signature lacked current timeout keywords |
| Correct installed module/source signatures incl. verifier/solver | PASS via GitHub diff + builder post-install SHA/tests |
| Original 002 and selected 3/4/5 columns retained | PASS tracked UI + focused builder tests; 4 selected in owner screenshot |
| Explicit pinned real_max_visited=25000, timeout=90 | PASS tracked UI source; strict validator present |
| Independent load-check given same bounded values | PASS tracked `_run_canonical_artwork_route` source + focused fake verifier test |
| Invalid missing/NaN/boolean/string/out-of-range budget fail closed | PASS new strict `normalize_solver_budget` code + targeted builder test |
| **Actual native Godot Studio SOLVED/WIN/Difficulty/QA** | **NOT RUN** |
| Original immutable PNG/record and attested source kept | PASS per builder SHA evidence; no direct GPT disk verification |
| Desktop link launches safely updated Release | PASS per builder launch/proc/manifest evidence only |
| Owner final installed test and CPX-002/Release Pool/R2 | PENDING / NOT AUTHORIZED |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH
Builder's log documents *original installed* `supply_optimizer.py` `run_grid` signature ending in `progress=print`, missing `real_timeout_seconds` and `max_native_solver_invocations`, while installed `studio_extensions.py` already emitted `real_timeout_seconds`. Installed `scrubbots_solver.py` and `verify.py` were also stale and lacked their new pinned budget parameters; those installed file hashes matched the old Release manifest. This is a **substantiated stale installed dependency mismatch**, not a speculative guess. Builder honestly disclosed that owner screenshot says `real_timeout`, whereas the exact read-only correlated Activity JSONL terminal says `real_timeout_seconds`, and **no full traceback exists**. The exact literal discrepancy remains `ROOT_CAUSE_NOT_PROVEN`; do not falsely certify it reconstructed byte-for-byte. GitHub diff now supplies new limits and maps them through actual backend callsite. Builder tests are evidence rather than independent runtime proof.

## 6. FILE / SYMBOL EVIDENCE
- `level_factory/scripts/factory_studio_exact_ui.gd::_build_selected_source_pipeline_request`: request for exact 002 includes `real_max_visited:25000`, `solver_timeout_seconds:90` and user's `_column_count` (3,4,5) with Release-local pinned game root.
- `src/scrubbots_pixel_factory/supply_pipeline/solver_budget.py::normalize_solver_budget`: exact non-bool integer visits 1..25000; finite numeric non-bool seconds (0,90]; rejects None, strings, infinity, NaN, bool.
- `studio_extensions._run_canonical_artwork_route`: normalizes per selected GameRules, explicitly calls primary `SupplyOptimizer.run_grid(real_timeout_seconds=..., real_max_visited=..., max_native_solver_invocations=1 for pinned)`, then calls independent `verify_exported_supply(max_visited=..., timeout_seconds=...)`. No legacy `real_timeout` forwarding in inspected new tracked path.
- `supply_optimizer._run_prepared` validates pinned budgets and uses `batch_size=1` under pinned runtime and `max_native_solver_invocations` guard. `scrubbots_solver.run` validates pinned request 1 candidate, <=25K visits and <=90s; process launch separately bounds native timeout. `verify_exported_supply` validates bounded args before Godot discovery and native launch.
- New Python unit test uses the **actual installed Release imported module paths/hashes**, `inspect.signature`, production route `_run_canonical_artwork_route`, `inspect.Signature.bind`, and fake optimizer + fake load-check; 3/4/5 columns tested. It deliberately does not execute native Godot. The fake's `**kwargs` is constrained via `inspect.signature(real_run_grid).bind`, so keyword-shape coverage is meaningful but still not a true native execution.

## 7. FOCUSED TEST EVIDENCE
Builder reports `6/6 PASS` in new `tests/unit/test_r09_r02_r03_solver_contract.py` executed using `SCRUBBOTS_FACTORY_RUNTIME_ROOT` set to installed Release and Python 3.12 `-B`; new Godot request-builder suite PASS on columns 3/4/5, original 002 pin and 25000/90, with 0 worker calls. `git diff --check` and focused Python AST checks PASS. No test runs were independently reproduced by ChatGPT and no full legacy suite run is claimed.

## 8. REGRESSION EVIDENCE
Earlier successful R08/R09 and Godot suites were not repeated, consistent with owner's efficiency rule. No full LF regression. Crucial residual: no actual post-fix Studio solver invocation. New tests cannot certify a full screening run, Godot replay, Difficulty V1 or one further shipping load-check.

## 9. SECURITY / SAFETY / OFFLINE REVIEW
Builder reports no native solve/load-check, R2 write, game checkout modification, full Release copy, TEMP worktree, cleanup or destruction of owner-local paths. Original 002 source PNG SHA `49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa` and record SHA `858d302c10281ab2d70d4a9e22043e4eac216ebc6b6b0d89131b6e5930c232bb` reverified. Existing 232-pin game mini-runtime and extra local `CON` file left unchanged per builder; no credentials/publication.

## 10. ARCHITECTURE CONSISTENCY
Enforcing a shared normalizer over installed Studio request, actual optimizer, native ScrubBots solver and independent load-check is appropriate. Original snapshot remains a **pinned offline source-specific authority** only; it does not prove current game main at execution date, other eight source identities or CPX-002 full-game shipping. `Release Pool READY=0` remains correct. The current single candidate per pinned bridge limit helps bound native worker count; screening/candidate generation wall time is **not** proven capped by the 90s native process timeout.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS
Codex updated product/test code and appended existing R05 builder log rather than root `TASKS.md` or independent audits. Tests labelled as narrowly focused PASS, not actual SOLVED/WIN. Root TASKS remains GPT-owned and must be updated to distinguish code PASS vs actual live pipeline test pending.

## 12. FINAL REPOSITORY STATE
Builder final commits `17643de6756ba3d9552351eb237db19bd8d0c269` product, `9233d95e1cee5beedbf7a80e89e552d296761fa3` log, reported `HEAD=origin/main`, 0/0 clean. Installed Release revision `17643de...`, managed file count 2,314, SHA-backed old files and backup manifest recorded. Desktop link/PS1 reported byte-identical, existing shortcut launched current Release Godot process PID 25868. Independent audit publication may advance remote main without changing this installed code.

## 13. OPEN CROSS-MILESTONE FINDINGS
First **real owner-clicked Studio solver** after the corrected native keyword/budgets NOT yet tested. Other eight gameplay PNGs still intentionally source-restricted, generic LEVEL FACTORY pipeline not complete, CPX-002 full-game exact replay and R2 Family APK not authorized, full LF regression open.

## 14. DEFECTS BY SEVERITY
BLOCKER historical: stale installed optimizer/verifier/solver keyword signature and missing bounds, now narrowly remediated in source+builder-installed modules. MAJOR pending: actual runtime solver execution and independent load-check have zero post-fix evidence. MINOR evidence discrepancy: screenshot's `real_timeout` vs correlated JSONL `real_timeout_seconds` not proven to share literal traceback. NOTE performance: 90s caps native process but not candidate pre-screening; don't advertise whole pipeline as hard 90s.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES
Maintain a canonical installed module parity check for ALL dependencies in future narrow Release updates; otherwise imported mixed-version Python modules recreate these errors. Add eventual bounded end-to-end test only when owner explicitly authorizes true native run, and separately generic per-PNG attestation for nine-source usage.

## 16. UNVERIFIED ITEMS
Actual installed Release module bytes, backup SHA and PID are builder-only evidence; no independent GPT access to local Windows process. Original screenshot spelling discrepancy, true post-fix native SOLVED/WIN/QA and load-check, actual number of candidates surviving offline screening, eventual current-game-main shipping parity, and user visual acceptance pending.

## 17. REGRESSION RISK
High if stale installed modules recur or shortcuts resolve to another runtime; reduced by post-install hash/sig tests. Medium if screens permit missing limits in non-UI callers; normalizer fail-closed. Medium operational risk from screening CPU time and actual owner-click retry with no total wall-time bound beyond native solver.

## 18. AUDIT CONFIDENCE
High for current tracked GitHub Python/GDScript symbol-level argument contract and provenance of staged stale files documented in builder log. Medium for installed Windows SHA, 6/6 test outcomes and exact runtime module loading, since not independently executed. No confidence claim for native puzzle result absent live run.

## 19. FINAL VERDICT
**CONDITIONAL.** R09-R02-R03 bounded keyword/API remediation complete at source/targeted-builder-test level; **NOT YET end-to-end approved**. Stop manufacturing more task loops unless the owner's next single real run exposes a new issue. Parent R05 OPEN.

## 20. REQUIRED REMEDIATION / NEXT AUTHORITY
**No further Codex work yet.** Have owner use already-open updated desktop Studio, select the same original `002_32x32px.png` and 4 supply columns, press `Run Pipeline` ONCE, wait for terminal state and provide Activity + Details screenshot. This may consume real native CPU; owner chooses to start it. GPT audits actual result before any new corrective prompt. If terminal error, inspect exactly reported reason. Do not treat raw test pass as solver PASS; do not start R2/CPX-002/148 batch. If owner does not wish to spend one real native run yet, leave gated and await decision.
