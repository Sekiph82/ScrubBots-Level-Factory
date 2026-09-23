# SB-LF03-003-C001 — Canonical Legal-Move Provider Interface — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## 1. VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## 2. CONTRACT RECOVERY

Audited against the task-specific C001 prompt and strict audit criteria, the LF03 batch index, post-batch audit protocol, accepted SB-LF03-001/002 contracts, and canonical gameplay authority `Sekiph82/Scrubbots@1144704e6c3647ed1cf76c610be5bd675585734a`.

## 3. BRANCH / HEAD / DIFF SCOPE

- Level Factory implementation commit: `14de58bf55a412803dc03df994ce719370deb5b3`
- terminal builder-log commit: `0ce06958a77d3a7964868b8e7542349b512a3ee3`
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

## MAJOR-001 — Provider results are not intrinsically bound to the query/state they answer

`LegalMoveResult.from_query()` creates correct bindings, but the public `LegalMoveResult` constructor accepts arbitrary non-empty `query_digest` and `state_digest`. Its validation only binds authority/provider identity to `ProviderEvidence`; it does not prove those digests match the actual `LegalMoveQuery`.

Because the protocol allows any provider implementation, a buggy or hostile provider can return an AVAILABLE result carrying moves for a different query/state while still passing the result constructor.

This violates the explicit audit rule to fail closed on wrong state/digest binding.

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

Add one authoritative query/result validation path. An AVAILABLE/UNAVAILABLE/ERROR provider result must be validated against the exact `LegalMoveQuery` before consumption: query digest, state digest, authority, provider id/version, capability disposition/evidence and move column bounds/order. Direct construction must not permit an apparently valid unbound result to cross the provider boundary. Add negative tests with a syntactically valid result deliberately bound to another state/query.
