# SB-CP02-006-C001-R01 — Disabled Level Logical Identity Remediation

Document role: CODEX REMEDIATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent audit:
`.hiveai/audits/SB-CP02-006-C001_DISABLED_LEVELS_STRICT_AUDIT.md`

M13 master audit:
`.hiveai/audits/M13_CP02_001_012_MASTER_STRICT_AUDIT.md`

R01 criteria:
`.hiveai/audit-criteria/SB-CP02-006-C001-R01_DISABLED_LEVEL_IDENTITY_AUDIT_CRITERIA.md`

## FIRST OPERATION — mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify repository identity, branch, origin, HEAD, dirty tracked/untracked state, stashes and worktrees.
3. Run `git fetch --prune origin`.
4. Read `origin/main:TASKS.md`; require `SB-CP02-006-C001-R01` and this exact prompt.
5. Preserve all legitimate owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard.
6. If persistent checkout is not safely fast-forwardable, leave it untouched and create/reuse only:
   `%TEMP%\ScrubBots-Level-Factory\SB-CP02-006-C001-R01`
   from exact latest `origin/main`.
7. Never create a Desktop sibling clone/worktree.
8. Require execution worktree clean and 0/0 against `origin/main`.
9. Stop if repository identity, preservation or remote overlap is ambiguous.

Create builder log before product edits:

`.hiveai/codex-logs/SB-CP02-006-C001-R01_DISABLED_LEVEL_IDENTITY_CODEX_LOG.md`

## Current accepted state

- SB-CP02-001..005 = PASS/CLOSED.
- SB-CP02-006 = CHANGES_REQUIRED / R01.
- SB-CP02-007..011 = PASS/CLOSED.
- SB-CP02-012 = CONDITIONAL only because its cross-child corpus must prove this fix.
- Do not redesign the rest of M13.

## Defect

The manifest uses casefold-equivalent level IDs as one logical identity for:
- collision prevention;
- ownership/reference validation.

But `is_level_disabled()` currently uses exact-string membership.

Example:

- declared level: `Level-A`
- disabled entry: `level-a`
- CP02-009 reference validation accepts this logical reference;
- current `is_level_disabled(manifest, "Level-A")` incorrectly returns false.

## R01.1 — fix only disabled lookup semantics

Preserve exact spelling in:
- `ManifestLevelV1.level_id`;
- `disabled_levels`;
- serialized JSON.

Do NOT lowercase/rename existing IDs.

Change the pure disabled-state lookup so valid ID comparisons follow the same casefold logical identity already used by collision/reference validation.

Expected:
- disabled `level-a` => query `Level-A` true;
- disabled `Level-A` => query `level-a` true;
- query `LEVEL-A` true;
- unrelated valid ID false;
- invalid ID still raises/fails closed exactly as before.

Keep helper pure. No global state, clock, filesystem, runtime or network.

## R01.2 — regressions

Add focused tests to CP006 coverage for:
1. declared mixed-case level + disabled case variant;
2. helper queried with the declared exact spelling;
3. helper queried with another case-equivalent valid spelling;
4. unrelated valid ID false;
5. duplicate/casefold-collision rejection unchanged.

Add CP009 integration regression:
- declared `Level-A`;
- disabled `level-a`;
- otherwise valid local M12 pack evidence;
- reference gate accepts the disabled reference;
- helper reports declared logical level disabled.

Add CP012 corpus regression proving strict parse + helper/reference behavior remains aligned.

Do not alter CP009 eligibility semantics merely to avoid the test.

## R01.3 — documentation

Update manifest documentation narrowly to state:
- level ID spelling is preserved;
- logical collision/reference/disabled-state comparison is casefold-based.

Do not imply that level IDs are rewritten to lowercase.

## Safe full-suite rule

Preserve the already accepted M13-CONT-001 harness behavior.

For the full suite:
- do not set or infer owner Desktop `SCRUBBOTS_PROJECT` / `SCRUBBOTS_CANONICAL_CHECKOUT`;
- explicit capability skips are acceptable;
- no test may silently access the owner Desktop game checkout.

If an implicit external-checkout regression reappears, stop and report it instead of widening authority.

## Required verification

Run at minimum:

1. CP006 focused tests.
2. CP008 ownership tests.
3. CP009 reference tests.
4. CP012 parser/corpus tests.
5. all CP02-001..012 focused tests.
6. M12/M11 regressions.
7. governance/tracker tests.
8. safe unfiltered `python -m pytest -q`.
9. compileall.
10. all Content Pipeline schema/example JSON parses.
11. `git diff --check`.

## Publication

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.
Do not rewrite earlier child/master logs.

If all gates pass:
- commit remediation;
- commit this builder log separately;
- fetch/prune;
- normal non-force push to main;
- fetch again;
- require execution HEAD == origin/main, 0/0 divergence, clean worktree;
- stop for ChatGPT independent R01 re-audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP02-006-C001-R01_DISABLED_LEVEL_IDENTITY_CODEX_LOG.md
