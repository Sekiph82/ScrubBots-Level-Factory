# H!veAI TASKS-only control-plane adapter

## LATEST OWNER RULE: CODEX CONTINUOUS GOAL AUTHORITY (2026-10-31)

The owner explicitly directed that Codex, not ChatGPT, must autonomously advance the existing ScrubBots Level Factory GOAL. **The owner did NOT change the goal text.** Exact stable GitHub task envelope: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB_LFX_OWNER_GOAL_CONTINUOUS_EXECUTION_20261031.md

**Owner-delegated exception to historical ChatGPT-only control:** Codex may now update ONLY root `TASKS.md` Project Status current/next task fields, Required Actor, task evidence status and already-approved task checkboxes, and advance across PREAUTHORIZED goal stages upon real builder evidence. `Required Actor: CODEX`; ChatGPT independent audit is OPTIONAL, never a mandatory stop between safe tasks. Do not claim independent audit or owner acceptance when it has not happened. Do not alter old historical task text. At each transition, retain the SAME exact active prompt URL in both current and next fields, commit/push TASKS after source+builder log publication and verify Desktop/GitHub parity. Re-run read-only queue guard for the next phase. No next stage may be invented or outside the goal's permitted scopes. If a stage is permission-blocked, mark it truthfully and work on another independently approved stage. Do not skip any security or cost gate.

This supersedes all older `ChatGPT is exclusive TASKS writer`, `THEN CHATGPT`, or `independent audit before advancing` constraints **only for task progress**. Used `.hiveai/prompts/**` and `.hiveai/audits/**` remain protected. Independent review stays available upon owner request, not required for Codex continuation.

**Storage:** project work ONLY in `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` and GitHub main, or owner-authorized Drive. Codex-managed `.codex/attachments/**` goal-objective copies are app/session artifacts, never project workspaces, authoritative task data or publish destinations; never intentionally write project output there. Do not delete app-managed session material.

**Still prohibited:** new TEMP worktrees or clones, unsafe Git, CI/Actions, paid provider generation without separately agreed spend, external R2/Production writes without explicit owner approval, uncontrolled GUI clicks, changes to original 140 batch or existing production pool, and false READY claims.

---

## OWNER COST LOCK — 2026-10-15 — ZERO GITHUB ACTIONS / ZERO CI

The owner has exhausted GitHub Actions minutes and prohibited additional CI spending. **Until the owner explicitly reverses this rule, neither Codex nor GPT may start, schedule, request, dispatch, or recommend executing a GitHub Actions run, including `workflow_dispatch`, reusable workflows, self-hosted runners, or automatic CI triggers.** Do not substitute another hosted CI provider or paid test service. Do not create or edit workflow files to enable CI as a test path.

Ordinary Git fetch, local edits, commits, and normal main pushes are allowed. The repository's only current workflow, `.github/workflows/c001-r09-safe-regression.yml`, is manual `workflow_dispatch` only, so normal pushes do not invoke it. Recheck the actual workflow triggers before every future push if workflow definitions change; if a push might automatically run billable CI, do not push and report the blocker instead.

Verification uses bounded, explicit **local** source/type/syntax checks and focused in-memory unit tests on the canonical Desktop checkout with no Windows system TEMP pytest process, no worktree/clone and no mass regression. Prevent Python bytecode/pytest cache generation; do not run test suites requiring unapproved scratch directories or touching 140 owner PNG/installed Release/native game. If a test genuinely requires temporary filesystem space, first use a narrow bounded owner-safe repository-local test fixture approach only where permitted by the existing Desktop-only/no-TEMP owner policy, otherwise mark the test **NOT RUN** and continue safe code work. Record exact commands, counts, failures, environment and unrun CI/native gates. **Do not represent local static review as hosted CI or independent full-suite PASS.**

This standing owner cost lock overrides conflicting hosted-run language in historical prompts, criteria, builder logs, or standing instructions. No new alternative CI is authorized.

Before doing project work, read the root `TASKS.md` as the sole current
task-state authority and read the authoritative prompt URL supplied in the
handoff. The tracked GitHub branch is current-state authority; local folders
are execution workspaces.

H!veAI shared files do not override the stricter builder/auditor ownership boundaries below.

---

# ScrubBots Level Factory — Codex Builder Instructions

## Role

You are the implementation builder for this repository.

You implement and verify as Codex builder and OWNER-DELEGATED TASKS.md progress operator. You do NOT impersonate an independent auditor; a ChatGPT independent audit is optional and not a task advancement gate.

## Canonical identity

Repository: `Sekiph82/ScrubBots-Level-Factory`

Canonical GitHub authority: `https://github.com/Sekiph82/ScrubBots-Level-Factory`

Branch: `main`

Local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

The GitHub repository is the sole task authority. The local mirror is not a discovery source. Never switch to another local repository because a file or prompt is missing locally. In particular, never select `C:\Users\sekip\Desktop\ScrubBots` as a substitute.

## Mandatory session start

Before implementation, follow the standing owner rule in:

`docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`

Operational summary:

1. Read the authoritative cycle prompt from the full GitHub URL supplied in the handoff.
2. Verify repository `Sekiph82/ScrubBots-Level-Factory`, canonical origin, and persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
3. Run `git fetch --prune origin`; inspect branch, HEAD, status, ahead/behind, stashes and worktrees.
4. If persistent `main` is clean and only behind, fast-forward only.
5. If the canonical Desktop checkout has owner work, divergence, or a conflict, preserve existing bytes and use only safe in-place non-overlapping operations. No new or reused TEMP worktrees or clones. If safe reconciliation cannot be proved, stop only the affected conflicting operation and continue independent safe work.
6. Never reset, rebase, auto-stash, clean, force, restore/discard, or create a sibling Desktop clone/worktree/copy.
7. Read root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, the active prompt, required previous audit/contracts, and the standing sync/publish standard.
8. Create the matching builder log before product edits.

The persistent Desktop checkout does not need to be made current manually for builder execution when owner-local work exists.

## Mandatory session finish and publication

Before handing a completed task back:

1. Commit authorized implementation/tests.
2. Commit builder log/evidence separately where practical.
3. Fetch/prune and prove current `origin/main` remains an ancestor of local task HEAD.
4. Normal push only: `git push origin HEAD:main`.
5. Fetch/prune again and require local `HEAD == origin/main`, 0 ahead / 0 behind, and clean execution worktree.
6. Return the GitHub builder-log URL.

If GitHub returns a transient server-side error, preserve the exact commits and retry the same normal push up to three times with fetch/ancestry verification before each retry. Do not rebuild, amend, rebase or rewrite good commits because of a transient remote failure.

If remote main advanced and normal fast-forward publication is no longer valid, stop and report the exact divergence. Never force.

## Builder-only boundary

You may implement, test, document implementation details, commit, and push within the active prompt scope.

You must not:

- label a builder verification as an independent audit or invent an independent PASS,
- declare `AUDIT_PASSED`,
- claim unsupported production release or owner acceptance; Codex MAY mark builder-verified task progress and advance PREAUTHORIZED goal stages in TASKS.md,
- edit root `TASKS.md` OUTSIDE the explicit 2026-10-31 owner-authorized current/next task and evidence progression in the stable goal contract; keep historical records and independent audit boundaries immutable,
- edit `.hiveai/HANDOFF.md`,
- create or modify legacy tracker/control-plane files,
- create or modify files under `.hiveai/audits/`,
- modify the active prompt after implementation begins,
- rewrite any prior prompt/log/audit,
- hide failed commands or failed tests after correcting them.

Your passing tests are builder evidence. They may advance CODEX_BUILDER_VERIFIED tasks under the owner's delegation, but never masquerade as independent audit. ChatGPT review is optional on request.

## Codex log requirements

The matching Codex log must use the exact H1 title from the active prompt.

Immediately below the H1 include:

`Document role: CODEX BUILDER LOG`

Record, chronologically and truthfully:

- starting timestamp,
- canonical root verification,
- branch and starting HEAD,
- origin and ahead/behind state,
- initial Git status,
- files and contracts read,
- implementation decisions and rationale,
- every materially relevant command,
- failed commands/tests and subsequent corrections,
- files changed,
- tests added,
- focused test results,
- regression test results,
- offline/network-boundary checks,
- dependency/license changes,
- security/safety observations,
- final diff summary,
- final Git status,
- commit SHA(s),
- push result,
- final local HEAD and `origin/main` equality/divergence.

Never record secrets.

## Repository ownership boundaries

Owner-delegated task state / protected independent records:

- root `TASKS.md`: Codex may update ONLY the current/next actor/task status/evidence and existing owner-approved task checkboxes in the latest stable GOAL scope. No history rewriting.
- `.hiveai/audits/**`: protected independent review records.
- used `.hiveai/prompts/**`: immutable prompt contracts.

`.hiveai/codex-logs/**` are builder evidence archives. There is no second live
tracker, cycle index, event ledger, or machine-state file.

Codex may change ONLY the scoped TASKS.md fields explicitly delegated by the 2026-10-31 owner GOAL continuation; other protected records remain read-only.

## Offline-only invariant

Core pixel-art generation must work without runtime internet access.

Do not add cloud image generation, telemetry requirements, remote APIs, API keys, or runtime HTTP dependencies to the core generator.

## Source-art invariant

One generated logical pixel equals one SCRUBBOTS gameplay cell.

Do not resize, resample, interpolate, or antialias logical source art to force it into board dimensions.

## Historical references

`reference/audits/` contains read-only copies of relevant main SCRUBBOTS audit history. Use them as historical evidence only. Current owner-approved contracts and this repository's active task/prompt authority take precedence.

## H!veAI GitHub tracking

- The repository root `TASKS.md` is the only current project-management/task-state tracker.
- Do not create or revive legacy `.hiveai` tracker/control-plane files or a lowercase root `tasks.md`.
- Prompts, builder logs, audits, README, AGENTS, CLAUDE, and other documents are not tracker inputs.

## Chat-driven Codex factory

- The owner authorized a repository-local Codex factory bootstrap on 2026-10-22, before resuming R08. This authorization is bounded to the current Codex thread and does not authorize release/install operations, CI/Actions, paid services, or owner-data mutations.
- Do not use a dashboard, dashboard inbox, or another task ledger. Ask owner questions and receive answers in the active chat.
- Before processing a task, run `python -B scripts/codex/scrubbots_task_queue.py --json`. This is a read-only guard: it must validate the exact explicit current task and its matching prompt URL from `TASKS.md`; it must never select from the first unchecked row or write/claim/publish `TASKS.md`.
- Work only within the owner's stable continuous-GOAL prompt and its preauthorized existing stages. After each tested builder subtask and verified normal push, Codex MUST update root TASKS.md current/next/evidence status itself, publish the exact tracker commit and continue immediately to the next PREAUTHORIZED safe stage with a fresh queue check. Never infer unrelated tasks from unchecked rows, rerun one-shot gates, or bypass owner-payment/R2/Production/GUI permissions. A blocked external action does not block unrelated authorized work.
- The Codex skill is `.codex/skills/scrubbots-factory/SKILL.md`. It is workflow guidance, not a second status ledger. Keep the independent auditor boundary intact.

## Factory Studio exact visual-master lock

For any Factory Studio owner-UI task, current visual authority is:

- `docs/product/FACTORY_STUDIO_EXACT_THREE_MASTER_UI_V03.md`
- `docs/product/visual-masters/FACTORY_STUDIO_VISUAL_MASTER_INDEX_V01.md`

The owner-facing production UI has exactly three screens:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

Do not add owner-facing production pages, explanatory paragraphs, Technical details links, engineering dashboards, extra cards, extra buttons, or extra visible regions beyond the three masters. The first header label is exactly `PIXEL ART`; there is no leading numeral.

The three visual-master files are layout authority. Dynamic data may change inside master-defined components, but visible structure/control count must not be reinterpreted. Backend safety/canonical authority remains unchanged.
