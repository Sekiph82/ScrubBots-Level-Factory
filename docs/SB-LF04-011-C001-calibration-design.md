# SB-LF04-011-C001 — Future Calibration Design

Calibration is `DISABLED_UNTIL_POLICY_APPROVED`. The current production path performs no player-data collection, analytics upload, HTTP request, SDK integration, identifier generation, profiling, or runtime calibration.

The future import boundary accepts only deterministic aggregate records: Challenge Score policy version, an approved anonymous cohort token, completion/failure aggregates, move-count aggregates, and sample counts meeting the declared minimum. Names, email addresses, device/account identifiers, IP addresses, raw event streams, and free-form PII are prohibited by the closed schema.

Any future calibration requires explicit privacy, product, security, retention, consent, and governance approval. It must introduce a new policy version and may not silently alter Difficulty V1.
