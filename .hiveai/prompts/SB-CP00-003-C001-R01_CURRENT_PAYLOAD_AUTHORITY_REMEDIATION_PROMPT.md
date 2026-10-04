# SB-CP00-003-C001-R01 — Current Payload Authority Remediation

Document role: CODEX REMEDIATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent strict audit:
`.hiveai/audits/SB-CP00-003-C001_DECLARATIVE_ONLY_REMOTE_PAYLOAD_POLICY_STRICT_AUDIT.md`

M11 master audit:
`.hiveai/audits/M11_CP00_003_009_MASTER_STRICT_AUDIT.md`

R01 criteria:
`.hiveai/audit-criteria/SB-CP00-003-C001-R01_CURRENT_PAYLOAD_AUTHORITY_AUDIT_CRITERIA.md`

## FIRST OPERATION — mandatory local <-> GitHub synchronization

Before implementation, tests, or builder-log work:

1. Verify the canonical persistent Level Factory root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify repository identity, branch, origin, HEAD, dirty tracked/untracked state, stashes, and registered worktrees.
3. Run `git fetch --prune origin`.
4. Read current GitHub/`origin/main:TASKS.md`; require `SB-CP00-003-C001-R01` and this exact remediation prompt.
5. Preserve every byte of legitimate owner-local dirty work. Do not reset, clean, auto-stash, rebase, force, restore, overwrite, or discard it.
6. If the persistent checkout cannot be safely fast-forwarded, leave it untouched and create/reuse only:
   `%TEMP%\ScrubBots-Level-Factory\SB-CP00-003-C001-R01`
   from exact latest `origin/main`.
7. Do not create a Desktop sibling clone/worktree.
8. Require the execution worktree clean and 0/0 against `origin/main` before product edits.
9. Stop if repository identity, preservation, or remote overlap is ambiguous.

## Scope

Close only CP003 audit findings F01..F04.

SB-CP00-004, 005 and 006 are already PASS/CLOSED.

SB-CP00-007, 008 and 009 have no independent implementation defect; they are conditional only because their dependency chain includes CP003. Revalidate them after this fix.

Do not redesign M11.

## R01.1 — correct LevelData V1 representation

Current Scrubbots authority:
- `cells` are integer palette indices;
- current production example uses integers 0..palette_size-1;
- `level_validator.gd` builds `PackedInt32Array`.

Fix the validator and all CP003/downstream positive fixtures accordingly.

Require:
- each cell is a real integer, not bool;
- length == width × height;
- 0 <= cell < len(palette);
- string cells such as `"C01"` are not accepted as current LevelData.

### Production dimensions

Use the locked production envelope from canonical Level Factory authority:
- width 20..59;
- height 20..59 independently.

Do not retain 1..256 as the remote-production acceptance envelope.

## R01.2 — correct supply-plan structural authority

Preserve:
`scrubbots.level_supply_plan.v1`, version 1, columnCount 3..5, preview depth 3, non-empty columns.

Add current loader-aligned checks:
- `maxRobotsPerBatch` positive integer;
- every batch `robots` is integer and 1..maxRobotsPerBatch;
- every batchId non-empty and globally unique across the plan;
- each cid is canonical C01..C16;
- batch objects contain only the current structural fields.

### intendedColumnClicks

Do NOT invent a 0-based or 1-based indexing rule unless current authority explicitly defines one.

Current game loader does not consume/validate this field and current production evidence contains 1,2,3 values for three columns.

For payload safety, only validate the field as inert declarative JSON structure consistent with current producer evidence. It must not cause an otherwise current production plan to be rejected because of a guessed click-index convention.

Do not reproduce solver/gameplay logic.

## R01.3 — real production fixtures

Add deterministic pinned fixtures/evidence from current `Sekiph82/Scrubbots` authority for at least:
- one real production LevelData file;
- its real supply-plan file.

Record:
- authority repository;
- authority commit SHA;
- source paths;
- exact SHA-256 of fixture bytes.

The tests must prove the exact fixture bytes pass the corrected payload validator when paired with truthful descriptors.

If external `main` moves during execution, pin a resolved commit and verify the relevant contract/source files are consistent before publishing.

Do not create a runtime network dependency for ordinary unit tests.

## R01.4 — downstream fixture correction

Search M11 tests for synthetic LevelData cells such as:
`["C01", ...]`

Correct CP007/CP008 or other M11 positive fixtures that rely on CP003 so they use current integer cell representation.

Do not change CP004..009 product behavior merely to make tests pass.

## R01.5 — preserve every accepted security surface

Do not weaken:
- strict UTF-8;
- malformed/duplicate/non-finite rejection;
- byte/depth/collection/string limits;
- exact payload digest;
- descriptor contract binding;
- executable-content rejection;
- path/app-code boundary;
- staging/production separation;
- append-only release state;
- secret boundary;
- dry-run no-mutation gate;
- provider abstraction;
- GitHub coordination ownership.

## Required tests

Run at minimum:

1. R01 real-authority payload tests.
2. Original CP003 tests.
3. CP004, CP005, CP006 focused tests.
4. CP007, CP008, CP009 focused tests with corrected current LevelData fixtures.
5. CP001/CP002/R01 tests.
6. root governance/tracker tests.
7. one cumulative M11 CP001..009 focused command.
8. full `python -m pytest -q`.
9. compileall.
10. `git diff --check`.

Full pytest must be green except truthful pre-capability skips.

## Builder log

Create before product edits:

`.hiveai/codex-logs/SB-CP00-003-C001-R01_CURRENT_PAYLOAD_AUTHORITY_CODEX_LOG.md`

Record:
- synchronization disposition;
- pinned external authority SHA;
- exact real fixture source paths/digests;
- old-vs-correct representation evidence;
- focused/cumulative/full results;
- implementation commit;
- builder-log commit;
- final push parity.

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.
Do not rewrite prior child/master logs.

## Publication

Only after all gates pass:
- commit remediation;
- commit builder log separately;
- fetch/prune;
- normal non-force update to Level Factory `main`;
- fetch again and require execution HEAD == origin/main and 0/0 divergence;
- stop for ChatGPT independent R01 re-audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-003-C001-R01_CURRENT_PAYLOAD_AUTHORITY_CODEX_LOG.md
