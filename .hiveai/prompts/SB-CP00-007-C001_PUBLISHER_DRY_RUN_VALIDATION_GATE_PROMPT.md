# SB-CP00-007-C001 - Publisher Dry-Run / Validation Gate

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent sequence:
`SB-CP00-001..006` must be implemented and green before this child begins in M11 master mode.

## FIRST OPERATION - mandatory local <-> GitHub synchronization

Before implementation, tests, or builder-log work:

1. Verify the canonical persistent Level Factory path, repository identity, branch, origin, HEAD, dirty state, stashes, and registered worktrees.
2. Fetch/prune current `origin/main`.
3. Read task authority from GitHub/`origin/main:TASKS.md`. Accept either standalone authority for `SB-CP00-007 / SB-CP00-007-C001`, or the explicit M11 master authority `.hiveai/prompts/M11_CP00_003_009_MASTER_IMPLEMENTATION_PROMPT.md` that lists this child in sequence.
4. Preserve legitimate owner-local dirty work. Do not reset, clean, auto-stash, rebase, force, overwrite, restore, or discard it.
5. In standalone mode, if the persistent checkout cannot be safely synchronized, use only an explicitly authorized temp worktree under `%TEMP%\ScrubBots-Level-Factory\SB-CP00-007-C001`, based on current `origin/main`.
6. In M11 master mode, reuse the single master execution worktree. Do not create another child worktree.
7. Do not create a Desktop sibling clone/worktree.
8. Stop only if repository identity, remote authority, or safe preservation is ambiguous.

## Goal

Implement:

`SB-CP00-007 - Publisher dry-run/validation-only before remote mutation.`

This task creates the mandatory pre-mutation planning/validation gate. It does NOT authorize any live remote write.

## Required dry-run plan

Add a deterministic local publication-plan model built only from:
- accepted declarative descriptors/payload validation results;
- explicit environment target;
- current auditable release state;
- non-secret provider capability description;
- explicit owner-approval intent where required.

A plan must contain enough immutable evidence to show what a future publisher would try to do, including:
- plan/schema version;
- target environment;
- exact content identities and SHA-256 values;
- proposed logical operations in deterministic order;
- validation checks and their results;
- current expected state/version;
- whether the plan is mutation-eligible in principle.

Do not include secret values.

## Mandatory validation gate

A future mutating path must be representable only from a dry-run result that is:
- accepted;
- complete;
- current for the exact content digests/environment/state;
- explicitly owner-approved where the existing contract requires it.

In this milestone there is no live mutator. Model the gate/precondition only.

Reject:
- planning from unvalidated payloads;
- stale state/version;
- hash/content mismatch;
- environment mismatch;
- production direct-publish bypass where promotion is required;
- missing owner approval;
- secret-bearing plan input;
- nondeterministic operation ordering.

## CLI / local UX

Extend the Content Pipeline CLI or validation API with a true local dry-run mode if appropriate.

The command must:
- perform zero remote mutation;
- print/write deterministic report data;
- make it unambiguous that no remote write occurred;
- return nonzero/fail closed when validation gates fail.

Do not expose a live publish flag in this task.

## Mutation canary

Tests must use a fake/canary provider or mutator that raises immediately if any mutation method is called. Dry-run tests must prove zero mutation calls.

Do not require network access.

## Architecture preservation

Preserve SB-CP00-001..006, especially staging/production separation, append-only release state, and secret references.

No provider implementation, credentials, runtime integration, pack/manifest upload, or remote storage operation.

## Tests

Required:
- deterministic plan bytes/order;
- validated payload prerequisite;
- environment/state/hash binding;
- explicit production promotion rule;
- owner approval gate;
- stale plan rejection;
- secret value exclusion;
- mutation canary remains untouched;
- CLI dry-run no-mutation behavior;
- prior SB-CP00-001..006 regressions green;
- governance, full pytest, compileall, diff check.

## Builder log

Create:
`.hiveai/codex-logs/SB-CP00-007-C001_PUBLISHER_DRY_RUN_VALIDATION_GATE_CODEX_LOG.md`

Do not edit root `TASKS.md` or audits.

## Publication

After all gates pass:
- commit implementation;
- commit this child builder log separately;
- fetch/prune;
- normal non-force update to Level Factory `main`;
- verify execution HEAD == `origin/main` and divergence 0/0.

Standalone mode: stop for independent ChatGPT audit.

M11 master mode: do not edit root `TASKS.md`, do not write an audit, do not wait for human review, and continue directly to `SB-CP00-008-C001`.

## Final response

Standalone mode: return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-007-C001_PUBLISHER_DRY_RUN_VALIDATION_GATE_CODEX_LOG.md

M11 master mode: no user handoff here. Return control to the master prompt.