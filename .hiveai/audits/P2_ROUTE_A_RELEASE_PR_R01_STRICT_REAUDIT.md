# P2-ROUTE-A-C001-R01 — Final Publication Closure

Document role: CHATGPT INDEPENDENT STRICT RE-AUDIT

Date: 2026-10-03

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent audit:
`.hiveai/audits/P2_ROUTE_A_RELEASE_PR_STRICT_AUDIT.md`

R01 criteria:
`.hiveai/audit-criteria/P2_ROUTE_A_RELEASE_PR_R01_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md`

Implementation commit:
`c64345844f095159e619f51fe3ce6b8dc2cd3418`

Builder-log publication:
`f41a0234800eaa311bb91f636e47f9f6a55d4cf1`

Final receipt/log commit:
`8550f9b21c541363dff34a730930ba6170affc64`

## 1. VERDICT

**PASS / CLOSED**

All parent P2 findings F01..F03 are closed and the final publication gate is satisfied.

## 2. CONTRACT RECOVERY

P2 Route A must prepare a reviewable release branch + PR in `Sekiph82/Scrubbots` only after owner-approved CampaignBuilder authorization, while preserving:
- no push to game `main`;
- exact canonical remote identity;
- exact contiguous P1 publication orders;
- current-game verification;
- allow-listed diff only;
- one release commit;
- public-repo warning;
- release receipt;
- idempotent refusal;
- exact rollback on failure.

R01 specifically had to close:
- F01 exact checkout rollback;
- F02 caller-overridable remote identity;
- F03 authentic current-game verifier execution.

## 3. BRANCH / HEAD / DIFF SCOPE

Published R01 implementation commit:
`c64345844f095159e619f51fe3ce6b8dc2cd3418`

Compared to pre-finalization authority, published implementation changes are limited to:
- `level_factory/scripts/factory_core_gateway.gd`;
- `src/scrubbots_pixel_factory/supply_pipeline/release_route_a.py`;
- `tests/integration/test_p3_headless_pipeline_parity.py`;
- `tests/integration/test_release_route_a_authentic_verifier.py`;
- `tests/unit/test_release_route_a.py`;
- `tests/unit/test_sb_lf00_007_governance_authority.py`;
- `tests/unit/test_sb_lf03_009_canonical_bridge.py`;
- `tests/unit/test_sb_lf03_012_regression_fixtures.py`.

The two later commits are builder-log/evidence only.

No root `TASKS.md`, prompt, audit, dependency, or live game-repository file was changed by Codex.

## 4. ACCEPTANCE CRITERIA MATRIX

### A. Exact rollback — PASS

Production now snapshots:
- branch;
- HEAD;
- porcelain status;
- refs;
- staged index entries;
- tracked-file hashes;
- checkout inventory.

Rollback verification compares the restored checkout against that preflight snapshot.

Dedicated regressions exist for:
- verification failure;
- PR-create failure after push;
- allow-list violation with unexpected file/directory;
- post-PR label/edit failure;
- local commit failure before push;
- cleanup failure reporting.

Unexpected post-preflight residue is removed rather than preserved.

Rollback uncertainty raises `RouteARollbackError` and is recorded as `ROLLBACK_FAILED`, not falsely reported as restored.

### B. Canonical remote identity — PASS

The production Route A API no longer exposes `expected_remote` or equivalent caller authorization override.

Production preflight reads `origin` and requires normalized identity equal to the fixed module authority:
`https://github.com/Sekiph82/Scrubbots.git`.

The unit test `test_public_route_api_cannot_override_canonical_remote` covers the removed public bypass.

### C. Authentic current-game verifier — PASS

The authentic integration:
- resolves current public `Sekiph82/Scrubbots main`;
- clones current authority;
- archives the exact current commit;
- extracts a full isolated game project;
- selects a non-empty real production catalog row with real level/metadata/supply files;
- runs the production default `_verify_game`;
- requires `FACTORY_ROUTE_A_VERIFY_PASS`;
- verifies catalog and selected row files remain byte-identical;
- verifies fail-closed unknown identity;
- removes the temporary verifier runner.

The current default verifier executes:
- LevelCatalog load/validate;
- DifficultyV1CatalogCheck;
- LevelLoader;
- SupplyPlanLoader;
- ProofState;
- SolvabilitySolver solve/replay;
- LevelDifficultyAnalyzerV1 measurement/score;
- supported metadata parity.

This satisfies the corrected F03 boundary without conflating verifier integration with the separately observed Order-11 calibration/content-availability issue.

### D. Accepted P2 behavior preserved — PASS

Source inspection confirms retained:
- explicit Studio approval gate;
- stale plan/current-input revalidation;
- deterministic `levels/release-N-M` branch;
- exact contiguous approved orders;
- allow-list staging;
- one release commit with plan hash;
- branch-only push;
- PR create + `levels-release` label;
- public-repository warning;
- release receipt with plan hash, branch, game commit, PR URL, and file digests;
- idempotent branch/collision refusal.

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder claim: public remote override removed.
Result: **CONFIRMED** by production signature and fixed remote preflight.

Builder claim: exact rollback implemented.
Result: **CONFIRMED** by snapshot/verification code and dedicated failure regressions.

Builder claim: real verifier uses non-empty current production row.
Result: **CONFIRMED** by published authentic integration test.

Builder claim: previously excluded sibling-authority tests were executed safely.
Result: **SUPPORTED** by published harness changes honoring `SCRUBBOTS_PROJECT` and builder evidence.

Builder claim: full pytest passed without exclusions.
Result: **SUPPORTED BY BUILDER EVIDENCE**. This auditor cannot execute the Windows/Godot suite directly through the available GitHub connector, but no contradictory repository evidence was found.

## 6. FILE / SYMBOL EVIDENCE

Primary production symbol:
`release_approved_campaign(...)`

No caller-controlled remote override is present.

Primary preflight:
`_release_approved_campaign_impl(...)`

Primary rollback evidence:
`_snapshot_checkout(...)`
`_verify_checkout_snapshot(...)`

Primary game verifier:
`_verify_game(...)`

## 7. FOCUSED TEST EVIDENCE

Published builder evidence reports:
- exact three previously capability-sensitive nodes: all PASS;
- P2/Route A/P1/R02/governance focused command: **54 passed**;
- Factory Studio action/runtime set: **26 passed**;
- authentic verifier integration: PASS.

The three formerly excluded files were adjusted only to honor explicit `SCRUBBOTS_PROJECT` test authority rather than hard-binding to the sibling owner checkout.

## 8. REGRESSION EVIDENCE

Final unfiltered repository-wide pytest:
- **1172 collected**
- **1169 passed**
- **3 skipped**
- **0 failed**

Reported skips:
1. explicit slow 37x37/59x59 opt-in;
2. compact solver canonical-bridge capability not supplied;
3. LF04 regression canonical-bridge capability not supplied.

None of the previously excluded 18 nodes was skipped.

Also reported:
- compileall PASS;
- git diff --check PASS;
- Factory Studio committed runtime marker PASS.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

The final test harness used an isolated git-backed Scrubbots authority under the authorized temp workspace.

No live game working-tree bytes were required for test execution.

No real game release branch or PR was created by tests.

Production Route A remains the only path that may push/open a real game release branch/PR after explicit owner approval.

## 10. ARCHITECTURE CONSISTENCY

Route A continues to reuse accepted P1 CampaignBuilder/P1 publication authority rather than inventing a second ordering/publication system.

F03 verifier proof is correctly separated from the early-progression calibration issue.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

The builder log preserves failed/blocked intermediate runs rather than rewriting history.

The governance guard was narrowly updated to accept the tracker owner's valid single-token `*_AUTHORIZED` state form while retaining existing multi-part state checks.

Codex did not edit root `TASKS.md`.

## 12. FINAL REPOSITORY STATE

Level Factory final published builder head:
`8550f9b21c541363dff34a730930ba6170affc64`

Implementation:
`c64345844f095159e619f51fe3ce6b8dc2cd3418`

No extra Level Factory branch or PR was created.

## 13. OPEN CROSS-MILESTONE FINDINGS

The Order-11 search produced valid negative calibration evidence:
- eight targeted valid 20x20 candidates missed the live Order-11 window;
- best observed D1 remained above the hard limit;
- existing early production EASY levels are also materially above early progression targets.

This is not a P2 verifier defect and does not reopen P2.

It remains a separate future calibration/content-availability concern.

## 14. DEFECTS BY SEVERITY

No BLOCKER, MAJOR, or MINOR defect remains for P2-R01.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Future work may formalize isolated current-game authority setup as a shared test fixture/helper to avoid repeated per-test environment handling.

## 16. UNVERIFIED ITEMS

No required P2 criterion remains unverified at the repository-contract level.

The Windows/Godot full suite was not independently rerun by ChatGPT because the available audit tool is GitHub-only. Builder evidence is consistent with source/test truth and no contradiction was found.

## 17. REGRESSION RISK

Low to moderate.

Rollback code is safety-critical and filesystem-sensitive, but it now has explicit multi-stage failure tests and byte/state verification.

## 18. AUDIT CONFIDENCE

High.

## 19. FINAL VERDICT

**PASS / CLOSED**

## 20. REQUIRED REMEDIATION

None.

`P2 Route A / SB-CPX-003 = PASS / CLOSED`.
