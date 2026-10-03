# SB-CP00-002-C001-R01 — Current Production Contract Binding

Document role: CODEX BUILDER LOG

## Chronological Record

### Session start and mandatory synchronization preflight

- Starting timestamp: 2026-10-04 01:54:30 +03:00 (Europe/Istanbul).
- Authoritative prompt: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-CP00-002-C001-R01_CURRENT_PRODUCTION_CONTRACT_BINDING_PROMPT.md
- Canonical persistent root verified: `C:/Users/sekip/Desktop/Scrubbots - Pixel Art Generator`; repository origin is `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`, branch `main`, starting HEAD `7c6051589d0a95fc785d7f182ccd0d7f8d7013ce`.
- Before fetch, persistent checkout had 123 modified tracked paths and 53 untracked paths (176 porcelain entries), 18 stashes, and 11 registered worktree entries. The persistent checkout was not edited or synchronized because owner-local work is present.
- `git fetch --prune origin` succeeded and advanced `origin/main` to `e737c98acfcaef9c8568151d4b0d89ebbead813a`; persistent `main` is 0 ahead / 54 behind.
- Per the exact R01 prompt fallback, created detached worktree `C:/Users/sekip/AppData/Local/Temp/ScrubBots-Level-Factory/SB-CP00-002-C001-R01` at `origin/main`. Verified canonical origin, clean status, and 0/0 against `origin/main`.
- Synchronization disposition: persistent checkout is preserved; isolated execution worktree is synchronized and safe for this authorized R01.

### Authority and contract recovery

- Live `origin/main:TASKS.md` Project Status identifies `SB-CP00-002-C001-R01`, `CHANGES_REQUIRED / R01_AUTHORIZED / REMEDIATE_THEN_REAUDIT`, and limits this run to F01/F02 contract binding and drift-guard closure. Root `TASKS.md` was not modified.
- Read the authoritative R01 prompt, `origin/main:AGENTS.md`, `origin/main:GOVERNANCE.md`, parent strict audit `.hiveai/audits/SB-CP00-002-C001_APP_VS_REMOTE_CONTENT_BOUNDARY_STRICT_AUDIT.md`, and R01 audit criteria `.hiveai/audit-criteria/SB-CP00-002-C001-R01_CURRENT_PRODUCTION_CONTRACT_BINDING_AUDIT_CRITERIA.md`.
- Parent audit accepted the fail-closed classifier and security behavior and opened only F01 (production schema identity mismatch) and F02 (self-referential tests without cross-authority drift guards). Those accepted security behaviors are preserved.
- Read current Level Factory `SupplyExporter` and `game_publisher.py` sources from `origin/main`. SupplyExporter builds LevelData with `version`, `id`, `name`, `difficulty`, `width`, `height`, `palette`, and `cells`; its supply output embeds schema `scrubbots.level_supply_plan.v1`, version 1, plus `levelId`, `columnCount`, `visiblePreviewDepth`, and `columns`. The publisher emits metadata schema `scrubbots.level.metadata.v1`, version 1.
- Read current Scrubbots `scripts/data/level_data.gd`, `scripts/gameplay/supply/supply_plan_loader.gd`, and `docs/03_LEVEL_DATA_SPEC.md` read-only at GitHub main commit `5881a68eefdb8a25f28f15f4fc3047e19fbc64df`. LevelData authority is `FORMAT_VERSION == 1` with actual fields `version`, `id`, `name`, `difficulty`, `width`, `height`, `palette`, and `cells`; it has no embedded schema string. SupplyPlanLoader requires schema `scrubbots.level_supply_plan.v1` and version 1.
- Prior implementation files reviewed: CP002 classifier, JSON schema, three examples, README, package exports, and CP002 security tests. No tests or implementation changes had yet been made when this log was created.

### Implementation and verification

- Implementation, focused tests, regression results, publication, and final synchronization evidence will be appended chronologically.
- Replaced misleading root `schema_id` values with explicitly boundary-owned `descriptor_contract_id` values and separate `payload_contract` objects. Supply and publisher metadata carry their actual embedded schema/version; LevelData carries the documented `Level Data Specification` authority/version pair without claiming an embedded schema string.
- Updated the JSON Schema, examples, and README accordingly. Metadata and supply descriptor attributes are documented and tested as projections (`id` to `level_id`, `columnCount` to `columns`, `visiblePreviewDepth` to `preview_depth`) of current producer output.
- Added source-based drift tests that parse the current Factory `SupplyExporter` and `game_publisher.py` AST without importing/executing them, plus a commit-pinned, read-only current Scrubbots contract fixture at `5881a68eefdb8a25f28f15f4fc3047e19fbc64df`. The tests prove LevelData version/field mapping and supply/metadata producer identity; prior synthetic schema IDs are rejected.
- Preserved prior fail-closed/security coverage. Executable key matching now uses whole key tokens so the safe field `descriptor_contract_id` is not mistaken for a script field, while explicit tests retain camel-case `scriptPath`, `nativeCode`, and `modulePath` rejection.
- Changed paths (implementation commit only): `content_pipeline/README.md`, `content_pipeline/schemas/v1/content-boundary.schema.json`, the three schema examples, `content_pipeline/src/scrubbots_content_pipeline/content_boundary.py`, the original CP002 unit test, new `tests/unit/test_sb_cp00_002_r01_contract_binding.py`, and `tests/fixtures/sb_cp00_002_r01/current_scrubbots_contracts.json`.
- No runtime network/provider operation, game/runtime import, Level Factory reverse dependency, credentials, dependency/license change, or root tracker/audit/prompt/prior-log edit was introduced. Classifier and cross-authority verification are local/static and offline.
- Implementation commit: `23b4af21cec49efde150722d343c5bbe0b836eef` (`fix(content-pipeline): bind allowlist to production contracts`), 9 files changed, 360 insertions, 43 deletions.
- After implementation commit, worktree status is clean except for this new R01 builder log; HEAD is detached at the implementation commit, based directly on synchronized `origin/main` `e737c98acfcaef9c8568151d4b0d89ebbead813a`.
- First focused run `python -m pytest tests/unit/test_sb_cp00_002_content_boundary.py tests/unit/test_sb_cp00_002_r01_contract_binding.py -q` failed with 23 failures and 15 passes. Root cause: the existing executable-field scanner treated `descriptor_contract_id` as executable because `descriptor` contains the substring `script`. I am narrowing marker detection to whole normalized key tokens; the failed result is retained here.
- Corrected focused rerun: `python -m pytest tests/unit/test_sb_cp00_002_content_boundary.py tests/unit/test_sb_cp00_002_r01_contract_binding.py -q` — PASS, 38 tests.
- Schema/example/authority fixture JSON parsing with `python -m json.tool` — PASS.
- An initial JSON-validation command was rejected before execution because its workdir argument contained a malformed path; corrected the workdir and reran successfully. No repository files changed during the rejected invocation.
- One read-only `rg` search used an invalid PowerShell-style path glob; reran against explicit test and fixture paths successfully. No repository files changed during the rejected search.
- Prior CP001 and governance focused regression: `python -m pytest tests/unit/test_sb_cp00_001_content_pipeline_boundary.py tests/unit/test_sb_lf00_007_governance_authority.py -q` — PASS, 13 tests.
- `python -m compileall -q content_pipeline/src/scrubbots_content_pipeline src/scrubbots_pixel_factory` and `git diff --check` — PASS; Git emitted only expected LF-to-CRLF working-copy warnings.
- Initial complete `python -m pytest -q` — PASS, 1213 passed and 3 capability/configuration skips in 1321.57s. I then added focused coverage preserving camel-case `nativeCode`/`modulePath` rejection and pinned the external contract fixture identity; rerunning full pytest against this final test/code state before publication.
- Final focused CP002/R01/CP001/governance rerun after that hardening: `python -m pytest tests/unit/test_sb_cp00_002_content_boundary.py tests/unit/test_sb_cp00_002_r01_contract_binding.py tests/unit/test_sb_cp00_001_content_pipeline_boundary.py tests/unit/test_sb_lf00_007_governance_authority.py -q` — PASS, 52 tests. Final compileall and diff check — PASS.
- Final full regression `python -m pytest -q` after all production-code changes and the pinned authority fixture — PASS, 1214 passed, 3 expected configuration/capability skips in 1076.52s. Skip reasons: `SCRUBBOTS_SLOW=1` was not set; canonical ScrubBots checkout capability was not supplied for two bridge tests, so no bridge was exercised.
- After the full run, I clarified the README's descriptor projection mapping and added two focused source/projection assertions without changing production code. The exact final focused CP002/R01/CP001/governance rerun again passed 52 tests; compileall and `git diff --check` again passed.
