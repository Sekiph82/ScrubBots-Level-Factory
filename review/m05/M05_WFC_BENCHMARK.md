# M05 WFC 59×59 benchmark evidence

This is measured evidence only; PAG-M10 has not established a V1 performance budget.

- Python: `3.12.10`
- Platform: `Windows-11-10.0.26200-SP0`
- Exemplar: `wfc-synthetic-benchmark-10` (synthetic test-only)

| N | Output periodic | Placement | Raw windows | Transformed observations | Unique patterns | Runs | Median ms | P95 ms | Worst ms |
|---:|:---:|:---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | False | 58×58 | 384 | 384 | 21 | 3 | 337.944 | 343.11 | 343.11 |
| 2 | True | 59×59 | 384 | 384 | 21 | 3 | 316.473 | 321.625 | 321.625 |
| 3 | False | 57×57 | 384 | 384 | 32 | 3 | 595.187 | 1106.688 | 1106.688 |
| 3 | True | 59×59 | 384 | 384 | 32 | 3 | 941.887 | 999.574 | 999.574 |
