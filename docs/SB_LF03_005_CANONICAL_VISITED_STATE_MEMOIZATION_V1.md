# SB-LF03-005 — Canonical Visited-State Memoization / Hashing

Document role: DURABLE BUILDER BOUNDARY EVIDENCE

`visited_memoization.py` accepts only an opaque canonical semantic key returned
by a versioned provider bound to the exact gameplay authority and source
contract. `DeterministicVisitedMemo` records first visits and memo hits in a
stable set, with counts kept separate and no mutation of compact state.

The SB-LF03-002 Factory envelope digest is request/state identity only. It is
explicitly rejected when supplied as the canonical semantic key. The
production key provider remains `UNAVAILABLE` until canonical runtime supplies
the key; fixture providers in the unit suite are test-only and are not
exported as gameplay authority.
