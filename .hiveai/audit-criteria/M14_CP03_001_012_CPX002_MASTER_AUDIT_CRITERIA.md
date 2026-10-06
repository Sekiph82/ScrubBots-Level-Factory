# M14 MASTER - Independent Audit Wrapper

This wrapper does not replace child audit criteria.

## M14 PASS rule

M14 closes only if ChatGPT independently audits every active M14 child as PASS/CLOSED:

1. SB-CP03-001-C001 - `.hiveai/audit-criteria/SB-CP03-001-C001_PUBLISHER_VALIDATION_ONLY_MODE_AUDIT_CRITERIA.md`
2. SB-CP03-002-C001 - `.hiveai/audit-criteria/SB-CP03-002-C001_SERIALIZE_ACCEPTED_FACTORY_OUTPUT_TO_PACKS_AUDIT_CRITERIA.md`
3. SB-CP03-003-C001 - `.hiveai/audit-criteria/SB-CP03-003-C001_HASHES_CANDIDATE_MANIFEST_AUDIT_CRITERIA.md`
4. SB-CP03-004-C001 - `.hiveai/audit-criteria/SB-CP03-004-C001_UPLOAD_PACKS_BEFORE_MANIFEST_AUDIT_CRITERIA.md`
5. SB-CP03-005-C001 - `.hiveai/audit-criteria/SB-CP03-005-C001_VERIFY_REMOTE_OBJECT_INTEGRITY_AUDIT_CRITERIA.md`
6. SB-CP03-006-C001 - `.hiveai/audit-criteria/SB-CP03-006-C001_PUBLISH_STAGING_FIRST_AUDIT_CRITERIA.md`
7. SB-CP03-007-C001 - `.hiveai/audit-criteria/SB-CP03-007-C001_VERIFY_STAGING_REAL_DOWNLOAD_AUDIT_CRITERIA.md`
8. SB-CPX-002-C001 - `.hiveai/audit-criteria/SB-CPX-002-C001_CURRENT_MAIN_SUPPLY_REPLAY_PROMOTION_GATE_AUDIT_CRITERIA.md`
9. SB-CP03-008-C001 - `.hiveai/audit-criteria/SB-CP03-008-C001_EXPLICIT_STAGING_TO_PRODUCTION_PROMOTION_AUDIT_CRITERIA.md`
10. SB-CP03-009-C001 - `.hiveai/audit-criteria/SB-CP03-009-C001_NEW_VERSIONED_PRODUCTION_MANIFEST_AUDIT_CRITERIA.md`
11. SB-CP03-010-C001 - `.hiveai/audit-criteria/SB-CP03-010-C001_NO_SILENT_LIVE_OVERWRITE_AUDIT_CRITERIA.md`
12. SB-CP03-011-C001 - `.hiveai/audit-criteria/SB-CP03-011-C001_ONE_COMMAND_PUBLISH_ORCHESTRATOR_AUDIT_CRITERIA.md`
13. SB-CP03-012-C001 - `.hiveai/audit-criteria/SB-CP03-012-C001_PUBLISH_REPORT_AUDIT_CRITERIA.md`

SB-CPX-003 is already PASS/CLOSED historical authority and is not part of this execution batch.

## Independent audit requirements

ChatGPT must:
- fetch live source, diffs and builder logs from GitHub;
- audit each child against its own criteria;
- write one strict audit per child;
- independently inspect provider-neutral transaction ordering, pack/manifest byte identity, staging verification, CPX-002 current-main replay, production CAS/version behavior and report integrity;
- never accept Codex PASS claims without source evidence;
- open focused remediation only for failed children;
- keep already passing children closed unless direct regression evidence exists;
- keep M14 open until all 13 active children close.

## Master invariants

Require:
- sync-first evidence;
- 13 distinct child logs;
- implementation/log commit separation;
- root TASKS and audits untouched by Codex;
- main-only Level Factory repository;
- no real vendor adapter/credentials;
- no production bypass of staging;
- packs verified before manifest activation;
- CPX-002 authentic current-main Godot replay PASS before production promotion;
- exact current-main drift fence;
- owner approval;
- strictly newer production content version;
- conditional no-silent-overwrite gate;
- deterministic secret-free publish report;
- final full regression green.

Root `TASKS.md` remains sole lifecycle tracker.
