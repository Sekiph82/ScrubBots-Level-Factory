# SB-CP01-001-C001 — .scrubpack V1 Spec

Document role: CHATGPT INDEPENDENT STRICT AUDIT

## VERDICT

**PASS / CLOSED**

Implementation commits:
- `af03ac84a6c040e47e9610a306225d8493935352`
- `f20375e3be147302a2ac654916ba66601bd3792d`
- `72a5107b7fb8ef95d699320439274097bbea8c8b`
- `e59e1bf44ee8d216068e834df902bde163e1029c`

The V1 spec defines a fixed ZIP-based declarative layout with:
- `.scrubpack` extension;
- `pack.json`;
- one fixed LevelData / supply-plan / metadata triplet per level;
- path-safe ASCII IDs;
- no traversal, absolute paths, duplicate/case-colliding names, scripts, scenes/resources, shaders, plugins, binaries, symlinks or executable entries;
- machine-readable schema plus durable documentation.

M11 declarative-only rules remain authoritative. No runtime/provider/network behavior was added.

Builder evidence:
- focused: 28 passed;
- cumulative: 191 passed;
- governance: 13 passed;
- full pytest: 1360 passed, 3 documented skips;
- compileall/schema/diff check PASS.

No tracker/audit mutation by Codex.

`SB-CP01-001 = PASS / CLOSED`
