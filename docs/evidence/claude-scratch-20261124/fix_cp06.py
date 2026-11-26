import re
from pathlib import Path

p = Path(r"C:\Users\sekip\Desktop\ScrubBots\tests\cp06_disabled_levels.gd")
s = p.read_text(encoding="utf-8")
s = s.replace("var _builtin_ids: Array = []\n", "var _builtin_ids: Array = []\nvar _B := 0  # builtin level count; the remote fixture levels follow it\n", 1)
old = "	for e in cat.get_entries_ordered():\n		_builtin_ids.append(e.id)\n"
assert old in s
s = s.replace(old, old + "	_B = _builtin_ids.size()\n", 1)
s = s.replace("## SB-CAMPAIGN-L31-L200: builtin levels are 1..200, so the remote fixture levels fam_l011..13 sit at 201..203.",
              "## The remote fixture levels fam_l011..13 sit right after the builtin catalog (_B + 1.._B + 3).")
STRING = re.compile(r'("(?:[^"\\]|\\.)*")')
lines = s.split("\n")
start = next(i for i, line in enumerate(lines) if "_B + 1.._B + 3" in line)


def fix_line(line: str) -> str:
    parts = STRING.split(line)
    for i in range(len(parts)):
        if i % 2 == 0:
            parts[i] = re.sub(r"\b20([1-5])\b", lambda m: "_B + %s" % m.group(1), parts[i])
        else:
            parts[i] = re.sub(r"\b20([1-5])\b", lambda m: "N+%s" % m.group(1), parts[i])
    return "".join(parts)


lines = lines[:start + 1] + [fix_line(line) for line in lines[start + 1:]]
p.write_text("\n".join(lines), encoding="utf-8")
print("ok")
