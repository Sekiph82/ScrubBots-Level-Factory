# MAINT-LOCAL-HYGIENE-C003 — Preserve/Merge/Delete Criteria

## PASS rule

PASS only if all three exact SB-LF04 target folders are absent at the end, and any legitimate unique work they contained has first been preserved in canonical GitHub `main`.

There is no keep/skip outcome.

## Required preservation checks

For each target:
- inspect Git/worktree identity;
- inspect commits, branches, stashes and uncommitted meaningful files;
- compare against current `origin/main`;
- classify unique state as redundant, superseded, generated, or legitimate.

Any legitimate unique work must be integrated into canonical main before deletion.

## Required integration behavior

If unique legitimate work exists:
- port/merge only meaningful changes;
- preserve current accepted contracts;
- run relevant focused regressions;
- publish with normal non-force update;
- verify preserved state is reachable from `origin/main`.

## Required deletion behavior

All three exact targets must be deleted after preservation:
- registered worktrees removed cleanly;
- no wildcard deletion;
- no sibling cleanup;
- no persistent-root deletion.

Final disposition per target:
- `PRESERVED_IF_NEEDED_AND_DELETED`
or
- `REDUNDANT_AND_DELETED`.

## Collateral safety

After deletion:
- canonical repo intact;
- no accidental changes outside the three targets;
- unrelated stashes/worktrees unchanged;
- any preserved unique work exists on GitHub main;
- all three target paths absent.

Codex must not edit `TASKS.md`.
