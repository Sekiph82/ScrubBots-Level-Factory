# P2 — Route A Release PR — Independent Strict Audit

Date: 2026-10-02
Auditor: ChatGPT
Verdict: **CHANGES_REQUIRED**

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Builder log:
`.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_CODEX_LOG.md`

Implementation commit:
`0ac1bc70606bf2b74c87147d18c254a52f3dfc10`

Owner prompt:
`.hiveai/prompts/P2_ROUTE_A_RELEASE_PR.md`

Audit criteria:
`.hiveai/audit-criteria/P2_ROUTE_A_RELEASE_PR_AUDIT_CRITERIA.md`

## Executive result

The Route A architecture is substantially correct and is retained:
- explicit CampaignBuilder APPROVE gate;
- stale-plan revalidation before branch creation;
- deterministic `levels/release-N-M` branch;
- no direct game-main push;
- exact P1 contiguous publication reuse;
- strict release-path allow-list;
- real game verifier implementation;
- one provenance-rich release commit;
- branch push + PR + `levels-release` label;
- public-repository warning;
- hash-bound release receipt;
- temporary local bare remotes in tests;
- no real Scrubbots release was attempted without an owner-approved live plan.

However, three P2 strict-closure findings remain.

## F01 — Allow-list failure does not restore the checkout byte-for-byte — BLOCKER

Owner P2 requires:
- failure at any step restores the checkout to the preflight state;
- exact rollback is a required test contract.

Current rollback intentionally preserves an unexpected path:
`unexpected-owner.txt`.

The focused test explicitly asserts that this post-preflight file remains after Route A fails.

That contradicts byte-for-byte preflight restoration. Preflight requires a clean worktree, so a new post-preflight path cannot be part of the recorded preflight state.

Required closure:
- snapshot/record the clean preflight state;
- after every failed Route A attempt restore tracked bytes/index/branch/HEAD to that state;
- remove every operation-created untracked path, including allow-list violations;
- keep failure evidence in the Level Factory evidence area, not as residue in the game checkout;
- verify final game checkout branch, HEAD, index, tracked bytes and untracked-path set equal the preflight snapshot;
- add injected allow-list, verifier, local-commit/push, PR-create and post-PR label/edit failure tests.

Do not use failure residue in the game checkout as evidence.

## F02 — Canonical Scrubbots remote can be caller-overridden in the public Route A service — MAJOR

P2 requires the configured target remote to be exactly:
`Sekiph82/Scrubbots`.

The production Studio path correctly calls Route A without overriding the canonical remote. However, the exported public service:
`release_approved_campaign(..., expected_remote=...)`
allows a caller to replace the expected remote with an arbitrary repository/path.

The current temporary-remote tests rely on this production argument.

Required closure:
- remove caller-controlled `expected_remote` from the public production API;
- production preflight must compare `origin` only against the fixed canonical Scrubbots identity;
- keep testability through an internal/private seam, monkeypatched module authority, or test-only dependency that cannot be supplied through the production Studio request/API;
- prove an arbitrary remote cannot be authorized through production arguments.

## F03 — The real default current-game verifier is implemented but not authentically executed in P2 tests — MAJOR

The default verifier code is promising and invokes:
- current `LevelCatalog.load_manifest/validate_all`;
- current `LevelLoader`;
- current `SupplyPlanLoader`;
- current `ProofState`;
- current `SolvabilitySolver.solve/replay`;
- current `LevelDifficultyAnalyzerV1`;
- current `DifficultyV1CatalogCheck`;
- metadata score parity at 1e-6.

But every focused Route A test injects a stub `verifier=` callback.

Therefore the exact P2 game verifier has not been proven executable against current Scrubbots authority. This matters because earlier campaign integration work already exposed real Godot API mismatches that static inspection did not catch.

Required closure:
- use a full isolated archive/temp copy of current `Sekiph82/Scrubbots origin/main`;
- stage a valid representative release batch only in that temp copy;
- execute the real default Route A verifier with current Godot;
- require explicit `FACTORY_ROUTE_A_VERIFY_PASS`;
- when Godot + canonical game authority exist, timeout/nonzero/API mismatch is FAIL, not SKIP;
- live owner Scrubbots checkout remains untouched;
- tests still never push/open a real remote PR.

## Independently accepted P2 behavior

### Approval and stale-plan gate — PASS
Route A requires explicit Studio approval and revalidates the exact current plan hash and current CampaignBuilder inputs before branch creation.

### Branch/main safety — PASS structurally
The production flow checks clean `main`, fetches `origin`, requires 0/0 divergence, creates a deterministic release branch, and never issues a push to game `main`.

F02 must still remove the remote-identity bypass seam.

### Allow-list / append-only catalog — PASS before rollback concern
The normal success path enforces only the owner-authorized level/supply/metadata/preview paths plus append-only production catalog.

### PR body / label / public warning — PASS
The PR body includes campaign table, shortage summary, verification summary, plan hash, factory SHA and game SHA. The Studio and return payload warn that the public repository exposes unreleased content.

### Receipt — PASS
A successful route writes a plan-bound/game-commit-bound receipt with PR URL and file digests and surfaces it to Studio.

## Regression evidence

Builder:
- Route A focused tests included success, preflight refusals, stale plan, allow-list refusal, verifier failure rollback, push failure, PR-create failure and collision refusal;
- focused combined set: PASS;
- compileall: PASS;
- git diff --check: PASS;
- no real game remote was touched.

The full-suite tracker failures were ChatGPT-owned and have been repaired separately; they are not P2 implementation findings.

## Final disposition

`P2 Route A = CHANGES_REQUIRED`

`SB-CPX-003 = REMEDIATE_THEN_REAUDIT`

Preserve the accepted Route A architecture. Remediate only F01..F03.
