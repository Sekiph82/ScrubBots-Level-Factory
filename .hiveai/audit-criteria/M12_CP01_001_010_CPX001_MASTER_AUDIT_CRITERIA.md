# M12 Master — .scrubpack Format & Packager — Audit Wrapper

This wrapper does not replace child audit criteria.

## M12 PASS rule

ChatGPT may close M12 only after independent strict audit of all 11 children:

1. SB-CP01-001-C001 — `.hiveai/audit-criteria/SB-CP01-001-C001_SCRUBPACK_V1_SPEC_AUDIT_CRITERIA.md`
2. SB-CP01-002-C001 — `.hiveai/audit-criteria/SB-CP01-002-C001_PACKAGE_DECLARATIVE_LEVELS_ONLY_AUDIT_CRITERIA.md`
3. SB-CP01-003-C001 — `.hiveai/audit-criteria/SB-CP01-003-C001_PACK_ID_VERSION_TIME_LEVELS_AUDIT_CRITERIA.md`
4. SB-CP01-004-C001 — `.hiveai/audit-criteria/SB-CP01-004-C001_PER_PACK_SHA256_AUDIT_CRITERIA.md`
5. SB-CP01-005-C001 — `.hiveai/audit-criteria/SB-CP01-005-C001_DETERMINISTIC_PACK_SERIALIZATION_ORDER_AUDIT_CRITERIA.md`
6. SB-CP01-006-C001 — `.hiveai/audit-criteria/SB-CP01-006-C001_DUPLICATE_LEVEL_ID_PREVENTION_AUDIT_CRITERIA.md`
7. SB-CP01-007-C001 — `.hiveai/audit-criteria/SB-CP01-007-C001_VALIDATE_EVERY_LEVEL_BEFORE_PACK_AUDIT_CRITERIA.md`
8. SB-CP01-008-C001 — `.hiveai/audit-criteria/SB-CP01-008-C001_SAFE_UNPACK_INSPECT_TOOLING_AUDIT_CRITERIA.md`
9. SB-CP01-009-C001 — `.hiveai/audit-criteria/SB-CP01-009-C001_DETERMINISTIC_SCRUBPACK_BYTES_AUDIT_CRITERIA.md`
10. SB-CP01-010-C001 — `.hiveai/audit-criteria/SB-CP01-010-C001_UNSUPPORTED_PACK_VERSION_REJECTION_AUDIT_CRITERIA.md`
11. SB-CPX-001-C001 — `.hiveai/audit-criteria/SB-CPX-001-C001_SOLVER_PROVEN_SUPPLY_IDENTITY_PACK_BINDING_AUDIT_CRITERIA.md`

Every child must be PASS/CLOSED.

## Independent audit requirements

ChatGPT must:
- fetch live GitHub implementation/log evidence;
- audit each child against its own criteria;
- write one strict audit file per child;
- never accept Codex self-claims without repository verification;
- issue focused remediation prompt/criteria for any failed child;
- keep already-passing child work closed unless regression evidence proves breakage;
- keep M12 open until all 11 children close.

## Master-level invariants

Require:
- 11 distinct child builder logs;
- implementation/log commit separation;
- root TASKS.md untouched by Codex;
- audit files untouched by Codex;
- sync-first evidence;
- final main parity 0/0;
- no network/provider/runtime/game mutation;
- declarative-only pack format;
- no legacy solver-evidence authority for CPX-001.

Root `TASKS.md` remains sole lifecycle tracker.
