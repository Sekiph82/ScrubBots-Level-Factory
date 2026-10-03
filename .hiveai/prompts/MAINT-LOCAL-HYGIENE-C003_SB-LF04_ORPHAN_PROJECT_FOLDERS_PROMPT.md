# MAINT-LOCAL-HYGIENE-C003 — Preserve, Merge and Remove SB-LF04 Orphan Project Folders

Document role: CODEX MAINTENANCE PROMPT

Repository authority:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Persistent local root:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## FIRST OPERATION — mandatory local ↔ GitHub synchronization preflight

Before inspecting, merging, or deleting anything:

1. Verify the persistent root is exactly the expected Level Factory repository.
2. Verify branch, origin, local HEAD, `origin/main`, ahead/behind, dirty tracked/untracked state, stashes, and registered worktrees.
3. Fetch/prune the canonical GitHub origin.
4. Read current task authority from fetched GitHub/`origin/main:TASKS.md`; require `MAINT-LOCAL-HYGIENE-C003`.
5. Preserve all legitimate owner work in the persistent checkout. Do not reset, clean, rebase, force-push, or discard owner state.
6. If a clean integration workspace is needed, use only one temp worktree under `%TEMP%\ScrubBots-Level-Factory\MAINT-LOCAL-HYGIENE-C003`.
7. Snapshot repository/worktree status before any merge or deletion.

Do not proceed if repository identity is ambiguous.

## Owner-authorized target paths

These THREE exact directories must be removed by the end of this task:

1. `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Scrubbots - Pixel Art Generator-SB-LF04-001`
2. `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Scrubbots - Pixel Art Generator-SB-LF04-001-R01`
3. `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Scrubbots - Pixel Art Generator-SB-LF04-001-R01-VERIFY`

There is NO `KEEP_REVIEW_REQUIRED` outcome.

If unique legitimate work exists, preserve and integrate it first. Then delete the folder.

No other path is authorized for deletion.

## Phase A — inspect and classify every target

For each target record:

- normal directory vs symlink/junction/reparse point;
- nested Git repo/worktree identity;
- origin, branch, HEAD;
- tracked/untracked changes;
- stashes;
- local branches;
- commits not reachable from canonical `origin/main`;
- meaningful source/config/docs/tests/data files;
- generated/cache/build/environment-only content.

Meaningful includes at least:
`.gd`, `.py`, `.json`, `.md`, `.tscn`, `.tres`, `.cfg`, `.ini`, `.toml`, `.yaml`, `.yml`, `project.godot`, scripts, tests, tools, docs, data and source assets.

## Phase B — preserve everything legitimate before deletion

For EACH target, compare unique state against current canonical `origin/main`.

### If no unique legitimate state exists
Mark it `REDUNDANT_READY_TO_DELETE`.

### If unique commits/branches exist
- identify the exact commits and changed paths;
- determine whether that work is already superseded by canonical main;
- if not superseded, integrate the legitimate changes into a clean temp integration worktree based on current `origin/main`;
- resolve conflicts against current canonical behavior, preserving newer accepted contracts;
- run relevant focused regressions;
- commit the preserved integration with clear provenance noting the source target folder.

### If unique uncommitted meaningful files exist
- diff them against canonical files;
- port only the legitimate product/source/config/test/doc changes into the clean temp integration worktree;
- do not copy generated caches/build artifacts/environments;
- preserve behavior, not stale folder structure;
- resolve conflicts in favor of current accepted authority unless the unique change is clearly newer and compatible;
- run relevant focused regressions;
- commit the preserved integration with provenance.

### If unique evidence/log files exist
- preserve only meaningful evidence not already present in GitHub;
- place it in the correct canonical evidence/log location when appropriate;
- do not revive obsolete tracker/control-plane files.

## Phase C — publish preserved work to canonical main

If any legitimate unique work was integrated:

1. Run focused tests for affected code.
2. Run governance/tracker tests.
3. Run compileall and `git diff --check`.
4. Run any relevant Godot/Factory Studio regression needed by the touched scope.
5. Fetch current `origin/main` again.
6. Integrate/publish with a normal non-force update to Level Factory `main`.
7. Fetch again and verify the preserved commits/files are reachable from `origin/main`.
8. Verify no legitimate unique file/commit remains only inside the three target folders.

Do not claim preservation until GitHub main contains it.

## Phase D — mandatory deletion of all three targets

After preservation verification, delete ALL THREE exact target directories.

Rules:
- if a target is a registered worktree, detach/remove it cleanly from Git worktree registration first, preserving any already-integrated commits;
- remove only the exact target path;
- no wildcard deletion;
- do not delete any canonical sibling directory;
- do not delete the persistent root.

After deletion verify:
- target 1 does not exist;
- target 2 does not exist;
- target 3 does not exist;
- no stale worktree registration points to any of them.

Final disposition for every target must be:
`PRESERVED_IF_NEEDED_AND_DELETED`
or
`REDUNDANT_AND_DELETED`.

No target may remain.

## Phase E — collateral verification

After deletion:

- persistent canonical root still exists and identifies as `Sekiph82/ScrubBots-Level-Factory`;
- GitHub `main` contains any legitimate preserved work;
- repository state outside the three targets has no accidental deletion;
- unrelated stashes/worktrees are unchanged;
- canonical project still opens/tests as required;
- the three target folders are absent.

## Builder log

Create/update:

`.hiveai/codex-logs/MAINT-LOCAL-HYGIENE-C003_SB-LF04_ORPHAN_PROJECT_FOLDERS_CODEX_LOG.md`

For each folder include:
- original repo/worktree/HEAD status;
- unique commits/files found;
- exact preservation mapping into canonical repo;
- integration commit SHA if any;
- GitHub verification;
- deletion mechanism;
- final absence proof.

Do not edit root `TASKS.md`.
Do not edit prior audits/prompts/logs.

This task is complete only when all three target folders are gone.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/MAINT-LOCAL-HYGIENE-C003_SB-LF04_ORPHAN_PROJECT_FOLDERS_CODEX_LOG.md
