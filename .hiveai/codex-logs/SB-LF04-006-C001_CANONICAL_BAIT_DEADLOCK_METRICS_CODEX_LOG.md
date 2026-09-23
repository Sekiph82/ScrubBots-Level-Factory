# SB-LF04-006-C001 — Canonical Bait / Deadlock Metrics

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-23 Europe/Istanbul.

Canonical root verification: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` maps to `Sekiph82/ScrubBots-Level-Factory` on `origin`.

Branch and starting HEAD: `main`, `e08186eed3c67551abf737caf1ff1b6e27bb8c77`.

Origin and divergence: `HEAD` was equal to `origin/main` before edits.

Initial Git status: tracked files clean; pre-existing untracked Godot `.uid` files preserved and excluded.

Authorized scope read: root `TASKS.md`, governing instructions, M03 closure, LF04-001 through LF04-005 contracts/evidence, the M04 index/master prompt, LF04-006 prompt, and LF04-006 audit criteria.

Implementation decisions and rationale: added a versioned `BaitDeadlockResult` and counterfactual-child adapter. Only children classified `PROVEN_UNSOLVABLE` are counted; `INCONCLUSIVE`, unavailable, or error children cannot produce an exact ratio. Aggregate search dead ends are not reused.

Commands and test evidence: Initial focused run failed one test due to a fixture typo (`SolverOutcome.SOLVED`); corrected it and reran. Focused LF04-006 plus LF04-005/004 tests passed 18 tests. `python -m compileall -q src tests`, Godot 4.7.2 headless editor boot, `git diff --check`, and `git diff --exit-code -- TASKS.md` passed. Full `python -m pytest -q -p no:cacheprovider` passed 899 tests with 1 pre-existing canonical-bridge capability skip in 308.78 seconds; no failures or xfails were introduced.

Files changed: `src/scrubbots_pixel_factory/difficulty_analysis.py`, package exports, this builder log, and `tests/unit/test_sb_lf04_006_bait_deadlock.py`.

Final diff, status, commits, push, and `origin/main` equality: pending publication.
