# SB-CP00-010-C001 — Mobile / Store Policy Boundary Re-Verification — Audit Criteria

## PASS rule

PASS only if current official Apple/Google policy is re-checked, the evidence is first-party and date/section specific, the M11 architecture remains explicitly declarative-data-only, and no definitive store-approval claim is made.

## A. Official authority

Require current first-party sources only.

At minimum:
- Google Play Device and Network Abuse;
- Google Play Deceptive Behaviour / behaviour transparency;
- Google Play current policy-version context/archive;
- Apple App Review Guidelines, including current executable-code/self-contained-app boundary;
- Apple Developer Program License Agreement current executable/interpreted-code boundary.

Every source must record exact official URL, platform, check date and relevant section/guideline identifier.

## B. Declarative architecture mapping

Require explicit mapping of:
- LevelData V1;
- supply-plan V1;
- metadata V1;
- CP003 executable-content rejection;
- CP007 zero-mutation dry-run;
- CP008 provider-neutral/no-concrete-provider state;
- CP006 no-credentials-in-Git boundary.

## C. Explicit forbidden boundary

Require remote executable/script/plugin/native/interpreted-code injection, hidden remote feature activation and review evasion to remain forbidden.

Do not silently rely on Apple mini-app/software exceptions.

## D. Honest conclusion

Allowed:
- architecture currently consistent with a declarative remote-data boundary;
- future runtime/provider behavior not yet verified;
- final release recheck required.

Forbidden:
- APP_STORE_APPROVED;
- PLAY_APPROVED;
- guaranteed store acceptance;
- legal certification/compliance claim.

If official policy materially conflicts or is ambiguous, PASS is forbidden and the task must report BLOCKED / OWNER_POLICY_REVIEW_REQUIRED.

## E. Machine-readable evidence

Require:
- `docs/security/MOBILE_STORE_POLICY_BOUNDARY_V01.md`;
- `content_pipeline/policy/mobile_store_policy_boundary_v1.json`;
- versioned JSON schema;
- deterministic snapshot;
- `final_recheck_required=true`;
- M20 / SB-CP09-001 and SB-CP09-002 ownership references.

## F. Architecture preservation

No product web scraper, network/provider implementation, runtime downloader, credential path, game mutation, second tracker, or audit/tracker edit by Codex.

## G. Regression

Require:
- CP010 focused PASS;
- cumulative CP001..010 PASS;
- governance PASS;
- full pytest PASS except truthful pre-capability skips;
- compileall PASS;
- schema/snapshot parse PASS;
- git diff --check PASS.

Codex must not edit root `TASKS.md` or `.hiveai/audits/**`.
