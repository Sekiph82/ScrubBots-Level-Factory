# SB-LF03-011-C001 — Deterministic Budgets / UNSOLVED vs INCONCLUSIVE — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## 1. VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 0
- MAJOR: 2
- MINOR: 0

## 2. CONTRACT RECOVERY

Audited against the task-specific C001 prompt and strict audit criteria, the LF03 batch index, post-batch audit protocol, accepted SB-LF03-001/002 contracts, and canonical gameplay authority `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`.

## 3. BRANCH / HEAD / DIFF SCOPE

- Level Factory implementation commit: `766eae9f85d5ac73d70634c7216316a4abf33699`
- terminal builder-log commit: `f157e33a11a2ffef0ddb3ca631980dde1038377a`
- post-batch repository HEAD inspected: `5d4522dcaa5160f7f2d0af895557029490b9d57e`
- canonical Scrubbots main independently rechecked and remains `1144704e6c3647ed1cf76c610be5bd675585734a`.

## 4. ACCEPTANCE CRITERIA MATRIX

- versioned/headless contract: reviewed
- gameplay authority separation: reviewed
- deterministic/fail-closed semantics: reviewed
- focused tests: reviewed
- retained/full regression evidence: reviewed
- TASKS builder no-diff: builder evidence confirmed by master log
- task-specific acceptance: **NOT FULLY SATISFIED**

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

The builder publication is internally consistent and the batch reports a final repository-wide `840 passed, 3 skipped, 1 warning`. Passing tests are treated as evidence only and do not override the direct contract finding below.

## 6. FILE / SYMBOL EVIDENCE

## MAJOR-001 — Baseline `max_visited_states` is not an execution budget

`EvidenceSearchEngine` runs `BaselineSearchEngine.search()` to completion using only a depth bound. Only after the search returns does `classify_search_result()` compare collected `visited_count` with `max_visited_states`.

So a configured state budget does not bound work at all. It is a post-hoc label and cannot protect a large search.

The canonical main-game solver stops when the visited-state bound is reached.

## MAJOR-002 — Operational timeout state is included in canonical outcome identity

`BudgetedSolverResult.canonical_dict()` includes `operational_timeout_exhausted` and `OPERATIONAL_TIMEOUT` exhaustion, and `SolverEvidenceReport.canonical_dict()` embeds the budget result. Thus a machine-dependent wall-clock timeout can alter canonical evidence bytes/digest.

The criteria require operational timeout to be separately recorded non-canonical telemetry and not become canonical replay identity.

## 7. FOCUSED TEST EVIDENCE

Committed focused tests were inspected. They do not cover the failing boundary described above, so the green focused result does not close the finding.

## 8. REGRESSION EVIDENCE

Final batch-wide builder evidence:
- retained LF03: `79 passed, 3 skipped, 1 warning`;
- full pytest: `840 passed, 3 skipped, 1 warning`;
- compileall PASS;
- Godot 4.7.2 headless editor boot PASS;
- diff-check PASS;
- TASKS builder diff zero.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

No runtime network dependency, provider-credit test consumption, secret persistence, WFC-as-gameplay-solver substitution or main-game source mutation was found in this task's implementation.

## 10. ARCHITECTURE CONSISTENCY

The Factory continues to avoid copying canonical ScrubBots gameplay mechanics into Python. The finding is a boundary/evidence correctness defect, not authorization to create a second gameplay engine.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Builder did not modify root TASKS and did not claim independent audit closure. Master batch log truthfully records unavailable canonical integration where applicable.

## 12. FINAL REPOSITORY STATE

Implementation is retained. Task remains open for bounded R01 remediation.

## 13. OPEN CROSS-MILESTONE FINDINGS

No M04/M05 work should use an affected LF03 claim as canonical production truth until remediation/re-audit closes this task.

## 14. DEFECTS BY SEVERITY

BLOCKER: 0
- MAJOR: 2
- MINOR: 0

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Keep generic algorithms separate from gameplay authority and prefer reusable boundary validators rather than duplicate ad-hoc checks across search/count/evidence layers.

## 16. UNVERIFIED ITEMS

Real cross-repository canonical execution remains unverified in the published C001 environment.

## 17. REGRESSION RISK

MEDIUM/HIGH if this boundary is promoted to production canonical truth without remediation.

## 18. AUDIT CONFIDENCE

HIGH. Repository source, tests, builder/master logs, task criteria and current main-game solver authority were inspected directly.

## 19. FINAL VERDICT

**CHANGES_REQUIRED**

## 20. REQUIRED REMEDIATION

Enforce max-visited directly during baseline traversal, with deterministic stop before expanding beyond policy and INCONCLUSIVE/MAX_VISITED_STATES on exhaustion. Separately move wall-clock timeout policy/exhaustion to an operational telemetry channel excluded from canonical solver/evidence digest and reproduction identity. Keep timeout mapping to INCONCLUSIVE. Add tests showing a wide/deep graph stops at the configured visit bound, plus identical canonical evidence with/without different operational timing metadata.
