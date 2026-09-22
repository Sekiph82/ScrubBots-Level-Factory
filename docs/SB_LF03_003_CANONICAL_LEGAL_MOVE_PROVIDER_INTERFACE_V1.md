# SB-LF03-003 — Canonical Legal-Move Provider Interface

Document role: DURABLE BUILDER BOUNDARY EVIDENCE

`legal_move_provider.py` defines a versioned, immutable transport boundary for
canonical column/front decisions. `LegalMoveQuery` binds a query to the
`CompactSolverState` digest and exact authority. `LegalMoveResult` binds the
response to the query, state, provider identity, authority, capability
evidence, and deterministic ascending move order.

The Factory does not derive legal moves from slot or supply state, apply moves,
create child states, or implement gameplay transitions. The production
`CanonicalLegalMoveProvider` reports `UNAVAILABLE` until a verified canonical
headless execution path exists. It performs no source scraping and carries no
fixture moves.

Test-only providers in the focused unit suite prove structural validation,
duplicate/out-of-range rejection, zero-move availability, immutability, and
truthful unavailable behavior. An `AVAILABLE` result requires verified
authority/source-contract evidence and canonical runtime execution evidence;
zero available moves carry no solver verdict.
