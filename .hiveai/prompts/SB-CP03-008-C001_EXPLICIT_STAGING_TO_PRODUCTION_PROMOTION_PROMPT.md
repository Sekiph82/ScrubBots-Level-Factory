# SB-CP03-008-C001 - Explicit STAGING to PRODUCTION Promotion

## FIRST OPERATION - mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-008 / SB-CP03-008-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard.
5. If persistent checkout cannot be safely synchronized, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses the single master worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require clean 0/0 execution authority before edits.

## Goal

Implement an explicit provider-neutral promotion transaction from the exact verified STAGING release to PRODUCTION.

Requirements:
- direct local-to-production publication is forbidden;
- require current CP03-007 verified-staging receipt;
- require current PASS CPX-002 current-main replay receipt;
- require owner approval;
- require production target and provider capability negotiation including PRODUCTION_PROMOTION, CONDITIONAL_WRITE, INTEGRITY_VERIFY and ATOMIC_MANIFEST_PUBLISH;
- promotion source must be exact STAGING object identities/bytes already verified;
- promote/copy pack objects into PRODUCTION first, preserving exact bytes and logical identities;
- independently re-read and verify promoted production pack bytes;
- only after all production pack objects verify may the production manifest become write-eligible;
- revalidate CPX-002 receipt freshness immediately before manifest mutation, including current game-main authority drift fence;
- append M11 promotion-pending release-state evidence before final manifest activation;
- any stale staging receipt, owner approval loss, provider conflict, object mismatch or game authority drift blocks;
- no delete/rollback behavior in this child;
- tests use deterministic provider implementation, not real cloud vendor.

If the provider protocol lacks an explicit promotion/copy operation, extend it narrowly and provider-neutrally. Do not implement a vendor adapter.

## Verification and publication

Run focused tests, prior M14 regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered full pytest, compileall, Content Pipeline JSON parse and diff checks.

Builder log:
`.hiveai/codex-logs/SB-CP03-008-C001_EXPLICIT_STAGING_TO_PRODUCTION_PROMOTION_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`. Separate implementation/log commits. Fetch/prune, normal non-force push, fetch again, require 0/0 clean parity.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `SB-CP03-009-C001`.