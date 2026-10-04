# SB-CP00-003-C001-R01 — Current Payload Authority

Document role: CHATGPT INDEPENDENT STRICT RE-AUDIT

Date: 2026-10-04

Parent audit:
`.hiveai/audits/SB-CP00-003-C001_DECLARATIVE_ONLY_REMOTE_PAYLOAD_POLICY_STRICT_AUDIT.md`

R01 criteria:
`.hiveai/audit-criteria/SB-CP00-003-C001-R01_CURRENT_PAYLOAD_AUTHORITY_AUDIT_CRITERIA.md`

Implementation:
`040f9f53a36fcfcd0e01fbb14f76ef1ca152f1c5`

Final builder publication state observed on main:
`725541b4d76890d2c1ddf698e521cc7427a04c04`

## VERDICT

**PASS / CLOSED**

All parent findings F01..F04 are closed.

## F01 — LevelData V1 representation

**PASS**

Current validator now requires:
- integer cells with exact `type(cell) is int`, excluding bool;
- exact width × height cell count;
- each cell in `0..len(palette)-1`;
- non-empty unique palette strings.

The pinned real production fixture `data/levels/level_002_apple.json` from `Sekiph82/Scrubbots` is accepted byte-for-byte.

The fixture is a 32×32 LevelData payload with 1,024 integer palette-index cells.

String color IDs no longer masquerade as LevelData cell values.

## F02 — production dimensions

**PASS**

Remote production LevelData now enforces independent:
- width 20..59;
- height 20..59.

Publisher metadata keeps its separate prior dimension bound and was not accidentally narrowed.

Boundary tests cover 20×59, 59×20, and the 19/60 rejection edges.

## F03 — supply-plan structural authority

**PASS**

Current `scrubbots.level_supply_plan.v1` validation now requires:
- version 1;
- columnCount 3..5;
- exact columns length;
- non-empty FIFO columns;
- preview depth exactly 3;
- positive integer `maxRobotsPerBatch`;
- every robot count an integer in `1..maxRobotsPerBatch`;
- globally unique non-empty batch IDs;
- canonical C01..C16 CIDs;
- exact current batch object field set.

The prior invented click-index rule is gone. `intendedColumnClicks` is treated as an inert integer list only, so the real production fixture carrying 1,2,3 values is accepted.

## F04 — real-authority tests

**PASS**

Tests now include pinned production evidence from:
`Sekiph82/Scrubbots@31f8e8f03807cacb00bd7ea0d91a2b727b784f35`

Source paths:
- `data/levels/level_002_apple.json`;
- `data/levels/supply/level_002_apple_supply_v1.json`.

Required source path, authority commit and SHA-256 evidence are recorded.

Independent audit confirmed:
- fixture LevelData Git blob equals the pinned/current game source blob;
- fixture supply-plan Git blob equals the pinned/current game source blob;
- current Scrubbots main is `e89b43ae3127dc207fee9f54700286a711224cce`;
- the relevant production files and contract sources are unchanged from the builder's pin/recheck.

## Security preservation

**PASS**

Retained:
- strict UTF-8;
- malformed JSON rejection;
- duplicate-key rejection;
- non-finite-number rejection;
- deterministic byte/depth/collection/string limits;
- exact byte SHA-256 binding;
- descriptor family/identity/projection binding;
- executable/script/plugin/native/resource rejection;
- no payload execution/import/I/O;
- no provider/network/runtime mutation.

## Downstream revalidation

**PASS**

Builder final evidence:
- CP003 focused: 50 passed;
- cumulative CP001..009: 157 passed;
- CP004..006 focused: 33 passed;
- CP007..009 focused: 29 passed;
- CP001/002/R01: 45 passed;
- governance/tracker: 29 passed;
- full pytest: **1326 passed, 3 documented skips, 0 failed**;
- compileall: PASS;
- git diff --check: PASS.

CP007 and CP008 positive fixtures were corrected to integer palette-index LevelData without changing their product semantics.

## Publication / scope

**PASS**

Implementation/log publication was separated. Root `TASKS.md` and `.hiveai/audits/**` were not modified by Codex.

Canonical dirty Desktop owner work remained untouched; execution used the prompt-authorized TEMP worktree.

## Non-blocking audit note

`tests/fixtures/sb_cp00_003_r01/authority.json` contains a typo in the extra informational `git_blob_sha1` field for the supply fixture.

Recorded there:
`d47328643fa9afaaaa6284ecabf10f477628d5f4`

Actual pinned/current Git blob:
`d47328643fa9afaaaa6284ecb9f10f477628d5f4`

This does **not** fail the R01 criteria because the required authority commit, source path, fixture bytes and SHA-256 evidence are correct, and independent audit proved the fixture Git blob itself is exactly equal to the source Git blob. The typo is not used as acceptance authority.

## FINAL

`SB-CP00-003 = PASS / CLOSED`
