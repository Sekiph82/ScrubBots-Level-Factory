# SB-CP00-004-C001 - Separate Staging and Production

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parents:
- `SB-CP00-001 = PASS / CLOSED`
- `SB-CP00-002 = PASS / CLOSED`
- `SB-CP00-003` must be implemented and green before this child begins in M11 master mode.

## FIRST OPERATION - mandatory local <-> GitHub synchronization

Before implementation, tests, or builder-log work:

1. Verify the canonical persistent Level Factory path, repository identity, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Fetch/prune current `origin/main`.
3. Read task authority from GitHub/`origin/main:TASKS.md`. Accept either standalone authority for `SB-CP00-004 / SB-CP00-004-C001`, or the explicit M11 master authority `.hiveai/prompts/M11_CP00_003_009_MASTER_IMPLEMENTATION_PROMPT.md` that lists this child in sequence.
4. Preserve legitimate owner-local dirty work. Do not reset, clean, auto-stash, rebase, force, overwrite, restore, or discard it.
5. In standalone mode, if the persistent checkout cannot be safely synchronized, use only an explicitly authorized temp worktree under `%TEMP%\ScrubBots-Level-Factory\SB-CP00-004-C001`, based on current `origin/main`.
6. In M11 master mode, reuse the single master execution worktree. Do not create another child worktree.
7. Do not create a Desktop sibling clone/worktree.
8. Stop only if repository identity, remote authority, or safe preservation is ambiguous.

## Goal

Implement:

`SB-CP00-004 - Separate staging/production.`

This is a local control-plane environment boundary. It must make it impossible for staging and production to collapse into the same logical target by accident.

Do not implement provider network calls, remote storage mutation, credentials, runtime downloads, or game activation.

## Required environment model

Extend the existing `Environment.STAGING / PRODUCTION` concept into a versioned target model that has explicit, deterministic identities for at least:
- environment;
- logical namespace/target ID;
- state namespace;
- content namespace;
- whether direct publication is permitted;
- whether promotion from staging is required.

Exact type names are implementation-defined.

Hard rules:
- staging and production identities must be distinct;
- production cannot reuse the staging state/content namespace;
- production is not a synonym/alias for staging;
- unknown environment values fail closed;
- production content must be represented as the result of an explicit future promotion path, not as an accidental staging write target;
- no endpoint URL, bucket credential, token, password, or provider-specific secret is required in this milestone.

## Cross-environment safety

Add pure/local checks that reject:
- identical staging and production namespace identities;
- production configuration using a staging-only target identity;
- environment mismatch between a plan/report and its target;
- attempts to treat a staging artifact/state record as production without an explicit promotion intent;
- ambiguous/unknown environment labels.

No remote mutation is permitted.

## Serialization and evidence

Environment configuration/state identity must serialize deterministically and be versioned.

Local dry-run/report evidence must always name the target environment explicitly. No report may omit environment or infer production silently.

## Architecture preservation

Preserve SB-CP00-001..003:
- declarative-only content;
- no executable payload;
- no provider implementation;
- no network mutation;
- no secrets;
- no game/runtime imports;
- no reverse dependency;
- root `TASKS.md` remains sole tracker.

## Tests

Required focused tests:
- staging and production target identities are distinct;
- same namespace/state target cannot serve both;
- unknown environment fails closed;
- environment mismatch fails closed;
- staging -> production requires explicit promotion intent;
- deterministic serialization;
- no endpoint/credential material required;
- no network/provider mutation;
- prior SB-CP00-001..003 tests remain green.

Run:
- focused SB-CP00-004 tests;
- SB-CP00-001..003 focused regressions;
- governance/tracker tests;
- full pytest;
- compileall;
- git diff --check.

## Builder log

Create before product edits:
`.hiveai/codex-logs/SB-CP00-004-C001_STAGING_PRODUCTION_SEPARATION_CODEX_LOG.md`

Log exact implementation commit, test counts, publication commit, and final origin/main parity.

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.

## Publication

After all gates pass:
- commit implementation;
- commit this child builder log separately;
- fetch/prune;
- normal non-force update to Level Factory `main`;
- verify execution HEAD == `origin/main` and divergence 0/0.

Standalone mode: stop for independent ChatGPT audit.

M11 master mode: do not edit root `TASKS.md`, do not write an audit, do not wait for human review, and continue directly to `SB-CP00-005-C001`.

## Final response

Standalone mode: return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-004-C001_STAGING_PRODUCTION_SEPARATION_CODEX_LOG.md

M11 master mode: no user handoff here. Return control to the master prompt.