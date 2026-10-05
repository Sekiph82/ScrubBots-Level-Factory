# M12 MASTER — .scrubpack Format & Packager

Document role: CODEX MASTER IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Execution order:
1. SB-CP01-001-C001
2. SB-CP01-002-C001
3. SB-CP01-003-C001
4. SB-CP01-004-C001
5. SB-CP01-005-C001
6. SB-CP01-006-C001
7. SB-CP01-007-C001
8. SB-CP01-008-C001
9. SB-CP01-009-C001
10. SB-CP01-010-C001
11. SB-CPX-001-C001

# FIRST TASK — synchronize GitHub and Desktop local repository

Before any child implementation:

1. Verify canonical persistent root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Record branch, HEAD, origin URL, tracked/untracked dirty state, stashes, registered worktrees.
3. Run `git fetch --prune origin`.
4. Compare persistent local HEAD with `origin/main`.
5. Read `origin/main:TASKS.md`; require this exact M12 master prompt as current authority.
6. Preserve all legitimate owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard.
7. Clean behind-only persistent main may fast-forward. If owner-local state makes synchronization unsafe, leave it untouched and create/reuse exactly one master worktree:
   `%TEMP%\ScrubBots-Level-Factory\M12-CP01-001-010-CPX001-MASTER`
   from exact latest `origin/main`.
8. No Desktop sibling clone/worktree.
9. Require execution worktree clean and 0/0 with `origin/main`.
10. Create master builder log before product edits:
    `.hiveai/codex-logs/M12_CP01_001_010_CPX001_MASTER_CODEX_LOG.md`
11. Record truthful sync disposition.

If identity/preservation is ambiguous, STOP before product edits.

# Continuous execution rule

Execute every child below in exact order.

For each child:
- read current child prompt + audit criteria from execution HEAD;
- implement only that child scope;
- create/update only its own child builder log;
- run all required focused/cumulative/full regressions;
- ordinary in-scope failures must be fixed before moving on;
- commit implementation separately;
- commit child log separately;
- fetch/prune immediately before push;
- normal non-force `HEAD:main` push only;
- fetch again and require 0/0 parity;
- append child base/implementation/log/test/parity facts to the master log;
- never edit root `TASKS.md`;
- never write `.hiveai/audits/**`;
- do not wait for human/ChatGPT audit between passing children;
- continue immediately to next child.

Standalone stop/final-response clauses inside child prompts are overridden by this master.

A true blocker is only:
- unsafe repository/preservation ambiguity;
- child contract impossible without changing owner authority or another repository outside authorization;
- required tests cannot be made green without weakening accepted M11/M12 contracts.

On true blocker, publish truthful child/master log if safe and stop. Do not fabricate PASS or continue dependent children.

# Cross-child architecture rules

Across M12:
- `.scrubpack` V1 remains declarative-only and offline/local;
- no executable/script/plugin/resource/native payloads;
- no remote provider/upload/CDN/runtime integration;
- no credentials;
- reuse M11 validators rather than duplicating security logic;
- final pack SHA-256 remains external to the bytes it hashes;
- time used in deterministic core is explicit input;
- no first/last-wins duplicate semantics;
- safe inspection/extraction never executes content;
- `src/scrubbots_pixel_factory/solver_evidence.py` remains LEGACY_NON_PRODUCTION and is not CPX-001 authority;
- SB-CPX-001 uses current canonical READY/Release Pool/supply pipeline evidence only;
- SB-CPX-002 current-main promotion replay remains future M14 scope;
- root `TASKS.md` stays ChatGPT-owned.

## Child 1 — SB-CP01-001-C001

Prompt: `.hiveai/prompts/SB-CP01-001-C001_SCRUBPACK_V1_SPEC_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP01-001-C001_SCRUBPACK_V1_SPEC_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP01-001-C001_SCRUBPACK_V1_SPEC_CODEX_LOG.md`

## Child 2 — SB-CP01-002-C001

Prompt: `.hiveai/prompts/SB-CP01-002-C001_PACKAGE_DECLARATIVE_LEVELS_ONLY_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP01-002-C001_PACKAGE_DECLARATIVE_LEVELS_ONLY_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP01-002-C001_PACKAGE_DECLARATIVE_LEVELS_ONLY_CODEX_LOG.md`

## Child 3 — SB-CP01-003-C001

Prompt: `.hiveai/prompts/SB-CP01-003-C001_PACK_ID_VERSION_TIME_LEVELS_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP01-003-C001_PACK_ID_VERSION_TIME_LEVELS_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP01-003-C001_PACK_ID_VERSION_TIME_LEVELS_CODEX_LOG.md`

## Child 4 — SB-CP01-004-C001

Prompt: `.hiveai/prompts/SB-CP01-004-C001_PER_PACK_SHA256_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP01-004-C001_PER_PACK_SHA256_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP01-004-C001_PER_PACK_SHA256_CODEX_LOG.md`

## Child 5 — SB-CP01-005-C001

Prompt: `.hiveai/prompts/SB-CP01-005-C001_DETERMINISTIC_PACK_SERIALIZATION_ORDER_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP01-005-C001_DETERMINISTIC_PACK_SERIALIZATION_ORDER_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP01-005-C001_DETERMINISTIC_PACK_SERIALIZATION_ORDER_CODEX_LOG.md`

## Child 6 — SB-CP01-006-C001

Prompt: `.hiveai/prompts/SB-CP01-006-C001_DUPLICATE_LEVEL_ID_PREVENTION_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP01-006-C001_DUPLICATE_LEVEL_ID_PREVENTION_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP01-006-C001_DUPLICATE_LEVEL_ID_PREVENTION_CODEX_LOG.md`

## Child 7 — SB-CP01-007-C001

Prompt: `.hiveai/prompts/SB-CP01-007-C001_VALIDATE_EVERY_LEVEL_BEFORE_PACK_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP01-007-C001_VALIDATE_EVERY_LEVEL_BEFORE_PACK_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP01-007-C001_VALIDATE_EVERY_LEVEL_BEFORE_PACK_CODEX_LOG.md`

## Child 8 — SB-CP01-008-C001

Prompt: `.hiveai/prompts/SB-CP01-008-C001_SAFE_UNPACK_INSPECT_TOOLING_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP01-008-C001_SAFE_UNPACK_INSPECT_TOOLING_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP01-008-C001_SAFE_UNPACK_INSPECT_TOOLING_CODEX_LOG.md`

## Child 9 — SB-CP01-009-C001

Prompt: `.hiveai/prompts/SB-CP01-009-C001_DETERMINISTIC_SCRUBPACK_BYTES_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP01-009-C001_DETERMINISTIC_SCRUBPACK_BYTES_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP01-009-C001_DETERMINISTIC_SCRUBPACK_BYTES_CODEX_LOG.md`

## Child 10 — SB-CP01-010-C001

Prompt: `.hiveai/prompts/SB-CP01-010-C001_UNSUPPORTED_PACK_VERSION_REJECTION_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP01-010-C001_UNSUPPORTED_PACK_VERSION_REJECTION_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP01-010-C001_UNSUPPORTED_PACK_VERSION_REJECTION_CODEX_LOG.md`

## Child 11 — SB-CPX-001-C001

Prompt: `.hiveai/prompts/SB-CPX-001-C001_SOLVER_PROVEN_SUPPLY_IDENTITY_PACK_BINDING_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CPX-001-C001_SOLVER_PROVEN_SUPPLY_IDENTITY_PACK_BINDING_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CPX-001-C001_SOLVER_PROVEN_SUPPLY_IDENTITY_PACK_BINDING_CODEX_LOG.md`

# Final master verification

After Child 11 publishes:

1. Fetch/prune origin.
2. Require execution HEAD == `origin/main`, 0/0 divergence, clean execution worktree.
3. Verify all 11 child logs exist on `origin/main` and are distinct.
4. Verify Codex did not modify root `TASKS.md` or `.hiveai/audits/**`.
5. Verify no real network/provider/game/runtime mutation occurred.
6. Run one final cumulative M11+M12 focused suite, full pytest, compileall, diff check.
7. Record each child base SHA, implementation commit, log commit/final SHA, focused result, full-suite result, and parity in master log.
8. Commit/push only final master-log update if needed, normal non-force.
9. Final fetch and parity verification.

Do not delete master worktree until publication checks finish.

# Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/M12_CP01_001_010_CPX001_MASTER_CODEX_LOG.md
