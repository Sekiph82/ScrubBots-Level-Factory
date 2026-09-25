# SB-LF07-001..010 C001 — Implementation and Audit Index

Document role: CHATGPT AUTHORIZATION / INDEX

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main

M07 batch policy:
- Codex implements all ten tasks sequentially without waiting for intermediate ChatGPT audit.
- Root TASKS.md and .hiveai/audits/** remain ChatGPT-owned and must not be edited by Codex.
- Builder logs are evidence claims only. No task becomes PASS/CLOSED until independent ChatGPT strict audit.
- Each task has its own implementation prompt, strict audit criteria and builder log.
- After SB-LF07-010, Codex stops. ChatGPT audits 001..010 individually from their published logs/commits.
- Any CHANGES_REQUIRED tasks will receive a dedicated remediation batch; only if all ten close may the tracker advance to M08.

## SB-LF07-001
- Prompt: `.hiveai/prompts/SB-LF07-001-C001_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_PROMPT.md`
- Audit criteria: `.hiveai/audit-criteria/SB-LF07-001-C001_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF07-001-C001_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_CODEX_LOG.md`

## SB-LF07-002
- Prompt: `.hiveai/prompts/SB-LF07-002-C001_SAFE_HARDENING_CANONICAL_MECHANICS_PROMPT.md`
- Audit criteria: `.hiveai/audit-criteria/SB-LF07-002-C001_SAFE_HARDENING_CANONICAL_MECHANICS_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF07-002-C001_SAFE_HARDENING_CANONICAL_MECHANICS_CODEX_LOG.md`

## SB-LF07-003
- Prompt: `.hiveai/prompts/SB-LF07-003-C001_SAFE_EASING_CANONICAL_MECHANICS_PROMPT.md`
- Audit criteria: `.hiveai/audit-criteria/SB-LF07-003-C001_SAFE_EASING_CANONICAL_MECHANICS_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF07-003-C001_SAFE_EASING_CANONICAL_MECHANICS_CODEX_LOG.md`

## SB-LF07-004
- Prompt: `.hiveai/prompts/SB-LF07-004-C001_RESOLVE_REVALIDATE_EVERY_MUTATION_PROMPT.md`
- Audit criteria: `.hiveai/audit-criteria/SB-LF07-004-C001_RESOLVE_REVALIDATE_EVERY_MUTATION_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF07-004-C001_RESOLVE_REVALIDATE_EVERY_MUTATION_CODEX_LOG.md`

## SB-LF07-005
- Prompt: `.hiveai/prompts/SB-LF07-005-C001_SEED_PARENT_MUTATION_PROVENANCE_PROMPT.md`
- Audit criteria: `.hiveai/audit-criteria/SB-LF07-005-C001_SEED_PARENT_MUTATION_PROVENANCE_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF07-005-C001_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md`

## SB-LF07-006
- Prompt: `.hiveai/prompts/SB-LF07-006-C001_TARGET_CHALLENGE_SCORE_RANGE_PROMPT.md`
- Audit criteria: `.hiveai/audit-criteria/SB-LF07-006-C001_TARGET_CHALLENGE_SCORE_RANGE_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF07-006-C001_TARGET_CHALLENGE_SCORE_RANGE_CODEX_LOG.md`

## SB-LF07-007
- Prompt: `.hiveai/prompts/SB-LF07-007-C001_BOUNDED_MUTATION_ATTEMPTS_PROMPT.md`
- Audit criteria: `.hiveai/audit-criteria/SB-LF07-007-C001_BOUNDED_MUTATION_ATTEMPTS_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF07-007-C001_BOUNDED_MUTATION_ATTEMPTS_CODEX_LOG.md`

## SB-LF07-008
- Prompt: `.hiveai/prompts/SB-LF07-008-C001_MUTATE_VS_REGENERATE_EFFICIENCY_PROMPT.md`
- Audit criteria: `.hiveai/audit-criteria/SB-LF07-008-C001_MUTATE_VS_REGENERATE_EFFICIENCY_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF07-008-C001_MUTATE_VS_REGENERATE_EFFICIENCY_CODEX_LOG.md`

## SB-LF07-009
- Prompt: `.hiveai/prompts/SB-LF07-009-C001_OWNER_SOURCE_ART_NON_MUTATION_PROMPT.md`
- Audit criteria: `.hiveai/audit-criteria/SB-LF07-009-C001_OWNER_SOURCE_ART_NON_MUTATION_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF07-009-C001_OWNER_SOURCE_ART_NON_MUTATION_CODEX_LOG.md`

## SB-LF07-010
- Prompt: `.hiveai/prompts/SB-LF07-010-C001_DETERMINISTIC_MUTATION_REGRESSION_PROMPT.md`
- Audit criteria: `.hiveai/audit-criteria/SB-LF07-010-C001_DETERMINISTIC_MUTATION_REGRESSION_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF07-010-C001_DETERMINISTIC_MUTATION_REGRESSION_CODEX_LOG.md`

