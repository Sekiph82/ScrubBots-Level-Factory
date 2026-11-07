"""Explain saved 070/090 PNG batch failures without editing owner data.

Read-only: inspects current and historical SHA-sealed sequential PNG batch jobs
and their exact canonical pipeline evidence. Does not run/retry solver, Godot,
providers, R2, or filesystem cleanup.

Run from the canonical project root with Python, no args.
"""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "level_factory" / "output" / "studio-extensions" / "png-batches" / "jobs"
PIPELINES = ROOT / "level_factory" / "output" / "studio-extensions" / "pipelines"
NAMES = ("070", "090")
MAX_JOBS = 300
MAX_BYTES = 1024 * 1024


def _safe_json(file: Path, expected_root: Path) -> dict:
    if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(expected_root.resolve()):
        raise ValueError("Unsafe or unavailable evidence file")
    if file.stat().st_size > MAX_BYTES:
        raise ValueError("Unexpectedly large evidence file")
    obj = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("Evidence is not a JSON object")
    return obj


def _canonical(obj: dict) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _job_state_is_valid(obj: dict) -> bool:
    if obj.get("schema") != "scrubbots-studio-png-sequential-batch" or obj.get("version") != 1:
        return False
    unsigned = dict(obj)
    stated = unsigned.pop("state_digest", None)
    return isinstance(stated, str) and sha256(_canonical(unsigned)).hexdigest() == stated


def _name_match(item: dict) -> str | None:
    for key in ("original_filename", "display_name"):
        name = Path(str(item.get(key, ""))).name.lower()
        for n in NAMES:
            if re.match(r"^0*" + str(int(n)) + r"(?:[_. -]|$)", name):
                return n
    return None


def _explain(reason: str) -> str:
    r = reason.upper()
    if "READY_POOL_ENTRY_FAILED" in r:
        if "REAL_PLAY_V1 LOST" in r:
            return "Solver buldu ve replay WIN gördü, ama gerçek oyun oynatımında tık sırası kaybetti veya tıkandı. Release Pool bu yüzden reddetti."
        if "REAL_PLAY_V1 WON_CANONICAL_ONLY" in r:
            return "Oyun yalnızca bir zamanlama hızında kazanıldı; 1/30, 1/60, 1/120 koşullarının hepsinde kanıt yok."
        if "REAL_PLAY_V1 SEARCH_EXHAUSTED" in r:
            return "Gerçek oyun için denenen tıklama sıralarında dayanıklı kazanma bulunamadı."
        if "REAL_PLAY_V1 SEARCH_BUDGET" in r:
            return "Alternatif oyun sırası aramasının güvenli bütçesi doldu; kazanma doğrulanamadı."
        if "TIMED OUT" in r or "TIMEOUT" in r:
            return "Gerçek oyun veya Release Pool doğrulaması süre sınırına takıldı."
        return "Asıl çözüm/QA başarılı olabilir, ancak Release Pool'un ek gerçek-oyun/kanıt/kimlik doğrulaması geçmedi. Ayrıntı için aşağıdaki ham gerekçeye bak."
    if "SOURCE_REVALIDATION" in r or "IDENTITY" in r or "SHA" in r:
        return "Kaynak PNG veya kanıt kimliği/hash eşleşmesi doğrulanamadı; solver başarısı tek başına yeterli değil."
    if "TIMEOUT" in r or "BUDGET" in r:
        return "Bir çözüm/doğrulama süre veya arama bütçesi aşıldı."
    if r in {"UNAVAILABLE", "NOT_AVAILABLE", "CANONICAL_READY_PROOF_MISSING"}:
        return "Kanonik READY kanıtlarının tamamı bulunamadı; eksik doğrulama yüzünden güvenli biçimde FAILED kaldı."
    return "Kesin teknik gerekçe alttaki reason alanında; ek kanıt olmadan neden uydurulmamalı."


def main() -> int:
    if not JOBS.is_dir():
        print("NO_BATCH_JOB_DIR: saved batch evidence is not available at the canonical root.")
        return 2
    paths = list(JOBS.glob("png-batch-*.json"))
    if len(paths) > MAX_JOBS:
        print(f"TOO_MANY_JOBS: {len(paths)} job records; refusing an unbounded scan.")
        return 2
    results: dict[str, list[tuple[str, str, dict, dict]]] = {name: [] for name in NAMES}
    for path in paths:
        try:
            job = _safe_json(path, JOBS)
            if not _job_state_is_valid(job):
                continue
            for item in job.get("items", []):
                if not isinstance(item, dict):
                    continue
                name = _name_match(item)
                if name:
                    results[name].append((str(item.get("finished_at") or item.get("started_at") or job.get("updated_at") or ""),
                                          str(job.get("job_id", "")), item, job))
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
            continue
    for name in NAMES:
        matches = sorted(results[name], key=lambda entry: entry[0], reverse=True)
        print(f"\n=== {name}.png: {len(matches)} saved attempts ===")
        if not matches:
            print("NO_MATCHING_SAVED_JOB: cannot determine the reason without this job evidence.")
            continue
        for when, job_id, item, _job in matches[:5]:
            print(f"Date: {when} | Job: {job_id}")
            print(f"Source: {item.get('original_filename') or item.get('display_name')} | Columns: {item.get('column_count')} | Status: {item.get('status')}")
            reason = str(item.get("reason") or "(no failure reason persisted)")
            print(f"Reason: {reason}")
            print(f"Meaning: {_explain(reason)}")
            pool = item.get("release_pool")
            if isinstance(pool, dict) and pool:
                print(f"Pool: {pool.get('disposition')} | readback_verified={pool.get('readback_verified')} | {pool.get('reason', '')}")
            run_id = str(item.get("run_id", ""))
            if run_id.startswith("pipeline-") and re.fullmatch(r"pipeline-[a-z0-9_-]{1,100}", run_id):
                p = PIPELINES / f"{run_id}.json"
                try:
                    pipeline = _safe_json(p, PIPELINES)
                    primary = pipeline.get("primary", {})
                    primary = primary if isinstance(primary, dict) else {}
                    acceptance = primary.get("acceptance", {})
                    acceptance = acceptance if isinstance(acceptance, dict) else {}
                    print(f"Pipeline: {pipeline.get('disposition')} | solver={acceptance.get('solver_status')} | replay={acceptance.get('replay')} | difficulty={acceptance.get('difficulty')}")
                    print(f"Load check: {primary.get('load_check', {}).get('state') if isinstance(primary.get('load_check'), dict) else 'UNKNOWN'}")
                except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
                    print("Pipeline: exact persisted run JSON not available")
    return 0


if __name__ == "__main__":
    sys.exit(main())
