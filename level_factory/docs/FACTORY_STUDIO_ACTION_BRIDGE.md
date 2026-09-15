# Factory Studio action bridge

The Generate and Reproduce buttons are presentation controls over the
canonical Python Factory Core. The Godot adapter discovers a local Python
executable, invokes the committed `scripts/factory_core_launcher.py` with a
discrete executable-and-argument vector, captures the process result, and
renders only evidence returned by the Core. The optional
`SCRUBBOTS_FACTORY_PYTHON` environment setting can name a local Python
executable; its value is never displayed or written to the builder log. When
it is absent, the adapter probes bounded `python`/`py` names and the local
`PATH` entries.

Generate forwards the draft difficulty, independent width and height, seed,
and mode. The candidate presentation label is never forwarded as a canonical
candidate ID. Output is restricted to `level_factory/output/`. Reproduce uses
the most recent successful Generate `metadata.json` and writes to a separate
reproduction output root so the original bundle is not overwritten.

Solve, Validate, and Analyze remain visible but disabled with explicit
unavailability reasons. They are not simulated by WFC, guessed from UI
state, or backed by provider/network calls.
