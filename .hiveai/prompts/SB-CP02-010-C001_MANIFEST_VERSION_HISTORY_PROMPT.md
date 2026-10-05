# SB-CP02-010-C001 — Keep Prior Manifest / Version History

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository and git identity/state.
2. Fetch/prune origin.
3. Read current TASKS; accept standalone `SB-CP02-010-C001` or M13 master authority.
4. Preserve all owner-local work; no destructive git operation.
5. Standalone TEMP path: `%TEMP%\ScrubBots-Level-Factory\SB-CP02-010-C001`; master mode reuses master worktree.
6. No Desktop sibling clone/worktree.
7. Require clean 0/0 execution authority.

## Goal

Define deterministic append-only manifest history suitable for later rollback/audit milestones.

Each history record must bind:
- sequence;
- content_version;
- exact manifest SHA-256;
- exact immutable manifest bytes or a canonical content-addressed representation sufficient to reconstruct/verify the historical manifest;
- previous history-record digest;
- current record digest;
- explicit normalized UTC record time supplied by caller.

Rules:
- content_version must increase strictly;
- no duplicate content_version;
- no record deletion or in-place rewrite;
- chain tampering, reordering, missing record, byte mutation and digest mutation fail verification;
- historical manifest bytes remain inspectable/parseable through current history tooling even if current app compatibility later rejects their schema;
- history itself performs no rollback activation.

Provide deterministic serialize/parse/replay verification APIs.

M17 owns rollback execution. M14 owns remote publication.

## Verification and publication

Run focused/prior M13, M12/M11, governance, full pytest, compileall, schema parse, diff check.

Builder log:
`.hiveai/codex-logs/SB-CP02-010-C001_MANIFEST_VERSION_HISTORY_CODEX_LOG.md`

No TASKS/audit edits. Separate commits. Master continues to `SB-CP02-011-C001`.
