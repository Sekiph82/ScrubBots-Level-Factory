# SB-LFX-015-C001 — Session Recovery / Autosave — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 1
- MAJOR: 4
- MINOR: 0
- NOTE: 0

## Audited chain

- Start: `70d441e39d7f3f39b1307b5df412bd50c7660617`
- Implementation: `a6c65bd69213a9a52434732c7f0cedef9b3de8ad`
- Task-final log-only: `d92a5a236dfb36b54e5513572a1b3a193d22179e`

## Accepted implementation semantics

The session record is versioned, stored separately from canonical source/candidate artifacts, and top-level keys whose names contain secret/token/password/api_key are omitted. No TASKS mutation or provider call is introduced.

## BLOCKER-001 — nested secrets can be persisted

`save_session()` scrubs only top-level keys:

`{key: value for key, value in state.items() if ...}`

Nested structures are copied recursively through JSON serialization without secret-field filtering.

For example a state such as:

`{"provider": {"api_key": "...", "token": "..."}}`

would persist those secrets.

The criteria explicitly make persisted secrets/provider tokens a blocker.

### Required remediation

Use a recursive allowlist-based session schema rather than generic secret-name filtering. Persist only explicitly approved continuity fields and bounded draft values. Reject unknown nested structures rather than attempting heuristic secret scrubbing.

## MAJOR-001 — canonical references are not revalidated on restore

`restore_session()` checks only:
- session schema;
- state is a mapping.

It then returns:

`validated_references: true`

without resolving or validating any source/candidate/batch/pipeline/revision/retry reference.

This is a false evidence claim.

### Required remediation

Define typed allowed reference fields and revalidate each against its canonical reader/validator. Missing, corrupt, mismatched or stale references must be reported individually and must never be recreated from session data.

## MAJOR-002 — recovery classification is fabricated

Every successfully parsed session is returned as:

`recovery = RESUMED`

There is no determination of whether the referenced work is:
- RESUMED;
- RETRIED;
- NEW;
- NOT_RESUMABLE;
- NEEDS_OPERATOR_ACTION.

There is also no logic proving that already successful stages will be reused rather than rerun.

### Required remediation

Derive recovery disposition from verified durable job/stage state and the actual resumability contract. Never label a context RESUMED merely because a session JSON parsed.

## MAJOR-003 — no actual autosave/recovery workflow in Studio

`FactoryStudioSession` is informational only:
- no save/autosave trigger;
- no session selection;
- no restore action;
- no recovered context;
- no status per canonical reference.

Its snapshot always reports AVAILABLE.

### Required remediation

Wire a bounded real Studio session controller to save/restore approved continuity state and display explicit recovery classifications/reasons.

## MAJOR-004 — required interruption/restart integration is absent

The task requires a real interruption/restart scenario using multi-stage or batch work and proof that:
- completed stages remain unchanged;
- eligible work resumes;
- duplicate source/candidate creation does not occur;
- corrupt session fails closed;
- missing canonical references are reported;
- secrets are absent.

Only a small Python serialization test exists. No real Godot restart/interruption integration was committed.

## Disposition

`SB-LFX-015` remains open pending remediation and re-audit.
