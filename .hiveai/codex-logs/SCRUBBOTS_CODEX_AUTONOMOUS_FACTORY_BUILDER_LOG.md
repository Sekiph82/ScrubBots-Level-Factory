# ScrubBots Codex Autonomous Factory Bootstrap
Document role: CODEX BUILDER LOG

## Start

- Started: 2026-10-22 21:31 Europe/Istanbul.
- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Canonical origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Starting branch/HEAD: `codex/sb-lfx-018-r05-v13-cd-recovery-20261021` / `504f4401a66ba5227ff78fb223ab56eb68459785`.
- Initial remote state: `origin/main` advanced to `e9e4971395f8a0a09a8f9894555d6c5e31dddabb`, three commits ahead; tracked tree clean; 89 untracked owner paths preserved.
- Safe sync: `git merge --ff-only origin/main`; completed. No untracked path overlapped the three incoming paths. Current branch now equals `origin/main` at setup start.
- User explicitly authorized repository-internal factory work before returning to R08, no dashboard, and edits to `TASKS.md` and `AGENTS.md`.

## Research and decisions

- Read the PackLab and FormuLab root agent rules, task state, relevant queue code, and the FormuLab MIT license. Their working trees contain owner changes; no source was copied and neither repository was modified.
- PackLab's queue has useful explicit-current-task validation but also edits/publishes its own `TASKS.md`; FormuLab's queue includes claiming and dashboard-answer handling. These mutation/dashboard paths are not suitable here.
- Implement a small read-only adapter for ScrubBots' explicit Project Status fields and a Codex skill that asks questions in this chat. It must not inspect dashboard state or infer a task from checkbox order.
- No runtime dependencies, API calls, CI/Actions, TEMP, worktree, clone, Release, PNG, job, or Pool operations are part of the factory bootstrap.

## Changes and verification

- Added `scripts/codex/scrubbots_task_queue.py`: validates the exact explicit Project Status fields, pinned repository/branch and same prompt URL; reads only; writes no tracker state.
- Added `tests/codex/test_scrubbots_task_queue.py`: 4 stdlib tests cover exact prompt selection, wrong repo/branch, ambiguous/mismatched prompt, duplicate status section and wrong actor.
- Added `.codex/skills/scrubbots-factory/SKILL.md`: directs Codex to the read-only guard, current chat for owner Q/A, one explicit prompt at a time, and no dashboard/second ledger.
- Updated `AGENTS.md` with bounded owner chat authorization and the dashboard-free factory entry point.
- Updated `TASKS.md` Project Status with the owner's requested sequence: bootstrap first, then continue R08; no checkbox or acceptance state was changed.
- Local checks: `python -B -m unittest discover -s tests/codex -v` — 4/4 passed in memory; `python -B scripts/codex/scrubbots_task_queue.py --json` — validated current R08 prompt; `git diff --check` — passed. No pytest, bytecode, dashboard, API, CI, Actions, or native/Release operation used for factory tests.
- R08 follow-on: one fresh CIM inventory at `2026-10-22T18:33:22.0689421Z`; 948 visible processes, 22 candidates named `godot-ai.exe`. PID groups: `33168,22312` at `...\uv\cache\archive-v0\UOx1IqKpEMBu7Z2L\Scripts\godot-ai.exe`; `22624` at `...\uv\cache\archive-v0\uSLijXdw6fkMLznE\Scripts\godot-ai.exe`; `15788,13460,33764,6192,2124,36152,12072,8948,6548,11988,34200,20524,18476,28664,30316,4624,40772,41760,40536` at `...\uv\cache\archive-v0\8-tKefbYMY-voaXc\Scripts\godot-ai.exe`. Start time and Godot project root were unavailable for every candidate. No native executable was identified/launched; returned exact R08 blocker `R08_NATIVE_BLOCKED_SHARED_GODOT_PROCESS` under the prompt's incomplete-attribution fail-closed condition. No process was stopped.
- R08 native parser: NOT RUN. No Godot 4.7.2 path/script/cache preflight was attempted after the process inventory gate failed. No R08-only report/log was created.
- Final diff and publication: pending.
- Pending: final diff, commit/push result, and final `HEAD`/`origin/main` equality.

## Final diff, commits, and publication

- Committed implementation diff: 5 files, 255 insertions, 1 deletion; `git diff --check origin/main...HEAD` passed.
- Implementation commit: `b04ced9` (`feat(codex): add chat-driven ScrubBots task factory`).
- Post-commit queue guard: `python -B scripts/codex/scrubbots_task_queue.py --json` returned repository `Sekiph82/ScrubBots-Level-Factory`, tracker branch `main`, and the explicit R08 prompt; tracked working tree was clean before this log update.
- Workflow recheck: `.github/workflows/c001-r09-safe-regression.yml` has only `workflow_dispatch`; normal push does not trigger Actions. No workflow file changed.
- Builder log is committed separately. Publication uses normal fast-forward `git push origin HEAD:main`; no force or rewrite.
