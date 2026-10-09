# SB-LFX-018-C001-R02-R05-B01-R03 — Disk Accounting Forensics and Safe Resume — Strict Audit Criteria

R03 is a continuation of R05 and B01-R02, not a relaxation of the owner's 4 GiB/test, 8 GiB total incremental test-generated storage budget. Original R05 and R02 acceptance tests remain binding.

## Safety and preservation

- Source worktree and existing uncommitted R05 implementation/log preserved byte-for-byte except authorized in-place edits; no clone/archive/full pytest before forensic preflight.
- Prior `pytest-2308` fixture paths were absent at 2026-10-09 stop; no unsupported claim of deleting them, no gate bypass, no unrelated data deletion.
- Git source authority verified, owner Desktop and durable Release untouched before all original R05 gates pass; Codex does not edit root `TASKS.md` or `.hiveai/audits/**`.
- No attempted 65 GB-class output; no >4 GiB predicted single case; no >8 GiB actual cumulative test-created growth; uncertain out-of-root growth fails closed.

## Forensic truth

- Report exactly: previous free-space delta = 22,604,811,520 bytes; measured basetemp = 1,484,869,840 bytes; unexplained by basetemp = 21,119,941,680 bytes; most recent free space observed = 191,108,395,008 bytes.
- Read-only, timestamped inventory identifies relevant directories and subprocess output roots; differentiates old files vs newly allocated bytes, apparent vs allocated size, outside-basetemp pytest/Godot/uv/Git writes, and plausible OS/other-process activity without claiming a cause without evidence.
- Historical unprovable cause remains `HISTORICAL_CAUSE_UNPROVEN` rather than assigned fictitiously. Baseline/end free-space subtraction alone is insufficient for pytest budget accounting.

## Prospective enforceability

- Test-run monitoring captures both relevant subprocess output roots and C: volume, includes peak not just final footprint, and flags material uncontrolled out-of-root growth.
- Hard fail-closed conditions for unknown growth, unsupported measurements, unexpected cache/write roots and exceeding B01-R02 limits.
- Static inspection addresses root causes of duplicate multi-GB archives/extractions and leak-prone pytest retention; correct original real current-game authority, non-mutating source and isolated writable runtime remain.
- Monitor evidence and estimated peak footprint established before **any** new real test. If impossible, deliver investigation log only, NO TEST/INSTALL/PUSH.

## Conditional test and product gates

- Only after justified disk-accounting PASS: focused real tests and one fully monitored, authority-enabled unfiltered pytest finish 0 fail/0 error; no fake solver, skip/xfail, or downgraded proof.
- Original genuine PNG identity A READY/B FAILED/C READY, immutable source/supply/replay/Difficulty binding and contiguous order, two genuine successive production releases N->N+1->N+2 via CP03-008/009, LF19/VOID ancestry, headless test timeout, native runtime, installer, screenshots/sha, secrets/compileall/diff remain required.
- Three-master maximize/resize behavior fills usable client area while retaining topology; 150-PNG LEVEL FACTORY selection is demonstrably accessible in real native UI, runs independent canonical per-PNG supply/solver stages, does not regenerate successes on resume, and auto-includes only READY into Release Pool. Product improvement is not accepted on static button text or mock execution.
- Installed Alpix external capability is represented honestly; never claim live smoke if absent.

## Audit outcome

- `FORENSICS PASS / R05_UNVERIFIED` if truthful forensic attribution and monitor preparation are done but not all original R05 gates.
- `R05_BLOCKED_DISK_ACCOUNTING` if relevant uncontrolled growth prevents defensible safe execution.
- `CHANGES_REQUIRED` for unsupported or incomplete test/product evidence.
- A full R05 PASS is available ONLY after all inherited technical gates and independent GPT strict audit; Codex cannot self-approve.
