# Clean Checkout Boot Contract

`level_factory/` is expected to boot from committed tracked files alone. The
minimum project descriptor and bootstrap scene are part of the repository; the
working tree must not supply hidden boot dependencies.

- The local `.godot/` directory is generated cache and is not required before
  first boot.
- Local generated output is not required.
- Local secrets or provider authentication material are not required.
- Files from a sibling or main-game repository are not required.

The canonical proof uses a newly created, isolated tracked-only snapshot of the
implementation commit. Materialize it with `git archive`, then run:

```text
godot --headless --path <TEMP_SNAPSHOT>\level_factory --editor --quit
```

A successful proof has exit code `0` and no parse, missing-resource, or
external-dependency failure. Godot may create a cache inside the disposable
snapshot during the run; that snapshot is removed afterward and is not a new
source-of-truth workspace.

The root `TASKS.md` remains the sole live task ledger. This document records a
boot contract only and is not a second tracker or acceptance authority.
