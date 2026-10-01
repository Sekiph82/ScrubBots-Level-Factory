# SB-LF08-001-C001-R01 — Strict Audit Criteria

PASS requires all original M08-001 criteria plus fail-closed restore/resume enforcement of exact attempt plan digests, contiguous prefixes, lane budgets, requested-count caps and recomputed history digest. A forged manifest with extra accepted entries, extra attempts, missing/wrong plan identity or arbitrary history digest must be rejected. The final suite must include these tests and preserve accepted M08-002/003/004/005/010 behavior.
