# SCRUBBOTS LEVEL FACTORY | CLAUDE SOLE EXECUTOR | OWNER HANDOFF 2026-11-10

Document role: OWNER-AUTHORIZED ACTIVE EXECUTION CONTRACT
Actor: CLAUDE ONLY
Canonical repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Canonical Windows workspace: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator
Current installed application: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio
Separate real game repository: https://github.com/Sekiph82/Scrubbots
Separate game workspace: C:\Users\sekip\Desktop\Scrubbots

## 0. MANDATE AND PRIORITY

I am handing this project from Codex to Claude because Codex ran out of usage. CLAUDE is the only active implementer, task selector, tester, debugger, reviewer, publisher, and owner-facing reporter. Do not wait for Codex or ChatGPT or claim their audit. Take over existing work without resetting completed milestones. Begin by reconciling the actual latest GitHub main, canonical Desktop source, installed Release, process state, TASKS.md, and screenshots. The root TASKS.md is the only task tracker. Audit its CURRENT truth before editing product code.

The immediate priority order is:
P0-A: Repair PIXEL ART page PixelLab batch continuation; one 4x4 atlas was generated and sliced into 16 Final PNGs, then a requested 176-row batch stopped after the first attempted row. Screenshots show "STOPPED_AFTER_FAILURE", "SOURCES_IMPORTED_NOT_READY", "Provider returned no detailed reason", and "175 remaining". Determine the actual phase and billable request state, fix the root cause and resume only safely unprocessed authorized rows.
P0-B: Repair LEVEL FACTORY "Batch mismatch" / restored stale batch and source projections after the legacy cleanup. Screenshots show 304 SOURCE_ONLY PNGs and "Batch 180 Pending · 116 READY · 6 FAILED · 2 REJECTED / 304" with owner-upload source-path resolution failures even though Release Pool was reset. The page must have a truthful source-only queue and a usable Run Pipeline, without fake READY.
P0-C: Verify and repair the ACTUAL installed Factory Studio, not just source. Open it through the existing Desktop shortcut, observe the application, exercise the flows, capture real in-app screenshots and compare them to the supplied screenshots and locked three-screen visual masters. First bring PIXEL ART and LEVEL FACTORY to owner-usable operation. Do not start Release Pool visual redesign or remote release/publication before the owner has inspected it.
P1: After both owner-facing pages are verified, autonomously select and implement remaining eligible open/partial TASKS.md requirements in dependency order. Preserve the owner's feature priorities, task identities, denominator and all historical evidence; do not mistake archival narratives for current truth. For work needing explicit external authorization, mark only that operation EXTERNAL_PERMISSION_REQUIRED and continue independently executable tasks. Do not arbitrarily change the main game or external Production.

Before debugging, read the owner-screenshot observation transcript at `docs/evidence/OWNER_WINDOWS_FACTORY_STUDIO_SCREENSHOTS_20261110_OBSERVATIONS.md`. The chat screenshot originals are not GitHub assets; do not claim to have inspected their raw bytes from the repo. Reproduce and capture actual new screenshots in the installed app.

## 1. TASKS FIRST, THEN CODE

Read current TASKS.md, CLAUDE.md, AGENTS.md, GOVERNANCE.md, docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md, docs/product/FACTORY_STUDIO_EXACT_THREE_MASTER_UI_V03.md, actual source/tests, and latest builder logs. Inspect both local and installed versions. The old live Codex continuation instruction and actor are superseded by this newer owner delegation.

As your first persisted work, audit TASKS.md against actual GitHub code, installed files and evidence: identify stale statuses, duplicate/contradictory owner-era locks, missing items, dependencies, blocked external steps, and completed work incorrectly described as pending. Update its LIVE current/next/status/actor/sprint fields, introduce explicit P0 defect acceptance items without rewriting historical task IDs or falsely completing checkboxes, and add a clear autonomous-selection rule applying to ALL current open/partial requirements. Make each relevant remaining row implementable through objective tests and evidence, not "wait for ChatGPT". Keep legitimate external permissions, costs, production publication and recovery risks as per-operation gates. Do not mass-mark tasks complete or reset 224/250 historical counts. Commit and push truthful TASKS updates. Then execute the two P0 repairs.

## 2. PIXEL ART P0-A: REAL PROVIDER FAILURE / BATCH RESUME

Trace the installed and source workflow end to end: selected CSV at data/input, row identities 1..176, provider adapter and token availability, request claim, paid POST and response, gallery/asset retrieval, raw 224x224 Grid Files save, exact 4x4 -> sixteen 56x56 PNGs in data/output/Pixellab/Final, file hashes/provenance, status transitions, batch cursor, retry/fail-fast stop policy, and next-row scheduler.

The first atlas appears visually generated and cut into 16 valid Final PNGs. Do not blindly mark its row FAILED or resubmit it. Distinguish generation succeeded from later import/status/reporting failure. Diagnose why the batch shows one failed and 175 remaining, specifically the UI messages STOPPED_AFTER_FAILURE and "Provider returned no detailed reason". Recover the precise failure from persisted logs, provider receipt, response body, or a reproducible local test. Fix false failure classification, incorrect row cursor, stopped/resume logic, stale source/runtime drift, and billing retry hazards. Handle genuine errors with a visible accurate reason, safe bounded retry only for provably unbilled operations, and continued progress for independent rows where safe. A generated atlas must always be split into exactly 16 per-sprite PNGs, with pixel/alpha integrity, canonical owner Palette V3 policy, no cross-atlas mixing and correct source identities.

The owner already selected the 176-row batch. Resumption may use its existing explicitly queued and still-unbilled rows within the configured account credit budget, after validating its exact owner-approved queue and available credits. Never repeat an accepted/billed request, never regenerate row 1 merely to debug, never issue a new paid POST as a probe, and never exceed an owner's existing budget/queue. If the currently connected provider cannot truthfully verify whether a request was billed, hold THAT row without repeat billing and continue independent offline diagnosis/other safe work. Use synthetic and existing paid evidence first. Do not spend on new unscheduled work. Check Windows Credential Manager by presence/read via permitted runtime only, without disclosing token values or logging secrets. Preserve ALPIX configuration without unnecessary changes.

## 3. LEVEL FACTORY P0-B: BATCH MISMATCH AND DATA CONSISTENCY

Reproduce on the installed application shown in the screenshots, not an imaginary test data set. Compare the source and Release build identity, data-root configuration, readback, library import/index, active/pending batch identities, Release Pool projections, source-path mapping and stale 180/304 batch references. Diagnose why previous cleanup left an owner-upload projection pointing to removed paths. Restore a logically consistent current source-only gallery from the owner's approved data/output/Pixellab/Final without silently importing old paths, repopulating emptied Release Pool, or relabeling SOURCE_ONLY as READY.

Honor the owner's most recent decisions: the 30 already transferred ScrubBots game levels remain immutable; original PixelLab Final and Grid Files artwork remain intact; old historical work and cold recovery archives are not hidden active sources; current new Level Factory source selection is Final-only. Read-only inspection/hashing of Final and Grid Files is now authorized for verification; no deletion, mutation, or uncontrolled re-generation there. If recent LF source-gallery states or the approved 304 Final PNG inventory conflict with the earlier empty view, determine precisely which installed/source root and snapshot is being read instead of guessing. Keep canonical 1/60 real-game-host search plus exact fresh-host replay and no 30/120 FPS sensitivity testing; do not reintroduce an independent release pool solve.

Remove the root cause of "Batch mismatch" and wrong stale source/owner-upload references, implement safe idempotent projection/migration if needed, and verify the batch queue, preview, selectable source files, Run Pipeline, actual solver proof, accurate QA states and restart persistence. If a historical batch cannot be projected because its original source was deleted, classify it as retired/unavailable without causing every new source to fail. Test that the user's first-click experience is usable. Do not fabricate successful batch, READY or recovered original files.

## 4. P0-C: INSTALLED WINDOWS GUI / SCREENSHOT EVIDENCE

The owner expressly authorizes repeated, controlled launch and UI testing of Factory Studio via the existing Windows Desktop .lnk, including safe screenshot capture and interactions with PIXEL ART and LEVEL FACTORY. The UI must follow exactly PIXEL ART | LEVEL FACTORY | RELEASE POOL. Respect locked visual masters and current responsive owner decisions. Do not add fourth tabs, dashboard clutter or unrelated UX changes. Do not leave the installed app running an uncontrolled batch.

Find the actual shortcut target and installed source/runtime, perform safe writer exclusion and a bounded, provenance-verified update of the installed Release from the tested source. Do not overwrite running owners' jobs or unknown modified files. If your execution environment lacks Windows GUI control/screen capture, mark that exact test NOT_RUN_WITH_REASON; do not claim screenshots or installed runtime success. Use the owner's real computer UI capabilities when available. Real screenshots must come from an actual running app, show (1) Pixel Art batch status before and after, (2) successful atlas, individual PNG and resumed row progress, (3) Level Factory opening clean, (4) selected Final PNG, (5) real Run Pipeline and status/replay, and (6) reopened application retaining correct state. Capture/crop app UI without exposing credentials, save proof artifacts in a safe owner-local workspace folder, and give owner the actual image locations. Where supported, link screenshots in the final report. Do not generate synthetic images or UI mockups as proof.

## 5. RECOVERY AND DELETION BOUNDARIES

The November 7 legacy reset accidentally deleted protected owner-upload sources because of a Windows path-separator bug. Preserve the recovery facts: 30 game levels and two retained inventories, 19/20 exact source PNGs recovered in a cold archive, one original missing, twenty source.json missing, eight old installed candidate directories ACL-inaccessible. Never reinterpret inaccessible files as absent. No broad delete, recursive cleanup, archive overwrite, ACL bypass, symbolic-link traversal, reset/clean/stash or fake file recovery. Only correct an identified app-owned stale index/record with a validated exact scope, before/after manifest and rollback procedure. Preserve original game assets, provenance and hashes. Repair path comparisons using canonical Windows-safe Path operations and test on Windows paths. Treat recovery items as independently tracked PARTIAL, not as a reason to prevent safe P0 development. Ask the owner only for a truly non-resolvable restricted permission or an external approval when required.

## 6. TEST, AUDIT, PUBLISH, CONTINUE

For each P0 fix:
- Add regression tests first/reproduce the concrete failure; verify no double charge and same-asset idempotency; check persisted source/project/version/data-root correctness; test Windows path handling, file provenance and restart.
- Run focused Python and Godot native tests relevant to changed code. Distinguish source unit PASS from real installed UI PASS. Check no 30/120 FPS robustness reintroduced.
- Conduct strict self-review and an independent Claude subagent review when available, fixing defects and rerunning affected tests. Never label self-review a human/ChatGPT independent audit.
- Update the canonical Desktop installed build when safe; capture actual GUI screenshots and verify both pages.
- Commit source and tests, update builder evidence and root TASKS.md, normal-push to GitHub, fetch/refcheck local HEAD == origin/main / ahead-behind 0/0. Do not trigger GitHub Actions or hosted paid CI.
- Continue choosing actual open/partial tasks from the same TASKS.md autonomously after both P0 owner-facing pages are working, with per-task measurable acceptance criteria and clean truthful progress. Leave Release Pool owner-facing UI changes pending until the owner reviews that screen, but continue other independent code/testing tasks. Do not pause for Codex/ChatGPT.

No invented milestones, test results, approvals or synthetic screenshots. No destructive replacement of owner files. No unapproved R2/Production publishing, no secret disclosure, and no paid POST duplication. When blocked on one action, do other safe work; keep the blocker precisely documented.

## 7. OWNER DELIVERY (TURKISH)

Report in Turkish, backed by actual logs and screenshots:
(1) root cause and fix for PixelLab row-1 stop, exact request/credit/row outcome and successful safe continuation;
(2) root cause and fix for Level Factory Batch mismatch, before/after counts, proper source folder and genuine pipeline proof;
(3) actual installed version and shortcut target, GUI screenshots with local paths;
(4) tests including failures, independent subagent review if performed, and status of unavailable GUI steps if relevant;
(5) root TASKS.md refresh, newly prioritized open tasks, safely completed items and precise blocked external actions;
(6) commit SHAs, normal pushes, Desktop and origin/main sync;
(7) existing protected 30 game levels, Final/Grid artwork, cold archive and empty Release Pool preservation.

Start with TASKS.md reconciliation, then repair PIXEL ART and LEVEL FACTORY. Do not begin by working on remote publication or polishing Release Pool. Complete the current session's technically executable work, verify it, and report accurately.