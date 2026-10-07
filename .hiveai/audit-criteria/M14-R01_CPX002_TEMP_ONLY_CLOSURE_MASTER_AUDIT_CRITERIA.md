# M14-R01 — CPX-002 TEMP-Only Closure — Master Audit Criteria

PASS only if SB-CPX-002-C001-R01 independently passes its dedicated criteria and no direct regression invalidates the already closed CP03 children.

Require:
- safe sync-first evidence;
- explicit TEMP-only ScrubBots authority before every Factory/solver/replay call;
- no implicit Desktop game checkout fallback;
- fresh authentic current-main Godot replay PASS;
- unchanged CPX-002 receipt semantics or explicit re-audit of any downstream child whose semantic dependency changed;
- focused/cumulative/unfiltered regressions green;
- separate implementation/log publication if implementation changes;
- clean final 0/0 parity.

If R01 passes without CPX-002 receipt-semantic changes, CP03-008..012 remain closed and M14 may receive final PASS/CLOSED re-audit.
