# MAINT-LOCAL-HYGIENE-C003 — SB-LF04 Orphan Project Folder Cleanup Criteria

## PASS rule

PASS only if each of the three exact owner-authorized folders is independently inspected and either safely deleted as redundant or retained with a concrete unique-state reason, with zero collateral changes outside those paths.

## Required checks per target

- exact path identity;
- reparse/symlink/junction check;
- parent tracking check;
- nested Git/worktree identity;
- HEAD/branch/origin;
- dirty/untracked state;
- stash state;
- unique commits/branches;
- meaningful-file comparison against canonical GitHub authority.

## Safe deletion

Deletion is allowed only with no unique meaningful state and no current worktree dependency.

No wildcard or sibling cleanup is authorized.

## Collateral safety

After maintenance:
- canonical persistent repository remains intact;
- status outside the three targets is unchanged from the pre-delete snapshot;
- unrelated worktrees/stashes are unchanged;
- no canonical product/config/source file is modified.

## Evidence

Builder log must give one disposition per target:
`DELETED_REDUNDANT`, `KEEP_REVIEW_REQUIRED`, or `NOT_FOUND`.

Codex must not edit `TASKS.md`.
