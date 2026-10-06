# M14-CONT-002 — CP03-005 Reverify and Resume — Audit Criteria

## PASS rule

PASS only if the corrected authoritative tracker makes governance green, CP03-005's already-published byte-integrity implementation passes its focused/cumulative/full regressions unchanged, and the existing M14 master batch then resumes at CP03-006 without reopening CP03-001..004.

## A. Tracker authority

Require:
- current origin/main contains tracker correction commit `67807bd54d6a31d29ddc8f672ca3f23a7f754a6a`;
- unified denominator is 248;
- parser count equals declared denominator;
- SB-CPX-001..004 extension accounting is coherent;
- Codex does not edit TASKS.md or governance tests.

## B. CP03-005 reverify

Require unchanged implementation commit:
`88d2d09e28e73e4d4f8c5d555efab2e60a809704`

Rerun:
- exact governance authority tests;
- CP03-005 focused integrity tests;
- CP03-003/004 dependency regressions;
- cumulative M14/M13/M12/M11/governance suite;
- safe unfiltered full pytest;
- compileall;
- all Content Pipeline JSON parses;
- git diff --check.

No product-code edit is expected unless a new independent defect appears.

## C. Resume order

If CP03-005 is green, continue existing master order exactly:

1. SB-CP03-006-C001
2. SB-CP03-007-C001
3. SB-CPX-002-C001
4. SB-CP03-008-C001
5. SB-CP03-009-C001
6. SB-CP03-010-C001
7. SB-CP03-011-C001
8. SB-CP03-012-C001

Do not reopen CP03-001..004.

## D. Evidence/publication

Append continuation evidence to the existing M14 master log and CP03-005 child log without rewriting prior history.

Use separate implementation/log commits for future children exactly as the master requires.

Final parity must be clean 0/0 after each publication.

Codex must not edit root TASKS.md or .hiveai/audits/**.
