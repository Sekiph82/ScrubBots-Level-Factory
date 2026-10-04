# SB-CP00-008-C001 - Provider Abstraction

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent sequence:
`SB-CP00-001..007` must be implemented and green before this child begins in M11 master mode.

## FIRST OPERATION - mandatory local <-> GitHub synchronization

Before implementation, tests, or builder-log work:

1. Verify the canonical persistent Level Factory path, repository identity, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Fetch/prune current `origin/main`.
3. Read task authority from GitHub/`origin/main:TASKS.md`. Accept either standalone authority for `SB-CP00-008 / SB-CP00-008-C001`, or the explicit M11 master authority `.hiveai/prompts/M11_CP00_003_009_MASTER_IMPLEMENTATION_PROMPT.md` that lists this child in sequence.
4. Preserve legitimate owner-local dirty work. Do not reset, clean, auto-stash, rebase, force, overwrite, restore, or discard it.
5. In standalone mode, if the persistent checkout cannot be safely synchronized, use only an explicitly authorized temp worktree under `%TEMP%\ScrubBots-Level-Factory\SB-CP00-008-C001`, based on current `origin/main`.
6. In M11 master mode, reuse the single master execution worktree. Do not create another child worktree.
7. Do not create a Desktop sibling clone/worktree.
8. Stop only if repository identity, remote authority, or safe preservation is ambiguous.

## Goal

Implement:

`SB-CP00-008 - Provider abstraction.`

Turn the existing placeholder ProviderAdapter into a clear provider-neutral control-plane contract without shipping a real network/storage provider.

## Required abstraction

Define versioned provider-neutral contracts for at least:
- provider identity;
- capability declaration;
- environment support;
- read-only validation/inspection;
- future object write/delete/verify semantics as interfaces only;
- deterministic provider result/error categories.

Separate read/plan capability from future mutation capability so dry-run code cannot accidentally depend on a mutating concrete implementation.

Exact class names are implementation-defined.

## Capability model

Capabilities must be explicit and fail closed. Examples may include:
- object upload support;
- object integrity/hash verification;
- manifest/object atomicity capability;
- conditional write/version preconditions;
- delete/rollback support.

Do not pretend unsupported capabilities exist.

A provider missing a capability required by a plan must fail validation before mutation.

## Vendor neutrality

Core orchestration and dry-run planning must depend only on the provider abstraction.

Forbidden:
- boto3, cloud SDKs, HTTP clients, vendor credentials;
- provider-specific bucket/container semantics leaking into core state;
- hard-coded vendor names as required logic;
- live network calls.

Tests may use deterministic in-memory/fake adapters only.

## Error contract

Normalize provider-neutral errors/result states such as:
- unavailable;
- unsupported capability;
- conflict/stale precondition;
- integrity mismatch;
- unauthorized reference;
- transient failure.

Do not include secret values in errors.

## Architecture preservation

Preserve SB-CP00-001..007:
- declarative-only payload;
- environment separation;
- audit state;
- secret references;
- mandatory dry-run;
- zero live mutation.

## Tests

Required:
- provider protocol/interface surface only;
- capability negotiation fail-closed;
- core plan independent of vendor implementation;
- two fake providers with same capabilities yield equivalent provider-neutral planning result;
- unsupported capability blocks plan;
- secret-free errors;
- no network/vendor dependency/import;
- prior SB-CP00-001..007 regressions;
- governance, full pytest, compileall, diff check.

## Builder log

Create:
`.hiveai/codex-logs/SB-CP00-008-C001_PROVIDER_ABSTRACTION_CODEX_LOG.md`

Do not edit root `TASKS.md` or audits.

## Publication

After all gates pass:
- commit implementation;
- commit this child builder log separately;
- fetch/prune;
- normal non-force update to Level Factory `main`;
- verify execution HEAD == `origin/main` and divergence 0/0.

Standalone mode: stop for independent ChatGPT audit.

M11 master mode: do not edit root `TASKS.md`, do not write an audit, do not wait for human review, and continue directly to `SB-CP00-009-C001`.

## Final response

Standalone mode: return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-008-C001_PROVIDER_ABSTRACTION_CODEX_LOG.md

M11 master mode: no user handoff here. Return control to the master prompt.