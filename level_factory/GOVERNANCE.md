# Level Factory Project-Local Governance

This document defines ownership boundaries for `level_factory/` only. It
defers to the root `GOVERNANCE.md` and root `TASKS.md` for task status,
milestone/sprint/cycle acceptance, audit authority, and builder/auditor
separation.

ChatGPT remains the independent auditor and tracker owner. Codex remains the
implementation builder only; builder evidence does not grant acceptance.

`level_factory/` may contain Godot-facing workspace, presentation, and
integration surfaces. Canonical Factory algorithms remain in their accepted
implementation until a later audited task explicitly migrates them. The
main-game runtime code is not owned here; it belongs to the separately
authorized game repository boundary.

This project-local document does not create a competing H!veAI control plane,
tracker, event ledger, prompt index, task denominator, or acceptance state.
Broader coordination and governance normalization remains the separately
authorized `SB-LF00-007` scope. Unrelated root governance drift is not repaired
here.
