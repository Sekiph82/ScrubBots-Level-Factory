# SB-LFX-018-C001-R02-R05-B01-R01 — Resume R05 Without Any Cleanup

ROLE: CODEX continuation for the existing R05 task. This instruction **supersedes only the disk-cleanup stop condition** in R05-B01; the original R05 implementation, B01 preservation rules, and all original technical/audit gates remain in force.

Canonical repo: `Sekiph82/ScrubBots-Level-Factory`.
Original R05 prompt: `.hiveai/prompts/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_PROMPT.md`.
Parent B01 prompt: `.hiveai/prompts/SB-LFX-018-C001-R02-R05-B01_DISK_AND_TEST_RECOVERY_PROMPT.md`.
R05 audit: `.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_AUDIT_CRITERIA.md`.
B01-R01 audit: `.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05-B01-R01_NO_DELETION_TEST_RESUMPTION_AUDIT_CRITERIA.md`.

## Updated owner decision / blocking review

The exact-path PowerShell `Remove-Item` call was blocked by the automatic approval review (**blocked by policy**) and never executed. DO NOT RETRY, WORK AROUND, APPROACH VIA ANOTHER TOOL, or implicitly remove these paths:

1. `C:\Users\sekip\AppData\Local\Temp\pytest-of-sekip\pytest-2308\test_default_route_a_verifier_0`
2. `C:\Users\sekip\AppData\Local\Temp\pytest-of-sekip\pytest-2308\test_batch_published_catalog_l0`

Both are **PROTECTED FROM DELETION OR MODIFICATION FOR THIS CONTINUATION**. They contain potentially useful historical snapshot evidence at ScrubBots commit `4dbf1045c2f1988a08e3d76a3c7e6e40ba25bdfe`. Do not delete their parent, run pytest `--basetemp` against them, or allow test fixtures/housekeeping to implicitly purge or overwrite them.

Crucial changed fact: **C: free space was measured at 135,019,728,896 bytes immediately before the denied deletion attempt**. Consequently, deletion is no longer a prerequisite for R05 recovery. Previous **0 bytes free** was an earlier observation, NOT proof the disk is currently full. Proceed without deletion only if fresh read-only preflight confirms enough free headroom and no other blocker.

## Step 1: Non-destructive preflight

- Read-only inventory of exact R05 TEMP worktree `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\SB-LFX-018-C001-R02-EXACT-THREE-MASTER`: commit, origin, status, uncommitted work/diff summary, builder log presence, and Desktop owner state. Verify neither of the two protected pytest fixture directories was changed by the denied command.
- Repeat free-space measurement (total/free) before tests, identify whether any ongoing process is consuming space, and record available capacity plus planned expected test output. Use prior ~14.49 GB combined fixture size as a lower-bound data point, not a cap for whole-suite disk usage. Require a conservative measurable free-space reserve. If headroom is insufficient, stop `DISK_HEADROOM_INSUFFICIENT`, request an approved storage solution; never reattempt blocked deletion.
- Arrange new test output into a **new, empty, distinct, verified path** that cannot overlap either protected fixture or its parent; ensure pytest's usual temp retention/pruning and pre-run hooks cannot mutate the protected paths. Explicitly inspect pytest fixture/temp configuration BEFORE running new tests. Any risk of automatic cleanup of protected paths is a STOP, not permission to route deletion differently.
- GitHub `main` may have advanced because ChatGPT published B01/R01 guidance and tracker changes. Inspect/fetch non-destructively and preserve all local code/logs. Do not reset, clean, rebase, stash, overwrite or force-push to obtain a clean-looking workspace. If branch conflict requires a change to owner-local state, stop with evidence.

## Step 2: Diagnose, focused first

- Recover exact failed/error test names, traces and process invocation from the prior 84%-interrupted pytest, rather than assuming disk failure explains them. Separate environment/authority, code, test and solver-budget defects.
- Isolate `test_real_import_surface_integration_passes_headlessly` with real canonical authority, a bounded subprocess/solver/test-supervisor contract and recorded outcome. Fix root cause. No skip, xfail, fake pass, dropped coverage, or tiny arbitrary timeout.
- Run the real distinct-PNG **A READY / B FAILED-UNSOLVED / C READY** identity/order test to an actual passing result. Verify immutable source/derived artifacts and fail-closed cross-binding, contiguous A/C release numbering after existing tail with no B slot, and stable retry/resume through canonical CampaignBuilder authority. Previous `NOT_ENTERED` is not acceptable.
- Run repeated production N->N+1->N+2, strict history/readback, exact owner approval, STAGING, CP03-008/009 and all negative cases.
- Preserve R04 native three-master controls, LF19/VOID, Alpix/resume, production safety and owner data.

## Step 3: Full R05 closure only if focused green

- Once every focused defect is closed, run exactly one complete correctly configured authority-enabled repository pytest to a recorded terminal summary with 0 failures and 0 errors. Observe disk use and stop gracefully if safe free-space reserve is threatened; a stopped or 84%-complete run is NOT PASS.
- Fulfill original R05 final LF19, native UI, real renderer, Godot parse/import, launch/installer, compileall, git diff check, secret scan and 1536×1024 durable-runtime screenshots/evidence exact byte-copy gates. Do not install before verification; do not substitute snapshots with static owner masters.
- Only after all technical gates pass: code/test commit, separate evidence/log commit, safe fast-forward push and handoff to GPT independent re-audit. If Alpix plugin remains absent, preserve the external owner gate `OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED`.
- Never edit root `TASKS.md` or `.hiveai/audits/**`. Append the denied cleanup and no-deletion decision (including free-space timestamps, protected paths and actual test results) to the preserved R05 local builder log.
- Return only the published R05 GitHub builder-log URL on success. If blocked, return concise exact blocker and evidence, without claiming PASS.

## Owner decision in one line

**Decline further deletion; protect both prior fixtures; if current 135 GB-class headroom is confirmed and future tests cannot prune the fixtures, continue R05 testing in a separate safe test area.**
