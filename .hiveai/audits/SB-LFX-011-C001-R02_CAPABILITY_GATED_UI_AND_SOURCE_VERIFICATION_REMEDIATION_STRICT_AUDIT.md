# SB-LFX-011-C001-R02 — Capability-Gated UI + Source Verification Remediation — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0

## Material closure

R02 closes the prior UI/capability blockers:
- Exact Reproduce is disabled by default;
- only a fresh EXACT_REPRODUCIBLE capability for the current identity enables it;
- identity edits invalidate the capability;
- verified OWNER_UPLOAD uses the canonical source verifier;
- nonexistent OWNER_UPLOAD no longer becomes SOURCE_RETRIEVABLE_ONLY;
- unsupported/stale records do not become exact-reproducible.

## MAJOR-001 — required draft/preset divergence and real unsupported-record matrix is still incomplete

The authoritative R02 prompt requires the real Godot integration to materially change current Studio draft/preset values before Exact Reproduce and prove replay still MATCHes the recorded candidate.

The R02 integration patch does not perform that divergence. It replays the generated candidate without mutating current draft/preset state.

The unsupported case is also the literal ID `unsupported-provider-record`, not a real canonical unsupported/non-replayable record. This does not prove capability behavior against a durable unsupported record.

### Required follow-up

Extend the real integration to:
1. Generate a deterministic candidate.
2. Materially change current draft controls and/or an applied preset.
3. Invoke the UI-gated Exact Reproduce path and prove MATCH/byte identity still comes only from recorded metadata.
4. Create or load a real canonical non-replayable record and prove capability remains disabled with the visible reason.

## Disposition

`SB-LFX-011` remains open for R03.
