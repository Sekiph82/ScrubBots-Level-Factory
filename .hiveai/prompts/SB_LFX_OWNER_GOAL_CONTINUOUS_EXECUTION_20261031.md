# OWNER-AUTHORIZED CONTINUOUS EXECUTION | ScrubBots Level Factory | 2026-10-31

Document role: AUTHORITATIVE REPOSITORY EXECUTION CONTRACT FOR THE EXISTING OWNER GOAL.
This file does NOT replace, rewrite, shorten or extend the owner's existing Codex Goal text. The owner explicitly asked to make root TASKS.md continuously usable by Codex, WITHOUT ChatGPT acting as a task-state, audit, or next-step gate. This contract implements that owner permission and the existing goal's explicit authorization restrictions.

**Repo:** https://github.com/Sekiph82/ScrubBots-Level-Factory
**Other game repo:** https://github.com/Sekiph82/Scrubbots (read-only unless an existing explicitly granted scoped game task authorizes writing).
**ONLY canonical local factory checkout:** `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
**Only development branch:** GitHub `main`.
**Single task authority:** root `TASKS.md` and the existing owner goal, using this *single unchanging prompt URL* in both current and next tracker fields.
**Last builder snapshot before new authority:** `6472f90941c5f70eeaa03ed9cc3b0f5df1265161`. Always fetch current main; never hardcode SHA.
**Existing builder log:** append only, `.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md`.

## Why this authorization exists

Old policy reserved all `TASKS.md` writes, milestone closures and next-task decisions to ChatGPT and encoded `Required Actor: CODEX, THEN CHATGPT`. This left Codex blocked waiting for ChatGPT after safe builder completion even with a running owner GOAL. **The owner NOW directly delegates limited tracker progression to Codex.** This latest explicit owner direction supersedes ONLY the former ChatGPT-exclusive tracker/update/mandatory-auditor gate. ChatGPT remains an optional independent reviewer if requested, not a mandatory dependency for goal continuation. Independent audit must never be claimed when not conducted.

Codex may edit `TASKS.md` **only** to update its existing `## Project Status` control fields (`Current Milestone`, `Current Sprint`, `Current Task`, `Current Task Status`, `Next Task/Action`, `Required Actor`) and to check a task in the pre-existing canonical list ONLY with exact verifiable completion evidence. Do not rewrite historical entries, acceptance contracts or owner directions; do not touch used prompts, `.hiveai/audits/**`, visual masters, governance history or private account material. No separate tracker, queue index, periodic background automation or new local goal file.

The owner task-progression authorization does **not** authorize making up tasks, inventing a prompt, bypassing queue guard, skipping safety gates, paid provider generation, R2 or Production writes, owner data mutation, CI/Actions, or uncontrolled GUI use. Preserve every restriction of the user's goal. A builder can mark `BUILDER_VERIFIED`, `OWNER_VISUAL_APPROVED`, `PARTIAL`, `EXTERNAL_AUTH_REQUIRED`, `NOT_RUN`, or `BLOCKED`; never self-label `INDEPENDENT_AUDIT_PASS` or `PRODUCTION_PUBLISHED`.

## Stable task-envelope/queue mechanics

1. Keep **this exact prompt URL** as the ONLY prompt URL in each of `Next Task/Action` and `Current Task` in root `TASKS.md`. Set `Required Actor: CODEX`; no `THEN CHATGPT` wait state. Use the existing `scripts/codex/scrubbots_task_queue.py --json` unchanged. Do not disable or spoof the guard. Use the current stage name, status and evidence SHA to identify the in-progress work in `Current Task` and `Current Task Status`, while the one stable GitHub prompt URL remains identical in both fields.
2. At task start, `git fetch --prune origin`, check canonical root, origin, status, ancestry and existing owner modifications. Fast-forward ONLY if safe, never reset, clean, rebase, auto-stash or new worktree. Run queue guard. If the only reason for a short lived dirty status is your own in-progress task, finish and commit safely before running guard for the NEXT stage; never weaken checkout validation.
3. After each independently bounded task/substage, run affected local tests **once**, inspect exact diff, commit only task files, append builder result (separate commit), normal safe push to `origin/main`, refetch, verify `HEAD == origin/main`, ahead/behind `0/0`, clean tracked tree and relevant installed-runtime source/manifest parity. Then, as an **explicitly authorized separate scoped GitHub commit**, update root `TASKS.md` with the completed stage, its evidence SHAs, exact unverified limitations and the next stage from the PREAUTHORIZED sequence below. Safe push+fetch+parity check again. Rerun queue guard on the clean checkout and immediately proceed; no ChatGPT check-in required.
4. A stage needing approval is `EXTERNAL_AUTH_REQUIRED`; do not attempt that operation. Continue another independent PREAUTHORIZED safe stage and record its active stage. If **no independently authorized work remains**, preserve truthful pending status and stop; GOAL remains open. Never loop no-op fetch/test/log commits merely to appear active.
5. If a task fails locally, identify and repair its actual source/environment defect and focused test within the permitted scope. No unapproved unsafe workaround. Do not replay already-passed tests without a code change or missing evidence.
6. The existing Goal runs only while Codex is actively executing. Do not make a background runner, scheduled job or separate automation. Never guarantee perpetual operation beyond the agent session's execution limits.

## Existing V06 completion baseline (do not redo)

2026-10-31 Codex commits `df332c5d` and `6472f909` reported:
- Nine owner-requested folders exist; per-provider output paths, 4x4 atlas -> 16 PNG, SHA idempotent intake and separate owner archive `Pending / Ready / Failed / Rejected` implemented.
- Focused offline functional tests **16 passed in 2.70s**, no owner PNG/old pool edits.
- Installed managed Studio source/UI SHA matches, install receipt/writer safety already reported.
- Owner explicitly **APPROVED 38px Pixel Art visual/page design**. Extra runtime coordinate measurement is `NOT_MEASURED_NONBLOCKING`; never reopen owner visual acceptance or assume laptop GUI permission.
- GitHub `main` and canonical tracked checkout clean/equal at reported receipt.

Codex may mark **R10 V06 IMPLEMENTATION_BUILDER_VERIFIED, OWNER_VISUAL_APPROVED, native GUI geometry NOT_MEASURED_NONBLOCKING** in TASKS with exact evidence, rather than leaving the old `R10 V06 ACTIVE` forever. Do not claim complete third-party ALPIX live generation, future end-to-end game results or independent audit from these tests. A missing independent ChatGPT review MUST NOT block the next authorized safe stage.

## PREAUTHORIZED ordered work, under the owner's EXISTING goal

Use this fixed set of scopes. Inspect actual latest source/test/evidence first; if a stage is already verifiably done, mark it DONE/VERIFIED with original evidence and move on without rerunning it. Do not create a novel milestone, feature, repo, paid call, release or scope.

**A. Pixel Art provider/runtime completeness, zero-spend first.**
Read-only inspect ALPIX Claude plugin/connector and Claude Code MCP actual tool capabilities; no invented ALPIX PNG API or fake READY. Verify PixelLab Credential Manager status only without exposing secrets; inspect actual available provider calls. Verify CSV `data/input`, ALPIX/Pixellab output routing, atlas Grid Files vs Final 16, source identities, retry/no duplicate charge, clear errors. Use synthetic fixtures/offline mocks. ALPIX remote drawing/canvas mutation and PixelLab billable generate remain PENDING until owner explicitly authorizes exact call/cost.

**B. Level Factory correctness with authentic game contract (offline/local safe work).**
Validate folder/multi-PNG intake, 5-slot FIFO replenishment when a slot empties, no reprocessing same SHA, canonical solver + genuine replay WIN/LOSE, Supply, Difficulty, level-number assignment vs actual `Scrubbots` game rules. No original 140 batch, no owner existing READY/Pool modifications. Use approved synthetic or existing immutably copied fixtures only when safe. If game-native verification would change or run an unauthorized game project, check the exact existing contract/owner permissions; use read-only source parity or mark native verification NOT_RUN and continue other tasks.

**C. Release Pool product correctness.**
Read-only audit source/actual READY-index list, selected identities/counts, filters, preflight/manifest consistency, historical broken-entry surfacing, Fail/Reject separate owner archive and explicit Retry Failed gating. Fix only proven source defects and affected tests. No auto-promotions to READY, no production pool writes.

**D. Staging and Production delivery preparation (no external writes without explicit approval).**
Inspect configured Cloudflare R2 targets and game HTTPS consumer read-only; prepare offline staging and production preflight, valid manifests/payloads/hash indexes and dry-run/verification fixtures only within previously approved file scope. Distinguish Staging from Production. **Actual R2 PUT, overwrite, delete, promote, Production activation or public release is NOT AUTHORIZED merely by this goal**. Capture exact immutable plan, target/bucket/keys, anticipated changes, rollback and verification procedure, then mark `EXTERNAL_AUTH_REQUIRED_R2_WRITE` and continue other safe tasks. Do not publish actual R2 content until explicit later owner authorization. No App Store / Google Play release claims.

**E. Final local product and GitHub parity evidence.**
Verify current installed Factory Studio managed hashes, all real completed local tests and what was NOT_RUN, preserve 140 originals and original Pool evidence, no unrelated regressions, no orphaned task-created project files. Compare canonical tracked checkout with GitHub current main. Produce final concise builder evidence identifying completed, partial and blocked provider/R2/Production aspects and store under existing builder log. Do not claim entire goal DONE unless **every** completion criterion is actually proven.

## Protection and artifact-location policy

**NO extra clones/worktrees/TEMP implementation/test areas.** Existing `C:\Users\sekip\.codex\attachments\...\goal-objective.md` paths are Codex product/session-managed attachments, not canonical project source, task ledger or publish destination. Their existence is not evidence that the agent intentionally created a secondary repo. Codex MUST NOT create project-owned goals, code, prompts, tests, manifests, logs, images, plans, outputs or permanent files in `.codex/attachments`, `%TEMP%`, another Desktop directory or user home. Authorized durable source+reports belong in the canonical checkout and normal GitHub main, or an explicitly user-approved connected Drive location. **If Codex itself automatically stores session attachment copies outside the repo, don't claim those are controllable project files.** Do not delete or overwrite existing app-managed session files without owner authorization. Do not refer to such session copies as task authority. Only `TASKS.md` is the live task state.

All previous owner data locks remain: 140 original PNGs, existing Release Pool records, historical commits and 18 stashes immutable without new permission; no destructive cleanup, no CI/Actions, no unauthorized paid API, no game/R2 write, no uncontrolled laptop GUI interaction, no false success or fake production delivery.

Owner's Windows UI is English. Audit citations/evidence can be in Turkish or English.

**Completion is not a report loop. Completion is working code, safe evidence, sync, then immediate next PREAUTHORIZED stage. No ChatGPT audit or tracker edit is a prerequisite anymore.**
