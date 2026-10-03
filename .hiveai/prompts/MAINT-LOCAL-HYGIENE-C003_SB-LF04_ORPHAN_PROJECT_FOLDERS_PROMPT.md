# MAINT-LOCAL-HYGIENE-C003 — Inspect and Remove SB-LF04 Orphan Project Folders

Document role: CODEX MAINTENANCE PROMPT

Repository authority:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Persistent local root:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## FIRST OPERATION — mandatory local ↔ GitHub synchronization preflight

Before inspecting or deleting anything:

1. Verify the persistent root is exactly the expected Level Factory repository.
2. Verify branch, origin, local HEAD, `origin/main`, ahead/behind, dirty tracked/untracked state, stashes, and registered worktrees.
3. Run fetch/prune against the canonical GitHub origin.
4. Read current task authority from fetched GitHub/`origin/main:TASKS.md`; require `MAINT-LOCAL-HYGIENE-C003`.
5. The persistent checkout currently contains legitimate owner work. Do not reset, clean, stash, rebase, restore, switch, overwrite, or otherwise reconcile that work.
6. Use current `origin/main` as the comparison authority. If a clean execution/evidence workspace is needed, one temporary worktree under `%TEMP%\ScrubBots-Level-Factory\MAINT-LOCAL-HYGIENE-C003` is explicitly authorized. No Desktop sibling clone/worktree is allowed.
7. Snapshot the persistent root's git status outside the three target folders before any deletion so collateral changes can be detected afterward.

Do not proceed if repository identity or target paths are ambiguous.

## Owner-authorized target paths

Inspect ONLY these exact directories:

1. `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Scrubbots - Pixel Art Generator-SB-LF04-001`
2. `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Scrubbots - Pixel Art Generator-SB-LF04-001-R01`
3. `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Scrubbots - Pixel Art Generator-SB-LF04-001-R01-VERIFY`

The owner suspects these are obsolete SB-LF04 task copies because each contains its own `project.godot`.

No other path is authorized for deletion.

## Per-folder forensic inspection

For EACH target independently, record:

- exists / missing;
- normal directory vs symlink/junction/reparse point;
- whether the parent Level Factory repository tracks any path underneath it;
- whether it has its own `.git` directory/file;
- whether it is a registered Git worktree;
- repository identity and origin if it is Git-backed;
- branch and HEAD;
- working-tree status including untracked files;
- stashes;
- local commits not reachable from canonical Level Factory `origin/main`;
- local branches containing commits not preserved by canonical GitHub authority;
- whether any meaningful file exists only in this target or differs from the canonical project.

Meaningful files include at least:
- `project.godot`;
- `.gd`, `.py`, `.json`, `.md`, `.tscn`, `.tres`, `.cfg`, `.ini`, `.toml`, `.yaml`, `.yml`;
- scripts/tools/tests/source/data/docs;
- any other non-generated file.

Known generated/cache/environment folders may be classified separately, but never use that classification to ignore a potentially unique source/config file.

## DELETE-SAFE gate

A target may be deleted ONLY when ALL of the following are proven:

1. It is one of the three exact owner-authorized target paths.
2. It is not a symlink/junction/reparse-point surprise.
3. The parent repository does not track files beneath that target.
4. It contains no stash or uncommitted meaningful work that exists only there.
5. It contains no commit/branch state not already reachable/preserved by canonical GitHub authority.
6. Every meaningful file is either:
   - byte-equivalent to canonical repository content, or
   - obsolete/generated evidence with no unique product/source/config value.
7. It is not required by any current registered worktree.
8. Deleting it will not alter files outside that exact target.

If ANY condition is uncertain or false, DO NOT DELETE that target. Mark it `KEEP_REVIEW_REQUIRED` and explain exactly why.

## Deletion procedure

For a target that passes the DELETE-SAFE gate:

- if it is a registered worktree, remove it using the repository's normal Git worktree mechanism only after proving it has no unique state;
- otherwise remove only that exact directory;
- never use a broad wildcard;
- never delete the persistent root;
- never delete `.hiveai`, `src`, `tests`, `tools`, `level_factory`, `data`, `docs`, or any other sibling directory.

After each deletion verify the exact target no longer exists.

## Collateral-damage verification

After all three decisions:

- verify the persistent canonical root still exists and remains the same repository;
- compare git status outside the three targets against the pre-delete snapshot;
- require zero new tracked/untracked changes outside those targets caused by this maintenance;
- verify all non-target registered worktrees/stashes are unchanged;
- verify canonical files were not modified.

If collateral state changed, stop and report it immediately.

## Evidence / result

Create a builder log:

`.hiveai/codex-logs/MAINT-LOCAL-HYGIENE-C003_SB-LF04_ORPHAN_PROJECT_FOLDERS_CODEX_LOG.md`

For each target record exactly one disposition:
- `DELETED_REDUNDANT`
- `KEEP_REVIEW_REQUIRED`
- `NOT_FOUND`

Include:
- Git/worktree findings;
- unique-state checks;
- file comparison summary;
- deletion command/mechanism if deleted;
- post-delete verification;
- final persistent-root status comparison.

Do not modify root `TASKS.md`.
Do not modify prior prompts/audits/logs.

This is local hygiene only. Do not make product-code changes.

## Publication of evidence

If a clean temporary Level Factory worktree was needed for the log, publish only the builder log to Level Factory `main` with a normal non-force update after fetching current authority again. Do not use the dirty persistent checkout to make a repository commit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/MAINT-LOCAL-HYGIENE-C003_SB-LF04_ORPHAN_PROJECT_FOLDERS_CODEX_LOG.md
