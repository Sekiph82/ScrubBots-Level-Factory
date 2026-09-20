# SB-LFX-015-C001-R02 — Typed Session Recovery + Real Interruption Remediation

Work only on:
`.hiveai/audits/SB-LFX-015-C001-R01_SESSION_SECRET_CONTAINMENT_REFERENCE_RECOVERY_AND_RUNTIME_REMEDIATION_STRICT_AUDIT.md`

Original criteria:
`.hiveai/audit-criteria/SB-LFX-015-C001_FACTORY_STUDIO_SESSION_RECOVERY_AUTOSAVE_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/SB-LFX-015-C001-R02_TYPED_SESSION_RECOVERY_AND_INTERRUPTION_REMEDIATION_CODEX_LOG.md`

Create log before edits.

## Mission

Close BLOCKER-001 and MAJOR-001..004.

### Explicit allowlisted session schema
Replace arbitrary JSON state + heuristic scrubbing with a versioned allowlist.

Persist only approved fields such as:
- selected_surface;
- typed source/candidate/batch/pipeline/retry/revision references;
- active stage/attempt reference;
- bounded explicitly non-canonical drafts;
- autosave_generation.

Reject unknown keys and arbitrary nested mappings. Secrets/tokens/credentials have no valid field in the schema.

### Typed canonical reference validation
Every reference type must resolve through its canonical reader/validator and return:
- field/type;
- ID;
- evidence path/hash where relevant;
- VALID / MISSING / CORRUPT / STALE / COMPLETED / NOT_RESUMABLE.

A syntactically valid but nonexistent ID is never VALID.

### Recovery classification
Derive:
- NEW;
- RESUMED;
- RETRIED;
- NOT_RESUMABLE;
- NEEDS_OPERATOR_ACTION

from verified durable state.

Successful durable stages/output identities must be reused, not rerun.

### Real autosave/recovery
Implement a bounded real autosave trigger/controller, not only manual Save.

Real interruption test:
1. start a real durable batch/pipeline/retry job with identifiable successful stage(s);
2. save/autosave continuity;
3. terminate/reinstantiate Studio;
4. restore;
5. prove completed stage/output identities unchanged;
6. prove eligible work resumes rather than duplicates;
7. missing/deleted reference -> NEEDS_OPERATOR_ACTION;
8. completed/non-resumable -> NOT_RESUMABLE as appropriate;
9. retry continuity -> RETRIED;
10. no-start continuity -> NEW;
11. corrupt session fails closed;
12. persisted session contains no secrets.

Do not restore canonical bytes from the session itself.

Run full regressions. One R02 implementation + terminal log-only commit. Do not edit TASKS.md.
