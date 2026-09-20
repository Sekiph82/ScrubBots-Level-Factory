# SB-LFX-011-C001 — Exact Reproduce Action — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 3
- MINOR: 0
- NOTE: 0

## Audited chain

- Start: `f5e10b019b55f4ca443c206fd25c2ac9f60c3b58`
- Implementation: `bec72af1b3545a44d74783711b1e480c4106b168`
- Task-final log-only: `0da0d10bef76909ddd3cf0b0f544d7aae29e7b9d`

## Accepted implementation semantics

The capability evaluator distinguishes canonical-looking deterministic candidates from stale/unavailable records and does not mislabel OWNER_UPLOAD source retrieval as regeneration. The UI itself is non-mutating.

## MAJOR-001 — Exact Reproduce action is not implemented

The product surface contains only a **Check capability** button.

The launcher exposes only `reproduce-capability` for this extension. There is no LFX-011 exact-reproduce operation that:
- invokes canonical Factory Core Reproduce;
- uses recorded candidate metadata;
- produces separate output;
- verifies canonical MATCH;
- returns reproduction evidence.

This is the core capability requested by the task.

### Required remediation

Add an enabled action only for `EXACT_REPRODUCIBLE` records and route it through the already accepted canonical Reproduce path. Preserve original bytes and create separate governed reproduction output/evidence.

## MAJOR-002 — exact capability is classified too coarsely

`reproduce_capability()` treats a candidate as EXACT_REPRODUCIBLE primarily from its `origin` string being one of MASK/RULES/HYBRID/AUTO/WFC/PROCEDURAL.

The criteria require capability to be based on actual recorded canonical identities/config/version and underlying replay support.

### Required remediation

Validate the exact recorded metadata/replay contract before enabling the action. Unsupported/tampered/version-incompatible records must become STALE/INVALID or NOT_REPRODUCIBLE.

## MAJOR-003 — required real integration matrix is absent

No real Godot Exact Reproduce integration exists. The focused unit test checks only that one generated candidate receives the capability label.

Missing required proof:
- actual canonical MATCH;
- current draft/preset divergence does not affect replay;
- OWNER_UPLOAD distinction;
- unsupported/provider path disabled;
- tampered metadata fail-closed;
- original bytes unchanged.

## Disposition

`SB-LFX-011` remains open pending remediation and re-audit.
