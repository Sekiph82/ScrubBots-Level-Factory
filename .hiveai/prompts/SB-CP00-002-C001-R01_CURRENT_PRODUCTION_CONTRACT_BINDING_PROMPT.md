# SB-CP00-002-C001-R01 — Current Production Contract Binding

Document role: CODEX REMEDIATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent strict audit:
`.hiveai/audits/SB-CP00-002-C001_APP_VS_REMOTE_CONTENT_BOUNDARY_STRICT_AUDIT.md`

R01 criteria:
`.hiveai/audit-criteria/SB-CP00-002-C001-R01_CURRENT_PRODUCTION_CONTRACT_BINDING_AUDIT_CRITERIA.md`

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

Before implementation, tests, or builder-log work:

1. Verify the canonical persistent Level Factory path, repository identity, branch, origin, local HEAD, dirty state, stashes, and registered worktrees.
2. Fetch/prune current `origin/main`.
3. Read task authority from GitHub/`origin/main:TASKS.md`; require `SB-CP00-002 / SB-CP00-002-C001-R01`.
4. Preserve legitimate owner-local dirty work. Do not reset, clean, stash, rebase, force, overwrite, restore, or discard it.
5. If the persistent checkout cannot be safely synchronized, use only an explicitly authorized temp worktree under `%TEMP%\ScrubBots-Level-Factory\SB-CP00-002-C001-R01`, based on current `origin/main`.
6. Do not create a Desktop sibling clone/worktree.
7. Stop if incoming remote changes overlap remediation scope ambiguously.

## Scope

Close only strict-audit findings F01 and F02.

Preserve all existing SB-CP00-002 security/fail-closed behavior.

Do not add remote publishing, provider implementations, runtime activation, credentials, CDN/storage, or network mutation.

## R01.1 — truthfully bind current payload contracts

Update the Content Pipeline boundary contract so the three remotely eligible families correspond to the current real product authorities.

### Supply plan

Current Level Factory `SupplyExporter` emits and current Scrubbots `SupplyPlanLoader` requires:

`scrubbots.level_supply_plan.v1`

Use that real identity.

### Published metadata

Current Level Factory `game_publisher.py` emits:

`scrubbots.level.metadata.v1`

Use that real identity for current publisher metadata.

### LevelData

Current game authority is **Level Data Spec Version 1**.

Current LevelData is version-based and carries `version: 1`; it does not carry the current classifier's invented `scrubbots.level.v1` embedded schema string.

Model this truthfully.

A boundary-owned normalized descriptor contract ID is allowed only if:
- it is explicitly documented as a Content Pipeline descriptor identity, not a payload-embedded schema;
- the descriptor separately captures the actual payload authority/version;
- tests prove it maps to current LevelData V1.

Do not fabricate an embedded payload schema field that current LevelData does not contain.

## R01.2 — cross-authority drift guards

Add focused tests that derive/check the contract against current repository authority rather than task-local examples alone.

At minimum:

1. LevelData:
   - prove a descriptor representing current Level Factory LevelData V1 output is REMOTE_DECLARATIVE;
   - verify the production authority remains version 1 and the expected LevelData structural contract is represented.

2. Supply plan:
   - prove a descriptor carrying `scrubbots.level_supply_plan.v1` is REMOTE_DECLARATIVE;
   - add a guard that would fail if current SupplyExporter authority changes without the Content Pipeline contract being updated.

3. Metadata:
   - prove a descriptor carrying `scrubbots.level.metadata.v1` is REMOTE_DECLARATIVE;
   - add a guard against current `game_publisher.py` authority drift.

4. Cutover:
   - `scrubbots.supply-plan.v1` must no longer be accepted as current supply authority;
   - `scrubbots.approved-metadata.v1` must no longer be accepted as current publisher metadata authority;
   - any obsolete task-local level schema naming must not masquerade as an embedded current LevelData schema.

Do not execute or import game/runtime payloads to perform these checks. Static source/fixture inspection is acceptable.

## R01.3 — preserve existing security contract

Re-run and preserve:
- executable fields/references rejected;
- .gd/.py/native/plugin/resource/shader families never remote;
- unknown types/schemas fail closed;
- absolute/traversal/noncanonical paths reject;
- deterministic reason codes;
- no dynamic import/eval/exec/open of payload;
- no network/provider implementation;
- no reverse dependency;
- root TASKS only.

## Required verification

Run:
- focused R01 cross-authority tests;
- original SB-CP00-002 boundary tests;
- prior SB-CP00-001 tests;
- governance/tracker tests;
- full pytest;
- compileall;
- git diff --check.

Full pytest must be green except truthful pre-capability skips.

## Builder log

Create:
`.hiveai/codex-logs/SB-CP00-002-C001-R01_CURRENT_PRODUCTION_CONTRACT_BINDING_CODEX_LOG.md`

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.
Do not rewrite prior builder logs.

## Publication

After all gates pass:
- commit remediation;
- commit builder log separately;
- fetch/prune;
- normal non-force push to Level Factory `main`;
- verify local/remote 0/0;
- stop for independent ChatGPT re-audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-002-C001-R01_CURRENT_PRODUCTION_CONTRACT_BINDING_CODEX_LOG.md
