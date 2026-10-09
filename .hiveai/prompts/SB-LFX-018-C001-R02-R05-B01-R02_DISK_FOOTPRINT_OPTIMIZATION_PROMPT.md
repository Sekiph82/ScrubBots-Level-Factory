# SB-LFX-018-C001-R02-R05-B01-R02 — Owner-Locked Low-Disk R05 Recovery

ROLE: CODEX continuation / selective engineering optimization, under existing R05; not a new milestone.

STATUS: This R02 **supersedes the B01-R01 "do not delete" owner-policy assumption**. The owner did NOT instruct ChatGPT to make a permanent keep/delete decision and explicitly rejects 65 GB-class disk-consuming workflows. Do not interpret free disk capacity (135,019,728,896 bytes at an earlier check) as permission to use it.

Parent authoritative R05 scope:
`.hiveai/prompts/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_PROMPT.md`.
Parent R05 audit:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_AUDIT_CRITERIA.md`.
This optimization audit:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05-B01-R02_DISK_FOOTPRINT_OPTIMIZATION_AUDIT_CRITERIA.md`.

## Non-negotiable owner constraints

1. **No 65 GB-class test operation or bulk duplicate generation.** Inventory exact current free space, fixture destinations and sizes; establish baseline before any new tests. Engineering limit for this continuation: **no more than +8 GiB total incremental test-generated disk consumption above that baseline**; any individual proposed test requiring more than +4 GiB must be optimized before running. These are conservative guardrails, not a target to use. If a complete genuine test suite cannot fit without violating them, STOP and document the blocker rather than silently expand the budget.
2. **Both cleanup and optimization are acceptable owner-level options; no assistant-mandated permanent retention.** However the previous exact-path PowerShell deletion was **blocked by policy** and did not execute. This new prompt does NOT override the automatic security/approval gate. Do not retry forbidden deletion through PowerShell, Python, shell redirection, alternate tools, renames, IDE, automated pytest pruning or any bypass. If the review system offers a legitimate explicit approval pathway for exact-path deletion, present the exact targets to the owner and use it only after that system allows it. If the system continues to block, leave those files alone and optimize without deletion. Never remove parent directories, user data, active worktrees, any project files or historical evidence.
3. Existing R05 changes, local uncommitted builder log, durable runtime, owner Desktop files, code/tests, `TASKS.md` and audits must remain intact. First read-only inventory TEMP worktree, local Git state, git commit authority, output and test processes. No git reset/clean/rebase/stash drop/force push.
4. Do not start another full pytest or clone/archive/extract regression until its worst-case per-test AND cumulative output footprint has been inspected and optimized. No unmonitored bulk test run.

## Evidence-backed duplication to remove FROM FUTURE TEST DESIGN

Current `tests/integration/test_release_route_a_authentic_verifier.py` creates:
- `git clone --depth 1` `scrubbots-source`: 4,718,474,047 bytes (including a 2,195,436,761-byte Git pack);
- `scrubbots-origin-main.tar`: 2,526,218,240 bytes;
- `scrubbots-isolated`: 2,201,273,075 bytes.
This *one test* generated 9,445,965,362 bytes.

Current `tests/integration/test_release_batch_level_catalog.py` creates:
- `scrubbots-authority.tar`: 2,526,218,240 bytes;
- `scrubbots-authority`: 2,522,194,909 bytes.
This *second test* generated 5,048,419,271 bytes.

Both tested exact-current game authority and must **retain genuine current-game, isolated, full-content integration behavior**. They do NOT have to waste disk on an additional local clone plus an on-disk tar plus an extracted copy at the same time.

## Narrow optimization tasks (preserve test meaning)

A. Reuse an already available, origin-verified, exact-current `Scrubbots` Git authority checkout as **read-only archive source**. Validate remote identity, clean tracked status where required, exact SHA == queried canonical `origin/main`, full required Git-object/history capability, and protect source checkout from writes. If exact-current authority is not locally available, set up **one** safely authorized authority source rather than cloning a fresh 4.7 GB copy for each integration test. Never modify owner Desktop work and never weaken history/VOID provenance requirements.

B. For the two evidenced tests, replace the persisted archive file with a **streaming `git archive` -> safe tar extraction into ONE isolated runtime tree**, after checking source commit identity. Handle Windows subprocess pipes/exit/timeout/errors robustly, validate extraction safety, ensure no partial success masquerades as PASS, and report complete archive/tree hashes where appropriate. Preserve selected authentic production row, real Godot verifier/LevelCatalog and all canonical replay/solver/Difficulty assertions, negative fail-closed cases, and immutable-source checks. No fake game tree or mock replacing canonical integrations.

C. Search remaining integration tests/fixtures for nested clone, persisted 2.5 GB tar, archive extraction, repeated authority copies or pytest tmp retention; measure rather than guess. Replace redundant copies with verified shared **immutable authority reference** plus dedicated writable isolation per test. Do not hardlink files that a test or Godot may mutate; do not share mutable project trees across tests without a proven reset/isolation contract. No weakened or skipped tests.

D. Before running, inspect pytest's temporary-directory and retention/pruning behavior to ensure tests cannot remove or overwrite the earlier policy-protected `pytest-2308` fixtures. New testing must use genuinely separate paths; do not treat indirect auto-cleanup as acceptable. Monitor baseline vs current free space, per-test peak and cumulative incremental bytes, no >4 GiB predicted per case and no >8 GiB cumulative additional. If uncertain, STOP with evidence.

E. Determine root causes of the earlier full pytest 84% failures/errors and the hang in `test_real_import_surface_integration_passes_headlessly`, retaining traceback and precise environment. Fix real unbounded budget/test-harness defects without fake SOLVED, skip or xfail.

F. Execute real identity/order `A READY -> B FAILED/UNSOLVED -> C READY` to a green result and strictly contiguous production ordering with canonical CampaignBuilder, stable retry/resume and cross-binding rejection. Then genuine repeated-production N->N+1->N+2 canonical CP03-008/009 plus adversarial negatives. Recheck LF19/VOID and native three-master R04 behavior.

G. ONLY if optimized disk budget, focused tests and all real gates pass, run one correctly configured full repository pytest to a terminating zero-failure/zero-error report, monitoring incremental disk throughout. Finish original R05 Godot, safety, native runtime, screenshot SHA evidence, installer, compileall, diff and secret scan gates. Only then install, commit implementation/tests, separately commit evidence/log and push fast-forward for GPT independent audit.

## End states

- SAFE OPTIMIZATION/VALIDATION PASS: publish original R05 work per original contract, not a fabricated audit PASS.
- BLOCKED CLEANUP REVIEW: do not bypass; proceed with truly low-disk optimization only if it does not trigger the forbidden cleanup.
- DISK BUDGET CANNOT BE MET: stop and state exact size/test requiring more than the owner budget.
- UNRESOLVED TESTS: do not install, push or claim R05 complete.

Codex must never edit root `TASKS.md` or `.hiveai/audits/**`. Update the **existing** local R05 builder log only. Owner must not be asked to manually delete files or run commands merely to make an inefficient fixture work.
