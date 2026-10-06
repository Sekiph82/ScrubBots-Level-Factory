# M14 MASTER - Publisher, Staging & Production Promotion

Document role: CODEX MASTER IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Execution order:
1. SB-CP03-001-C001
2. SB-CP03-002-C001
3. SB-CP03-003-C001
4. SB-CP03-004-C001
5. SB-CP03-005-C001
6. SB-CP03-006-C001
7. SB-CP03-007-C001
8. SB-CPX-002-C001
9. SB-CP03-008-C001
10. SB-CP03-009-C001
11. SB-CP03-010-C001
12. SB-CP03-011-C001
13. SB-CP03-012-C001

## FIRST TASK - mandatory GitHub ↔ Desktop synchronization

Before any M14 implementation:

1. Verify canonical persistent root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Record repository identity, branch, HEAD, origin URL, tracked/untracked dirty state, stashes and registered worktrees.
3. Run `git fetch --prune origin`.
4. Compare local HEAD with `origin/main`.
5. Read `origin/main:TASKS.md`; require `M14_MASTER_BATCH_AUTHORIZED` and this exact master prompt.
6. Preserve all legitimate owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard.
7. If persistent checkout is unsafe to synchronize, leave it untouched and create/reuse exactly one execution worktree:
   `%TEMP%\ScrubBots-Level-Factory\M14-CP03-001-012-CPX002-MASTER`
   from exact latest `origin/main`.
8. Never create a Desktop sibling clone/worktree.
9. Require execution worktree clean and 0/0 against `origin/main`.
10. Create the master log before product edits:
    `.hiveai/codex-logs/M14_CP03_001_012_CPX002_MASTER_CODEX_LOG.md`

Stop before edits only for unsafe repository identity/preservation/divergence ambiguity.

## Continuous execution rule

Execute all children in exact order.

For every child:
- read its current prompt and audit criteria from execution HEAD;
- create/update only that child's distinct builder log;
- implement only that scope;
- run focused tests, all prior M14 regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered full pytest, compileall, JSON parse and diff checks as required;
- fix ordinary in-scope failures before continuing;
- commit implementation separately;
- commit child log separately;
- fetch/prune before every push;
- push only normal non-force `HEAD:main`;
- fetch after push and require HEAD == `origin/main`, 0/0 divergence, clean worktree;
- append child base SHA, implementation SHA(s), log SHA(s), tests and parity to the master log;
- never edit root `TASKS.md`;
- never write `.hiveai/audits/**`;
- continue immediately to next passing child.

Standalone stop clauses in child prompts are overridden by this master.

True blockers only:
- unsafe repo/owner-work preservation;
- child contract requires violating accepted M11-M13 authority;
- CPX-002 cannot resolve/authentically replay exact current Scrubbots main with Godot;
- required tests cannot be made green without weakening accepted contracts.

On a true blocker, publish truthful evidence if safe and stop. Never fabricate PASS.

## Provider boundary

M14 implements provider-neutral publishing semantics.

Hard rules:
- do not select AWS, GCS, Azure, Cloudflare, Firebase or another real vendor;
- do not add credentials;
- do not add a real cloud/network provider adapter;
- deterministic stateful test provider implementations are allowed for upload/download/promotion transaction tests;
- provider-returned bytes must actually be independently verified where required;
- M18 remains the real provider/CDN integration milestone.

Git/network access used solely to resolve the exact current `Sekiph82/Scrubbots` main authority for CPX-002 is permitted by that child and must use an isolated TEMP authority, never owner Desktop game checkout.

## Safety invariants

Across M14:
- no production mutation before verified staging;
- no production manifest eligibility before every production pack object verifies;
- no promotion without owner approval;
- no promotion without fresh CPX-002 current-main replay PASS;
- no blind overwrite;
- no last-write-wins;
- no deletion of last-known-good content;
- no rollback implementation yet;
- exact pack/manifest bytes and hashes remain authoritative;
- content_version strictly monotonic;
- release-state/history evidence append-only;
- no hidden clock/random authority;
- no credentials/secrets in reports/logs;
- Route A CPX-003 remains PASS/CLOSED and is not rerun.

## Child authority map

### 1. SB-CP03-001-C001
Prompt: `.hiveai/prompts/SB-CP03-001-C001_PUBLISHER_VALIDATION_ONLY_MODE_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-001-C001_PUBLISHER_VALIDATION_ONLY_MODE_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-001-C001_PUBLISHER_VALIDATION_ONLY_MODE_CODEX_LOG.md`

### 2. SB-CP03-002-C001
Prompt: `.hiveai/prompts/SB-CP03-002-C001_SERIALIZE_ACCEPTED_FACTORY_OUTPUT_TO_PACKS_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-002-C001_SERIALIZE_ACCEPTED_FACTORY_OUTPUT_TO_PACKS_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-002-C001_SERIALIZE_ACCEPTED_FACTORY_OUTPUT_TO_PACKS_CODEX_LOG.md`

### 3. SB-CP03-003-C001
Prompt: `.hiveai/prompts/SB-CP03-003-C001_HASHES_CANDIDATE_MANIFEST_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-003-C001_HASHES_CANDIDATE_MANIFEST_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-003-C001_HASHES_CANDIDATE_MANIFEST_CODEX_LOG.md`

### 4. SB-CP03-004-C001
Prompt: `.hiveai/prompts/SB-CP03-004-C001_UPLOAD_PACKS_BEFORE_MANIFEST_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-004-C001_UPLOAD_PACKS_BEFORE_MANIFEST_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-004-C001_UPLOAD_PACKS_BEFORE_MANIFEST_CODEX_LOG.md`

### 5. SB-CP03-005-C001
Prompt: `.hiveai/prompts/SB-CP03-005-C001_VERIFY_REMOTE_OBJECT_INTEGRITY_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-005-C001_VERIFY_REMOTE_OBJECT_INTEGRITY_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-005-C001_VERIFY_REMOTE_OBJECT_INTEGRITY_CODEX_LOG.md`

### 6. SB-CP03-006-C001
Prompt: `.hiveai/prompts/SB-CP03-006-C001_PUBLISH_STAGING_FIRST_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-006-C001_PUBLISH_STAGING_FIRST_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-006-C001_PUBLISH_STAGING_FIRST_CODEX_LOG.md`

### 7. SB-CP03-007-C001
Prompt: `.hiveai/prompts/SB-CP03-007-C001_VERIFY_STAGING_REAL_DOWNLOAD_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-007-C001_VERIFY_STAGING_REAL_DOWNLOAD_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-007-C001_VERIFY_STAGING_REAL_DOWNLOAD_CODEX_LOG.md`

### 8. SB-CPX-002-C001
Prompt: `.hiveai/prompts/SB-CPX-002-C001_CURRENT_MAIN_SUPPLY_REPLAY_PROMOTION_GATE_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CPX-002-C001_CURRENT_MAIN_SUPPLY_REPLAY_PROMOTION_GATE_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CPX-002-C001_CURRENT_MAIN_SUPPLY_REPLAY_PROMOTION_GATE_CODEX_LOG.md`

### 9. SB-CP03-008-C001
Prompt: `.hiveai/prompts/SB-CP03-008-C001_EXPLICIT_STAGING_TO_PRODUCTION_PROMOTION_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-008-C001_EXPLICIT_STAGING_TO_PRODUCTION_PROMOTION_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-008-C001_EXPLICIT_STAGING_TO_PRODUCTION_PROMOTION_CODEX_LOG.md`

### 10. SB-CP03-009-C001
Prompt: `.hiveai/prompts/SB-CP03-009-C001_NEW_VERSIONED_PRODUCTION_MANIFEST_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-009-C001_NEW_VERSIONED_PRODUCTION_MANIFEST_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-009-C001_NEW_VERSIONED_PRODUCTION_MANIFEST_CODEX_LOG.md`

### 11. SB-CP03-010-C001
Prompt: `.hiveai/prompts/SB-CP03-010-C001_NO_SILENT_LIVE_OVERWRITE_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-010-C001_NO_SILENT_LIVE_OVERWRITE_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-010-C001_NO_SILENT_LIVE_OVERWRITE_CODEX_LOG.md`

### 12. SB-CP03-011-C001
Prompt: `.hiveai/prompts/SB-CP03-011-C001_ONE_COMMAND_PUBLISH_ORCHESTRATOR_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-011-C001_ONE_COMMAND_PUBLISH_ORCHESTRATOR_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-011-C001_ONE_COMMAND_PUBLISH_ORCHESTRATOR_CODEX_LOG.md`

### 13. SB-CP03-012-C001
Prompt: `.hiveai/prompts/SB-CP03-012-C001_PUBLISH_REPORT_PROMPT.md`
Criteria: `.hiveai/audit-criteria/SB-CP03-012-C001_PUBLISH_REPORT_AUDIT_CRITERIA.md`
Builder log: `.hiveai/codex-logs/SB-CP03-012-C001_PUBLISH_REPORT_CODEX_LOG.md`

## Final master verification

After SB-CP03-012:
1. Fetch/prune and require HEAD == origin/main, 0/0, clean.
2. Verify all 13 distinct child logs exist.
3. Verify Codex did not modify root TASKS or audit files.
4. Verify no real vendor/provider adapter or credentials were introduced.
5. Verify production path cannot bypass staging, byte verification, CPX-002, owner approval, version monotonicity or conditional-write gates.
6. Verify CPX-002 receipt records authentic current Scrubbots main SHA and authority hashes from a real Godot current-main replay.
7. Run final cumulative M14 + M13/M12/M11 + governance tests.
8. Run safe unfiltered full pytest.
9. Run compileall, Content Pipeline JSON parse and diff check.
10. Append exact final evidence to master log.
11. Publish final master-log update separately and verify final parity.

Stop for ChatGPT independent audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/M14_CP03_001_012_CPX002_MASTER_CODEX_LOG.md
