# R09-R02-R02 — Owner Live Run Keyword-Contract Failure | Independent Strict Audit V02

Document role: CHATGPT INDEPENDENT AUDIT. Date: 2026-10-13. Repo: `Sekiph82/ScrubBots-Level-Factory` / `main`.
**Verdict: FAIL for end-to-end owner Studio pipeline; earlier narrow source/VOID/UI code PASS remains a separate accepted gate. R05 parent OPEN.**

## 1. VERDICT
The user's **actual installed Desktop Studio screenshot** shows `Solver: ERROR` and exact `Pipeline failed before completion: SupplyOptimizer.run_grid() got an unexpected keyword argument 'real_timeout'`. The monitored stages reached SOURCE PASS, PALETTE/STRUCTURE VALIDATION PASS, CANDIDATE PASS, then ANALYZE/PLAN RUNNING, followed by PIPELINE ERROR. **No native solver start, SOLVED, WIN, Difficulty V1, QA, shipping load-check or READY was proved for this CLICK.** This is a programming API/callsite mismatch, NOT proof the frog level is unsolvable.

## 2. CONTRACT RECOVERY
Owner wants ONE real installed Studio Run Pipeline working for original SHA-bound `002_32x32px.png` while preserving left top settings / Run / large Activity and three other screen layouts. Prior offline R09-R02 accepted SOLVED/WIN/QA + load-check is separate from a Studio click and CPX-002 full-game replay remains open.

## 3. BRANCH / HEAD / DIFF SCOPE
Read GitHub `main` `src/scrubbots_pixel_factory/studio_extensions.py`, `supply_pipeline/supply_optimizer.py`, `supply_pipeline/scrubbots_solver.py`, `supply_pipeline/verify.py`, `level_factory/scripts/factory_studio_exact_ui.gd`, and existing root TASKS/R05 builder log. Previous product commit `ccbdef4b2070ac4beea240eeeb326032afb46d45`, log checkpoint `10f495971dd3580890cb824b7619669ce960671a`. This new audit and future prompt are NOT a Codex-installed patch.

## 4. ACCEPTANCE CRITERIA MATRIX
- Owner source and structural validation: **PASS in screenshot**.
- Actual solver `SupplyOptimizer.run_grid` invocation signature: **FAIL**, TypeError.
- Current GitHub `SupplyOptimizer.run_grid` signature includes `real_timeout_seconds`, NOT `real_timeout`: **SOURCE VERIFIED**.
- Current GitHub `studio_extensions._run_canonical_artwork_route` uses `real_timeout_seconds=...` correctly: **SOURCE VERIFIED**.
- Actual installed worker code/import path/stack passed `real_timeout`: **UNVERIFIED ROOT CAUSE**, strongly suggests stale runtime/different imported callsite/wrapper or branch; screenshot alone cannot identify which.
- Pin visit limit: **POTENTIAL NEXT BLOCKER**, source-proven: Studio Run request omits `real_max_visited`, extension forwards `None`; pinned `SupplyOptimizer._run_prepared` requires integer 1..25000 and raises `NoValidSupply` if absent.
- Independent load-check visit limit: **POTENTIAL NEXT BLOCKER**, source-proven: `verify_exported_supply(...max_visited=solver_max_visited)` also receives `None`, but pinned `ScrubBotsSolver.run` requires 1..25000.
- Any SOLVED/READY/Release Pool eligibility from this owner click: **NOT PRESENT**.

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH
Previous builder checked code/tests and attested 002 original/VOID authority, but explicitly performed ZERO Studio native solve. Test PASS did not verify the actual installed `run_grid` keyword call or hard solver limits; the first real owner click now reveals runtime integration failure. Do not treat passing mocked tests as owner acceptance.

## 6. FILE / SYMBOL EVIDENCE
Current tracked `SupplyOptimizer.run_grid(...real_timeout_seconds=90,max_native_solver_invocations=None)`, `SupplyOptimizer._run_prepared` requires `real_max_visited` for pinned runtime; `ScrubBotsSolver.run` similarly requires valid `max_visited` and bounded `timeout` and exactly one candidate. `studio_extensions._run_canonical_artwork_route` forwards request `real_max_visited` directly into BOTH primary solve and independent shipping load-check. In current `factory_studio_exact_ui.gd::_build_selected_source_pipeline_request`, selected column count / game_project / level number are present but `real_max_visited` and `solver_timeout_seconds` are ABSENT. The screenshot TypeError names `real_timeout` (without suffix) while current tracked extension uses `real_timeout_seconds`; **do not invent the exact installed import source**. This discrepancy demands runtime `__file__` + `inspect.signature` + traceback before changing signatures.

## 7. FOCUSED TEST EVIDENCE
Old 4 Python + one fake-Godot UI suite PASS are historical builder evidence, not applicable proof for the real keyword/limit. New targeted reflective installed-runtime signature and non-native full Python route mock must exercise actual run_grid/load-check args, not a manually constructed expectation or a fake wrapper that bypasses parameter binding.

## 8. REGRESSION EVIDENCE
No full LF regression or 148 solver calls required. No repeat of previously green unrelated suites.

## 9. SECURITY / SAFETY / OFFLINE REVIEW
Owner original PNG/source.json, nine gameplay sources, installed pinned runtime, 57 preexisting LF untracked roots, accidental `CON`, launcher/link, local dirty separate Scrubbots game repo remain protected. No cloud/R2, CPX-002 production, new game clone/TEMP worktree, installer rebuild or heavy native solver tests authorized. No cleanup.

## 10. ARCHITECTURE CONSISTENCY
The source-authority gate now lets the owner click proceed through candidate preparation; pin source is not game full shipping authority. Solver function signatures, runtime imported Python modules, job timeout/visit budgets and independent load-check must share ONE agreed bounded contract. Fix caller or stale installed module to match **canonical tracked signature**, do not weaken pinned bounds or globally allow unknown kwargs.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS
Root TASKS must mark R09-R02-R02 as owner **LIVE FAILED** despite previous narrow technical PASS. Codex must implement remediation only and append existing R05 log, GPT authors this audit/prompts and updates root TASKS.

## 12. FINAL REPOSITORY STATE
Existing original source is verifiably untouched by this audit; it currently exposes `real_timeout_seconds` rather than `real_timeout`. Exact installed Windows worker import path/traceback not available through GitHub; owner screenshot is decisive about terminal error.

## 13. OPEN CROSS-MILESTONE FINDINGS
Real Studio solver/win/load-check, general support for other eight PNGs, current-game-main equivalence, CPX-002 full-game replay, READY Pool and R2 publish remain OPEN.

## 14. DEFECTS BY SEVERITY
**BLOCKER-F01:** actual worker `real_timeout` unexpected keyword; **BLOCKER-F02 (latent source-verified):** omitted pinned `real_max_visited` and load-check limit; **MAJOR-F03:** no actual installed-runtime signature/trace verification in previous tests; **MAJOR-F04:** callback/Activity currently shows only pre-solve stage then ERROR, must surface accurate terminal and avoid false solver status; **NOTE-F05:** owner selected 4 columns, whereas prior offline R09 proof may have been a different request, so don't reuse output or assert win.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES
Cheap pre-native contract probe: import canonical installed modules using exact desktop launcher Python environment; trace module __file__, SHA256, inspect.signature, call binding for every request parameter, enforce positive max_visited and <=90s timeout in one shared safe request builder; no unnecessary solver call. Preserve source-level SOLVED/timeout reason distinctions and ready proof.

## 16. UNVERIFIED ITEMS
Which installed path produced the `real_timeout` kwarg; complete owner-local traceback; whether a stale Python module or dynamically forwarded request caused the issue; CPU/perf behavior once corrected.

## 17. REGRESSION RISK
High if masked by adding permissive **kwargs, loosening pin or run retries without budget; medium if updating wrong Release copy while Studio running; medium if next pinned limit bug left untested.

## 18. AUDIT CONFIDENCE
HIGH on screenshot exact TypeError and tracked source omissions/signature; MEDIUM on stale import hypothesis; LOW on the native solver's eventual solution until a new deliberate owner click.

## 19. FINAL VERDICT
**FAIL end-to-end actual Studio Run.** Code/source partial PASS only, native result entirely unverified for this click.

## 20. REQUIRED REMEDIATION
One **R09-R02-R03** narrow Codex prompt: read screenshot-correlated backend traceback and actual installed Python module origins, fix exact kwarg source (keep canonical `real_timeout_seconds`), explicitly send validated `real_max_visited` <=25000 and timeout <=90 through both primary and shipping load-check, demonstrate real installed `inspect.signature` and no-native fake solver contract tests that invoke actual production caller, preserve Run selected 002 4 columns and pinned VOID, safely hash-backup/update only impacted installed files and verify existing Desktop shortcut launch. ZERO Codex-run native solves; owner later clicks once and sends Activity/Details receipt. No R2/CPX-002 or game checkout changes.
