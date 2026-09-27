# SB-LF09-002-C001-R01 — Fitness Result Integrity Remediation

Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

## Authorization

Remediate only the two findings from the independent
`SB-LF09-002-C001` strict audit. Preserve the closed LF09-002 metric catalog,
the PASS/CLOSED LF09-001 R02 selector, accepted M00-M08 evidence, the offline
boundary, and all existing product contracts. Do not begin SB-LF09-003 or any
other M09, Content Platform, main-game, provider, or production-publication
work.

## Findings to close

1. `FitnessEvaluation.for_candidate()` returns a caller-rehashed altered
   `CandidateFitness` when candidate ID, lineage, and policy digest match; it
   does not recompute the result from accepted artifact bytes.
2. `FitnessEvaluation.from_dict()` and `FitnessEvaluation.__post_init__()`
   accept duplicate candidate results, so the supposedly canonical evaluation
   is ambiguous.

## Required implementation

1. Make every public path that retrieves or accepts a fitness result fail
   closed unless the result is recomputed or equivalently verified against the
   exact accepted candidate artifact bytes, the exact candidate lineage, and
   the exact closed fitness policy. The fix must cover a result loaded from a
   caller-authored dictionary with a freshly recomputed self-digest.
2. Make `FitnessEvaluation` reject duplicate candidate IDs and duplicate
   lineage identities, and retain strict canonical candidate ordering during
   direct construction and `from_dict()` restoration.
3. Preserve deterministic canonical values/digests, integer finite scoring,
   policy binding, candidate-specific artifact identity checks, explicit
   experimental opt-in, source-art immutability, and no production promotion.
4. Add focused negative tests for:
   - a forged but rehashed result retrieved through the public evaluation path;
   - duplicate candidate IDs and duplicate lineage identities in restored
     evaluations;
   - cross-candidate lookup and stale artifact bytes;
   - the existing positive replay and exact validation path.

## Boundaries

- Create the matching CODEX builder log before implementation or tests. Its H1
  must exactly match this prompt title and it must immediately declare
  `Document role: CODEX BUILDER LOG`.
- Do not edit root `TASKS.md`, `.hiveai/audits/**`, this prompt, or its audit
  criteria.
- Keep implementation and log-publication commits separate.
- Do not weaken, skip, or xfail tests.
- Do not add network, provider, telemetry, API-key, runtime HTTP, cloud image
  generation, production-router, main-game, or publication integration.
- Run focused LF09-002 tests, retained LF09-001/M07/M08 regressions, full
  pytest, compileall, Godot headless boot, diff-check, and protected-file
  checks. Report unavailable canonical bridge capability truthfully.
- Stop after non-forceful publication with the exact final marker
  `AWAITING_CHATGPT_AUDIT`.

## Required handoff

Record the exact implementation and separate log-publication SHAs and full
GitHub URLs, every failed command and correction, changed files, focused and
regression results, offline/security review, final status, and final equality
or divergence with `origin/main`. Passing builder evidence is not acceptance.
