import re
from pathlib import Path

p = Path(r"C:\Users\sekip\Desktop\ScrubBots\tests\remote_content_family_fixture.gd")
s = p.read_text(encoding="utf-8")
a = s.index("func _run() -> void:")
b = s.index("\nfunc ", a + 10)
body = s[a:b]
old = '''	print("[f01 builtin 1-200 in res://]")
	var cat := LevelCatalog.new()
	_ok(cat.load_manifest().ok and cat.size() == 200, "builtin production catalog = 200 levels")
	var builtin := cat.get_entries_ordered()
	_ok(builtin.map(func(e): return e.order) == range(1, 201) and builtin.all(func(e): return String(e.level_path).begins_with("res://")), "orders 1..200, all res://")'''
new = '''	var cat := LevelCatalog.new()
	_ok(cat.load_manifest().ok and cat.size() >= 200, "builtin production catalog has at least the 200 campaign levels")
	var nb := cat.size()
	print("[f01 builtin 1-%d in res://]" % nb)
	var builtin := cat.get_entries_ordered()
	var last_id := String(builtin.back().id)
	_ok(builtin.map(func(e): return e.order) == range(1, nb + 1) and builtin.all(func(e): return String(e.level_path).begins_with("res://")), "orders 1..N contiguous, all res://")'''
assert old in body
body = body.replace(old, new)
old = '_ok(_resolve(app, 200)["entry_id"] == "level_200_sea_wyrm", "frontier 200 -> builtin")'
assert old in body
body = body.replace(old, '_ok(_resolve(app, nb)["entry_id"] == last_id, "last builtin frontier -> builtin")')

STRING = re.compile(r'("(?:[^"\\]|\\.)*")')


def fix_line(line: str) -> str:
    if "tampered[" in line:
        return line
    parts = STRING.split(line)
    for i in range(len(parts)):
        if i % 2 == 0:
            parts[i] = re.sub(r"\b20([1-4])\b", lambda m: "nb + %s" % m.group(1), parts[i])
        else:
            parts[i] = re.sub(r"\b20([1-4])\b", lambda m: "N+%s" % m.group(1), parts[i])
    return "".join(parts)


body = "\n".join(fix_line(line) for line in body.split("\n"))
s = s[:a] + body + s[b:]
s = s.replace('"ProductionGameplayHost.build() for remote level 201 (%s)"', '"ProductionGameplayHost.build() for the first remote level (%s)"')
p.write_text(s, encoding="utf-8")
print("ok")
