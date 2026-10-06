# SB-CP03-010-C001 - Audit Criteria

PASS only if production manifest writes are exact expected-state compare-and-swap operations, stale/racing/mismatched writes leave prior production untouched, blind last-write-wins is impossible, and exact idempotent repeats are accepted only with full byte/hash/version/ledger identity.