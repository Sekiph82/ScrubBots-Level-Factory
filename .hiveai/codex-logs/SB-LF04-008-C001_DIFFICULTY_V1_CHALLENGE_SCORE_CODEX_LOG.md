# SB-LF04-008-C001 — Difficulty V1 Challenge Score

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-24 Europe/Istanbul.

Canonical root verification: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` maps to `Sekiph82/ScrubBots-Level-Factory` on `origin`.

Branch and starting HEAD: `main`, `8e14117252e44acc87216476d6bc053bd3417320`.

Origin and divergence: `HEAD` was equal to `origin/main` before edits.

Initial Git status: tracked files clean; pre-existing untracked nested worktree artifacts and Godot `.uid` files preserved and excluded.

Authorized scope read: root `TASKS.md`, governing instructions, M03 closure, LF04-001 through LF04-007 contracts/evidence, the M04 index/continuation prompt, LF04-008 prompt, and LF04-008 audit criteria.

Implementation decisions and rationale: added immutable versioned Challenge Score V1 results and component breakdowns. The calculation uses only move count, states visited, dead ends, branching, and forced moves with the exact fixed normalizers and coefficients. Optional diagnostics and descriptive metadata are excluded from the formula.

Commands and test evidence: focused LF04-008 plus LF04-007/006 tests passed 14 tests. `python -m compileall -q src tests`, Godot 4.7.2 headless editor boot, `git diff --check`, and `git diff --exit-code -- TASKS.md` passed. Full `python -m pytest -q -p no:cacheprovider` passed 908 tests with 1 pre-existing canonical-bridge capability skip in 330.58 seconds; no failures or xfails were introduced.

Files changed: `src/scrubbots_pixel_factory/difficulty_analysis.py`, package exports, this builder log, and `tests/unit/test_sb_lf04_008_challenge_score.py`.

Implementation commit: `32ef779d445950be75ab4728d9381c34b71defdc`, pushed successfully. Final tracked status was clean; pre-existing untracked nested worktree artifacts and Godot `.uid` files remained preserved and unstaged. `TASKS.md` had zero diff. Terminal log-only commit: pending.
