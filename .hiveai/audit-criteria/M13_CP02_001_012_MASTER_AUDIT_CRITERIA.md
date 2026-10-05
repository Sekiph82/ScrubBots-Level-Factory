# M13 MASTER — Remote Manifest & Content Versioning — Audit Wrapper

This wrapper does not replace child audit criteria.

## M13 PASS rule

ChatGPT may close M13 only after independently auditing all 12 children:

1. SB-CP02-001-C001 — `.hiveai/audit-criteria/SB-CP02-001-C001_REMOTE_MANIFEST_V1_SCHEMA_AUDIT_CRITERIA.md`
2. SB-CP02-002-C001 — `.hiveai/audit-criteria/SB-CP02-002-C001_MONOTONIC_CONTENT_VERSION_AUDIT_CRITERIA.md`
3. SB-CP02-003-C001 — `.hiveai/audit-criteria/SB-CP02-003-C001_MINIMUM_GAME_VERSION_COMPATIBILITY_AUDIT_CRITERIA.md`
4. SB-CP02-004-C001 — `.hiveai/audit-criteria/SB-CP02-004-C001_PACK_IDS_LOCATIONS_HASHES_AUDIT_CRITERIA.md`
5. SB-CP02-005-C001 — `.hiveai/audit-criteria/SB-CP02-005-C001_LEVEL_METADATA_NONCONTIGUOUS_IDS_AUDIT_CRITERIA.md`
6. SB-CP02-006-C001 — `.hiveai/audit-criteria/SB-CP02-006-C001_DISABLED_LEVELS_AUDIT_CRITERIA.md`
7. SB-CP02-007-C001 — `.hiveai/audit-criteria/SB-CP02-007-C001_SCHEDULED_ACTIVATION_WINDOWS_AUDIT_CRITERIA.md`
8. SB-CP02-008-C001 — `.hiveai/audit-criteria/SB-CP02-008-C001_REJECT_DUPLICATE_PACK_LEVEL_OWNERSHIP_AUDIT_CRITERIA.md`
9. SB-CP02-009-C001 — `.hiveai/audit-criteria/SB-CP02-009-C001_VALIDATE_REFERENCES_BEFORE_PUBLISH_AUDIT_CRITERIA.md`
10. SB-CP02-010-C001 — `.hiveai/audit-criteria/SB-CP02-010-C001_MANIFEST_VERSION_HISTORY_AUDIT_CRITERIA.md`
11. SB-CP02-011-C001 — `.hiveai/audit-criteria/SB-CP02-011-C001_APP_CONTENT_SCHEMA_COMPATIBILITY_AUDIT_CRITERIA.md`
12. SB-CP02-012-C001 — `.hiveai/audit-criteria/SB-CP02-012-C001_MANIFEST_PARSER_SCHEMA_TESTS_AUDIT_CRITERIA.md`

Every child must be PASS/CLOSED.

## Independent audit requirements

ChatGPT must:
- fetch live implementation/log evidence from GitHub;
- audit each child against its own criteria;
- write one strict audit file per child;
- independently inspect manifest model/schema/parser/history/reference validation;
- never accept Codex PASS claims without source evidence;
- issue focused remediation prompt/criteria only for failed children;
- keep already-passing children closed unless regression evidence proves breakage;
- keep M13 open until all 12 close.

## Master invariants

Require:
- 12 distinct child logs;
- implementation/log commit separation;
- sync-first evidence;
- root TASKS.md untouched by Codex;
- audit files untouched by Codex;
- final main parity 0/0;
- no provider/network/runtime/game mutation;
- no credentials;
- declarative manifest only;
- provider-neutral pack locations;
- M12 pack hashes/identity preserved as reference authority;
- no hidden clock;
- no contiguous level-ID assumption;
- append-only manifest history;
- strict parser/schema closure.

Root `TASKS.md` remains the sole lifecycle tracker.
