# SB-LF07-001-C001-R01 — Strict Re-Audit
Document role: INDEPENDENT CHATGPT STRICT RE-AUDIT

## Result
CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED

## Evidence reviewed
- C001 frozen audit
- R01 builder log
- R01 implementation commit `270f934878b0bd13b43801303fa60a2201da304c`
- current `src/scrubbots_pixel_factory/mutation.py`
- current R01 authority tests
- Scrubbots commit chronology during R01

## Closed findings
- The default/base registry is now empty and can execute with no concrete operators.
- Hard-coded historical `CANONICAL_GAMEPLAY_SHA` is no longer treated as current truth.
- A read-only injected current-main/source-blob resolver exists and can return AVAILABLE/UNAVAILABLE/DRIFT/ERROR.
- Parent/request/result identity determinism and immutability remain intact.

## Remaining frozen findings
1. **The SB-LF07-001 layer is still not separated from later-task semantics.** The same public `mutation.py` module and `__all__` still own/export concrete hardening/easing transforms, M03/M04/M05 evidence models, targeting, attempt budgeting, efficiency comparison, and OWNER_UPLOAD helpers. R01 changed the default registry but did not create the required base-substrate vs concrete-policy separation.
2. R01 task001 changed tests across 002..010 in the same implementation commit, continuing the cross-task scope coupling that the C001 audit froze.
3. The resolver abstraction is acceptable, but the R01 support path hard-codes a one-time `CURRENT_MAIN_SHA`; later tasks reused that value rather than resolving current main per authority-dependent task.

## R02 requirement
Physically/API-separate the SB-LF07-001 base substrate from concrete M07 services. The base module/public surface may contain only immutable candidate/request/result/lineage/registry/authority-resolution interfaces. Move operator policy, evidence validation, targeting, attempts, efficiency and source protection to task-owned modules/services. Tests for 001 must not import or depend on future-task implementations. Preserve the resolver seam.

## Disposition
R01 does not close SB-LF07-001.