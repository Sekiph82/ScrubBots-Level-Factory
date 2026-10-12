# SB-LFX-018-C001-R02-R05-R07 — Independent Strict Audit V01

**Date:** 2026-10-12
**Repository:** `Sekiph82/ScrubBots-Level-Factory`, `main`.
**Verdict: R07 SAFE STOP ACCEPTED; GIT-OBJECT-ONLY ASSUMPTION PROVED TOO RESTRICTIVE; ONE REAL LEVEL NOT READY. Parent R05 OPEN.**

## Actual audited publication and evidence

Read the actual current R05 builder log, verified R07 GitHub log-only final publication `9e67118da01105be4864ab6d0e605de22b4024fe` (preceded by log commit `87e82636eb98748530d755949871ee2429b8f561`). This record contains no LF product-code/test change and no game-repository commit. The builder reports successful LF main fast-forward, 0/0 parity and unchanged 57 owner-local untracked roots; local claims are not independently observable from GitHub.

Codex read-only observation: game remote `main` was `963797820e3fd8b2755b131928356137ee2fe7f6`; that commit was **absent from the existing dirty game repository's local Git object store**. The historical VOID ancestor object exists locally but cannot be proved ancestor of an object absent from local storage. Consequently stopped: **0 solver calls, 0 new LF runtime, 0 derivative, 0 actual candidate, 0 READY, 0 Release Pool, 0 R2 activity**. R06 owner-source SHA, 32×32, seven legitimate palette colors, 288 VOID, and unchanged owner original are older accepted records, not freshly repeated R07 tests. No product changes imply no new tests was correct.

One scoped instruction deviation was disclosed: an inventory redirection **may have created an empty file** at `%LOCALAPPDATA%\Temp\R07_TREE_LIST_READONLY.txt`. It was not inspected or deleted. This is a non-compliant possible side-effect under no-TEMP policy. Treat this as a procedural warning, not as a green clean-disk claim. Explicitly prohibit all redirects to TEMP in the next task; do not instruct Codex to bypass deletion protections or perform cleanup without owner approval.

## Independently verified alternative to avoid another circular blocker

**GitHub public read access to EXACT committed sources actually works, without any local game Git objects**:
- `GET https://api.github.com/repos/Sekiph82/Scrubbots/commits/963797820e3fd8b2755b131928356137ee2fe7f6` returned the immutable game commit metadata.
- `GET https://api.github.com/repos/Sekiph82/Scrubbots/git/trees/963797820e3fd8b2755b131928356137ee2fe7f6?recursive=1` returned a full **non-truncated** tree of 5,645 entries, including **234 source/config/palette candidate files** totaling **1,977,597 bytes** (`209` `.gd` scripts and `25` small data/config + data/palette entries including `.gitkeep`).
- `GET https://raw.githubusercontent.com/Sekiph82/Scrubbots/963797820e3fd8b2755b131928356137ee2fe7f6/scripts/gameplay/solver/solvability_solver.gd` and matching GitHub pinned-commit file read succeeded. Its returned Git blob SHA `0b5fb14a9e597fc50b7c4d79d5ad6b01fabb1545` is available as a concrete exact SHA integrity target.

This means the **old prerequisite 'new main commit must already be present locally' is avoidable**. The preferred R08 should pull only exact small files directly from the read-only GitHub HTTPS endpoints, verifying their Git blob SHA-1 from `b"blob " + byte-length + b"\\0" + bytes`, matching the commit tree's file path→mode→blob SHA entry before any game-runtime use. **NO clone, fetch into game, local game's `.git` changes, or whole 2.58 GB repo download.** The user has repeatedly demanded this LF-only approach.

**Evidence limitation:** This independent API check proves remote source accessibility *through the connected GitHub read interface here*, not that Codex's local Windows HTTP client can access all 234 files reliably or that a headless mini Godot project has complete game-solver runtime semantics. It also does NOT prove historic audited VOID ancestry to latest game main; R08 must check remote compare ancestry separately and fail closed if unverifiable. A source-only mini runtime cannot satisfy separate CPX-002 current full game publication replay without future specific authorization; do not weaken that gate.

## Next audited disposition

Close **R07 as a truthful no-solve safety stop**, superseding its local-objects-only architecture prerequisite, not marking it successful gameplay. Open **R08 as a single targeted execution cycle using commit-pinned GitHub REST tree + raw source HTTPS**, with strict 8-MiB/260-file LF-owned materialization, immutable source validation, genuine Godot canary/at most one single source end-to-end solver operation, and honest output. Prohibit repeating the same local game status/object checks or R07 tests. No game repo writes, TEMP command redirects, Cloudflare writes, broad LF regression or unapproved release actions. Parent R05 remains OPEN.
