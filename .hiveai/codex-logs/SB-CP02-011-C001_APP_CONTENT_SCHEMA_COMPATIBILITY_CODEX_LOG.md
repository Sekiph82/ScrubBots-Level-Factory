# SB-CP02-011-C001 — App / Content Schema Compatibility Behavior

Document role: CODEX BUILDER LOG

## Session start
- 2026-10-06T09:21:45Z (UTC); M13-CONT-001 master continuation.
- Canonical repo `Sekiph82/ScrubBots-Level-Factory`, origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; canonical Desktop work remains preserved. Authorized TEMP execution worktree `%TEMP%\ScrubBots-Level-Factory\M13-CONT-001`.
- Fetched start HEAD and `origin/main`: `0ba2ddc11693c9b10a850a30f4bbf0f0dad0c6c8`; clean status and 0/0 divergence.
- Live root `TASKS.md` confirms M13 master authority and M13-CONT-001 sequential continuation through CP02-012.
- Prompt `.hiveai/prompts/SB-CP02-011-C001_APP_CONTENT_SCHEMA_COMPATIBILITY_PROMPT.md`; SHA-256 `3443A0CCAF238B22044DB08BA50D93AA0FBC69EC9AF7AC2E9D7C6282CD46C66A`.
- Criteria `.hiveai/audit-criteria/SB-CP02-011-C001_APP_CONTENT_SCHEMA_COMPATIBILITY_AUDIT_CRITERIA.md`; SHA-256 `42EBC55618C0B419284F1DB8C77D863C248953BEE6F1E3EFD92A070D2FAB4DE0`.

## Scope
- Pure compatibility decision over explicit game version, supported manifest schema versions, supplied manifest schema/version, and minimum game version.
- Stable outcomes for compatible, unsupported schema, too-old app, invalid app version, and invalid manifest fields.
- No auto-upgrade/downgrade, download, activation, mutation, runtime integration, or bypass of disable/schedule/reference gates.
- Document the exact compatibility decision M15 runtime must later consume without editing the game repository.

## Contracts read
- CP02-011 prompt and audit criteria; live root `TASKS.md`; M13 architecture invariants.
- Existing pure version helpers in `content_pipeline/src/scrubbots_content_pipeline/manifest_v1.py`.

## Implementation and verification
- In progress; no CP02-011 edits or tests yet.
- Focused child compatibility tests: **20 passed in 0.13s**.
- Cumulative CP02-001/009/010/011 + CP01/M12 + CP00/M11 + governance regression set: **388 passed in 14.56s**.

## Implementation and verification
- Added pure `check_app_content_compatibility()` with explicit current game version, app-supported schema/version mapping (positive version sets/sequences or ranges), supplied manifest schema/version, and minimum game version.
- Stable outcomes include `COMPATIBLE`, `UNSUPPORTED_SCHEMA_VERSION`, `GAME_VERSION_TOO_OLD`, `INVALID_APP_VERSION`, `INVALID_APP_CAPABILITY`, and `INVALID_MANIFEST_COMPATIBILITY_FIELDS`. Unknown future schemas and unsupported schema versions fail closed.
- Compatibility stays separate from content-version history, parsing, references, disabled levels, and schedules. The M15 documentation names the exact explicit inputs and requires separate parser/reference/disable/schedule steps after compatibility PASS.
- Focused child tests: **20 passed in 0.13s**.
- Cumulative CP02-001/009/010/011 + CP01/M12 + CP00/M11 + governance set: **388 passed in 14.56s**.
- Unfiltered `python -m pytest -q`: **1,546 passed, 19 skipped in 851.86s**. Skips were existing explicit unavailable ScrubBots/Godot capability checks.
- `python -m compileall -q content_pipeline/src tests/unit/test_sb_cp02_011_compatibility.py`: PASS.
- All **16** Content Pipeline JSON files parsed: PASS. `git diff --check` and staged diff check: PASS; only configured LF-to-CRLF warnings.
- No remote/provider/network operations, credentials, dependencies, runtime/game integration, or TASKS/audit edits.
- Implementation commit: `199860ab55c5bd6254e18438dce4f5565a3149da` (`Add explicit app content compatibility gate`).
- Files changed: compatibility API/module, package exports, compatibility tests, and `REMOTE_CONTENT_MANIFEST_V1.md` M15 contract documentation.

## Publication
- Child log commit and normal push/fetch parity will be recorded after publication.
- Normal non-force push `git push origin HEAD:main` succeeded; remote advanced from `0ba2ddc11693c9b10a850a30f4bbf0f0dad0c6c8` to `bc82bbc793d950008dfb274631d36d3aa4b726dd`.
- Post-push `git fetch --prune origin` verified local HEAD == `origin/main` == `bc82bbc793d950008dfb274631d36d3aa4b726dd`, 0/0 divergence, and clean status. Initial child log commit: `bc82bbc793d950008dfb274631d36d3aa4b726dd`.
