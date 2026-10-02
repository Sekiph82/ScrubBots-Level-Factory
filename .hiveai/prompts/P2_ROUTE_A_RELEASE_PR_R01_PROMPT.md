# P2-ROUTE-A-C001-R01 — Strict Closure Remediation

Document role: CODEX REMEDIATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent owner prompt:
`.hiveai/prompts/P2_ROUTE_A_RELEASE_PR.md`

Parent strict audit:
`.hiveai/audits/P2_ROUTE_A_RELEASE_PR_STRICT_AUDIT.md`

R01 audit criteria:
`.hiveai/audit-criteria/P2_ROUTE_A_RELEASE_PR_R01_AUDIT_CRITERIA.md`

## Scope

Modify only `Sekiph82/ScrubBots-Level-Factory`.

Preserve the accepted P2 architecture. Close only F01..F03.

Do not create a real Scrubbots release branch or PR.
Do not push to `Sekiph82/Scrubbots`.
Do not modify the owner's live Scrubbots checkout.

Tests that need a remote must use a temporary local bare remote.

## R01.1 — Exact byte-for-byte game-checkout rollback

Current allow-list failure deliberately leaves an unexpected post-preflight path behind. That violates the owner rollback contract.

Fix Route A so every failed operation restores the game checkout to the exact preflight state.

At preflight, record enough state to prove restoration:
- branch;
- HEAD;
- index/worktree clean state;
- tracked-file identity;
- untracked-path set (must be empty under the current clean preflight contract).

On failure:
- restore tracked/index state to the preflight HEAD;
- remove all files/directories created by the Route A attempt, including unexpected allow-list paths;
- return to the original `main` branch;
- delete the deterministic local release branch;
- if pushed, delete the deterministic remote release branch;
- if a PR was already created, close it before/while deleting its remote branch;
- preserve diagnostic/failure evidence only under Level Factory output/evidence, not as residue in the game checkout.

After cleanup, VERIFY:
- current branch equals preflight branch;
- HEAD equals preflight HEAD;
- `git status --porcelain --untracked-files=all` equals the preflight status;
- tracked bytes/index are unchanged;
- no operation-created path remains.

Add tests for:
1. allow-list violation creating an unexpected extension/path;
2. real verifier failure after publication staging;
3. failure after local commit but before push;
4. PR create failure after branch push;
5. PR label/edit failure after PR creation;
6. any rollback-cleanup failure must be reported truthfully, not labeled `ROLLED_BACK`.

The old test that expects `unexpected-owner.txt` to survive must be removed/reversed.

## R01.2 — Canonical remote must not be caller-overridable

Remove the caller-controlled public argument:
`expected_remote=`.

Production Route A must always require `origin` to normalize exactly to the canonical:
`https://github.com/Sekiph82/Scrubbots.git`.

The Studio/launcher request must expose no field that can replace this identity.

For tests using a local bare remote:
- use a private/internal test seam or monkeypatch module authority;
- do not leave a caller-accessible production API argument that can authorize an arbitrary remote.

Add a regression proving:
- production call against arbitrary origin is refused;
- no function/request argument can make that arbitrary origin acceptable.

## R01.3 — Execute the real current-game verifier

Do not accept static presence of the verifier as proof.

Add an authentic integration test that:
1. resolves canonical read-only `Sekiph82/Scrubbots origin/main`;
2. creates a FULL isolated git archive/temp game copy;
3. stages a representative valid Route A batch in the temp copy using the accepted P1 transaction;
4. invokes Route A's REAL default `_verify_game` path, not an injected stub;
5. requires `FACTORY_ROUTE_A_VERIFY_PASS`;
6. proves LevelCatalog, LevelLoader, SupplyPlanLoader, ProofState, SolvabilitySolver solve/replay, DifficultyV1CatalogCheck and Difficulty V1 metadata parity execute successfully.

Use repository Godot discovery conventions.

When Godot + canonical game authority exist:
- timeout = FAIL;
- nonzero = FAIL;
- API mismatch = FAIL;
- missing PASS marker = FAIL.

A truthful SKIP is allowed only when required capability is unavailable before the test begins.

Never mutate the live Scrubbots checkout.

Never push/open a real PR in this integration.

## Preserve accepted P2 behavior

Do not redesign:
- CampaignBuilder APPROVE gate;
- plan hash/current-input revalidation;
- deterministic branch naming;
- P1 exact contiguous batch transaction;
- normal allow-list;
- one release commit;
- branch-only push;
- PR body/label;
- public-repo warning;
- release receipt;
- idempotent collision refusal.

## Required verification

Run:
- P2-R01 focused tests;
- all existing Route A tests;
- authentic default-verifier integration;
- P1 CampaignBuilder/Release Pool regression;
- R02 publication/catalog regression;
- governance tracker tests;
- full pytest;
- compileall;
- git diff --check;
- Factory Studio runtime/action integration suites.

Full pytest must be green except truthful pre-capability skips.

## Builder governance

Do not edit:
- root `TASKS.md`;
- `.hiveai/audits/**`;
- active prompt/criteria;
- prior logs.

Create before product edits:
`.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md`

Commit implementation separately from final log publication.
Push Level Factory `main`.
Fetch again and prove local/origin 0/0.

STOP for independent ChatGPT re-audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md
