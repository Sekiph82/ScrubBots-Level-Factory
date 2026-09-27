# SB-LF08-007-C001 — Owner Review / Approval Gate Before Publication — Strict Audit Criteria

Target: `SB-LF08-007`

## Accepted foundation
- SB-LFX-006 owner review queue = PASS/CLOSED.
- SB-LF08-006 accepted batch-result artifact contract is prerequisite.
- Factory QA acceptance and owner review remain separate authorities.

## Contract

Integrate accepted M08 batch entries into the existing canonical SB-LFX-006 Candidate Inbox / append-only owner-review evidence chain.

Do not create a second review database or infer owner approval from QA.

For every accepted batch entry:
- initial publication state is NEEDS_REVIEW unless a valid existing owner-review record for the exact candidate/artwork identity exists;
- latest valid append-only ACCEPT => OWNER_ACCEPTED / publication-eligible for the next handoff gate;
- latest valid REJECT => OWNER_REJECTED / publication-blocked;
- corrupt/tampered review evidence fails closed and cannot become latest truth;
- review history remains append-only and candidate/source bytes remain unchanged.

## Batch-level review view

Provide deterministic derived counts/listing:
- NEEDS_REVIEW;
- OWNER_ACCEPTED;
- OWNER_REJECTED;
- INVALID_REVIEW_EVIDENCE if present.

Review state must never change Factory accepted counts in the batch result. It only controls publication/handoff eligibility.

## Negative tests

QA ACCEPT with no owner review; review for another candidate/artwork; stale artwork hash; corrupt chain; rewritten prior review; ACCEPT then REJECT; REJECT then ACCEPT; duplicate review ID; source/candidate byte mutation attempt.

## Required gates

Focused 007 + retained SB-LFX-006/007 + M08 001/006; full retained M03–M07; full pytest/compileall/Godot/diff/protected-file gates.

## PASS rule

PASS only when batch owner-review truth is the existing append-only review authority and no candidate can reach publication handoff without a valid latest owner ACCEPT.
