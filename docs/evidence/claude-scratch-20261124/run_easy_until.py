"""Run the MEDIUM->EASY variant tool; stop it once the pool holds TARGET EASY (<49) levels."""
import sqlite3
import subprocess
import sys
import time

REPO = r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator"
DB = REPO + r"\data\Level Factory\factory.db"
TARGET = 3750


def easy_count() -> int:
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=30)
    try:
        rows = conn.execute(
            "SELECT candidate_id, CAST(json_extract(entry_json,'$.challenge_score') AS REAL) FROM release_entries"
            " WHERE folder='Ready' ORDER BY candidate_id, json_extract(entry_json,'$.pipeline.created_at'), pipeline_run_id").fetchall()
    finally:
        conn.close()
    newest = {cid: score for cid, score in rows}  # last row per candidate = newest run
    return sum(1 for s in newest.values() if s is not None and s < 49), len(newest)


proc = subprocess.Popen([sys.executable, "-B", "scripts/easy_difficulty_variants.py", "--min", "49", "--max", "53.7",
                         "--keep-below", "49", "--limit", "5000", "--workers", "10", "--results", "medium_to_easy49.jsonl"],
                        cwd=REPO)
print("start", easy_count(), flush=True)
while proc.poll() is None:
    time.sleep(300)
    try:
        easy, total = easy_count()
    except sqlite3.Error as error:
        print("db busy", error, flush=True)
        continue
    print(time.strftime("%H:%M"), "EASY", easy, "of", total, flush=True)
    if easy >= TARGET:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)])
        print("TARGET REACHED", easy, flush=True)
        break
print("exit", proc.poll(), easy_count(), flush=True)
