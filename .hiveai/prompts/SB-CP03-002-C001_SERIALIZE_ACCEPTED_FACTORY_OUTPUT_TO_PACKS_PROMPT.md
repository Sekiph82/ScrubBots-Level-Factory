# SB-CP03-002-C001 — Serialize Accepted Factory Output into Packs

## FIRST OPERATION — mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-002 / SB-CP03-002-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve every byte of legitimate owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard it.
5. If the persistent checkout is not safely synchronizable, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses its single TEMP worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require the execution worktree clean and 0/0 with `origin/main` before edits. Stop for unsafe identity/preservation/divergence ambiguity.

## Goal

Create the M14 local candidate-pack assembly path from accepted current Factory authority.

Requirements:
- source only current accepted Factory/Release Pool authority, never arbitrary filesystem discovery;
- every packed level must have current owner ACCEPT + current READY authority;
- reuse CPX-001 current-proof freshness at final build;
- build M12 deterministic solver-proven `.scrubpack` bytes;
- one exact logical level appears in one pack only;
- pack ID/version/time/membership are explicit inputs;
- no requested difficulty filter, no hidden wall clock/randomness;
- return exact archive bytes plus M12 immutable build evidence;
- any stale review/READY/pipeline/supply/level/solver identity fails before candidate pack success;
- no remote/provider call.

Do not mutate Factory review state or game repository.

## Verification and publication

Run focused tests, all prior M14 child regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered `python -m pytest -q`, compileall, Content Pipeline JSON parse checks and `git diff --check`.

Builder log:
`.hiveai/codex-logs/SB-CP03-002-C001_SERIALIZE_ACCEPTED_FACTORY_OUTPUT_TO_PACKS_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

Commit implementation and builder log separately. Fetch/prune, normal non-force push to `main`, fetch again, require 0/0 parity and clean worktree.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `SB-CP03-003-C001`.