# SB-CP00-002-C001 — App Code vs Remote Content Boundary

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-10-04

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Builder log:
`.hiveai/codex-logs/SB-CP00-002-C001_APP_VS_REMOTE_CONTENT_BOUNDARY_CODEX_LOG.md`

Prompt:
`.hiveai/prompts/SB-CP00-002-C001_APP_VS_REMOTE_CONTENT_BOUNDARY_PROMPT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-CP00-002-C001_APP_VS_REMOTE_CONTENT_BOUNDARY_AUDIT_CRITERIA.md`

Implementation commit:
`e255b936732271a2ef2257849bd654133e6ea732`

Final builder publication:
`4d827949c848f8c5a51d6b115b165cfb46f8e717`

## 1. VERDICT

**CHANGES_REQUIRED**

The fail-closed security boundary is structurally strong, but the accepted remote-declarative contracts are not yet bound to the actual current Level Factory / Scrubbots production content authorities.

## 2. PASSED SURFACES

The following are accepted and must not be reopened without regression evidence:

- root-level `content_pipeline/` boundary remains intact;
- versioned deterministic classifier exists;
- allow-list/fail-closed model exists;
- stable disposition and reason codes exist;
- absolute paths and traversal reject;
- scripts, Python, binaries, plugins/addons, scenes/resources, shaders and unknown types do not become remote content;
- executable fields/references reject;
- classifier performs no payload execution/import;
- no provider implementation or remote mutation exists;
- no network client or credentials were introduced;
- no game/runtime import or reverse Level Factory dependency was introduced;
- root `TASKS.md` remains the sole tracker;
- focused suite passed 32 tests;
- full suite passed 1207 with 3 truthful skips;
- compileall and diff checks passed.

## 3. FINDINGS

### F01 — MAJOR — Remote allow-list schema identities are detached from current production authorities

The classifier currently declares:

- level: `scrubbots.level.v1`
- supply: `scrubbots.supply-plan.v1`
- metadata: `scrubbots.approved-metadata.v1`

But current product authority is different.

Current Level Factory `SupplyExporter` emits:

`schema = "scrubbots.level_supply_plan.v1"`

Current Scrubbots `SupplyPlanLoader` requires exactly:

`scrubbots.level_supply_plan.v1`

Current Level Factory `game_publisher.py` emits metadata with:

`schema = "scrubbots.level.metadata.v1"`

Current LevelData does not carry the classifier's `scrubbots.level.v1` string. Current game authority calls it **Level Data Spec Version 1** and validates the payload by `version == LevelData.FORMAT_VERSION`, currently version 1, plus the LevelData required fields.

Therefore a descriptor that truthfully reports the current supply-plan schema or current publisher metadata schema is rejected by the new classifier as `UNKNOWN_SCHEMA`.

This violates audit criterion D:

> valid current declarative level/supply/metadata descriptors can be accepted

The current tests only prove acceptance of newly invented self-consistent descriptor examples, not actual current production contract identities.

### F02 — MAJOR — Focused tests are self-referential and contain no cross-authority drift guard

The focused tests load examples created by this same task and verify them against constants created by this same task.

There is no regression proving that:
- a current Level Factory LevelData V1 output descriptor is accepted;
- a current `scrubbots.level_supply_plan.v1` output descriptor is accepted;
- a current `scrubbots.level.metadata.v1` publisher descriptor is accepted;
- future drift between Content Pipeline's allow-list and the production exporter/publisher authority fails loudly.

Without that bridge, the remote-content boundary can silently diverge from the actual content it is supposed to package.

## 4. REQUIRED REMEDIATION

Do not weaken any existing rejection/security behavior.

### R01.1 — Bind the three accepted families to current payload authority

Represent the current payload contracts truthfully.

Supply-plan descriptors must bind to:
`scrubbots.level_supply_plan.v1`

Metadata descriptors for current Level Factory publication must bind to:
`scrubbots.level.metadata.v1`

LevelData descriptors must bind to the actual current Level Data Spec Version 1 contract. Since current LevelData authority is version-field based rather than a string `schema` field, do not falsely claim an embedded schema string that the payload does not carry.

The implementation may use a boundary-owned normalized contract identifier only if it separately records and validates the real current payload contract/version semantics and documentation makes that distinction explicit.

### R01.2 — Add cross-authority regression evidence

Tests must prove the allow-list against current source authority, not only task-local examples.

At minimum prove:
- current Level Factory LevelData V1 output shape/version maps to an accepted descriptor;
- current SupplyExporter `scrubbots.level_supply_plan.v1` maps to an accepted descriptor;
- current game_publisher `scrubbots.level.metadata.v1` maps to an accepted descriptor;
- mismatched/obsolete synthetic identifiers such as the current task's `scrubbots.supply-plan.v1` and `scrubbots.approved-metadata.v1` are rejected after cutover;
- production contract drift causes a focused regression failure rather than silent acceptance.

Tests may inspect stable source/fixture authority without importing or executing game/runtime code.

### R01.3 — Preserve all passed security boundaries

Retain:
- allow-list/fail-closed;
- no execution/import;
- executable/reference rejection;
- path escape rejection;
- no network/provider mutation;
- no game/runtime imports;
- no reverse dependency;
- no second tracker.

## 5. FINAL VERDICT

**CHANGES_REQUIRED / R01**

No other defect is opened.

`SB-CP00-002` remains active.
