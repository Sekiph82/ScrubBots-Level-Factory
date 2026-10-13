# SB-LFX-018-C001-R02-R05-R09-R02-R04 — Independent Strict Audit Criteria

Reviewer: ChatGPT (Codex is builder only). Source: owner 2026-10-13 installed screenshots + `.hiveai/audits/SB-LFX-018-C001-R02-R05-R09-R02-R04_OWNER_SCREENSHOT_AND_CODE_FAILURE_AUDIT_V01.md`. Every Codex `PASS` is a claim requiring independent code/schema/evidence verification.

## Mandatory gates

- **A. Safe preflight:** Git main/desktop sync, no destructive path operations, untracked preservation, original 002 and 003 immutable source PNG + source.json SHA unchanged, 232 pinned-game files/VOID ancestry preserved. No full game clone, no R2, no bulk nine solve, **zero Codex native solver/load-check invocations**.
- **B. 003 eligibility:** Prove why 002-only UI+backend restriction existed, implement source/game-rule attestation separation without weakening fixed 002 attestation and fail closed on forged SHA/source.json/alpha/VOID/unsupported input. 003 select does not auto-start solver; explicit Run for an eligible source builds source-exact bounded request. If trust gap remains, F01 = BLOCKED, no false 003 READY.
- **C. Real Release Pool:** Inspect a real durable existing 002 run; prove producer and consumer have the same canonical official `solver_metrics.official_difficulty_v1` data with actual 7 challengeVector axes, profile.dominant, challengeScore identical to primary difficulty score. Independent missing/malformed/error tests must fail closed. Valid new READY => auto included exactly once, Accept => same included state, Reject => excluded; no publication. If archived old 002 run cannot be fully verified, leave it explicitly NOT_ENTERED, no fabricated recovery.
- **D. Per-source persistence:** Verified 002 stored result returns on 002→003→002 and app restart, 003 stays its own unrun state; selecting during an in-flight 002 worker never misattributes activity, ready, Accept, pool entry, source/candidate/replay. Real immutable run file untouched.
- **E. Supply/Replay truth:** Supply Plan dialog shows actual nonempty selected columns and totals from canonical export with verified hash; Replay displays actual WIN and trace/evidence. Missing files show specific error and no fake proof; no `{}` success dialog.
- **F. UI exactness:** Existing three tabs/masters, gallery paging, selected previews, 3/4/5 columns, 25k visits / 90s native per-call budgets, no unrelated auto-launch, no intrusive overlay or second tracker.
- **G. Evidence/installer:** Only new affected focused Python+Godot tests; SHA/diff tests, original source hashes before/after, installed Release code and existing launcher proof, normal safe Git main FF. Honest known limitations. Real owner Windows screenshots remain an owner acceptance gate, never supplied by builder as substitute.

## Independent verdict policy

FAIL if one fake-ready or source-mismatch leak exists; FAIL if `Release Pool` requires fabricated official vector; FAIL if UI incorrectly reports user-reviewed status while actual pool entry is NOT_ENTERED; FAIL if originals are changed or native load test spent without owner permission. PARTIAL/BLOCKED is appropriate for safely gated 003 if attestation cannot be proven, but F02/F03/F04 must still be independently audited. Only close R04 after source-code+new tests+saved evidence+installed Windows owner proof meet all gates; leave parent R05, CPX-002 and R2 open.
