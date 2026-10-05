# SB-CPX-001-C001 — Solver-Proven Supply Identity Pack Binding

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Implementation: `43be43fa6bfdf5ef92a6e39d05b8758449b2e8f6`

## VERDICT

**CHANGES_REQUIRED / R01**

Most cryptographic/structural binding is correct, but current owner-review authority is not revalidated at final pack-emission time.

## PASS surfaces

The implementation correctly:
- does not use legacy `solver_evidence.py` as production authority;
- adds identity at the canonical READY solver-result boundary;
- binds exact LevelData bytes/SHA-256;
- binds exact supply-plan bytes/SHA-256;
- binds exact FIFO columns, batch IDs, CIDs and robot counts;
- binds columnCount, preview depth and maxRobotsPerBatch;
- binds canonical initial-state digest;
- binds canonical solver-result/evidence digest;
- requires SOLVED/WIN, replay solved with zero active, color conservation PASS and load check READY;
- binds Scrubbots repository/branch/git-head authority present in the canonical run;
- prefers Release Pool when available;
- validates Release Pool digest and exact pipeline identity;
- rejects level/supply/FIFO/count/CID/state/evidence byte drift;
- keeps CPX-002 current-main promotion replay out of M12.

## F01 — BLOCKER — stale owner review can race after proof resolution

`current_solver_proof_for_candidate(candidate_id)` correctly reads the current latest review and refuses to issue a new accepted-READY proof after owner REJECT.

However, `build_solver_proven_scrubpack(... proofs=...)` accepts a previously resolved `ScrubpackSolverProof` without re-reading current Factory review authority.

Race:

1. Owner review is ACCEPT.
2. Caller resolves a valid `ScrubpackSolverProof`.
3. Owner later records REJECT for the same candidate.
4. Caller still passes the old proof to `build_solver_proven_scrubpack()`.
5. `_proof_for_level()` validates only the frozen proof/pipeline bytes and review-id prefix. It does not verify that the proof's review ID is still the current latest ACCEPT review.
6. Pack emission can therefore proceed from stale owner authorization.

The focused test only proves that **new proof resolution** fails after REJECT:
`current_solver_proof_for_candidate(candidate_id)`

It does not attempt to build with the already-resolved old proof after the REJECT.

This violates the prompt's explicit requirement:
> stale READY/review/pipeline identity fails

and the audit criterion's requirement to use **current production authority**.

## Required remediation

At final solver-proven pack build, revalidate each proof source against current canonical Factory authority.

For accepted-READY fallback, require:
- candidate still exists;
- current latest review is ACCEPT;
- current review ID exactly equals proof review ID;
- current latest READY pipeline identity exactly equals proof pipeline run ID;
- exact current pipeline bytes/digest still match;
- exact current level/supply files still match.

For Release Pool source, require the entry is still present in the current `release_entries()` projection and its entry digest/pipeline identity exactly match the proof.

Then rerun the existing cryptographic drift suite plus a real stale-race regression:
- resolve proof while ACCEPT;
- change latest owner review to REJECT or a different ACCEPT identity;
- attempt build with the old proof;
- final pack emission must fail.

Do not reopen SB-CP01-001..010 unless regression evidence shows breakage.

## FINAL

`SB-CPX-001 = CHANGES_REQUIRED / R01`
