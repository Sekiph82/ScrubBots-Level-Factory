# SB-LF08 C001 — Implementation and Audit Index

Document role: CHATGPT AUTHORIZATION / INDEX

## Existing accepted M08 foundation
Already PASS/CLOSED and not to be reimplemented:
- SB-LF08-002 — Separate generated from accepted count
- SB-LF08-003 — Rejection statistics
- SB-LF08-004 — Deterministic/resumable batch jobs
- SB-LF08-005 — Prevent duplicate IDs/seeds/artifacts
- SB-LF08-010 — Reruns create no meaningless diffs
- SB-LFX-013/014/015 M08 extensions remain PASS/CLOSED.

Open C001 implementation tasks:
- 001, 006, 007, 008, 009.

Codex implements all five sequentially without intermediate ChatGPT review. ChatGPT audits each separately after the complete batch.

## SB-LF08-001
- Prompt: `.hiveai/prompts/SB-LF08-001-C001_ACCEPTED_COUNTS_LANE_CLASS_CADENCE_PROMPT.md`
- Strict criteria: `.hiveai/audit-criteria/SB-LF08-001-C001_ACCEPTED_COUNTS_LANE_CLASS_CADENCE_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF08-001-C001_ACCEPTED_COUNTS_LANE_CLASS_CADENCE_CODEX_LOG.md`

## SB-LF08-006
- Prompt: `.hiveai/prompts/SB-LF08-006-C001_ACCEPTED_BATCH_RESULT_ARTIFACT_SET_PROMPT.md`
- Strict criteria: `.hiveai/audit-criteria/SB-LF08-006-C001_ACCEPTED_BATCH_RESULT_ARTIFACT_SET_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF08-006-C001_ACCEPTED_BATCH_RESULT_ARTIFACT_SET_CODEX_LOG.md`

## SB-LF08-007
- Prompt: `.hiveai/prompts/SB-LF08-007-C001_OWNER_REVIEW_GATE_BEFORE_PUBLICATION_PROMPT.md`
- Strict criteria: `.hiveai/audit-criteria/SB-LF08-007-C001_OWNER_REVIEW_GATE_BEFORE_PUBLICATION_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF08-007-C001_OWNER_REVIEW_GATE_BEFORE_PUBLICATION_CODEX_LOG.md`

## SB-LF08-008
- Prompt: `.hiveai/prompts/SB-LF08-008-C001_CONTENT_PIPELINE_PRODUCTION_HANDOFF_PROMPT.md`
- Strict criteria: `.hiveai/audit-criteria/SB-LF08-008-C001_CONTENT_PIPELINE_PRODUCTION_HANDOFF_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF08-008-C001_CONTENT_PIPELINE_PRODUCTION_HANDOFF_CODEX_LOG.md`

## SB-LF08-009
- Prompt: `.hiveai/prompts/SB-LF08-009-C001_HIGH_REJECTION_STRESS_SAFETY_PROMPT.md`
- Strict criteria: `.hiveai/audit-criteria/SB-LF08-009-C001_HIGH_REJECTION_STRESS_SAFETY_AUDIT_CRITERIA.md`
- Builder log: `.hiveai/codex-logs/SB-LF08-009-C001_HIGH_REJECTION_STRESS_SAFETY_CODEX_LOG.md`

