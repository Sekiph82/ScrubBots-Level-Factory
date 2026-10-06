# SB-CP03-005-C001 - Verify Remote Object Integrity

Document role: CODEX BUILDER LOG

## Start and inherited M14 synchronization

- Starting timestamp: `2026-10-06T19:27:53+03:00`.
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`, origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Reusing the authorized TEMP worktree `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\M14-CP03-001-012-CPX002-MASTER`.
- CP03-004 final published HEAD/origin/main: `189a7544305302fd7c35a1b56d9d744cdf134d62`; fetch verified 0/0 and clean before this child.
- Live tracker still authorizes ordered M14 master execution. The owner-priority roadmap remains after M14; no task switch was made.

## Child authority and contracts read

- `.hiveai/prompts/SB-CP03-005-C001_VERIFY_REMOTE_OBJECT_INTEGRITY_PROMPT.md` and `.hiveai/audit-criteria/SB-CP03-005-C001_VERIFY_REMOTE_OBJECT_INTEGRITY_AUDIT_CRITERIA.md` from current execution HEAD.
- Exact scope: extend provider-neutral read surface only for exact stored bytes; fetch every just-uploaded staging pack; compare byte length; recompute local SHA-256; compare exact candidate pack evidence; run M12 `inspect_scrubpack()`; reject truncation, mutation, swaps, wrong keys, stale/wrong digests; withhold manifest-write authority on every mismatch. Use deterministic stateful test provider, no vendor adapter, credentials, or network code.
- Implementation decisions, commands, failures/corrections, changed files, tests, commits, push and parity evidence will be appended chronologically.

## Implementation, test evidence and blocking tracker mismatch

- Extended the provider-neutral `ReadOnlyProvider` surface with `read_object_bytes` returning exact immutable bytes and an explicit result object key. `inspect_scrubpack()` now accepts exact bytes directly as well as its prior explicit path input. The staging upload gate re-reads each successful pack, verifies result identity/key/environment, requires exact length, recomputes SHA-256 locally, compares byte-for-byte to CP03-003/M12 evidence, and inspects those downloaded bytes with M12 before authorizing the next manifest step.
- Added stateful test-provider cases for exact valid bytes, reported SUCCESS with truncated/mutated/swapped/wrong-key reads, stale candidate digest, and missing capability/integrity. The provider stores bytes in memory only; no vendor/network/deletion/production path was added.
- One combined PowerShell inspection/test command initially failed to parse due unsupported brace expansion before tests started. Reissued file inspection and pytest separately; tests then ran normally.
- First cumulative regression reported two failures: the existing static boundary test correctly rejected writing a temporary file inside the Content Pipeline package, and governance reported live TASKS denominator `247` vs parsed rows `248`. Removed temporary-file writes by extending `inspect_scrubpack()` to accept bytes directly; did not weaken the static boundary test.
- Corrected focused provider/M12/CP03-003 tests: **35 passed in 0.89s**. Corrected cumulative regression: **1 failed, 1,396 passed, 4 skipped in 295.13s**. The sole failure is `tests/unit/test_sb_lf00_007_governance_authority.py::test_current_tasks_rows_are_parser_safe_and_declared_denominator_matches` at line 190: live root `TASKS.md` declares 247 while its parser counts 248 after owner commit `e33cfc4` added the SB-CPX-004 task row. No product/boundary failure remained.
- Corrected required unfiltered `python -m pytest -q`: **1 failed, 1,593 passed, 19 skipped in 964.08s**. The sole failure is the same live TASKS denominator mismatch (247 declared vs 248 parsed); all 19 skips are existing explicit missing canonical ScrubBots/Godot capability cases.
- `python -m compileall -q content_pipeline/src src tests` passed; all 16 Content Pipeline JSON files parsed; `git diff --check` exited 0 (only Windows LF-to-CRLF notices).
- Product implementation commit `88d2d09e28e73e4d4f8c5d555efab2e60a809704` was pushed normally; post-push fetch confirmed `HEAD == origin/main` at that SHA, 0/0. The child remains blocked despite safe publication of the verified byte-integrity code.
- This child cannot be marked green or advanced to CP03-006 until the tracker owner reconciles the live TASKS denominator or provides another authoritative resolution. This builder did not edit `TASKS.md` or the governance test, and did not alter `.hiveai/audits/**`. Separate evidence-log commit and parity will be appended after publication; CP03-005 remains blocked pending that authority fix.
