# MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01 — Durable Install + Real Shortcut Launch Audit Criteria

## PASS rule

PASS only if the Desktop shortcut survives TEMP cleanup and a real launch through the actual `.lnk` is independently evidenced.

## A. Stable runtime root

Require:

- runtime/install root outside `%TEMP%`;
- recommended location: `%LOCALAPPDATA%\ScrubBots Factory Studio\runtime`;
- source revision is the exact current published Factory repository revision used by the installer;
- dirty/stale owner Desktop source checkout remains untouched except for the explicitly authorized `Release\\ScrubBots Factory Studio` deployment subtree;
- no Desktop sibling clone/worktree;
- stable runtime contains all Factory Studio runtime dependencies;
- install/repair is idempotent;
- the `Release` folder is created if absent;
- pre-existing unknown owner files under the runtime destination are preserved or cause fail-closed behavior, never silent destructive overwrite;
- owner-generated/output data is not silently destroyed.

## B. Shortcut durability

Require Desktop shortcut:

`%USERPROFILE%\Desktop\ScrubBots Factory Studio.lnk`

COM readback must prove:

- TargetPath is the intended Windows launcher host;
- launcher argument points exactly into `C:\\Users\\sekip\\Desktop\\Scrubbots - Pixel Art Generator\\Release\\ScrubBots Factory Studio`, never `%TEMP%`;
- WorkingDirectory is exactly that stable runtime root, never `%TEMP%`;
- Description remains `ScrubBots Factory Studio`;
- IconLocation is the authoritative owner ICO or byte-identical stable copy.

After the implementation TEMP worktree is removed or renamed, the shortcut must still resolve all referenced files.

## C. Real double-click-equivalent launch proof

Require a bounded smoke that executes the actual `.lnk` and proves:

- Factory Studio Godot process starts;
- process command line/project identity points to the stable runtime `level_factory`;
- no `--editor`;
- no terminal command is required by the owner;
- only the process created by the smoke is terminated after proof;
- unrelated Godot/editor processes remain untouched.

## D. Regression

Require:

- prior launcher/icon/Studio tests remain green;
- stable install/shortcut tests added;
- Godot stable-runtime headless/direct boot PASS;
- safe full repository regression green except truthful capability skips;
- compileall/diff/secret checks PASS;
- no builder edit to root `TASKS.md`;
- no builder write to `.hiveai/audits/**`.

## E. Sequencing

M17 remains blocked until this task receives independent `PASS / CLOSED`.
