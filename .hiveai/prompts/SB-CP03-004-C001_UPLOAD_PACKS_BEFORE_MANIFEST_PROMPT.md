# SB-CP03-004-C001 - Upload Packs Before Active Manifest References Them

## FIRST OPERATION - mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-004 / SB-CP03-004-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve legitimate owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard it.
5. If persistent checkout is unsafe to synchronize, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses its single TEMP worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require execution worktree clean and 0/0 with `origin/main` before edits. Stop on unsafe identity/preservation/divergence ambiguity.

## Goal

Implement provider-neutral object-upload orchestration with strict pack-before-manifest ordering.

M18 has not selected a real storage vendor. Use only the existing provider protocols plus deterministic stateful test providers.

Requirements:
- accept only a CP03-003 validated candidate;
- require provider capability negotiation for STAGING object write, integrity verify and conditional write;
- upload each immutable pack object first using its manifest object_key and exact SHA-256;
- deterministic pack operation order;
- fail immediately on first unsuccessful write and return no manifest-write authorization;
- candidate manifest must not be written or referenced until all pack object writes succeed;
- repeated upload of exact same immutable object may be idempotent only when provider evidence proves exact digest equality;
- conflicting existing object digest fails closed;
- no object delete;
- no production target;
- no real vendor SDK/credentials/network adapter in this milestone.

Add a stateful in-memory or local test provider that records call order and exact object bytes without external network.

## Verification and publication

Run focused tests, prior M14 regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered full pytest, compileall, Content Pipeline JSON parse checks and diff check.

Builder log:
`.hiveai/codex-logs/SB-CP03-004-C001_UPLOAD_PACKS_BEFORE_MANIFEST_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.
Commit implementation and builder log separately. Publish normally to main with fetch-before/after and 0/0 clean parity.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `SB-CP03-005-C001`.