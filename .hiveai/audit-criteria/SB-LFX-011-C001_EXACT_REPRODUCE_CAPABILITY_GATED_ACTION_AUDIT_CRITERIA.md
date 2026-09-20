# SB-LFX-011-C001 — Exact Reproduce Capability-Gated Action — Strict Audit Criteria

Target:
`SB-LFX-011 — Expose Exact Reproduce action only where recorded canonical identities and the underlying path support truthful reproducibility. [EXTENSION]`

## Principle

“Exact Reproduce” is a capability claim. It may be enabled only when the underlying canonical path can truthfully recreate the same artifact under recorded identities/config/version.

## BLOCKERS

FAIL if:
- provider/manual/imported content is claimed exactly reproducible without a real deterministic path;
- immutable source retrieval is mislabeled as regeneration;
- current draft/preset values replace recorded canonical reproduction inputs;
- reproduction MATCH is asserted without canonical identity/byte checks;
- an unsupported/stale candidate gets an enabled Exact Reproduce action;
- reproduced output silently replaces the source/candidate;
- TASKS is edited.

## Capability classification

For each selected candidate/source expose a derived capability:
- EXACT_REPRODUCIBLE;
- SOURCE_RETRIEVABLE_ONLY;
- NOT_REPRODUCIBLE;
- STALE/INVALID.

The reason and authoritative record must be visible.

Existing deterministic Factory Core Generate/Reproduce must be reused for procedural candidates with recorded metadata.

OWNER_UPLOAD may expose exact immutable source retrieval/restore separately, but must not call that “regeneration”.

External semantic/provider candidates are NOT_REPRODUCIBLE unless a provider path has independently proven deterministic exact replay.

## Reproduction evidence

A successful Exact Reproduce must:
- use recorded metadata/source/config/version identities;
- invoke canonical reproduction;
- verify MATCH using canonical artifact identities/bytes;
- create a separate reproduced output;
- preserve original source/candidate bytes;
- record reproduction evidence linked to source candidate.

## UI

Expose action only when capability permits it. Disabled states must explain why.

## Real integration

Prove:
- deterministic generated candidate enables and produces canonical MATCH;
- changing current draft/preset does not alter replay;
- OWNER_UPLOAD is source-retrievable but not falsely regenerated;
- unsupported/provider-like candidate remains disabled;
- tampered/stale reproduction metadata disables/fails closed;
- original bytes remain unchanged.

## PASS rule

PASS when the UI capability and action exactly match real reproducibility, with canonical replay authority and no false provider/manual claims.
