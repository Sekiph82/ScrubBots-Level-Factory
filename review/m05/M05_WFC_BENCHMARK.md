# M05 WFC 59×59 benchmark evidence

This is measured evidence only; PAG-M10 has not established a V1 performance budget.

- Python: `3.12.10`
- Platform: `Windows-11-10.0.26200-SP0`
- Exemplar: `wfc-synthetic-benchmark-10` (synthetic test-only)

| N | Output periodic | Placement | Unique patterns | Runs | Median ms | P95 ms | Worst ms |
|---:|:---:|:---:|---:|---:|---:|---:|---:|
| 2 | False | 58×58 | 21 | 3 | 385.928 | 431.622 | 431.622 |
| 2 | True | 59×59 | 21 | 3 | 366.673 | 370.625 | 370.625 |
| 3 | False | 57×57 | 32 | 3 | 540.377 | 571.877 | 571.877 |
| 3 | True | 59×59 | 32 | 3 | 481.873 | 533.067 | 533.067 |
