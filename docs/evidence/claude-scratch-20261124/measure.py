import sqlite3, json, datetime as dt, subprocess
c = sqlite3.connect("file:data/Level Factory/factory.db?mode=ro", uri=True)
now = dt.datetime.now(dt.timezone.utc)
since = "2026-11-23T10:21"
ev = []
for t, in c.execute("SELECT event_json FROM status_events WHERE sequence > 1"):
    e = json.loads(t)
    if e.get("created_at", "") >= since and e.get("status") in ("READY", "FAILED", "REJECTED"):
        ev.append(e["created_at"])
ev.sort()
print("now", now.isoformat()[:19], "terminal since relaunch", len(ev), "first", ev[:1], "last", ev[-1:])
if len(ev) > 1:
    a = dt.datetime.fromisoformat(ev[0]); b = dt.datetime.fromisoformat(ev[-1])
    print("rate/h", round((len(ev) - 1) / ((b - a).total_seconds() / 3600), 1))
print(dict(c.execute("SELECT status, count(*) FROM status GROUP BY status").fetchall()))
print(subprocess.run(["powershell", "-c", r"$os=Get-CimInstance Win32_OperatingSystem; 'free GB ' + [math]::Round($os.FreePhysicalMemory/1MB,1); (Get-Counter '\Memory\Pages/sec','\Memory\Committed Bytes' -SampleInterval 3 -MaxSamples 1).CounterSamples | % { $_.Path + ' ' + [int64]$_.CookedValue }; (Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 3 -MaxSamples 1).CounterSamples.CookedValue; Get-CimInstance Win32_Process | ?{ $_$_.Name -eq 'python.exe' -and $_.CommandLine -like '*spawn_main*' } | % { $p=Get-Process -Id $_.ProcessId; 'child ' + $_.ProcessId + ' privMB ' + [int]($p.PrivateMemorySize64/1MB) }"], capture_output=True, text=True).stdout)
