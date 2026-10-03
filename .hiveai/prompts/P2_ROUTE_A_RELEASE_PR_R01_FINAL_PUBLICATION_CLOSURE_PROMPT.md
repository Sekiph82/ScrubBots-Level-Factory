# P2-ROUTE-A-C001-R01 — Final Publication Closure

Document role: CODEX CONTINUATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent audit:
`.hiveai/audits/P2_ROUTE_A_RELEASE_PR_STRICT_AUDIT.md`

R01 criteria:
`.hiveai/audit-criteria/P2_ROUTE_A_RELEASE_PR_R01_AUDIT_CRITERIA.md`

Cleanup closure:
`.hiveai/audits/MAINT-LOCAL-HYGIENE-C003_OWNER_CONFIRMATION_CLOSURE_AUDIT.md`

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

Before any implementation, test, commit, or builder-log work:

1. Verify the persistent Level Factory root, repository identity, branch, origin, local HEAD, `origin/main`, ahead/behind, dirty state, stashes, and registered worktrees.
2. Fetch/prune the canonical GitHub origin.
3. Read task authority from fetched GitHub/`origin/main:TASKS.md`; require `SB-CPX-003 / P2-ROUTE-A-C001-R01` and this exact final-closure prompt.
4. Do not modify, reset, clean, stash, rebase, restore, switch, or discard the owner's dirty persistent Level Factory checkout.
5. Reuse only the already authorized P2 temp worktree under `%TEMP%\ScrubBots-Level-Factory\P2-ROUTE-A-C001-R01`.
6. Preserve all existing R01 implementation and append-only builder-log chronology.
7. Compare that temp worktree with current `origin/main`. If incoming commits are coordination/audit/tracker-only and non-overlapping, synchronize non-destructively while preserving R01 work. If product/test overlap or safe reconciliation is ambiguous, STOP.

No new Desktop clone/worktree is allowed.

## Current accepted builder evidence to preserve

Do not reopen already closed work unless regression evidence fails:

- F01 exact rollback implementation/regressions;
- F02 canonical remote override removal/regressions;
- Factory Studio Solve/Analyze unavailable-reason fix;
- five Factory Studio action checks PASS;
- Factory Studio runtime PASS;
- focused Route A/P1/R02 regressions PASS;
- F03 real default verifier PASS on current Scrubbots authority using a non-empty existing production row;
- explicit `FACTORY_ROUTE_A_VERIFY_PASS`;
- game catalog/level/metadata/supply files remained byte-identical.

The only remaining publication blocker is that the previous broad run excluded three tests capable of resolving/probing the sibling Scrubbots checkout.

## Final closure A — identify the exact three previously excluded tests

Before rerunning:

- recover and record the exact three pytest node IDs/files that were excluded in the previous safe broad run;
- record why each could resolve, clone, archive, or otherwise depend on the default sibling Scrubbots checkout;
- do not silently substitute different tests.

If the previous exclusion actually covered a file containing more than one test, record the exact collected node IDs affected.

## Final closure B — create isolated git-backed current-game authority

The live owner game checkout:
`C:\Users\sekip\Desktop\ScrubBots`

is **read-only authority only**. Tests must not run against its working tree.

Create one isolated game-authority workspace under the existing authorized temp tree, for example:

`%TEMP%\ScrubBots-Level-Factory\P2-ROUTE-A-C001-R01\scrubbots-test-authority`

The isolated authority must satisfy ALL:

- content is exact current `Sekiph82/Scrubbots origin/main`;
- HEAD equals the resolved current game `origin/main` SHA;
- it is git-backed, not merely an unpacked directory;
- `git remote get-url origin` normalizes to canonical `Sekiph82/Scrubbots`;
- `origin/main` resolves to the same exact SHA;
- initial worktree is clean;
- no files are copied from the owner's dirty game working tree state;
- creating it does not modify the live game checkout.

A read-only Git operation against the live game repository may be used only to resolve/archive/clone the committed `origin/main` object graph. Never consume its working-tree bytes.

Set for the test process:
`SCRUBBOTS_PROJECT=<isolated git-backed authority path>`

Use the normal discovered Godot executable.

## Final closure C — execute the three tests, then FULL pytest with zero exclusions

First execute the exact three previously excluded tests individually against the isolated authority.

When Godot and isolated current-game authority are available:
- these tests must EXECUTE;
- they must not be skipped for missing Scrubbots capability;
- any timeout, clone/archive failure, API mismatch, or assertion failure is FAIL.

Then run the repository's full pytest suite with:

- no `-k` exclusion;
- no `--ignore`;
- no deselection of the three tests;
- no manual node-list omission;
- the isolated `SCRUBBOTS_PROJECT` environment active.

Record:
- collected count;
- passed count;
- skipped count;
- exact skip reasons.

Truthful unrelated pre-capability skips remain allowed by R01 criteria, but the three previously excluded game-authority tests must not be among them.

## Final closure D — retained regression gates

After the full run, require:

- P2-R01 focused suite PASS;
- full Route A suite PASS;
- non-empty authentic verifier integration PASS;
- P1 CampaignBuilder / Release Pool regressions PASS;
- R02 publisher/catalog regressions PASS;
- governance/tracker guard PASS;
- Factory Studio action integration PASS;
- Factory Studio committed runtime PASS;
- compileall PASS;
- `git diff --check` PASS.

Do not edit root `TASKS.md`.

## Final publication

Only if ALL gates pass:

1. Review final diff against the R01 starting authority.
2. Confirm no live Scrubbots repository files were changed.
3. Commit the R01 implementation. Preserve truthful commit history if an earlier local preservation commit already exists.
4. Append final evidence to:
   `.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md`
5. Commit the final builder-log publication separately.
6. Fetch/prune Level Factory origin immediately before push.
7. If unrelated remote product/test changes overlap R01 scope, STOP.
8. Publish with a normal non-force update to Level Factory `main`.
9. Fetch again and require published HEAD == `origin/main`, divergence 0/0.
10. Do not create another branch or PR.

Do not delete the P2 temp worktree until after successful publication verification. If cleanup is safe after publication, remove only this explicitly authorized P2 temp worktree.

## Builder log final evidence

The log must include:

- exact three previously excluded node IDs;
- isolated game-authority path and exact Scrubbots SHA;
- proof HEAD == origin/main and canonical origin identity;
- individual results for the three tests;
- unfiltered full pytest command and result;
- skip reasons;
- all retained regression results;
- implementation commit SHA;
- builder-log commit SHA;
- push result;
- final Level Factory `origin/main` SHA and 0/0 divergence.

## STOP

After successful publication, stop for ChatGPT independent strict re-audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md
