# SB-LF08-007-C001 — Implementation Prompt

Integrate M08 accepted batch entries with the already accepted SB-LFX-006 Candidate Inbox / append-only owner review authority.

Required:
- each SB-LF08-006 accepted entry derives NEEDS_REVIEW unless an exact valid existing review chain exists;
- latest valid ACCEPT => OWNER_ACCEPTED;
- latest valid REJECT => OWNER_REJECTED;
- corrupt/tampered review evidence fails closed;
- append-only review history is preserved;
- QA ACCEPT never becomes owner ACCEPT;
- owner review never changes Factory accepted counts or candidate/source bytes;
- provide deterministic batch review summary counts/listing.

Reuse the existing review record/store/validator. Do not create a parallel review database.

Do not implement Content Pipeline handoff yet. Do not edit TASKS.md or ChatGPT audits.
