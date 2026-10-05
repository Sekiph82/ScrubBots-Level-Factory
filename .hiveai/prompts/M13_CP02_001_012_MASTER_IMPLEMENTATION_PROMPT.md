# M13 MASTER — Remote Manifest & Content Versioning

Document role: CODEX MASTER IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Execution order:
1. SB-CP02-001-C001
2. SB-CP02-002-C001
3. SB-CP02-003-C001
4. SB-CP02-004-C001
5. SB-CP02-005-C001
6. SB-CP02-006-C001
7. SB-CP02-007-C001
8. SB-CP02-008-C001
9. SB-CP02-009-C001
10. SB-CP02-010-C001
11. SB-CP02-011-C001
12. SB-CP02-012-C001

# FIRST TASK — mandatory GitHub ↔ Desktop synchronization

Before any M13 child implementation:

1. Verify canonical persistent root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Record repository identity, branch, HEAD, origin URL, tracked/untracked dirty state, stashes and registered worktrees.
3. Run `git fetch --prune origin`.
4. Compare persistent local HEAD with `origin/main`.
5. Read `origin/main:TASKS.md`; require `M13_MASTER_BATCH_AUTHORIZED` and this exact master prompt.
6. Preserve all legitimate owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard.
7. A clean behind-only persistent main may fast-forward. If owner-local state makes sync unsafe, leave it untouched and create/reuse exactly one authorized execution worktree:
   `%TEMP%\ScrubBots-Level-Factory\M13-CP02-001-012-MASTER`
   from exact latest `origin/main`.
8. Never create a Desktop sibling clone/worktree.
9. Require the execution worktree clean and 0/0 against `origin/main`.
10. Create the master builder log before product edits:
    `.hiveai/codex-logs/M13_CP02_001_012_MASTER_CODEX_LOG.md`
11. Record truthful sync disposition.

If repository identity, owner-work preservation or remote overlap is ambiguous, STOP before product edits.

# Continuous execution rule

Execute all 12 children in exact order.

For each child:
- fetch/read that child's prompt and audit criteria from current execution HEAD;
- implement only that child scope;
- create/update only that child's distinct builder log;
- run its focused tests plus all prior M13 child regressions, M12/M11 regressions, governance, full pytest, compileall, schema parse and diff check as required;
- fix ordinary in-scope failures before continuing;
- commit implementation separately;
- commit child log separately;
- fetch/prune immediately before push;
- push only normal non-force `HEAD:main`;
- fetch again and require HEAD == `origin/main`, 0/0 divergence, clean worktree;
- append child base SHA, implementation SHA(s), log SHA(s), test results and parity to the master log;
- never edit root `TASKS.md`;
- never write `.hiveai/audits/**`;
- continue immediately to the next passing child without owner/ChatGPT handoff.

Standalone stop clauses inside child prompts are overridden by this master.

A true blocker is only:
- unsafe repository/preservation ambiguity;
- a child contract cannot be satisfied without violating accepted M11/M12/M13 authority;
- required tests cannot be made green without weakening accepted contracts.

On true blocker, publish truthful child/master evidence if safe and stop. Do not fabricate PASS.

# M13 architecture invariants

Across all children:

- manifest is declarative JSON only;
- no executable/script/plugin/resource/native payload;
- no provider upload/download/network implementation;
- no CDN/URL/provider selection;
- pack locations remain provider-neutral relative logical object keys;
- no credentials/secrets in manifest/project data;
- M12 `.scrubpack` identity/hashes remain authoritative;
- content_version is numeric and strictly monotonic for successor/history semantics;
- level IDs never require contiguous numeric sequencing;
- disabled/scheduled metadata never mutates pack bytes;
- all activation-time evaluation uses explicit UTC input, never hidden clock;
- reference validation is local and binds to explicit M12 pack evidence;
- history is append-only and does not perform rollback;
- runtime compatibility logic remains pure Content Platform logic, not Godot/game integration;
- M14 owns publish/staging/production mutation;
- M15/M16 own game runtime/cache;
- M17 owns operational rollback/scheduling activation;
- M18 owns provider/CDN;
- root `TASKS.md` remains ChatGPT-owned.

# Child authority map

## Child 1 — SB-CP02-001-C001

Prompt: `.hiveai/prompts/SB-CP02-001-C001_REMOTE_MANIFEST_V1_SCHEMA_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-001-C001_REMOTE_MANIFEST_V1_SCHEMA_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-001-C001_REMOTE_MANIFEST_V1_SCHEMA_CODEX_LOG.md`

## Child 2 — SB-CP02-002-C001

Prompt: `.hiveai/prompts/SB-CP02-002-C001_MONOTONIC_CONTENT_VERSION_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-002-C001_MONOTONIC_CONTENT_VERSION_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-002-C001_MONOTONIC_CONTENT_VERSION_CODEX_LOG.md`

## Child 3 — SB-CP02-003-C001

Prompt: `.hiveai/prompts/SB-CP02-003-C001_MINIMUM_GAME_VERSION_COMPATIBILITY_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-003-C001_MINIMUM_GAME_VERSION_COMPATIBILITY_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-003-C001_MINIMUM_GAME_VERSION_COMPATIBILITY_CODEX_LOG.md`

## Child 4 — SB-CP02-004-C001

Prompt: `.hiveai/prompts/SB-CP02-004-C001_PACK_IDS_LOCATIONS_HASHES_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-004-C001_PACK_IDS_LOCATIONS_HASHES_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-004-C001_PACK_IDS_LOCATIONS_HASHES_CODEX_LOG.md`

## Child 5 — SB-CP02-005-C001

Prompt: `.hiveai/prompts/SB-CP02-005-C001_LEVEL_METADATA_NONCONTIGUOUS_IDS_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-005-C001_LEVEL_METADATA_NONCONTIGUOUS_IDS_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-005-C001_LEVEL_METADATA_NONCONTIGUOUS_IDS_CODEX_LOG.md`

## Child 6 — SB-CP02-006-C001

Prompt: `.hiveai/prompts/SB-CP02-006-C001_DISABLED_LEVELS_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-006-C001_DISABLED_LEVELS_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-006-C001_DISABLED_LEVELS_CODEX_LOG.md`

## Child 7 — SB-CP02-007-C001

Prompt: `.hiveai/prompts/SB-CP02-007-C001_SCHEDULED_ACTIVATION_WINDOWS_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-007-C001_SCHEDULED_ACTIVATION_WINDOWS_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-007-C001_SCHEDULED_ACTIVATION_WINDOWS_CODEX_LOG.md`

## Child 8 — SB-CP02-008-C001

Prompt: `.hiveai/prompts/SB-CP02-008-C001_REJECT_DUPLICATE_PACK_LEVEL_OWNERSHIP_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-008-C001_REJECT_DUPLICATE_PACK_LEVEL_OWNERSHIP_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-008-C001_REJECT_DUPLICATE_PACK_LEVEL_OWNERSHIP_CODEX_LOG.md`

## Child 9 — SB-CP02-009-C001

Prompt: `.hiveai/prompts/SB-CP02-009-C001_VALIDATE_REFERENCES_BEFORE_PUBLISH_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-009-C001_VALIDATE_REFERENCES_BEFORE_PUBLISH_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-009-C001_VALIDATE_REFERENCES_BEFORE_PUBLISH_CODEX_LOG.md`

## Child 10 — SB-CP02-010-C001

Prompt: `.hiveai/prompts/SB-CP02-010-C001_MANIFEST_VERSION_HISTORY_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-010-C001_MANIFEST_VERSION_HISTORY_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-010-C001_MANIFEST_VERSION_HISTORY_CODEX_LOG.md`

## Child 11 — SB-CP02-011-C001

Prompt: `.hiveai/prompts/SB-CP02-011-C001_APP_CONTENT_SCHEMA_COMPATIBILITY_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-011-C001_APP_CONTENT_SCHEMA_COMPATIBILITY_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-011-C001_APP_CONTENT_SCHEMA_COMPATIBILITY_CODEX_LOG.md`

## Child 12 — SB-CP02-012-C001

Prompt: `.hiveai/prompts/SB-CP02-012-C001_MANIFEST_PARSER_SCHEMA_TESTS_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP02-012-C001_MANIFEST_PARSER_SCHEMA_TESTS_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP02-012-C001_MANIFEST_PARSER_SCHEMA_TESTS_CODEX_LOG.md`

# Final master verification

After Child 12 publishes:

1. Fetch/prune origin.
2. Require execution HEAD == `origin/main`, 0/0 divergence, clean worktree.
3. Verify all 12 distinct child logs exist on `origin/main`.
4. Verify Codex did not modify root `TASKS.md` or `.hiveai/audits/**`.
5. Verify no provider/network/runtime/game mutation or credentials were introduced.
6. Run final cumulative CP02-001..012 suite, M12/M11 regressions, governance, full pytest, compileall, all Content Pipeline schema/example JSON parses and diff check.
7. Record exact final results and each child implementation/log commit in the master log.
8. Commit/push only the final master-log update if needed, normal non-force.
9. Final fetch and parity verification.

Do not delete the master worktree until all publication checks finish.

# Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/M13_CP02_001_012_MASTER_CODEX_LOG.md
