# M10_METRICS_REPORT

Executed deterministic owner-review evidence; all 100 logical candidates remain `PENDING_OWNER_REVIEW`.

- Attempts: 122
- Accepted: 100
- Rejected: 22 (0.180328)
- Duplicates: 0 (0.000000)

## Counts by difficulty

| Difficulty | Count |
|---|---:|
| EASY | 25 |
| HARD | 25 |
| MEDIUM | 25 |
| VERY_HARD | 25 |

## Counts by mode

| Mode | Count |
|---|---:|
| HYBRID | 40 |
| MASK | 35 |
| RULES | 25 |

## Rejection-code distribution

```json
{
  "RETRY_EXHAUSTED": 22
}
```

## Deterministic selection

`DeterministicRNG(root_seed).child('slot/{difficulty}/{slot:02d}/attempt/{attempt:02d}').next_bytes(32).hex()`

## Diversity and integrity

Comparable pairs: 80

Occupancy-mask median similarity: 0.29953423

Color-layout median similarity: 0.041827050000000005

Immutable GenerationResult.logical_grid values are copied only; no grid mutation, resize, interpolation, or resampling occurs.
