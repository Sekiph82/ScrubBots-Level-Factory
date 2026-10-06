# SB-CP03-001-C001 — Publisher Validation-Only Mode

## FIRST OPERATION — mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-001 / SB-CP03-001-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve every byte of legitimate owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard it.
5. If the persistent checkout is not safely synchronizable, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses its single TEMP worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require the execution worktree clean and 0/0 with `origin/main` before edits. Stop for unsafe identity/preservation/divergence ambiguity.

## Goal

Turn the existing local publication-plan boundary into an explicit publisher validation-only entry point.

Requirements:
- accepts only explicit local candidate inputs and current M11-M13 authorities;
- validates candidate pack/manifest readiness without invoking any mutating provider method;
- produces a deterministic immutable validation report with ordered checks and reason codes;
- requires current target binding, release-state replay, provider capability declaration, owner-approval policy state, manifest parser/reference validation, content-version/compatibility checks and secret-free inputs;
- report must state `remote_mutation_performed=false`;
- no upload/write/delete/promote call is reachable in validation-only mode;
- no network/provider implementation is added;
- malformed/stale inputs fail closed;
- accepted output is suitable input authority for later M14 children but performs no publication.

Preserve M11 `build_publication_plan()` semantics where still authoritative; extend rather than duplicate security logic.

## Verification and publication

Run focused tests, all prior M14 child regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered `python -m pytest -q`, compileall, Content Pipeline JSON parse checks and `git diff --check`.

Builder log:
`.hiveai/codex-logs/SB-CP03-001-C001_PUBLISHER_VALIDATION_ONLY_MODE_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`.

Commit implementation and builder log separately. Fetch/prune, normal non-force push to `main`, fetch again, require 0/0 parity and clean worktree.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `SB-CP03-002-C001`.