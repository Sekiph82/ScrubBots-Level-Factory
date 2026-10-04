# SB-CP00-002-C001-R01 — Current Production Contract Binding

Document role: CHATGPT INDEPENDENT STRICT RE-AUDIT

Date: 2026-10-04

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent audit:
`.hiveai/audits/SB-CP00-002-C001_APP_VS_REMOTE_CONTENT_BOUNDARY_STRICT_AUDIT.md`

R01 builder log:
`.hiveai/codex-logs/SB-CP00-002-C001-R01_CURRENT_PRODUCTION_CONTRACT_BINDING_CODEX_LOG.md`

R01 criteria:
`.hiveai/audit-criteria/SB-CP00-002-C001-R01_CURRENT_PRODUCTION_CONTRACT_BINDING_AUDIT_CRITERIA.md`

Implementation:
`23b4af21cec49efde150722d343c5bbe0b836eef`

Final builder publication:
`d1eb971276fa3d65b714cc313ae56fb2f9ea9226`

## 1. VERDICT

**PASS / CLOSED**

Parent findings F01 and F02 are closed. The previously accepted fail-closed security boundary remains intact.

## 2. F01 — CURRENT PRODUCTION CONTRACT BINDING

**PASS**

The classifier no longer pretends the payloads carry task-invented embedded schema names.

It now separates:
- boundary-owned `descriptor_contract_id`;
- real `payload_contract` authority/version.

Current bindings are truthful:

### LevelData
- descriptor identity: `scrubbots.content-pipeline.level-data.v1`;
- payload authority: `Level Data Specification`;
- payload version: `1`;
- no embedded schema string is claimed.

This matches current Level Factory `SupplyExporter` LevelData output and current Scrubbots Level Data Spec / `LevelData.FORMAT_VERSION == 1`.

### Supply plan
- payload schema: `scrubbots.level_supply_plan.v1`;
- version: `1`.

This matches current Level Factory `SupplyExporter` and current Scrubbots `SupplyPlanLoader`.

### Publisher metadata
- payload schema: `scrubbots.level.metadata.v1`;
- version: `1`.

This matches current Level Factory `game_publisher.py`.

The obsolete synthetic identities `scrubbots.supply-plan.v1`, `scrubbots.approved-metadata.v1`, and the prior fake LevelData embedded schema identity no longer pass as current payload authority.

## 3. F02 — CROSS-AUTHORITY DRIFT GUARDS

**PASS**

Focused R01 tests now inspect current Level Factory source authority statically rather than validating only task-local examples.

They verify:
- exact LevelData export field set and version;
- exact current supply schema/version plus projection fields;
- exact publisher metadata schema/version plus projection fields;
- obsolete synthetic identities fail closed.

A commit-pinned Scrubbots contract fixture records the external runtime/spec authority used by the remediation.

Independent audit additionally compared that pin `5881a68eefdb8a25f28f15f4fc3047e19fbc64df` to current Scrubbots `main` `11f0d9d96adc4b8e716718c1fef442964968a8c9`.

Relevant files:
- `scripts/data/level_data.gd`;
- `scripts/gameplay/supply/supply_plan_loader.gd`;
- `docs/03_LEVEL_DATA_SPEC.md`

are unchanged between those commits. The pinned authority therefore still represents current runtime contract truth at audit time.

## 4. SECURITY PRESERVATION

**PASS**

Retained:
- allow-list / fail-closed classification;
- deterministic dispositions/reason codes;
- absolute/traversal/noncanonical path rejection;
- app-code/plugin/resource/shader exclusion;
- executable-field/reference rejection;
- no payload execution/import;
- no provider/network mutation;
- no credentials;
- no runtime/game imports;
- no reverse dependency;
- no second tracker.

The executable-key hardening was corrected so safe `descriptor_contract_id` is not falsely matched by the substring `script`, while explicit `scriptPath`, `nativeCode`, and `modulePath` rejection remains tested.

## 5. DIFF / PUBLICATION SCOPE

Final R01 repository delta contains only:
- Content Pipeline contract/schema/examples/docs;
- R01 fixture/tests;
- R01 builder log.

Codex did not edit root `TASKS.md` or audit files.

Repository remains main-only.

## 6. REGRESSION EVIDENCE

Builder evidence reports final:
- CP002/R01/CP001/governance focused: **52 passed**;
- full pytest: **1214 passed, 3 expected skips, 0 failed**;
- compileall: PASS;
- git diff --check: PASS;
- JSON schema/examples/authority fixture parsing: PASS.

No contradictory repository evidence was found.

## 7. DEFECTS

No BLOCKER, MAJOR, or MINOR defect remains for SB-CP00-002.

## 8. TECHNICAL NOTE

The external Scrubbots authority is represented by a commit-pinned fixture rather than a live network dependency, which preserves offline deterministic tests. Future cross-repository contract refresh should update the pin deliberately when the external authority changes.

This is not a current defect because independent audit verified the pinned contract remains identical to current Scrubbots main for all relevant files.

## 9. FINAL VERDICT

**PASS / CLOSED**

`SB-CP00-002 = PASS / CLOSED`

## 10. REQUIRED REMEDIATION

None.
