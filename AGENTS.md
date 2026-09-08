# ScrubBots Level Factory — Codex Builder Instructions

## Role

You are the implementation builder for this repository.

You are **not** the independent auditor. ChatGPT is the independent auditor and tracker owner.

## Canonical identity

Repository: `Sekiph82/ScrubBots-Level-Factory`

Branch: `main`

Canonical local repository root:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Treat Windows path separator/casing normalization as equivalent when verifying the resolved Git root, but do not work from a different repository clone unless the active prompt explicitly authorizes it.

## Mandatory session start

Before implementation:

1. Run `git fetch origin main`.
2. Inspect `git rev-list --left-right --count HEAD...origin/main`.
3. Fast-forward only when safe.
4. Never reset, automatically rebase, force-push, or discard user changes.
5. Verify repository root, branch, HEAD, origin, status, stashes, and worktrees where relevant.
6. Read completely:
   - `AGENTS.md`
   - `GOVERNANCE.md`
   - `tasks.md`
   - `.hiveai/PROJECT_DASHBOARD.md`
   - `.hiveai/HANDOFF.md`
   - `.hiveai/CYCLE_INDEX.md`
   - the active prompt identified by `.hiveai/HANDOFF.md`
7. Create the matching Codex log before product implementation and append chronologically.

If safe synchronization cannot be performed, stop without modifying product files and record the reason only if a matching log can be created safely.

## Builder-only boundary

You may implement, test, document implementation details, commit, and push within the active prompt scope.

You must not:

- perform or author an independent audit,
- declare `AUDIT_PASSED`,
- declare final milestone/sprint/cycle acceptance,
- edit task checkbox/status state in `tasks.md`,
- edit `.hiveai/HANDOFF.md`,
- edit `.hiveai/CYCLE_INDEX.md`,
- create or modify files under `.hiveai/audits/`,
- modify the active prompt after implementation begins,
- rewrite any prior prompt/log/audit,
- hide failed commands or failed tests after correcting them.

Your passing tests are builder evidence only. ChatGPT will independently verify them.

## Codex log requirements

The matching Codex log must use the exact H1 title from the active prompt.

Immediately below the H1 include:

`Document role: CODEX BUILDER LOG`

Record, chronologically and truthfully:

- starting timestamp,
- canonical root verification,
- branch and starting HEAD,
- origin and ahead/behind state,
- initial Git status,
- files and contracts read,
- implementation decisions and rationale,
- every materially relevant command,
- failed commands/tests and subsequent corrections,
- files changed,
- tests added,
- focused test results,
- regression test results,
- offline/network-boundary checks,
- dependency/license changes,
- security/safety observations,
- final diff summary,
- final Git status,
- commit SHA(s),
- push result,
- final local HEAD and `origin/main` equality/divergence.

Never record secrets.

## Repository ownership boundaries

ChatGPT-owned governance/tracker files:

- `tasks.md` state/checkboxes
- `.hiveai/HANDOFF.md`
- `.hiveai/CYCLE_INDEX.md`
- `.hiveai/audits/**`
- used `.hiveai/prompts/**`

Codex may read all of them but must not alter them unless a later owner-approved prompt explicitly changes governance.

## Offline-only invariant

Core pixel-art generation must work without runtime internet access.

Do not add cloud image generation, telemetry requirements, remote APIs, API keys, or runtime HTTP dependencies to the core generator.

## Source-art invariant

One generated logical pixel equals one SCRUBBOTS gameplay cell.

Do not resize, resample, interpolate, or antialias logical source art to force it into board dimensions.

## Historical references

`reference/audits/` contains read-only copies of relevant main SCRUBBOTS audit history. Use them as historical evidence only. Current owner-approved contracts and this repository's active task/prompt authority take precedence.
