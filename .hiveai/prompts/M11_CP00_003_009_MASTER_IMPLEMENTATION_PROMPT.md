# M11 MASTER - SB-CP00-003 through SB-CP00-009

Document role: CODEX MASTER IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

This master executes seven already-authorized M11 child tasks continuously:

1. SB-CP00-003-C001
2. SB-CP00-004-C001
3. SB-CP00-005-C001
4. SB-CP00-006-C001
5. SB-CP00-007-C001
6. SB-CP00-008-C001
7. SB-CP00-009-C001

ChatGPT will audit the seven child tasks independently after this master finishes. Codex must not audit or edit root tracker state.

# FIRST TASK - synchronize GitHub and the Desktop local repository

This is the first operational task and must occur before any child implementation.

Canonical persistent Desktop root:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Canonical remote:
`https://github.com/Sekiph82/ScrubBots-Level-Factory.git`

Required preflight:

1. Verify the Desktop root is the canonical repository.
2. Record current branch, HEAD, origin URL, tracked/untracked dirty state, stashes, and all registered worktrees.
3. Run `git fetch --prune origin`.
4. Compare local HEAD and `origin/main`.
5. Read current `origin/main:TASKS.md` and require this exact M11 master prompt as current authority.
6. Synchronize non-destructively:
   - clean behind-only local main -> fast-forward;
   - if legitimate owner-local work exists, preserve every byte;
   - never reset, clean, auto-stash, rebase, force, restore, overwrite, or discard owner work;
   - if the persistent checkout cannot be safely fast-forwarded because of owner-local state, leave it untouched and create/reuse ONE clean master execution worktree at:
     `%TEMP%\ScrubBots-Level-Factory\M11-CP00-003-009-MASTER`
     from exact latest `origin/main`.
7. No Desktop sibling clone/worktree is allowed.
8. Verify the execution worktree is clean and 0/0 against current `origin/main`.
9. Create the master builder log before child product edits:
   `.hiveai/codex-logs/M11_CP00_003_009_MASTER_CODEX_LOG.md`
10. Record the synchronization disposition truthfully in the master log.

If canonical identity or preservation is ambiguous, STOP before product edits. Otherwise continue automatically.

# Master execution rule

After synchronization, execute the child prompts below in exact order.

For each child:
- read its prompt and audit criteria from current execution HEAD;
- implement only that child scope;
- create/update only that child's own builder log;
- run every focused/cumulative/full regression gate required by that child;
- fix in-scope failures before moving on;
- commit implementation separately;
- commit child builder log separately;
- fetch/prune immediately before push;
- push with a normal non-force `HEAD:main` fast-forward only;
- fetch again and require 0/0 parity;
- append child commit/log/test/parity facts to the master log;
- DO NOT edit root `TASKS.md`;
- DO NOT write any strict audit;
- DO NOT ask the owner/ChatGPT for approval between passing children;
- continue immediately to the next child.

The standalone "stop for audit" and standalone final-response clauses inside child prompts are overridden by this master only.

A true blocker is:
- unsafe repository divergence/preservation ambiguity;
- a child contract cannot be satisfied without changing owner authority or another repository outside its authorization;
- required tests cannot be made green within child scope without weakening prior accepted contracts.

On a true blocker:
- publish the truthful child log if safe;
- append blocker evidence to the master log;
- do not fabricate PASS;
- stop the master at that child. Do not build later dependent children on a failed base.

Ordinary test failures are not blockers. Diagnose and remediate them inside the authorized child scope until green.

# Child 1 - SB-CP00-003-C001

Prompt:
`.hiveai/prompts/SB-CP00-003-C001_DECLARATIVE_ONLY_REMOTE_PAYLOAD_POLICY_PROMPT.md`

Criteria:
`.hiveai/audit-criteria/SB-CP00-003-C001_DECLARATIVE_ONLY_REMOTE_PAYLOAD_POLICY_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-CP00-003-C001_DECLARATIVE_ONLY_REMOTE_PAYLOAD_POLICY_CODEX_LOG.md`

# Child 2 - SB-CP00-004-C001

Prompt:
`.hiveai/prompts/SB-CP00-004-C001_STAGING_PRODUCTION_SEPARATION_PROMPT.md`

Criteria:
`.hiveai/audit-criteria/SB-CP00-004-C001_STAGING_PRODUCTION_SEPARATION_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-CP00-004-C001_STAGING_PRODUCTION_SEPARATION_CODEX_LOG.md`

# Child 3 - SB-CP00-005-C001

Prompt:
`.hiveai/prompts/SB-CP00-005-C001_VERSIONED_AUDITABLE_RELEASE_STATE_PROMPT.md`

Criteria:
`.hiveai/audit-criteria/SB-CP00-005-C001_VERSIONED_AUDITABLE_RELEASE_STATE_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-CP00-005-C001_VERSIONED_AUDITABLE_RELEASE_STATE_CODEX_LOG.md`

# Child 4 - SB-CP00-006-C001

Prompt:
`.hiveai/prompts/SB-CP00-006-C001_SECRET_HANDLING_NO_CREDENTIALS_IN_GIT_PROMPT.md`

Criteria:
`.hiveai/audit-criteria/SB-CP00-006-C001_SECRET_HANDLING_NO_CREDENTIALS_IN_GIT_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-CP00-006-C001_SECRET_HANDLING_NO_CREDENTIALS_IN_GIT_CODEX_LOG.md`

# Child 5 - SB-CP00-007-C001

Prompt:
`.hiveai/prompts/SB-CP00-007-C001_PUBLISHER_DRY_RUN_VALIDATION_GATE_PROMPT.md`

Criteria:
`.hiveai/audit-criteria/SB-CP00-007-C001_PUBLISHER_DRY_RUN_VALIDATION_GATE_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-CP00-007-C001_PUBLISHER_DRY_RUN_VALIDATION_GATE_CODEX_LOG.md`

# Child 6 - SB-CP00-008-C001

Prompt:
`.hiveai/prompts/SB-CP00-008-C001_PROVIDER_ABSTRACTION_PROMPT.md`

Criteria:
`.hiveai/audit-criteria/SB-CP00-008-C001_PROVIDER_ABSTRACTION_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-CP00-008-C001_PROVIDER_ABSTRACTION_CODEX_LOG.md`

# Child 7 - SB-CP00-009-C001

Prompt:
`.hiveai/prompts/SB-CP00-009-C001_CONTENT_PLATFORM_GITHUB_COORDINATION_PROMPT.md`

Criteria:
`.hiveai/audit-criteria/SB-CP00-009-C001_CONTENT_PLATFORM_GITHUB_COORDINATION_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-CP00-009-C001_CONTENT_PLATFORM_GITHUB_COORDINATION_CODEX_LOG.md`

# Cross-child preservation rules

Across all seven children:
- do not reopen SB-CP00-001 or SB-CP00-002 unless a real regression proves breakage;
- preserve current LevelData/supply/metadata contract binding;
- no live provider/network mutation in M11;
- no credentials/secrets in Git;
- no Scrubbots runtime implementation;
- no generator/solver/Difficulty duplication;
- no second tracker, roadmap, dashboard, session index, or milestone ledger;
- root `TASKS.md` remains ChatGPT-owned;
- `.hiveai/audits/**` remains ChatGPT-owned;
- each child has its own builder log and implementation/log commit separation.

# Final master verification

After SB-CP00-009 passes and publishes:

1. Fetch/prune `origin`.
2. Require execution HEAD == `origin/main`, divergence 0/0, clean execution worktree.
3. Verify all seven child builder logs exist on `origin/main`.
4. Verify seven child log paths are distinct.
5. Verify root `TASKS.md` was not modified by Codex during the master.
6. Verify no `.hiveai/audits/**` file was modified by Codex.
7. Verify no real provider/network mutation or Scrubbots runtime mutation occurred.
8. Record for each child:
   - base SHA;
   - implementation commit;
   - builder-log commit/final SHA;
   - focused test result;
   - full pytest result;
   - compileall;
   - diff check;
   - final publication parity.
9. Append final master summary to `.hiveai/codex-logs/M11_CP00_003_009_MASTER_CODEX_LOG.md`.
10. Commit/push only the master-log final summary if needed, using normal non-force main publication and final 0/0 verification.

Do not delete the master execution worktree until all GitHub publication/parity checks are complete.

# Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/M11_CP00_003_009_MASTER_CODEX_LOG.md
