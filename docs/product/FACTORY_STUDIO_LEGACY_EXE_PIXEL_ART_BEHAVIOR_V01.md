# Factory Studio Legacy EXE Pixel-Art Behavior V01

Status: VERIFIED SOURCE-BEHAVIOR REFERENCE
Date: 2026-10-09

Source inspected:
owner-supplied `ScrubBots Level Factory(3).exe`

Packaging:
PyInstaller, Python 3.12.

The embedded application contains `pixelart_app.py` and `art_producer.py`.

## Reusable behavior verified from embedded code objects

### Claude discovery

`find_claude()` searches the normal `claude` command and `~/.local/bin/claude.exe`.

### Claude drawing

`claude_draw(prompt, size, out, notes, fill_bg, ref)`:

- states that Claude Code subscription login draws the sprite;
- runs Claude Code as a subprocess;
- supplies a pixel-art drawing instruction;
- saves the produced native-size image as `sprite.png`;
- supports optional reference, notes and background fill;
- has explicit usage/error handling;
- contains explicit `ANTHROPIC_API_KEY` handling and must not be changed into a paid API fallback for the owner workflow.

### Single UI

Legacy Single mode exposes:

- prompt;
- size;
- drawing method/provider;
- optional notes;
- optional reference;
- Generate.

### Production CSV / resumability

Legacy Production mode exposes:

- CSV selection;
- persistent jobs;
- default size;
- Level Factory import option;
- background/VOID intent;
- Start / Continue;
- Pause;
- Resume;
- Stop;
- Redo selected row;
- progress and per-row state.

`ArtJob.open_or_create()` keys the job by CSV SHA-256 and persists `job.json`.

`read_rows()` accepts:

- plain `prompt`;
- `prompt;size`;
- named columns including aliases for prompt, width/size, height, enabled and reference.

`ArtProducer.run()` persists row state and uses:

`PENDING -> DRAWN -> VALIDATED -> IMPORTED`

with `FAILED` for real row failures and `LIMIT` for Claude usage-limit pause.

Its embedded limit message explicitly says the Claude usage limit was reached and the job is paused until Resume after reset.

On restart/resume each row continues from its first incomplete step. Missing/corrupt artifacts are re-drawn, while valid completed artifacts are retained.

## Porting rule

Port this job/state/resume architecture into the new Factory Studio.

Do not repeatedly reverse-engineer the EXE at runtime.

Do not discard the already-implemented three-master UI.

For `ALPIX (Claude)`, retain the Claude subscription + persistent ArtJob/ArtProducer architecture and replace/extend the drawing action so Claude invokes the locally installed Alpix plugin/MCP.
