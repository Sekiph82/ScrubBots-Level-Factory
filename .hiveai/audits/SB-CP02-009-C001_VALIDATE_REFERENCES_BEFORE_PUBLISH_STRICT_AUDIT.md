# SB-CP02-009-C001 — Validate Manifest References Before Publish

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Implementation: `6c9a0ecd22e6969ca8a5accec892a127a35038be`

## VERDICT

**PASS / CLOSED**

The pure local gate validates:
- every level's declared pack reference;
- disabled-level references;
- schedule target references;
- pack/level ownership uniqueness;
- complete explicit M12 evidence coverage;
- no undeclared/duplicate evidence;
- exact pack ID/version;
- exact final archive SHA-256;
- exact archive byte length;
- exact level membership;
- archive integrity through M12 `verify_scrubpack_build`.

Eligibility is true only when every ordered check passes.

No remote lookup/provider mutation/runtime behavior is introduced.

The CP006 mixed-case helper defect is not caused by CP009. CP009's own reference semantics are internally consistent and correctly casefold logical level identity.

`SB-CP02-009 = PASS / CLOSED`
