# SB-CP00-003-C001 — Declarative-Only Remote Payload Policy

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-10-04

Implementation: `dedb4868343051143a1a8f7f431138ea38eb5075`
Builder log: `.hiveai/codex-logs/SB-CP00-003-C001_DECLARATIVE_ONLY_REMOTE_PAYLOAD_POLICY_CODEX_LOG.md`

## VERDICT

**CHANGES_REQUIRED / R01**

The strict parser/executable-content boundary is strong, but the validator is not compatible with current production LevelData/supply authority.

## PASS surfaces

Accepted and must be preserved:
- UTF-8 strict parsing;
- malformed JSON rejection;
- duplicate-key rejection;
- NaN/Infinity rejection;
- deterministic depth/collection/string/byte limits;
- descriptor/payload SHA-256 binding;
- no payload execution/import/resource loading;
- executable/script/plugin/native/resource smuggling rejection;
- exact descriptor family/contract binding;
- metadata family validation;
- no network/provider/runtime mutation;
- focused/full regression evidence.

## F01 — BLOCKER — LevelData V1 cells use the wrong representation

Current Scrubbots LevelData authority stores `cells` as palette-index integers.

Current production example `data/levels/level_002_apple.json` contains integer cells in range 0..palette_size-1.

Current game `level_validator.gd` constructs `PackedInt32Array` and validates each cell as an integer palette index.

The new validator instead requires every cell to be a string contained directly in `palette`.

Therefore real current production LevelData is rejected while the task-local synthetic fixture passes.

## F02 — MAJOR — Production dimension envelope is wrong

The validator accepts LevelData dimensions 1..256 through `MAX_LEVEL_DIMENSION = 256`.

Locked production truth in this repository is:
- width 20..59;
- height 20..59 independently.

The child prompt explicitly required validation within the existing accepted production envelope.

## F03 — MAJOR — Supply-plan structural validation diverges from current authority

Current game `SupplyPlanLoader` requires each batch robot count to be in:

`1..maxRobotsPerBatch`

The new validator only checks robots > 0 and never enforces the declared per-plan upper bound.

It also does not enforce globally unique batch IDs or canonical C01..C16 color IDs even though current loader authority does.

Conversely, it invents an `intendedColumnClicks` index-range rule (`0 <= index < columnCount`) that is not enforced by current game loader and rejects existing current production supply evidence containing values 1,2,3 for three columns.

The payload safety validator must not invent solver/click indexing semantics absent from the loader contract.

## F04 — MAJOR — Positive tests reproduce the incorrect synthetic contract

CP003 and downstream CP007 positive fixtures use string cells such as `"C01"` rather than current integer palette indices.

Thus the green test suite does not prove acceptance of real current declarative LevelData.

## Required remediation

Close only F01..F04.

Require:
- real LevelData integer palette indices;
- 20..59 dimensions;
- current supply loader structural bounds including robots <= maxRobotsPerBatch, unique batch IDs, canonical CIDs;
- no invented intendedColumnClicks indexing rule;
- pinned real current production LevelData + supply-plan fixtures/evidence;
- update downstream CP007/CP008 fixtures to current LevelData representation;
- preserve every existing security/fail-closed boundary;
- rerun cumulative CP003..009 + governance + full pytest.

No other M11 child is reopened by this audit unless cumulative remediation evidence fails.

## FINAL

`SB-CP00-003 = CHANGES_REQUIRED / R01`
