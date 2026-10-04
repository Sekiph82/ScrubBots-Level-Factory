# SB-CP00-006-C001 - Secret Handling, No Credentials in Git

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent sequence:
`SB-CP00-001..005` must be implemented and green before this child begins in M11 master mode.

## FIRST OPERATION - mandatory local <-> GitHub synchronization

Before implementation, tests, or builder-log work:

1. Verify the canonical persistent Level Factory path, repository identity, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Fetch/prune current `origin/main`.
3. Read task authority from GitHub/`origin/main:TASKS.md`. Accept either standalone authority for `SB-CP00-006 / SB-CP00-006-C001`, or the explicit M11 master authority `.hiveai/prompts/M11_CP00_003_009_MASTER_IMPLEMENTATION_PROMPT.md` that lists this child in sequence.
4. Preserve legitimate owner-local dirty work. Do not reset, clean, auto-stash, rebase, force, overwrite, restore, or discard it.
5. In standalone mode, if the persistent checkout cannot be safely synchronized, use only an explicitly authorized temp worktree under `%TEMP%\ScrubBots-Level-Factory\SB-CP00-006-C001`, based on current `origin/main`.
6. In M11 master mode, reuse the single master execution worktree. Do not create another child worktree.
7. Do not create a Desktop sibling clone/worktree.
8. Stop only if repository identity, remote authority, or safe preservation is ambiguous.

## Goal

Implement:

`SB-CP00-006 - Secret handling; no credentials in Git.`

Define the secret boundary without introducing real provider credentials or remote access.

## Required secret model

Add a small versioned secret-reference contract that stores only opaque references, never secret values.

Allowed examples:
- provider-neutral secret reference ID;
- logical purpose;
- environment binding;
- optional key/version label that is not itself secret.

Forbidden in tracked config/state/report objects:
- passwords;
- API keys;
- access/refresh tokens;
- private keys;
- client secrets;
- connection strings containing credentials;
- provider secret values of any kind.

Do not implement a live secret manager or OS credential retrieval in this task.

## Serialization/redaction

Requirements:
- secret references may serialize;
- secret values must have no serializable field in the core model;
- reports/plans/events must never include secret material;
- provide deterministic redaction/safe-repr behavior for future error/report integration;
- accidental mappings containing obvious secret-bearing field names fail validation or are redacted before evidence serialization.

Avoid false claims that regex scanning alone proves the repository secret-free.

## Repository guard

Add focused static guard/tests over relevant tracked Content Pipeline config/examples/code to catch obvious committed credential material and private-key blocks.

Use narrow patterns with fixture-safe exclusions so tests are stable.

No test may print a secret fixture value into logs.

## Environment separation

Secret references must be environment-scoped. A staging secret reference cannot silently satisfy a production requirement.

## Architecture preservation

No remote secret fetch, provider network call, runtime import, reverse dependency, or second tracker.

## Tests

Required:
- only opaque references accepted;
- raw secret fields rejected;
- serialization cannot expose secret value;
- redaction deterministic;
- staging/production secret-ref mismatch rejected;
- static tracked-file secret guard;
- no secret value in builder/report/state serialization;
- prior SB-CP00-001..005 regressions green;
- full pytest, compileall, diff check.

## Builder log

Create:
`.hiveai/codex-logs/SB-CP00-006-C001_SECRET_HANDLING_NO_CREDENTIALS_IN_GIT_CODEX_LOG.md`

Do not edit root `TASKS.md` or audits.

## Publication

After all gates pass:
- commit implementation;
- commit this child builder log separately;
- fetch/prune;
- normal non-force update to Level Factory `main`;
- verify execution HEAD == `origin/main` and divergence 0/0.

Standalone mode: stop for independent ChatGPT audit.

M11 master mode: do not edit root `TASKS.md`, do not write an audit, do not wait for human review, and continue directly to `SB-CP00-007-C001`.

## Final response

Standalone mode: return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-006-C001_SECRET_HANDLING_NO_CREDENTIALS_IN_GIT_CODEX_LOG.md

M11 master mode: no user handoff here. Return control to the master prompt.