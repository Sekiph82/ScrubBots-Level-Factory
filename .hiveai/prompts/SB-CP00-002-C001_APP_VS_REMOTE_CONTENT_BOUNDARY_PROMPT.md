# SB-CP00-002-C001 — App Code vs Remote Content Boundary

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Tracker:
root `TASKS.md`

Parent architecture:
`SB-CP00-001 = PASS / CLOSED`

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

Before implementation, tests, or builder-log work:

1. Verify the canonical persistent Level Factory path, repository identity, branch, origin, local HEAD, dirty state, stashes, and registered worktrees.
2. Fetch/prune current `origin/main`.
3. Read task authority from GitHub/`origin/main:TASKS.md`; require `SB-CP00-002 / SB-CP00-002-C001`.
4. Preserve legitimate owner-local dirty work. Do not reset, clean, stash, rebase, force, overwrite, restore, or discard it.
5. If the persistent checkout cannot be safely synchronized, use only an explicitly authorized temp worktree under `%TEMP%\ScrubBots-Level-Factory\SB-CP00-002-C001`, based on current `origin/main`.
6. Do not create a Desktop sibling clone/worktree.
7. Stop if incoming remote changes overlap implementation scope ambiguously.

## Goal

Define and mechanically enforce the M11 boundary:

`SB-CP00-002 — Define app code vs remote content boundary.`

This task defines what may be remotely delivered as declarative content and what must remain application/runtime code shipped with the app.

Do NOT implement remote download, provider storage, CDN, live publishing, or game runtime activation yet.

## Required canonical boundary contract

Under `content_pipeline/`, add a versioned declarative-content contract that explicitly separates:

### App-owned / non-remote code
At minimum classify as app-owned:
- GDScript / scripts;
- Python;
- native libraries/binaries;
- plugins/addons;
- scenes/resources whose behavior can execute code or instantiate arbitrary script references;
- shaders or executable/programmable payloads unless separately owner-approved later;
- project configuration that changes runtime/application behavior;
- any payload capable of introducing executable expressions, script paths, dynamic evaluation, reflection-driven code loading, or arbitrary filesystem/network actions.

### Remote-content-eligible declarative data
Define the initially allowed remote family narrowly around data-only content, such as:
- versioned level data;
- versioned supply-plan data;
- approved metadata;
- approved preview/art assets only where later pack/runtime contracts explicitly allow them;
- future manifest/pack metadata.

Remote eligibility must be **allow-list based**, not blacklist-only.

Anything unknown or unsupported must fail closed as app-owned/not-remotely-deliverable.

## Required implementation

Provide a versioned machine-readable schema/model for boundary classification.

Add a small pure/local classifier/validator API, for example:
- input: logical content descriptor/path/media type/schema identity;
- output: REMOTE_DECLARATIVE or APP_OWNED / REJECTED with deterministic reason codes.

Exact naming is implementation-defined, but semantics must be deterministic and versioned.

The implementation must:
- perform no network I/O;
- perform no remote mutation;
- execute no payload;
- import no game/runtime code;
- not inspect arbitrary code by executing/importing it;
- fail closed for unknown extension/type/schema;
- prevent path traversal and absolute-path escape from the logical content namespace.

## Executable-payload protection

Add explicit regression coverage that remote eligibility rejects at minimum:
- `.gd`;
- `.py`;
- executable/binary extensions;
- addon/plugin paths;
- script-bearing scene/resource payloads or descriptors;
- absolute paths;
- `..\` / `../` traversal;
- unknown schema/type;
- content descriptors that attempt executable expressions or script references.

Do not rely only on filename extension when a declarative descriptor/schema is available.

## Integration with SB-CP00-001

Preserve the control-plane skeleton.

The new boundary contract may be consumed by `validate_only()` only as a local validator if useful, but do not add publish/promote/rollback implementations.

Do not create a provider implementation.

Do not add a second tracker.

## Documentation

Extend Content Pipeline architecture docs with:
- app-owned vs remote-owned examples;
- allow-list/fail-closed rule;
- why executable payloads remain app-owned;
- boundary ownership;
- deferred future compatibility/runtime enforcement.

## Tests

Required focused tests:
- versioned classification contract;
- deterministic reason codes/results;
- valid declarative level/supply/metadata examples accepted;
- executable/script/plugin/binary examples rejected;
- path traversal and absolute path rejected;
- unknown schema/type rejected;
- no payload execution/import;
- no network/provider mutation;
- no runtime/game imports;
- no reverse dependency into Level Factory core;
- root `TASKS.md` remains sole tracker.

Run:
- focused SB-CP00-002 tests;
- prior SB-CP00-001 boundary tests;
- root governance/tracker tests;
- full pytest;
- compileall;
- git diff --check.

Full pytest must be green except truthful pre-capability skips.

## Builder log

Create before product edits:
`.hiveai/codex-logs/SB-CP00-002-C001_APP_VS_REMOTE_CONTENT_BOUNDARY_CODEX_LOG.md`

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.

## Publication

After all gates pass:
- commit implementation;
- commit builder log separately;
- fetch/prune;
- publish by normal non-force update to Level Factory `main`;
- verify local/remote 0/0;
- stop for independent ChatGPT audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-CP00-002-C001_APP_VS_REMOTE_CONTENT_BOUNDARY_CODEX_LOG.md
