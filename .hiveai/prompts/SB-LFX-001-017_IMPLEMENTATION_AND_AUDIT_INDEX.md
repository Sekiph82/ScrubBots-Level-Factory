# SB-LFX-001..017 — Implementation / Audit Index

Status: OWNER-AUTHORIZED BATCH WORKFLOW
Repository: Sekiph82/ScrubBots-Level-Factory

This index freezes the per-task evidence paths for the SB-LFX program.

- SB-LFX-001 and 002 are already independently audited PASS/CLOSED baselines.
- The batch implementation run covers SB-LFX-003 through SB-LFX-017.
- No SB-LFX-003..017 task becomes PASS/CLOSED merely because Codex implements it or its tests pass.
- After the complete builder batch, ChatGPT performs strict audits one task at a time using the per-task criteria below and saves one strict-audit file per task.
- Only after the post-batch audit set is complete are remediation prompts generated for tasks with findings.

| Task | Capability | Audit criteria | Implementation prompt | Builder log | Batch status |
|---|---|---|---|---|---|
| SB-LFX-001 | Factory Operations Dashboard | `.hiveai/audit-criteria/SB-LFX-001-C001_FACTORY_OPERATIONS_DASHBOARD_CANONICAL_DERIVED_VIEW_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-001-C001_FACTORY_OPERATIONS_DASHBOARD_CANONICAL_DERIVED_VIEW_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-001-C001_FACTORY_OPERATIONS_DASHBOARD_CANONICAL_DERIVED_VIEW_CODEX_LOG.md` | PASS/CLOSED baseline; do not reimplement in batch |
| SB-LFX-002 | Manual OWNER_UPLOAD Import | `.hiveai/audit-criteria/SB-LFX-002-C001_MANUAL_PIXEL_ART_OWNER_UPLOAD_IMMUTABLE_SOURCE_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-002-C001_MANUAL_PIXEL_ART_OWNER_UPLOAD_IMMUTABLE_SOURCE_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-002-C001_MANUAL_PIXEL_ART_OWNER_UPLOAD_IMMUTABLE_SOURCE_CODEX_LOG.md` | PASS/CLOSED baseline; do not reimplement in batch |
| SB-LFX-003 | Source Art Library | `.hiveai/audit-criteria/SB-LFX-003-C001_SOURCE_ART_LIBRARY_CANONICAL_CATALOG_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-003-C001_FACTORY_STUDIO_SOURCE_ART_LIBRARY_CANONICAL_CATALOG_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-003-C001_SOURCE_ART_LIBRARY_CANONICAL_CATALOG_CODEX_LOG.md` | batch |
| SB-LFX-004 | Import Validation Wizard | `.hiveai/audit-criteria/SB-LFX-004-C001_IMPORT_VALIDATION_WIZARD_CANONICAL_ANALYSIS_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-004-C001_FACTORY_STUDIO_IMPORT_VALIDATION_WIZARD_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-004-C001_IMPORT_VALIDATION_WIZARD_CODEX_LOG.md` | batch |
| SB-LFX-005 | One-Click Pipeline | `.hiveai/audit-criteria/SB-LFX-005-C001_ONE_CLICK_PIPELINE_TRUTHFUL_ORCHESTRATION_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-005-C001_FACTORY_STUDIO_ONE_CLICK_PIPELINE_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-005-C001_ONE_CLICK_PIPELINE_CODEX_LOG.md` | batch |
| SB-LFX-006 | Candidate Inbox + Review Queue | `.hiveai/audit-criteria/SB-LFX-006-C001_UNIFIED_CANDIDATE_INBOX_OWNER_REVIEW_QUEUE_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-006-C001_FACTORY_STUDIO_CANDIDATE_INBOX_REVIEW_QUEUE_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-006-C001_CANDIDATE_INBOX_REVIEW_QUEUE_CODEX_LOG.md` | batch |
| SB-LFX-007 | Side-by-Side Comparison | `.hiveai/audit-criteria/SB-LFX-007-C001_SIDE_BY_SIDE_CANDIDATE_COMPARISON_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-007-C001_FACTORY_STUDIO_SIDE_BY_SIDE_COMPARISON_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-007-C001_SIDE_BY_SIDE_COMPARISON_CODEX_LOG.md` | batch |
| SB-LFX-008 | Presets / Production Recipes | `.hiveai/audit-criteria/SB-LFX-008-C001_PRESETS_PRODUCTION_RECIPES_EXPANDED_REQUEST_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-008-C001_FACTORY_STUDIO_PRESETS_PRODUCTION_RECIPES_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-008-C001_PRESETS_PRODUCTION_RECIPES_CODEX_LOG.md` | batch |
| SB-LFX-009 | Search / Filter / Smart Collections | `.hiveai/audit-criteria/SB-LFX-009-C001_SEARCH_FILTER_SMART_COLLECTIONS_DERIVED_VIEW_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-009-C001_FACTORY_STUDIO_SEARCH_FILTER_SMART_COLLECTIONS_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-009-C001_SEARCH_FILTER_SMART_COLLECTIONS_CODEX_LOG.md` | batch |
| SB-LFX-010 | Production Readiness Card | `.hiveai/audit-criteria/SB-LFX-010-C001_PRODUCTION_READINESS_CARD_TRUTHFUL_GATES_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-010-C001_FACTORY_STUDIO_PRODUCTION_READINESS_CARD_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-010-C001_PRODUCTION_READINESS_CARD_CODEX_LOG.md` | batch |
| SB-LFX-011 | Exact Reproduce Action | `.hiveai/audit-criteria/SB-LFX-011-C001_EXACT_REPRODUCE_CAPABILITY_GATED_ACTION_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-011-C001_FACTORY_STUDIO_EXACT_REPRODUCE_ACTION_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-011-C001_EXACT_REPRODUCE_ACTION_CODEX_LOG.md` | batch |
| SB-LFX-012 | Manual Edit Revision History | `.hiveai/audit-criteria/SB-LFX-012-C001_IMMUTABLE_MANUAL_EDIT_REVISION_HISTORY_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-012-C001_FACTORY_STUDIO_MANUAL_EDIT_REVISION_HISTORY_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-012-C001_MANUAL_EDIT_REVISION_HISTORY_CODEX_LOG.md` | batch |
| SB-LFX-013 | Failure Inbox / Retry Center | `.hiveai/audit-criteria/SB-LFX-013-C001_FAILURE_INBOX_RETRY_CENTER_LINEAGE_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-013-C001_FACTORY_STUDIO_FAILURE_INBOX_RETRY_CENTER_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-013-C001_FAILURE_INBOX_RETRY_CENTER_CODEX_LOG.md` | batch |
| SB-LFX-014 | Multi-File Batch Import | `.hiveai/audit-criteria/SB-LFX-014-C001_MULTI_FILE_OWNER_UPLOAD_BATCH_IMPORT_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-014-C001_FACTORY_STUDIO_MULTI_FILE_BATCH_IMPORT_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-014-C001_MULTI_FILE_BATCH_IMPORT_CODEX_LOG.md` | batch |
| SB-LFX-015 | Session Recovery / Autosave | `.hiveai/audit-criteria/SB-LFX-015-C001_FACTORY_STUDIO_SESSION_RECOVERY_AUTOSAVE_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-015-C001_FACTORY_STUDIO_SESSION_RECOVERY_AUTOSAVE_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-015-C001_SESSION_RECOVERY_AUTOSAVE_CODEX_LOG.md` | batch |
| SB-LFX-016 | Advisory Visual Similarity | `.hiveai/audit-criteria/SB-LFX-016-C001_ADVISORY_VISUAL_SIMILARITY_GUARD_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-016-C001_FACTORY_STUDIO_VISUAL_SIMILARITY_GUARD_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-016-C001_VISUAL_SIMILARITY_GUARD_CODEX_LOG.md` | batch |
| SB-LFX-017 | Provider Cost / Credit Center | `.hiveai/audit-criteria/SB-LFX-017-C001_PROVIDER_COST_CREDIT_CENTER_TRUTHFUL_ACCOUNTING_AUDIT_CRITERIA.md` | `.hiveai/prompts/SB-LFX-017-C001_FACTORY_STUDIO_PROVIDER_COST_CREDIT_CENTER_PROMPT.md` | `.hiveai/codex-logs/SB-LFX-017-C001_PROVIDER_COST_CREDIT_CENTER_CODEX_LOG.md` | batch |

