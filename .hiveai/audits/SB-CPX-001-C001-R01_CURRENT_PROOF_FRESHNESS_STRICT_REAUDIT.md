# SB-CPX-001-C001-R01 — Current Proof Freshness

Document role: CHATGPT INDEPENDENT STRICT RE-AUDIT

Implementation:
`509082677376a5158f2845b5c172e26a525ca18a`

Builder log publication:
`49178a7ca1e2c0312818af59cf5b5b411814ecde`

Parent audit:
`.hiveai/audits/SB-CPX-001-C001_SOLVER_PROVEN_SUPPLY_IDENTITY_PACK_BINDING_STRICT_AUDIT.md`

## VERDICT

**PASS / CLOSED**

The stale-proof race is closed.

## Build-time freshness

`build_solver_proven_scrubpack()` now requires an explicit `current_authority_check` callback.

The callback runs after cryptographic/pack construction validation and immediately before any `ScrubpackBuildResult` is returned.

Without a callback, production solver-proven build fails closed.

Content Pipeline does not import Factory private implementation.

Factory owns:
`revalidate_current_solver_proofs()`

## Accepted READY authority

At final build, Factory re-resolves the candidate through current authority and requires:
- candidate still exists;
- latest owner review is ACCEPT;
- latest review ID equals proof review ID;
- latest READY pipeline run ID equals proof run ID;
- current pipeline bytes equal proof bytes;
- current proof source equals frozen proof source;
- current LevelData bytes equal packaged LevelData bytes;
- current supply-plan bytes equal packaged supply-plan bytes.

The verifier performs a second final authority read before returning success, closing the original ACCEPT -> proof -> REJECT race.

## Release Pool authority

PASS.

Current proof resolution starts from current `release_entries()`.

For pool proofs the verifier also requires:
- current pool entry remains present;
- current entry object equals the frozen proof source;
- entry digest is still valid;
- current pipeline bytes/digest match;
- level/supply source paths and exact bytes match.

Removing/revoking the current pool projection makes the old proof fail.

## Race regressions

PASS.

The integration test explicitly proves:

- Race A: ACCEPT -> resolve proof -> REJECT -> old proof build FAIL.
- Race B: ACCEPT A -> resolve proof -> newer ACCEPT B -> old proof build FAIL.
- Race C: READY A -> resolve proof -> newer READY B -> old proof build FAIL.
- Race D: current Release Pool projection -> resolve proof -> remove projection -> old proof build FAIL.
- Release Pool owner review revoked -> old proof build FAIL.
- Unchanged accepted READY proof -> PASS.
- Unchanged Release Pool proof -> PASS.

Each stale-path test leaves the build result variable `None`, so no success result is returned.

## Dependency direction

PASS.

Content Pipeline receives a narrow callback only.

Factory imports neither publisher implementation into Content Pipeline nor reverses the accepted M11/M12 dependency boundary.

Documentation distinguishes cryptographic proof verification from current-authority production build.

## Cryptographic binding preservation

PASS.

Retained:
- exact LevelData ID/bytes/SHA-256;
- exact supply-plan bytes/SHA-256;
- FIFO order/batch IDs/CIDs/robot counts;
- column/preview/max-batch configuration;
- solver-state digest;
- solver-evidence digest;
- SOLVED/WIN;
- replay solved / zero active;
- conservation PASS;
- load-check READY;
- canonical Scrubbots authority identity;
- Release Pool digest validation;
- detached identity artifact digest.

Legacy `solver_evidence.py` remains non-production.

CPX-002 current-main replay remains M14 scope.

## Regression / publication

Builder evidence:
- final CPX integration: 1 passed;
- CP01 pack suite: 82 passed;
- CP00 post-commit: 163 passed;
- final cumulative M11+M12+CPX/governance: 277 passed;
- full pytest: **1415 passed, 3 documented skips, 0 failed**;
- compileall PASS;
- 13 schema/example JSON files parse PASS;
- diff check PASS;
- root `TASKS.md` and `.hiveai/audits/**` untouched by Codex.

Independent GitHub verification:
- implementation/log commits are distinct;
- R01 compare touches only the required log, README, two scoped implementation files and focused integration test;
- no protected tracker/audit paths changed;
- `main` head = `49178a7ca1e2c0312818af59cf5b5b411814ecde`.

## FINAL

`SB-CPX-001 = PASS / CLOSED`
