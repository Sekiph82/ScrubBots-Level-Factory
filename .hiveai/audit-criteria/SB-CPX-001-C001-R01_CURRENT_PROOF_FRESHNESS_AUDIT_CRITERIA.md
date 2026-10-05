# SB-CPX-001-C001-R01 — Current Proof Freshness — Audit Criteria

## PASS rule

PASS only if final solver-proven pack emission cannot succeed from a proof whose owner-review / READY / Release Pool authority became stale after proof resolution.

## A. Build-time current-authority revalidation

The production solver-proven pack path must revalidate authority immediately before final pack emission.

For accepted-READY fallback require exact current:
- candidate existence;
- latest owner review disposition == ACCEPT;
- latest review ID == proof review ID;
- latest READY pipeline run ID == proof pipeline run ID;
- exact current pipeline bytes SHA-256 == proof pipeline SHA-256;
- exact current LevelData and supply-plan bytes == proof-bound bytes.

For Release Pool require:
- proof entry is still present in current `release_entries()`;
- current entry digest exactly matches proof entry digest;
- current pipeline run ID/digest/bytes exactly match;
- current level/supply bindings still match.

## B. Race regressions

Require real integration tests for:

1. ACCEPT -> resolve proof -> REJECT -> build with old proof => FAIL before pack emission.
2. ACCEPT A -> resolve proof -> new ACCEPT B/review identity -> build old proof => FAIL.
3. ACCEPT -> resolve proof -> newer READY pipeline identity -> build old proof => FAIL.
4. Release Pool proof removed/revoked from current projection -> old proof build => FAIL.
5. unchanged current proof => PASS.

No successful archive or success receipt may be returned on stale authority.

## C. Dependency boundary

Do not create a Content Pipeline -> Factory private implementation import.

Use dependency inversion / factory-side orchestration / explicit current-authority verifier seam.

The pure cryptographic checker may remain reusable, but a low-level stale proof must not be representable as a current production-authorized pack emission.

Documentation/public API must distinguish pure proof verification from current-authority production build.

## D. Preserve CPX-001 cryptographic binding

Retain all prior PASS behavior:
- exact LevelData/supply bytes and SHA-256;
- FIFO/batch/CID/count/config binding;
- initial-state digest;
- solver evidence digest;
- SOLVED/WIN/replay/conservation/load-check gates;
- canonical Scrubbots authority identity;
- Release Pool digest verification;
- legacy solver_evidence.py remains non-production;
- no CPX-002 current-main replay in M12.

## E. Regression

Require:
- focused R01 stale-race integration tests PASS;
- original CPX-001 tests PASS;
- all SB-CP01-001..010 tests PASS;
- M11 regressions PASS;
- governance/tracker PASS;
- full pytest PASS except truthful pre-capability skips;
- compileall PASS;
- schema parse PASS;
- git diff --check PASS.

Codex must not edit root `TASKS.md` or `.hiveai/audits/**`.
