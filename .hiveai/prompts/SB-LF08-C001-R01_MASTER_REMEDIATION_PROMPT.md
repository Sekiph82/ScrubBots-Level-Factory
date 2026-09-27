# SB-LF08-C001-R01 — M08 Strict Remediation Batch

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

Authoritative index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF08-C001-R01_REMEDIATION_INDEX.md

## Authorization

Remediate only `SB-LF08-001 -> SB-LF08-006 -> SB-LF08-007 -> SB-LF08-008 -> SB-LF08-009` in that order. Do not start M09, edit root `TASKS.md` or `.hiveai/audits/**`, or alter accepted M08-002/003/004/005/010 or SB-LFX-013/014/015.

## Required closure

1. Enforce exact plan/history binding, contiguous deterministic prefixes, finite budgets, requested-count caps and recomputed canonical history digests on both run and restore paths. Reject any missing/wrong attempt plan digest.
2. Make every accepted batch artifact identity complete and lineage-bound, including separately verifiable generation request/result/metadata bytes and deterministic per-lane statistics.
3. Reuse the actual SB-LFX-006 owner-review record/chain validator. Missing schema fields, identity hash, artwork/grid mismatch, sequence/predecessor gaps, duplicate IDs and any corrupt evidence must fail closed.
4. Make handoff READY depend on the strict parsed batch result, canonical latest owner ACCEPT and all immutable artifact/generation bytes; preserve explicit non-ready dispositions and deterministic no-op reruns.
5. Add the complete offline high-rejection matrix, including corruption/tamper restore cases, without relaxing thresholds or adding network/provider behavior.

## Protocol

For each task, read its R01 prompt and criteria, create its dedicated builder log before product edits, add adversarial tests, run focused and retained regressions, then full pytest, compileall, Godot headless, diff and protected-file checks. Commit product changes separately from the terminal log, push non-forcefully, verify against live `origin/main`, and continue in order. Create the master log last.

Builder evidence must state failures and capability limits truthfully and must not declare PASS/CLOSED or edit tracker/audit state. Stop after the final master log with `AWAITING_CHATGPT_AUDIT`.
