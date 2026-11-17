# P0-P S0 — baseline timings before the factory database (2026-11-17)

Source: installed Studio startup, Activity log
`data/Level Factory/Activity/pipeline-ui-20261116T204220Z-d4f83eb55443.jsonl`
(installed build with commit 03cd8ed6; data: 3053 Final PNG, 2735 status histories, 1484 READY receipts).
`elapsed_ms` is time since the startup inventory began.

| Startup stage | Ends at (ms) | Duration (s) |
|---|---:|---:|
| Release Pool status recovery (2735 histories) | 25,594 | 25.6 |
| Atlas provenance (2414 transaction records) | 27,641 | 2.0 |
| Discovery (3053 PNG listed) | 28,157 | 0.5 |
| File check (3053 PNG) | 32,047 | 3.9 |
| Final → Pending sync + READY reconcile (1484 receipts) | 301,922 | 269.9 |
| FAILED/REJECTED batch outcome reconcile | 327,750 | 25.8 |
| Finish (inventory publish) | 333,110 | 5.4 |
| **Total until buttons active** | **333,110** | **333.1** |

Run Pending Batch preparation (`png_batch._verified_ready_sources`, measured by CLAUDE on the same data
with the scratch harness used for commit ea57f002): 432 s before ea57f002, 10.1 s after (same result).

Targets for P0-P: startup < 10 s, first solve dispatched < 5 s after Run Pending Batch.
This table is re-measured after S2 and S4.
