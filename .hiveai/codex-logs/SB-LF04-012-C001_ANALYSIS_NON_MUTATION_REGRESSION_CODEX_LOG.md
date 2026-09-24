# SB-LF04-012-C001 — Analysis Non-Mutation / M04 Regression Closure

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-24 Europe/Istanbul.

Canonical root verification: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` maps to `Sekiph82/ScrubBots-Level-Factory` on `origin`.

Branch and starting HEAD: `main`, `12503d752874a954e09210ab7fd87029630c76da`.

Origin and divergence: `HEAD` was equal to `origin/main` before edits.

Initial Git status: tracked files clean; pre-existing untracked nested worktree artifacts and Godot `.uid` files preserved and excluded.

Authorized scope read: root `TASKS.md`, governing instructions, M03 closure, LF04-001 through LF04-011 contracts/evidence, the M04 index/continuation prompt, LF04-012 prompt, and LF04-012 audit criteria.

Implementation decisions and rationale: added versioned checksummed corpus `sb_lf04_m04_regression_v1.json` covering LF04-001 through LF04-011, plus deterministic regression and exact pre/post source-byte checks. Representative analysis is read-only and performs no source/art mutation or network write.

Commands and test evidence: M04-wide focused regression passed 80 tests. `python -m compileall -q src tests`, Godot 4.7.2 headless editor boot, `git diff --check`, and `git diff --exit-code -- TASKS.md` passed. Final full `python -m pytest -q -p no:cacheprovider` passed 937 tests with 1 pre-existing canonical-bridge capability skip in 278.12 seconds; no failures or xfails were introduced.

Files changed: checksummed M04 regression fixture, `tests/unit/test_sb_lf04_012_regression.py`, and this builder log.

Final diff, status, commits, push, and `origin/main` equality: pending publication.
