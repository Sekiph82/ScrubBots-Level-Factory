# SB-LF04-001-C001-R01 — Authoritative Reconciliation Handoff

Document role: CODEX AUTHORITATIVE HANDOFF

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-001 — Define versioned LevelMetrics`

## Authority correction

The prior Codex stop report is based on the wrong task state.

At handoff preparation, canonical GitHub `main` is:

`f178b8b5c814488f681a41c533ea681017dc0734`

That exact commit is:

`Record SB-LF04-001 audit and open R01`

The root canonical tracker at that exact commit is:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/TASKS.md

Its live parser fields are exactly:

- Current Milestone: `M04 — Difficulty Intelligence & Metrics`
- Current Sprint: `SB-LF04.C001-R01 — LevelMetrics acceptance-gate portability closure`
- Current Task: `SB-LF04-001 — Define versioned LevelMetrics`
- Current Task Status: `READY_FOR_REMEDIATION`
- Current Prompt: `.hiveai/prompts/SB-LF04-001-C001-R01_WINDOWS_RUNNER_IDENTITY_PORTABILITY_AND_FULL_GATE_CLOSURE_PROMPT.md`

Therefore `SB-LF04-001-C001-R01` is the authorized task.

## Sole tracker authority

Only repository-root:

`/TASKS.md`

is authoritative.

Do not use any other file named `TASKS.md` as live task state.

In particular, this path is historical migration evidence only and is **not** authoritative:

`docs/migration/legacy-task-trackers/TASKS.md`

Do not derive current task authorization from:
- legacy tracker files;
- stale owner worktrees;
- prior local branches;
- archived PAG state;
- cached H!veAI state;
- prompt-local historical text.

The repository root `TASKS.md` on current `origin/main` overrides all of them.

## Required clean synchronization before work

Do not trust the prior local worktree that produced the PAG-SP07 mismatch.

Before any remediation edits:

1. Fetch `origin/main`.
2. Resolve:
   `git rev-parse origin/main`
3. Read the canonical tracker directly from the fetched commit:
   `git show origin/main:TASKS.md`
4. Confirm it authorizes `SB-LF04-001-C001-R01`.
5. Create or use a clean execution worktree from `origin/main`.
6. Confirm execution HEAD equals fetched `origin/main`.
7. Confirm root `TASKS.md` in that execution worktree matches `git show origin/main:TASKS.md`.
8. Do not modify root `TASKS.md`.

If any of these checks fail, stop and report:
- exact `origin/main` SHA;
- exact execution HEAD;
- exact absolute path of the `TASKS.md` actually read;
- the six live parser fields from `git show origin/main:TASKS.md`.

Do not substitute another tracker.

## Authorized remediation

After reconciliation succeeds, execute exactly:

`.hiveai/prompts/SB-LF04-001-C001-R01_WINDOWS_RUNNER_IDENTITY_PORTABILITY_AND_FULL_GATE_CLOSURE_PROMPT.md`

Strict audit:

`.hiveai/audits/SB-LF04-001-C001_VERSIONED_LEVEL_METRICS_CONTRACT_STRICT_AUDIT.md`

Expected R01 builder log:

`.hiveai/codex-logs/SB-LF04-001-C001-R01_WINDOWS_RUNNER_IDENTITY_PORTABILITY_AND_FULL_GATE_CLOSURE_CODEX_LOG.md`

## Scope

The LevelMetrics product implementation is retained.

R01 is only:
- Windows exact-byte runner portability;
- required full repository green-gate closure.

Do not begin SB-LF04-002.

## Final response

After completing the R01 remediation, return only:

1. full GitHub URL of the R01 builder log;
2. implementation commit SHA;
3. terminal log-only commit SHA.

Then STOP for independent ChatGPT re-audit.
