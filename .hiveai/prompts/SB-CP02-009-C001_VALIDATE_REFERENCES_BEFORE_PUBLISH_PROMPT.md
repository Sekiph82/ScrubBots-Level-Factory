# SB-CP02-009-C001 — Validate Manifest References Before Publish

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch, origin, HEAD, dirty state, stashes, worktrees.
2. Run `git fetch --prune origin`.
3. Read current TASKS; accept standalone `SB-CP02-009-C001` or M13 master authority.
4. Preserve owner-local work. No reset/clean/auto-stash/rebase/force/restore/discard.
5. Standalone TEMP path only: `%TEMP%\ScrubBots-Level-Factory\SB-CP02-009-C001`; master mode reuses M13 master worktree.
6. No Desktop sibling clone/worktree.
7. Require clean 0/0 execution authority before edits.

## Goal

Add one fail-closed local manifest reference validation gate that must pass before any future publish plan may treat a manifest as eligible.

Validate at minimum:
- every level's pack_id references exactly one declared pack;
- every disabled level references a declared level;
- every schedule target references a declared pack/level of the matching target kind;
- pack IDs, logical locations and level ownership remain unique;
- each pack reference matches explicit local M12 pack evidence supplied by the caller:
  - pack_id;
  - pack_version;
  - final archive SHA-256;
  - archive byte length;
  - exact level membership;
- no manifest level is claimed by a pack that does not actually contain that level;
- no declared pack reference is silently accepted without corresponding local evidence.

Use M12 immutable build/inspection evidence where possible instead of reimplementing .scrubpack parsing.

Return deterministic per-check reason codes.

This child remains local-only. No remote HEAD/download/upload or provider call.

On any failed reference, future publish eligibility must be false.

## Verification and publication

Run focused/prior M13, M12/M11, governance, full pytest, compileall, schema parse, diff check.

Builder log:
`.hiveai/codex-logs/SB-CP02-009-C001_VALIDATE_REFERENCES_BEFORE_PUBLISH_CODEX_LOG.md`

No TASKS/audit edits. Separate commits. Master continues to `SB-CP02-010-C001`.
