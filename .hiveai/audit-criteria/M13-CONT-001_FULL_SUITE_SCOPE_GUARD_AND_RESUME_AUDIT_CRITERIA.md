# M13-CONT-001 — Full-Suite Scope Guard + Resume — Audit Criteria

## PASS rule

PASS only if the historical test harness no longer implicitly consumes the owner's Desktop Scrubbots checkout, the CP010 guard is durable for legitimate declarative M13 source growth, a safe unfiltered full pytest run completes, and M13 then resumes from SB-CP02-002 through SB-CP02-012 under the already-published child contracts.

## A. No implicit Desktop game authority

Require:
- no automatic `Path.home()/Desktop/ScrubBots` or equivalent case variant as test authority;
- `tests/integration/test_release_batch_level_catalog.py` uses game checkout only when `SCRUBBOTS_PROJECT` is explicitly provided;
- when the capability is absent, the integration skips truthfully before any git/Godot access to an owner checkout;
- an explicitly supplied checkout is verified as `Sekiph82/Scrubbots`;
- the supplied checkout is read-only; all test mutations occur only in extracted TEMP data;
- no other test introduced/retains an equivalent implicit Desktop fallback.

## B. Durable CP010 architecture guard

The historical CP010 security intent must remain.

Require:
- root `TASKS.md` ownership/protection remains;
- package-wide forbidden network/runtime/provider-client import checks remain;
- package scan is recursive across Content Pipeline Python source where needed;
- no exact per-child source-path whitelist is required for legitimate declarative M13 modules;
- the guard must fail on forbidden network/provider/runtime implementation, not on the mere existence of a new declarative source module.

## C. Safe full-suite gate

Before resuming child 002:
- run focused harness regressions;
- run full `python -m pytest -q` with `SCRUBBOTS_PROJECT` and `SCRUBBOTS_CANONICAL_CHECKOUT` explicitly absent unless this continuation itself created an authorized TEMP capability;
- full suite must complete, not be aborted;
- truthful capability skips are allowed;
- no test may read/write the owner's Desktop game checkout implicitly.

If another implicit external-checkout path appears, stop and record the exact test instead of broadening authority silently.

## D. Preserve child 001

`SB-CP02-001` remains PASS/CLOSED.

Do not redesign its manifest model/schema unless a new regression proves an actual defect.

## E. Resume M13 batch

After A-C pass, execute the already-published child prompts in order:

1. SB-CP02-002-C001
2. SB-CP02-003-C001
3. SB-CP02-004-C001
4. SB-CP02-005-C001
5. SB-CP02-006-C001
6. SB-CP02-007-C001
7. SB-CP02-008-C001
8. SB-CP02-009-C001
9. SB-CP02-010-C001
10. SB-CP02-011-C001
11. SB-CP02-012-C001

Each child must:
- satisfy its own existing audit criteria;
- have a distinct builder log;
- separate implementation and log commits;
- keep prior accepted children green;
- publish normally to main with 0/0 parity.

## F. Final master verification

Require:
- all 12 child logs present;
- continuation log present;
- M13 master log append-only updated with continuation and child 002..012 evidence;
- root `TASKS.md` untouched by Codex;
- `.hiveai/audits/**` untouched by Codex;
- no provider/network/runtime/game mutation;
- final cumulative M11+M12+M13 tests PASS;
- full pytest PASS except truthful pre-capability skips;
- compileall PASS;
- Content Pipeline schema/example parse PASS;
- git diff --check PASS;
- final main parity 0/0.

Codex must stop for ChatGPT independent audit after publication.
