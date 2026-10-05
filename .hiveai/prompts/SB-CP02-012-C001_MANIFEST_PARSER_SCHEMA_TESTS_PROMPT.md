# SB-CP02-012-C001 — Manifest Parser / Schema Tests

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

1. Verify canonical Desktop repository and git identity/state.
2. Run `git fetch --prune origin`.
3. Read current TASKS; accept standalone `SB-CP02-012-C001` or M13 master authority.
4. Preserve owner-local work byte-for-byte. No reset/clean/auto-stash/rebase/force/restore/discard.
5. Standalone TEMP path: `%TEMP%\ScrubBots-Level-Factory\SB-CP02-012-C001`; master mode reuses master worktree.
6. No Desktop sibling clone/worktree.
7. Require clean 0/0 execution authority.

## Goal

Close M13 with a strict bytes-to-model manifest parser and comprehensive schema/parser regression corpus.

The parser must:
- accept bytes, not trusted pre-parsed objects, at the external boundary;
- require strict UTF-8;
- reject duplicate JSON keys;
- reject NaN/Infinity;
- enforce deterministic maximum byte size, nesting depth, collection size and string length;
- require root object and exact V1 schema/model fields;
- reject unsupported/future schema versions;
- reject unknown fields at every closed schema level;
- reject malformed pack/location/hash/level/disable/schedule/version structures;
- produce immutable validated model only after all checks pass;
- canonical serialize -> parse -> serialize byte identity for accepted semantic content.

Do not execute/import/load any field value.

### Corpus

Add positive and mutation/negative tests spanning all SB-CP02-001..011 semantics, including:
- noncontiguous IDs;
- version gaps;
- too-old game;
- duplicate keys;
- ownership collisions;
- unknown pack/level/schedule references;
- disabled unknown level;
- malformed UTC windows;
- tampered history;
- provider URL/secret-like location rejection;
- future schema;
- malformed JSON/resource-limit cases.

If useful, extract a narrow shared strict-JSON helper only when it does not weaken or regress M11 CP003 authority. Do not rewrite accepted M11 behavior merely for code reuse.

## Verification and publication

Run:
1. CP02-012 focused corpus;
2. full CP02-001..012 focused suite;
3. M12/M11 regressions;
4. governance/tracker;
5. full pytest;
6. compileall;
7. all Content Pipeline JSON schema/example parse checks;
8. diff check.

Builder log:
`.hiveai/codex-logs/SB-CP02-012-C001_MANIFEST_PARSER_SCHEMA_TESTS_CODEX_LOG.md`

No TASKS/audit edits. Separate implementation/log commits. M13 master then performs final master verification and stops for ChatGPT independent audit.
