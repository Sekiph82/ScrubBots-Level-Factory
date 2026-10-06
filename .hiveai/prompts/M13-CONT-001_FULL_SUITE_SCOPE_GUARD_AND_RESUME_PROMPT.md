# M13-CONT-001 — Full-Suite Scope Guard + Resume M13

Document role: CODEX MASTER CONTINUATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent interim audit:
`.hiveai/audits/M13_CP02_001_012_MASTER_INTERIM_AUDIT.md`

Child 001 audit:
`.hiveai/audits/SB-CP02-001-C001_REMOTE_MANIFEST_V1_SCHEMA_STRICT_AUDIT.md`

Continuation criteria:
`.hiveai/audit-criteria/M13-CONT-001_FULL_SUITE_SCOPE_GUARD_AND_RESUME_AUDIT_CRITERIA.md`

Existing master prompt:
`.hiveai/prompts/M13_CP02_001_012_MASTER_IMPLEMENTATION_PROMPT.md`

## FIRST OPERATION — mandatory GitHub ↔ Desktop synchronization

Before any edit/test/log work:

1. Verify canonical persistent root:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify repository identity, branch, origin, HEAD, dirty tracked/untracked state, stashes and registered worktrees.
3. Run `git fetch --prune origin`.
4. Read `origin/main:TASKS.md`; require `M13-CONT-001` and this exact prompt.
5. Preserve every byte of legitimate owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard it.
6. If the persistent checkout is not safely fast-forwardable, leave it untouched and create/reuse only:
   `%TEMP%\ScrubBots-Level-Factory\M13-CONT-001`
   from exact latest `origin/main`.
7. Do not create a Desktop sibling clone/worktree.
8. Require execution worktree clean and 0/0 with `origin/main` before edits.
9. Stop if identity/preservation/remote overlap is ambiguous.

Create continuation log before edits:

`.hiveai/codex-logs/M13-CONT-001_FULL_SUITE_SCOPE_GUARD_AND_RESUME_CODEX_LOG.md`

Also append a new continuation section to:
`.hiveai/codex-logs/M13_CP02_001_012_MASTER_CODEX_LOG.md`

Do not rewrite or delete prior master-log text.

## Current accepted state

- SB-CP02-001 = PASS / CLOSED.
- SB-CP02-002..012 = NOT STARTED.
- Do not reimplement child 001.
- Its product contract is accepted.
- The blocker is historical test-harness scope, not manifest V1 semantics.

## CONT-001.1 — remove implicit Desktop game-checkout discovery

Fix:
`tests/integration/test_release_batch_level_catalog.py`

Current unsafe behavior:
- if `SCRUBBOTS_PROJECT` is absent, it probes `Path.home() / "Desktop" / "ScrubBots"`;
- on the owner's machine this silently consumes an unrelated checkout.

Required behavior:
- no Home/Desktop fallback at all;
- game authority capability exists only when `SCRUBBOTS_PROJECT` is explicitly non-empty;
- if absent, the integration skips before any git command or Godot launch involving a game checkout;
- if present, verify the directory exists and its origin resolves to `Sekiph82/Scrubbots`;
- treat that checkout read-only;
- continue to create an isolated archive/project under pytest TEMP for all mutation/Godot work.

Add a regression that proves an existing fake/home Desktop ScrubBots directory is ignored when the env capability is absent.

Repository-wide search for equivalent implicit Desktop Scrubbots/ScrubBots authority fallback in tests. Remove only equivalent test-harness auto-discovery patterns. Do not change product code merely to satisfy this search.

Do not weaken:
`tests/integration/test_release_route_a_authentic_verifier.py`
which owns its own isolated TEMP clone/archive semantics.

## CONT-001.2 — make CP010 source guard durable

Fix the historical guard in:
`tests/unit/test_sb_cp00_010_mobile_store_policy_boundary.py`

Current brittle behavior:
- exact changed/untracked source whitelist contains only `manifest_v1.py` and `__init__.py`;
- legitimate CP02-002..012 declarative modules would repeatedly fail this historical guard.

Preserve the security intent, but stop using a per-child exact source-file allowlist.

Require the guard to continue proving:
- root `TASKS.md` is the sole tracker;
- tracker has no Codex diff;
- Content Pipeline Python source contains no forbidden concrete network/runtime/provider-client imports;
- scan recursively across the package, not only a shallow one-file level if nested modules exist;
- no hidden HTTP/socket/provider SDK/subprocess runtime path is added by M13.

The guard should fail because of forbidden behavior/imports, not simply because a new declarative M13 module exists.

Add focused tests for this guard behavior if useful.

## CONT-001.3 — safe unfiltered full-suite gate

Before child 002 implementation:

1. Run focused tests for CONT-001 harness changes.
2. Explicitly ensure the full-suite process environment does NOT provide:
   - `SCRUBBOTS_PROJECT`
   - `SCRUBBOTS_CANONICAL_CHECKOUT`
   unless this prompt created an authorized TEMP capability for that exact run.
3. Run:
   `python -m pytest -q`
4. Let the suite complete.
5. Truthful pre-capability skips are acceptable.
6. If any test still attempts to use an owner Desktop game checkout implicitly, stop and record the exact test/path. Do not broaden task authority.

Also run compileall, schema parse and `git diff --check`.

Commit the harness remediation separately, then commit the continuation log update separately and publish by normal non-force push.

Fetch again and require 0/0 parity.

## CONT-001.4 — resume M13 from child 002

Only after CONT-001.1..3 are green, continue immediately through the existing M13 child prompts in this exact order:

1. `.hiveai/prompts/SB-CP02-002-C001_MONOTONIC_CONTENT_VERSION_PROMPT.md`
2. `.hiveai/prompts/SB-CP02-003-C001_MINIMUM_GAME_VERSION_COMPATIBILITY_PROMPT.md`
3. `.hiveai/prompts/SB-CP02-004-C001_PACK_IDS_LOCATIONS_HASHES_PROMPT.md`
4. `.hiveai/prompts/SB-CP02-005-C001_LEVEL_METADATA_NONCONTIGUOUS_IDS_PROMPT.md`
5. `.hiveai/prompts/SB-CP02-006-C001_DISABLED_LEVELS_PROMPT.md`
6. `.hiveai/prompts/SB-CP02-007-C001_SCHEDULED_ACTIVATION_WINDOWS_PROMPT.md`
7. `.hiveai/prompts/SB-CP02-008-C001_REJECT_DUPLICATE_PACK_LEVEL_OWNERSHIP_PROMPT.md`
8. `.hiveai/prompts/SB-CP02-009-C001_VALIDATE_REFERENCES_BEFORE_PUBLISH_PROMPT.md`
9. `.hiveai/prompts/SB-CP02-010-C001_MANIFEST_VERSION_HISTORY_PROMPT.md`
10. `.hiveai/prompts/SB-CP02-011-C001_APP_CONTENT_SCHEMA_COMPATIBILITY_PROMPT.md`
11. `.hiveai/prompts/SB-CP02-012-C001_MANIFEST_PARSER_SCHEMA_TESTS_PROMPT.md`

For every child:
- read its existing audit criteria from current HEAD;
- create/use only its already-defined distinct builder log;
- implement only that child scope;
- run focused + cumulative + full required verification;
- fix ordinary in-scope failures before continuing;
- commit implementation separately;
- commit child log separately;
- fetch/prune before push;
- normal non-force `HEAD:main`;
- fetch after push and require 0/0 parity;
- append exact evidence to the existing M13 master log;
- continue immediately to the next child without owner/ChatGPT handoff.

Do not mark child 001 as active again.

## Protected boundaries

Throughout continuation:
- do not edit root `TASKS.md`;
- do not edit `.hiveai/audits/**`;
- do not rewrite child 001 log;
- do not weaken M11/M12 security/integrity;
- no provider upload/download/CDN;
- no runtime/game implementation;
- no credentials;
- no hidden clock;
- no contiguous level-ID assumption;
- no remote mutation.

## Final verification

After child 012:
- verify all 12 child logs exist;
- final cumulative M11+M12+M13 suite PASS;
- full pytest PASS except truthful pre-capability skips;
- compileall PASS;
- all Content Pipeline schema/example JSON parse PASS;
- diff check PASS;
- protected paths unchanged;
- final main parity 0/0;
- execution worktree clean.

Append final results to the M13 master log and continuation log.

Stop for ChatGPT independent audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/M13_CP02_001_012_MASTER_CODEX_LOG.md
