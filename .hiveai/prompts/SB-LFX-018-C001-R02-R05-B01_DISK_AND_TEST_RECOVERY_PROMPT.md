# SB-LFX-018-C001-R02-R05-B01 — Disk Recovery and Strict R05 Test Resumption

Role: CODEX operational recovery continuation within the existing R05 task, **not** a new milestone or permission to weaken tests.

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory

Primary R05 implementation contract:
`.hiveai/prompts/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_PROMPT.md`

R05 audit:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_AUDIT_CRITERIA.md`

This recovery gate:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05-B01_DISK_AND_TEST_RECOVERY_AUDIT_CRITERIA.md`

Reported interruption (2026-10-09): C: **0 free bytes**; no alternative workspace volume. The full pytest stopped at 84% with failures/errors and then hung in `test_real_import_surface_integration_passes_headlessly`. The focused `A READY -> B FAILED/UNSOLVED -> C READY` order test has **no passing result** (`NOT_ENTERED`). All R05 product changes and builder log remain local, uncommitted, unpublished, and not installed. NO R05 acceptance or completion is authorized.

## Mandatory first operation: preserve everything

1. Inspect status of the existing TEMP worktree `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\SB-LFX-018-C001-R02-EXACT-THREE-MASTER`. Confirm actual path; do not assume it remains identical. Inventory worktrees and record current `HEAD`, `origin/main`, changed/untracked paths, diff statistics, local builder log path, test processes and available free disk bytes.
2. Do not run any bulk test, installation, sync mutation, `git clean`, `reset`, `rebase`, stash drop, force push, or blanket TEMP cleanup while C: is full. Preserve original Desktop checkout, local source and scripts, uncommitted changes, `.hiveai/codex-logs/**`, user images, evidence and installer. In particular, DO NOT delete the R05 execution worktree, its `.git` link, or any test output until provenance and usefulness are established.
3. Keep a read-only inventory (path, bytes, creator/test where identifiable, provenance, and KEEP/SAFE-TO-REGENERATE/UNVERIFIED disposition) of **large generated artifacts only**. Prioritize interrupted pytest-generated temporary fixtures, disposable render/import caches and reproducible test output. Identify process handles before considering deletion. Do not classify files merely by their folder name.
4. If the execution environment's deletion approval or automatic review refuses cleanup, **do not evade that gate** with shell alternatives, scripts, rename tricks, Python, PowerShell, another tool, or a different path. Request explicit owner approval for the **exact listed paths and expected reclaimed bytes**. On denial or ambiguity, stop with `OWNER_CLEANUP_APPROVAL_REQUIRED`; preserve all files. The existence of this prompt is not blanket deletion consent.
5. Once permission and provenance are established, remove **only explicitly approved disposable test-generated artifacts**; retain test failure logs and reproducibility metadata or copy them to an approved existing space first. Never remove git objects, tracked data, Desktop owner files, old release installations, important evidence, personal files or entire generic folders. Verify free-space delta, disk health/error messages and a reasonable test-run free-space budget before continuing. Stop with `DISK_RECOVERY_BLOCKED` if space cannot be safely reclaimed.
6. Resume from the preserved TEMP changes; **do not start over or discard R05 work**. Fetch and inspect exact current `origin/main` non-destructively after disk recovery. This ChatGPT-authored documentation update may advance main; integrate only by a safe conflict-free route with owner-local work preserved. Never overwrite uncommitted local work for a clean-looking checkout.

## Controlled test diagnosis, no full rerun yet

7. Reproduce and report the **exact** pytest failures/errors seen before the 84% interruption, from retained output first. Classify each as product defect, test defect, missing exact-current ScrubBots authority, infrastructure/disk error, or unknown. Record the exact test names, exception traces and invocation environment. Never silently discard failed results or re-label them as passes.
8. Isolate `test_real_import_surface_integration_passes_headlessly`. Inspect its subprocess/solver scope, deterministic termination contract, fixture volume and cleanup; distinguish external processes stalled by zero disk from an actual unbounded production path. Add narrowly scoped bounded supervision or reuse canonical budget mechanisms. No fabricated solver result; do not skip/xfail/remove coverage. Show exact bounded exit/fail-closed behavior, and prove the same real headless import integration **passes** once the defect is closed.
9. Re-run focused genuine A/C identity and order integration: distinct PNG A, B, C; A READY, B FAILED/UNSOLVED, C READY; stable SHA-to-LevelData/solver/supply/replay/Difficulty V1/publication binding; final production order A/C contiguous after prior catalog tail; B consumes no final slot; retry/resume stable; deliberate cross-binding rejected. `NOT_ENTERED` is not a pass. Use canonical CampaignBuilder/order authority.
10. Re-run focused repeated-production N->N+1->N+2 integration and negatives against canonical CP03-008/009 and manifest history authority. Preserve R04 native three-master UI, Alpix/resume, VOID correction, release installer and approval safety.

## Final locked gates

11. Only after all focused failures are green and the hang is bounded, run one complete authority-correct repository pytest to actual termination with **0 failures, 0 errors**, recording total passes/skips and commands. Do not turn new failures into skips/xfails or edit assertions solely to force green. All prior LF19 tests, launcher/native runtime, Godot parse/import, compileall, diff check, secret scan, release history, production precondition and identity/order gates from original R05 criteria must pass.
12. Stage and install R05 **only after** verified test closure, preserving managed release files and owner shortcut. Capture exact final 1536x1024 PIXEL_ART, LEVEL_FACTORY and RELEASE_POOL screenshots from that installed durable runtime. Publish byte-identical copies and SHA256SUMS under `.hiveai/evidence/SB-LFX-018-C001-R02-R05/`. Diagnose Godot shutdown diagnostics accurately.
13. Commit implementation/tests first, then evidence and the existing local R05 builder log separately; fast-forward push only. Final execution checkout clean, 0 ahead / 0 behind. Return the GitHub builder-log URL. If Alpix remains unavailable, flag `OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED` without hiding any technical defect.

## Scope/stop rules

- Code and test authority stays with the original R05 prompt and original R05 audit. This B01 prompt grants **no** shortcut to publication.
- Never edit root `TASKS.md` and never write `.hiveai/audits/**`; ChatGPT alone handles tracking and strict audit.
- If disk space or deletion approval remains blocked, publish nothing, install nothing, keep local log and changes, and report the **exact path inventory and blocking permission** (no fabricated green status).
