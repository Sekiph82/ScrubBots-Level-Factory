# SB-CP02-004-C001 — Pack IDs / Locations / Hashes

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Run `git fetch --prune origin`.
3. Read `origin/main:TASKS.md`; accept standalone authority for `SB-CP02-004 / SB-CP02-004-C001` or M13 master authority `.hiveai/prompts/M13_CP02_001_012_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve all legitimate owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard it.
5. Standalone mode may use only `%TEMP%\ScrubBots-Level-Factory\SB-CP02-004-C001` if needed. M13 master mode reuses the single master worktree.
6. Do not create a Desktop sibling clone/worktree.
7. Require the execution worktree clean and 0/0 with `origin/main` before edits. Stop only for unsafe identity/divergence/preservation ambiguity.

## Goal

Define provider-neutral pack references in manifest V1.

Each pack record must include at minimum:
- canonical `pack_id`;
- positive integer `pack_version`;
- logical immutable object key / location;
- exact final `.scrubpack` SHA-256;
- exact archive byte length.

### Location boundary

M18 provider choice is not open yet.

Manifest V1 location must therefore be a provider-neutral relative logical object key, not an HTTP/HTTPS URL, host/domain, filesystem absolute path, drive/UNC path, query/fragment, traversal path, backslash path, or credential-bearing string.

Require safe canonical forward-slash relative keys and `.scrubpack` suffix.

Pack IDs must use one documented safe grammar and reject case-normalized collisions.

Hashes are lowercase 64-hex and byte length is positive integer.

Provide deterministic pack-record serialization and focused malformed/path/hash tests.

Do not read/upload remote objects in this child.

## Verification and publication

Run focused tests, prior M13 regressions, M12/M11 regressions, governance, full pytest, compileall, schema parse and diff check.

Builder log:
`.hiveai/codex-logs/SB-CP02-004-C001_PACK_IDS_LOCATIONS_HASHES_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`. Commit implementation and child log separately. In M13 master mode continue immediately to `SB-CP02-005-C001`.
