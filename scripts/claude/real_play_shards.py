"""Run tools/real_play_verify.gd --regen for levels FIRST..LAST in N parallel project copies.

Each shard plays its own interleaved subset in its own copy (no shared writes). Results:
<work>/shard-<i>/  (provenance + possibly regenerated plan files) and <work>/shard-<i>.log.
Usage: python real_play_shards.py <base_project> <work> <first> <last> <shards>
"""
import subprocess
import sys
from pathlib import Path

base, work = Path(sys.argv[1]), Path(sys.argv[2])
first, last, shards = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
GODOT = r"C:\Users\sekip\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_Microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.7.2-stable_win64_console.exe"
work.mkdir(parents=True, exist_ok=True)
procs = []
for i in range(shards):
    copy = work / f"shard-{i}"
    if not copy.exists():
        subprocess.run(["robocopy", str(base), str(copy), "/E", "/XD", ".git", "validate_logs", "/NFL", "/NDL", "/NJH", "/NJS", "/NP", "/MT:8"], check=False)
    levels = ",".join(str(n) for n in range(first + i, last + 1, shards))
    log = open(work / f"shard-{i}.log", "w", encoding="utf-8")
    procs.append((subprocess.Popen([GODOT, "--headless", "--path", str(copy), "-s", "res://tools/real_play_verify.gd", "--", "--levels", levels, "--regen"],
                                   stdout=log, stderr=subprocess.STDOUT), log))
    print("shard", i, "started", flush=True)
codes = []
for proc, log in procs:
    codes.append(proc.wait())
    log.close()
print("exit codes", codes, flush=True)
for i in range(shards):
    text = (work / f"shard-{i}.log").read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith(("REAL PLAY VERIFY", "UNWINNABLE", "SEARCH")):
            print(f"shard {i}: {line}", flush=True)
