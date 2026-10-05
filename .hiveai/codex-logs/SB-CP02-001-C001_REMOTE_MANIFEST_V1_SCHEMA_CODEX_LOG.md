# SB-CP02-001-C001 — Define Versioned Remote Manifest V1 Schema

Document role: CODEX BUILDER LOG

## Chronological record

### Authority and implementation

- Timestamp: 2026-10-06 01:25:21 +03:00 (Europe/Istanbul client context).
- Executed in the M13-authorized worktree `%TEMP%\ScrubBots-Level-Factory\M13-CP02-001-012-MASTER`, based on `227f47af0b843043ac7d0c2756a59fee7e1da07f`; branch is detached, origin is `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`, and the worktree began clean at 0/0 with `origin/main`.
- Read this child prompt and audit criteria, M13 master prompt/wrapper, root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, M11 final closure audit, M12 final closure audit, and `docs/content_platform/SCRUBPACK_V1_SPEC.md`.
- Added immutable `ManifestPackV1`, `ManifestLevelV1`, and `ContentManifestV1` types in `manifest_v1.py`. The closed root uses `scrubbots.content.manifest.v1` and integer `schema_version = 1`; collection ordering and JSON bytes are deterministic. Unknown root/item fields, unsupported identity/version, invalid IDs, and duplicate IDs fail closed.
- Added the JSON Schema draft 2020-12 contract, canonical minimal empty fixture, Content Platform documentation, package exports, and focused tests. No content version, compatibility, location/hash, schedule, disable, history, network, provider, or game-runtime behavior was added.
- Updated the inherited CP010 source-change guard after its initial regression run rejected any Content Platform source change. It now permits only the authorized `manifest_v1.py` and package export paths and retains its full package AST scan for forbidden network/provider/runtime imports and its tracker checks.

### Commands and verification

- `python -m pytest -q tests/unit/test_sb_cp02_001_remote_manifest_v1.py`: initial run failed 1 / passed 8 because the fixture was pretty-printed while the model emits canonical compact JSON. The fixture and assertion were corrected; rerun passed **9**.
- M11/M12, governance, and child regression command: `python -m pytest -q` over all `tests/unit/test_sb_cp00_*.py`, `tests/unit/test_sb_cp01_*.py`, `tests/unit/test_sb_lf00_007_governance_authority.py`, and the child 001 test. Initial run had 260 passed / 1 failed on the inherited CP010 source-change guard described above. After the bounded guard update, rerun passed **261**.
- `python -m compileall -q content_pipeline/src`: passed.
- PowerShell JSON parse of all Content Pipeline schema/policy JSON plus the new minimal fixture: passed (17 files).
- `git diff --check`: passed. Protected path check for `TASKS.md` and `.hiveai/audits/**`: no changes. The first staged `git diff --cached --check` found an extra blank line at each log EOF; both logs were normalized to one final newline and the staged check then passed.
- `python -m pytest -q` was started as required for the full suite. During the run, the suite launched a Godot integration test whose process command pointed to the separate `C:\Users\sekip\Desktop\Scrubbots` project. That checkout is outside this task's authorized execution scope. I stopped the run before it completed. No full-suite result is claimed; full pytest remains unverified.

### Scope and safety

- No runtime provider, HTTP, CDN, credential, upload/download, or gameplay mutation code was introduced. The new manifest types are local immutable data and do not access external resources.
- No dependency or license changes.
- No root `TASKS.md` or `.hiveai/audits/**` changes.
- Files changed for this child: `content_pipeline/src/scrubbots_content_pipeline/manifest_v1.py`, `content_pipeline/src/scrubbots_content_pipeline/__init__.py`, `content_pipeline/schemas/v1/content-manifest.schema.json`, `content_pipeline/schemas/v1/examples/content-manifest-minimal.json`, `docs/content_platform/REMOTE_CONTENT_MANIFEST_V1.md`, `tests/unit/test_sb_cp02_001_remote_manifest_v1.py`, and the bounded CP010 regression-guard update in `tests/unit/test_sb_cp00_010_mobile_store_policy_boundary.py`.

### Publication

- Implementation commit: `1ed02965620bfbcc7ac39a8c52a97a2c390701a4`.
- Child log commit: pending.
- Push/parity: pending.
- Disposition: child 001 is not claimed green because the mandated unfiltered full pytest result is unverified; the M13 batch is stopping at this safety blocker unless an in-scope full-suite route is available.
