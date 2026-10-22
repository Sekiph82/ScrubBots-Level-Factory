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

## Publication verification follow-up

- First post-push `git fetch --prune origin` showed `HEAD` and `origin/main` both at `a8cefc7f7df3536d18383cbc00c9fe692148f10e`; `git rev-list --left-right --count HEAD...origin/main` returned `0<TAB>0`.
- The initial PowerShell parity assertion failed because it compared that tab-delimited output to a literal backtick-t string. The displayed SHA/counts were already equal; the check was corrected to parse the two whitespace-separated integer fields. No repository or Git state was changed by the failed assertion.
- The builder log commit `a8cefc7f7df3536d18383cbc00c9fe692148f10e` was successfully pushed by normal fast-forward. A follow-up log commit records this verification correction; final post-push parity is checked again after publishing it.
- Follow-up correction: the first parsed pre-push count assertion expected `0 ahead / 1 behind`; this orientation was reversed. The actual safe state was `1 ahead / 0 behind` after creating the log commit. Re-ran `git fetch --prune origin`, confirmed `origin/main` is an ancestor, then normal push succeeded (`a8cefc7..dba4f0e`). Post-push fetch confirmed `HEAD == origin/main == dba4f0e484628237674837ed16d587be3f493a86`, 0 ahead / 0 behind, and no tracked changes. The 3003 untracked owner paths remain untouched.

## Autonomous factory hardening continuation — 2026-10-22

- Owner directive: resume autonomous coding without a dashboard. Scope remains the chat-driven repository factory; the R08 native Godot gate stays blocked and was not repeated or bypassed.
- Read `TASKS.md`, the active R08 prompt, `AGENTS.md`, `GOVERNANCE.md`, `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`, and the factory files. R08 explicitly forbids rerunning the one-shot process gate or advancing to R09 after its block.
- Implementation: `scripts/codex/scrubbots_task_queue.py` now rejects any root other than the canonical Desktop checkout and requires the exact authoritative prompt to be tracked by Git. `AGENTS.md` and the factory skill now describe continuing only across explicitly authorized task boundaries, re-reading live task authority at each boundary, and respecting blocked/one-shot gates.
- Tests: `python -B -m unittest discover -s tests/codex -v` — 6/6 passed, including exact tracked-prompt acceptance and untracked-prompt rejection. `git diff --check` passed.
- Expected refusal before commit: running the queue CLI while these tracked implementation files were modified returned `Tracked working-tree changes exist; refusing to start an automated task`. After implementation commit `d88a8f8`, `python -B scripts/codex/scrubbots_task_queue.py --json` succeeded and selected the explicit R08 prompt; no task was auto-claimed or started by the guard.
- Correction notes: first patch application used a test class name that did not match the file; inspected the test module and reapplied against the actual `ScrubBotsTaskQueueTests` class. No source changes were lost. No dependencies, workflows, TASKS, audit, Release, PNG, or owner data changed.
- Product commit: `d88a8f8` (`feat(codex): harden autonomous task checkout gate`). Publication of this continuation and final parity are recorded below after normal push.
- Publication result: product commit `d88a8f8` and builder-log commit `e0bee30` were pushed normally (`29e9a30..e0bee30`). A fresh `git fetch --prune origin` confirmed `HEAD == origin/main == e0bee301476877364f8bdcb680a95cf6e0fe8e39`, 0 ahead / 0 behind, and zero tracked working-tree changes. This final log note is published as a separate normal fast-forward commit; final parity is verified once more after that push.

## Autonomous factory authority pinning — continued coding

- Added `validate_file_matches_origin()` and invoke it for both `TASKS.md` and the selected authoritative prompt. The guard compares clean-filtered local Git object identity to each `origin/main` blob, so local commits cannot substitute edited tracker/prompt content for GitHub authority. The existing tracked-prompt and canonical-checkout guards remain active.
- Tests: `python -B -m unittest discover -s tests/codex -v` — 8/8 passed; `git diff --check` passed.
- Real checkout check after commit: `python -B scripts/codex/scrubbots_task_queue.py --json` succeeded against the canonical Desktop path and selected the R08 prompt; current `TASKS.md` and prompt blobs matched `origin/main`. This is a queue validation only, not a retry of R08 native preflight.
- Product commit: `0e0196f` (`feat(codex): pin task authority to origin main`). No TASKS, prompt, audit, workflow, owner data, Release or PNG file changed. No CI/Actions, native Godot, paid API, TEMP or worktree operation.
- Publication: product commit `0e0196f` and builder-log commit `e489a9c` were published by normal fast-forward (`ee13dff..e489a9c`). Fresh fetch confirmed `HEAD == origin/main == e489a9cc30befc496c095df6dedff3380f1a4698`, 0 ahead / 0 behind, and no tracked changes. This verification note is published in a final builder-log commit and parity is checked again after that push.

## Autonomous factory fresh-authority fetch — continued coding

- Factory startup now performs bounded `git fetch --prune origin` after verifying the canonical remote, before accepting `origin/main` ancestry or comparing tracker/prompt blobs. A fetch error fails closed with an explicit stale-authority message; no task is selected from a stale remote-tracking ref.
- Tests: `python -B -m unittest discover -s tests/codex -v` — 10/10 passed; `git diff --check` passed. Test coverage includes successful fetch argument and fetch/network failure refusal.
- One test assertion initially expected the `fetch` argument triplet as a nested item, while subprocess receives a flat argv. It failed; assertion corrected to verify the final three argv elements, then the full focused suite passed 10/10.
- Real checkout: after product commit `c2b51b5`, `python -B scripts/codex/scrubbots_task_queue.py --json` successfully fetched origin and validated the explicit R08 prompt plus tracker/prompt blob equality. Queue validation does not rerun R08's native gate.
- Product commit: `c2b51b5` (`feat(codex): refresh task authority before selection`). No workflow, TASKS, prompt, audit, Release, PNG, job, Pool, owner data or dependency was changed. No Actions, paid API, native Godot, TEMP or worktree use.

## Exact task prompt URL parsing — autonomous factory continuation

- Found and fixed a selector edge case: the prior URL regex matched only the valid prefix, so a `?query` or `#fragment` suffix could pass despite the exact-canonical-URL requirement. The parser now captures the full prompt token and requires an exact full match after removing only terminal prose punctuation.
- Focused verification: `python -B -m unittest discover -s tests/codex -v` — 11/11 passed, including query and fragment rejection; `git diff --check` passed.
- After product commit `d19eea0`, `python -B scripts/codex/scrubbots_task_queue.py --json` passed on the real Desktop checkout, performed safe origin fetch, checked canonical root/remote, and validated current TASKS/prompt blobs. No native R08 preflight was repeated.
- Product commit: `d19eea0` (`fix(codex): reject decorated task prompt URLs`). No tracker, prompt, audit, workflow, Release, PNG, job, Pool or owner data changed. No CI/Actions, paid service or TEMP/worktree used.
- Publication result for the exact-URL guard: product `d19eea0` and log `1e324c0` were pushed normally (`0057cee..1e324c0`); post-fetch `HEAD == origin/main == 1e324c01190cc9a92053ace38ef3e5251cbea148`, 0/0, tracked clean.

## Authorized task actor parsing — autonomous factory continuation

- Fixed actor validation so strings merely starting with `CODEX` (for example `CODEX - NOT AUTHORIZED`) cannot pass. The parser now accepts a unique actor chain beginning with `CODEX`, with only recognized subsequent `CHATGPT` or `OWNER` actors.
- Tests: `python -B -m unittest discover -s tests/codex -v` — 11/11 passed; `git diff --check` passed. After product commit `285d066`, the real queue guard completed fetch and returned actor `CODEX, THEN CHATGPT` with the explicit R08 prompt.
- Product commit: `285d066` (`fix(codex): require unambiguous authorized task actors`). R08's one-shot native process gate was not repeated. No TASKS/prompt/audit/workflow/owner data changed; no CI, paid service, TEMP/worktree, Release, PNG, or native Godot operation.

## Bounded authority refresh — autonomous factory continuation

- Bounded the queue's `git fetch --prune origin` call to 30 seconds. A timed-out fetch now fails closed with a clear stale-authority error, so an unattended/heartbeat run cannot wait indefinitely or proceed on cached refs.
- Tests: `python -B -m unittest discover -s tests/codex -v` — 12/12 passed, including timeout and network-error fail-closed cases; `git diff --check` passed.
- A first patch application had stale context for the test assertion and failed without modifying files; inspected the current test and reapplied. No test failures remained after the corrected patch.
- After implementation commit `a141719`, `python -B scripts/codex/scrubbots_task_queue.py --json` passed against the real canonical Desktop checkout and selected the R08 prompt. This did not re-run its native gate.
- Product commit: `a141719` (`fix(codex): bound authority refresh wait`). No TASKS/prompt/audit/workflow/Release/PNG/owner data changes; no CI, paid API, native Godot, TEMP or worktree operation.
