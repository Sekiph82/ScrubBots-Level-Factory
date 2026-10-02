# P2-ROUTE-A-C001-R01 — Strict Closure Remediation

Document role: CODEX CONTINUATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Canonical GitHub authority:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Parent remediation prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/P2_ROUTE_A_RELEASE_PR_R01_PROMPT.md`

Parent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/P2_ROUTE_A_RELEASE_PR_STRICT_AUDIT.md`

R01 audit criteria:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/P2_ROUTE_A_RELEASE_PR_R01_AUDIT_CRITERIA.md`

## Why this continuation exists

The first R01 handoff stopped before implementation because the persistent Desktop checkout
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
was dirty and behind `origin/main`.

That stop preserved owner work correctly.

The reported task-state mismatch was caused by the stale local `TASKS.md`. GitHub `main` is the sole task authority. The live GitHub tracker authorizes:

- Current Task: `SB-CPX-003`
- Current Sprint: `P2-ROUTE-A-C001-R01`
- Current status: `CHANGES_REQUIRED / R01_AUTHORIZED / REMEDIATE_THEN_REAUDIT`

Do not use the stale Desktop `TASKS.md` to override GitHub task state.

## Explicit temporary-worktree authorization

Governance permits an explicitly authorized temporary worktree only under:
`%TEMP%\ScrubBots-Level-Factory\...`

This prompt grants that authorization for this R01 cycle because the persistent Desktop checkout contains legitimate dirty owner work that must not be touched.

Use exactly one temporary execution worktree under a path such as:

`%TEMP%\ScrubBots-Level-Factory\P2-ROUTE-A-C001-R01`

Do NOT create:
- another Desktop clone;
- another Desktop worktree;
- another persistent repository copy;
- any sibling of the canonical Desktop repository.

## Mandatory synchronization / recovery procedure

Before product work:

1. In the persistent canonical repository, verify:
   - root is `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`;
   - repository is `Sekiph82/ScrubBots-Level-Factory`;
   - origin is the expected GitHub repository;
   - local branch is `main`.
2. Run fetch/prune only.
3. Record:
   - local HEAD;
   - `origin/main`;
   - ahead/behind;
   - full tracked/untracked status;
   - stashes;
   - registered worktrees.
4. Do NOT modify the persistent checkout:
   - no reset;
   - no clean;
   - no stash;
   - no rebase;
   - no merge;
   - no checkout/switch;
   - no commit;
   - no restore;
   - no deletion of owner files.
5. Read current task state from GitHub `main` / fetched `origin/main:TASKS.md`, not the stale working-tree copy.
6. Confirm GitHub authority still says `SB-CPX-003 / P2-ROUTE-A-C001-R01`.
7. Create one detached temporary worktree from the exact current `origin/main`:
   `git worktree add --detach <TEMP_PATH> origin/main`
8. In the temporary worktree verify:
   - HEAD equals the fetched `origin/main`;
   - worktree is clean;
   - GitHub-authoritative `TASKS.md`, parent prompt, strict audit, R01 criteria, GOVERNANCE.md, AGENTS.md and CLAUDE.md are present and current.
9. If the requested temp path already exists:
   - inspect it first;
   - never delete unknown work blindly;
   - reuse only if it is provably this exact authorized worktree and clean at current authority;
   - otherwise stop and report.

The temporary worktree is the only implementation workspace for this continuation.

## Implementation scope

Execute the original P2 R01 remediation exactly as specified by the parent prompt.

Close only:

### F01
Exact byte-for-byte Route A rollback after every post-preflight failure.

### F02
Canonical `Sekiph82/Scrubbots` remote identity must not be caller-overridable in the production Route A API.

### F03
Execute the real default current-game Route A verifier against a full isolated current Scrubbots archive/temp copy with current Godot and require `FACTORY_ROUTE_A_VERIFY_PASS`.

Preserve all previously accepted P2 behavior.

Do not modify root `TASKS.md`.
Do not modify `.hiveai/audits/**`.
Do not modify prior prompts/logs.

## Scrubbots safety

The live owner checkout:
`C:\Users\sekip\Desktop\ScrubBots`
remains read-only authority only.

Never modify it.

Authentic verifier integration must use a full isolated archive/temp copy.

Never push or open a real PR against `Sekiph82/Scrubbots`.

Route A tests that need a remote use only a temporary local bare remote.

## Builder log

Create before product edits:

`.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md`

Use the exact H1:
`# P2-ROUTE-A-C001-R01 — Strict Closure Remediation`

Immediately below:
`Document role: CODEX BUILDER LOG`

The log must include the original Desktop synchronization blocker and the authorized temporary-worktree recovery path.

## Required verification

Run every verification required by the parent R01 prompt and criteria, including:
- P2-R01 focused tests;
- full Route A tests;
- authentic default-verifier integration;
- P1 CampaignBuilder/Release Pool regressions;
- R02 publication/catalog regressions;
- governance tracker tests;
- full pytest;
- compileall;
- git diff --check;
- Factory Studio runtime/action integration suites.

Full pytest must be green except truthful pre-capability skips.

## Commit / push from the temporary worktree

The persistent Desktop checkout remains untouched.

In the temporary worktree:

1. Commit the R01 implementation.
2. Commit the builder log separately from implementation.
3. Immediately before pushing:
   - `git fetch --prune origin`;
   - require the current `origin/main` still equals the base authority from which the temporary worktree was created, unless the only newer commits are this task's own already-pushed commits;
   - if unrelated `origin/main` advanced, STOP. Do not rebase, force, or silently merge.
4. Because `main` is already checked out in the persistent dirty worktree, keep the temp worktree detached and publish with a normal fast-forward:
   `git push origin HEAD:main`
5. Never force-push.
6. Fetch again.
7. Require temp HEAD == `origin/main` and divergence 0/0.
8. Confirm only remote branch `main` was created/updated by this Level Factory task.

After successful publication and final evidence:
- remove only the explicitly created temporary worktree through normal `git worktree remove <TEMP_PATH>`;
- do not prune/delete any other registered worktree;
- do not alter the persistent Desktop checkout.

If safe cleanup of the temp worktree cannot be completed, report it truthfully in the builder log.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md
