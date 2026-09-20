# SB-LFX-005-C001 — Factory Studio One-Click Pipeline

Builder log:
`.hiveai/codex-logs/SB-LFX-005-C001_ONE_CLICK_PIPELINE_CODEX_LOG.md`

Create log before edits. Work only on LFX-005.

Read TASKS, product spec, LFX-005 criteria, committed LFX-002..004 implementations/logs, canonical Generate/Reproduce/quality contracts, and current Studio.

Implement a bounded canonical pipeline orchestrator:

SOURCE → DERIVE/NORMALIZE when applicable → VALIDATE → CANDIDATE → SOLVE → DIFFICULTY → QA → REVIEW.

Rules:
- call/reuse canonical subsystems;
- record versioned stage dispositions and input/output identities;
- never synthesize solver/difficulty/QA/review truth;
- stop at first real blocking FAIL/NOT_AVAILABLE;
- exact OWNER_UPLOAD source stays immutable;
- exact-valid source may skip derivation;
- Generate uses real canonical bundle;
- any pipeline-run persistence contains lineage/references, not copied source truth.

UI: one Run Pipeline action, stage timeline, exact stop/failure reason, clear distinction between PASS and unavailable.

Tests: real Studio exact-upload path, Generate path, validation failure, unavailable M03/M04/M05 stop behavior, rerun lineage, source immutability, no false owner acceptance.

No LFX-006+ work. No TASKS edits.

Commit/push implementation, then exactly one task-final log-only commit. Continue only under the authorized batch master.
