# SB-CP03-010-C001 - No Silent Live Overwrite

## FIRST OPERATION - mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-010 / SB-CP03-010-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard.
5. If persistent checkout cannot be safely synchronized, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses the single master worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require clean 0/0 execution authority before edits.

## Goal

Make every live/production manifest mutation compare-and-swap safe and auditable.

Requirements:
- every production manifest write requires explicit expected current production digest and content_version;
- read current production authority immediately before mutation;
- mismatch, missing expected state, changed content_version, changed digest, changed release-state sequence or provider conditional-write conflict fails closed;
- no last-write-wins;
- no blind overwrite;
- exact repeat of already-completed production version may return deterministic idempotent ALREADY_CURRENT only when downloaded bytes/hash/version equal the intended release and release ledger already proves promotion;
- stale publication plans fail using current M11 `validate_plan_current` or stronger exact gate;
- concurrent/racing writer tests must prove only one valid expected-state write can win;
- failed overwrite attempt must not alter prior production object or release ledger;
- no delete/rollback semantics.

## Verification and publication

Run focused tests, prior M14 regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered full pytest, compileall, Content Pipeline JSON parse and diff checks.

Builder log:
`.hiveai/codex-logs/SB-CP03-010-C001_NO_SILENT_LIVE_OVERWRITE_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`. Separate implementation/log commits. Fetch/prune, normal non-force push, fetch again, require 0/0 clean parity.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `SB-CP03-011-C001`.