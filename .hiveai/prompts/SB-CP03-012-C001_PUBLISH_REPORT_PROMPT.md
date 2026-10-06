# SB-CP03-012-C001 - Publish Report

## FIRST OPERATION - mandatory GitHub ↔ Desktop synchronization

1. Verify canonical persistent root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository identity, branch, origin, HEAD, dirty state, stashes and worktrees.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; accept standalone authority for `SB-CP03-012 / SB-CP03-012-C001` or M14 master authority `.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`.
4. Preserve owner-local work byte-for-byte. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard.
5. If persistent checkout cannot be safely synchronized, leave it untouched and use only the prompt-authorized TEMP worktree. M14 master mode reuses the single master worktree.
6. Never create a Desktop sibling clone/worktree.
7. Require clean 0/0 execution authority before edits.

## Goal

Produce a deterministic, secret-free, machine-readable and human-readable report for a validation/staging/production publish attempt.

The report must bind exact evidence, not merely prose.

Include at minimum:
- report schema/version and deterministic report digest;
- Level Factory commit SHA;
- candidate manifest SHA-256/content_version/minimum_game_version;
- pack IDs/versions/object keys/SHA-256/byte lengths/level membership;
- validation-only outcome;
- staging upload/integrity/manifest/download-verification outcomes;
- CPX-002 current Scrubbots main commit SHA and authority source hashes;
- per-level current-main replay/conservation results;
- owner-approval state without personal data;
- production promotion/manifest/CAS outcome;
- release-state event digests and resulting production identity;
- exact failure stage/reason code when unsuccessful;
- explicit `production_mutated` boolean.

Requirements:
- no credentials/tokens/local absolute owner paths/provider secret endpoints;
- fixed reason codes, bounded safe diagnostics;
- deterministic canonical serialization;
- report recomputation with identical evidence yields identical bytes/digest except for an explicitly supplied report timestamp if the schema includes one;
- if timestamp included, it must be explicit UTC input;
- human rendering is derived from the machine report and cannot change authority.

## Verification and publication

Run focused tests, prior M14 regressions, M13/M12/M11 regressions, governance/tracker tests, safe unfiltered full pytest, compileall, Content Pipeline JSON parse and diff checks.

Builder log:
`.hiveai/codex-logs/SB-CP03-012-C001_PUBLISH_REPORT_CODEX_LOG.md`

Do not edit root `TASKS.md` or `.hiveai/audits/**`. Separate implementation/log commits. Fetch/prune, normal non-force push, fetch again, require 0/0 clean parity.

Standalone mode stops for ChatGPT audit. M14 master mode continues immediately to `M14 FINAL MASTER VERIFICATION`.