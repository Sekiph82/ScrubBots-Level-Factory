"""Read-only cost of the READY-finish lookups, old vs new. One scenario per process.

Usage: python measure_finish.py old|new|verify
  old    = list_candidates() lookup + full pipeline scan (what 783497dc and before ran)
  new    = find_candidate() lookup, no scan (08381ed7)
  verify = release_entries(candidate, verify=True), which both versions still run twice
"""
import sqlite3
import sys
import time

sys.path.insert(0, "src")
import psutil

me = psutil.Process()
peak = [0]


def mem() -> int:
    value = int(me.memory_info().private / 2**20)
    peak[0] = max(peak[0], value)
    return value


from scrubbots_pixel_factory import studio_extensions as s

s._save_candidate_disk_cache = lambda *a, **k: None  # read-only: never write the cache file
cid = sqlite3.connect("file:data/Level Factory/factory.db?mode=ro", uri=True).execute(
    "SELECT candidate_id FROM release_entries ORDER BY entry_name DESC LIMIT 1").fetchone()[0]
mode = sys.argv[1]
print(f"{mode}: start {mem()} MB", flush=True)
t0 = time.time()
if mode == "old":
    t = time.time()
    cand = next((i for i in s.list_candidates() if i.get("candidate_id") == cid), None)
    print(f"  list_candidates lookup {time.time() - t:.1f}s, {mem()} MB, found={cand is not None}", flush=True)
    t = time.time()
    runs = 0
    for path in s._pipeline_paths():
        try:
            value = s._read_json(path)
        except s.StudioExtensionError:
            continue
        mem()
        if value.get("candidate_id") == cid and value.get("disposition") == "READY":
            runs += 1
    print(f"  full pipeline scan {time.time() - t:.1f}s, {mem()} MB, runs={runs}", flush=True)
elif mode == "new":
    t = time.time()
    cand = s.find_candidate(cid)
    print(f"  find_candidate lookup {time.time() - t:.1f}s, {mem()} MB, found={cand is not None}", flush=True)
else:
    from scrubbots_pixel_factory.supply_pipeline.release_pool import release_entries
    for n in (1, 2):
        t = time.time()
        rows = release_entries(cid, verify=True)
        print(f"  release_entries verify call {n}: {time.time() - t:.1f}s, {mem()} MB, rows={len(rows)}", flush=True)
print(f"{mode}: total {time.time() - t0:.1f}s, peak {peak[0]} MB", flush=True)
