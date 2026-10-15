# ART_FIRST WIN-P01 | Native NTFS symlink/reparse audit criteria V01

Owner lock: **no GitHub Actions/CI, no elevated privileges, no Developer Mode change, no owner-data writes, no additional TEMP/worktree/pytest scratch**. Existing 16 task scratch entries deletion denied: preserve. This is read-only verification first, not R05 release.

Criteria:
1. Source code comparison identifies actual path trust checks in ART_FIRST, Studio upload reader, output bundle verified-source gate and Release Pool.
2. No path traversal or reparse-point loophole is invented or ignored. Test expectations distinguish `Path.is_symlink` vs Windows junction/reparse cases and `resolve(strict=True)` canonical containment.
3. Genuine native Windows symlink **PASS** requires actual permitted NTFS symlink being presented to relevant guards and rejection observed, with exact commands/exit/status and no owner assets touched. A monkeypatch/test-double alone counts ONLY synthetic branch proof. If WinError 1314, cleanup denial or no safe fixture: native symlink remains **BLOCKED / NOT RUN**, no privileged workaround.
4. Only proven scoped bugs generate code changes; preserve canonical source PNG bytes/current ACCEPT and TEST origin classifications. Avoid new scratch, clones, workflow edits or CI.
5. Builder evidence reports exact local SHA, Windows/Python environment and read-only outcomes, not invented true owner identity or full native R05. No new untracked paths or deletion of the existing 3,220 under the owner protection policy.
6. Codex commits and normal-push only via canonical Desktop checkout with Git ancestry and manual-only workflow verification. GPT independently audits code/evidence and records gate PASS or BLOCKED; source-closed LF02-004 and LF02-008 stay closed absent a demonstrated regression.

External true AI-provider original creator identity, authentic owner approval and R05 game/production remain separate OPEN gates.
