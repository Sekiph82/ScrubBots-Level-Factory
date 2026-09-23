# SB-LF03-006-C001 — Solver Evidence and Search Metrics — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## 1. VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## 2. CONTRACT RECOVERY

Audited against the task-specific C001 prompt and strict audit criteria, the LF03 batch index, post-batch audit protocol, accepted SB-LF03-001/002 contracts, and canonical gameplay authority `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`.

## 3. BRANCH / HEAD / DIFF SCOPE

- Level Factory implementation commit: `ce932adf2c5b1a550bf2850ca286259377575c51`
- terminal builder-log commit: `8c55d6fb7928a73b7f8e45db5f29b6fd8229a117`
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

## MAJOR-001 — `frontier_peak` is mislabeled and not the observed DFS frontier peak

`_EvidenceCollector.on_node()` computes:

`frontier_peak = max(frontier_peak, depth + 1)`

That is maximum recursion/path depth, not the size of the pending DFS frontier. The canonical ScrubBots solver measures frontier peak from the actual search stack size.

On a shallow node with many pending siblings the current metric can report 2 while the real frontier contains many nodes. The task requires honest observed metrics; a mislabeled deterministic number is still fabricated evidence.

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
- MAJOR: 1
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

Either instrument the baseline search to expose actual pending-frontier size and record its true peak, or remove/rename this field so it cannot claim frontier size. Keep maximum depth as its existing independent metric. Add a wide shallow graph fixture proving frontier peak differs from depth and is recorded correctly.
