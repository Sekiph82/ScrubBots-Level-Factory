# SB-CP03-011-C001 - One-Command Publish After Individually Testable Stages

## FIRST OPERATION - mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-011 / SB-CP03-011-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard.
5. If persistent checkout cannot be safely synchronized, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses the single master worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require clean 0/0 execution authority before edits.

## Goal

Add one high-level publisher command/API only by composing the already independently testable M14 stages.

It must not duplicate or bypass stage logic.

Required sequence:
1. validation-only gate;
2. accepted Factory -> solver-proven packs;
3. candidate manifest;
4. staging pack upload;
5. staging object integrity;
6. staging manifest publish;
7. staging byte-download verification;
8. CPX-002 current-main replay gate;
9. explicit staging -> production pack promotion;
10. versioned conditional production manifest activation;
11. no-silent-overwrite current-state fence.

Requirements:
- each stage returns typed/immutable evidence consumed by next stage;
- no stage can be skipped by the one-command path;
- any failure stops immediately;
- before production activation, all prior staging evidence remains inspectable;
- failures before production activation leave current production unchanged;
- validation-only and staging-only modes remain independently callable/testable;
- one-command production mode requires explicit owner approval;
- no hidden provider selection or credentials;
- no cleanup/delete that could destroy last-known-good data;
- deterministic operation journal.

CLI may be added only if it calls the same orchestration API and defaults safely.

## Verification and publication

Run focused tests, prior M14 regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered full pytest, compileall, Content Pipeline JSON parse and diff checks.

Builder log:
`.hiveai/codex-logs/SB-CP03-011-C001_ONE_COMMAND_PUBLISH_ORCHESTRATOR_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`. Separate implementation/log commits. Fetch/prune, normal non-force push, fetch again, require 0/0 clean parity.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `SB-CP03-012-C001`.