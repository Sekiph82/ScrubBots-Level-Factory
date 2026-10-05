# SB-CP02-011-C001 — App / Content Schema Compatibility Behavior

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository and git identity/state.
2. Fetch/prune origin.
3. Read current TASKS; accept standalone `SB-CP02-011-C001` or M13 master authority.
4. Preserve owner-local work; no destructive git operations.
5. Standalone TEMP path: `%TEMP%\ScrubBots-Level-Factory\SB-CP02-011-C001`; master mode reuses master worktree.
6. No Desktop sibling clone/worktree.
7. Require clean 0/0 execution authority.

## Goal

Implement pure Content Platform compatibility evaluation between an app capability declaration and a manifest.

Inputs must be explicit:
- current game version;
- set/range of supported manifest schema versions;
- manifest schema/version;
- manifest minimum_game_version.

Return deterministic reason codes at minimum:
- COMPATIBLE;
- UNSUPPORTED_SCHEMA_VERSION;
- GAME_VERSION_TOO_OLD;
- INVALID_APP_VERSION;
- INVALID_MANIFEST_COMPATIBILITY_FIELDS.

Rules:
- unknown future manifest schema fails closed;
- current app version below minimum fails closed;
- same/newer app version may pass;
- compatibility does not auto-upgrade/downgrade, download, activate or mutate anything;
- content_version monotonicity is independent from app semantic version;
- disabled/scheduled/reference validation remains separate and must not be bypassed by compatibility PASS.

Document exactly what M15 runtime must later consume, without editing the game repo.

## Verification and publication

Run focused/prior M13, M12/M11, governance, full pytest, compileall, schema parse, diff check.

Builder log:
`.hiveai/codex-logs/SB-CP02-011-C001_APP_CONTENT_SCHEMA_COMPATIBILITY_CODEX_LOG.md`

No TASKS/audit edits. Separate commits. Master continues to `SB-CP02-012-C001`.
