from pathlib import Path

p = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\src\scrubbots_pixel_factory\supply_pipeline\game_publisher.py")
s = p.read_text(encoding="utf-8")


def rep(old, new):
    global s
    assert old in s, old[:90]
    s = s.replace(old, new, 1)


HELPERS = '''

REAL_PLAY_PROVENANCE = "data/levels/supply/real_play_provenance_v1.json"
REAL_PLAY_NODE_BUDGET = 400  # RealPlayDriver.NODE_BUDGET


def _text_sha256(path: Path) -> str:
    """RealPlayDriver.plan_sha256: SHA-256 of the UTF-8 text with CRLF folded to LF."""
    return hashlib.sha256(path.read_text(encoding="utf-8").replace("\\r\\n", "\\n").encode("utf-8")).hexdigest()


def real_play_record(pipeline: Mapping[str, object], level_id: str, order: int, plan_path: Path) -> dict[str, object]:
    """The game's real_play_provenance_v1 record, taken from Level Factory's own canonical play.

    Level Factory already plays every level through the game's RealPlayDriver (model
    real_play_v1, 1/60) and keeps the WON_CANONICAL result; the game only needs this summary.
    """
    primary = pipeline.get("primary") if isinstance(pipeline.get("primary"), Mapping) else {}
    files = primary.get("files") if isinstance(primary.get("files"), Mapping) else {}
    if not files.get("real_play_result"):
        raise PublicationError(f"{level_id}: Level Factory real-play result is missing")
    result = _load(Path(str(files["real_play_result"])))
    canonical = (result.get("perDt") or {}).get("1/60") if isinstance(result, Mapping) else None
    plan = _load(plan_path)
    if (not isinstance(result, Mapping) or result.get("verdict") != "WON_CANONICAL" or result.get("model") != "real_play_v1"
            or result.get("canonicalDt") != "1/60" or result.get("searched") is not False or result.get("levelId") != level_id
            or not isinstance(canonical, Mapping) or canonical.get("won") is not True
            or not isinstance(plan, Mapping) or result.get("planClicks") != plan.get("intendedColumnClicks")
            or result.get("planSha256") != _text_sha256(plan_path)):
        raise PublicationError(f"{level_id}: Level Factory real-play result does not prove a canonical WON for this exact plan")
    return {"canonicalDt": "1/60", "clicks": [int(c) for c in plan["intendedColumnClicks"]], "framesAtCanonical": int(canonical.get("frames", 0)),
            "levelId": level_id, "model": "real_play_v1", "nodeBudget": REAL_PLAY_NODE_BUDGET, "order": int(order),
            "planSha256": result["planSha256"], "regenerated": False, "searchNodes": 0, "status": "WON"}


def _provenance_with(root: Path, records: list[dict[str, object]]) -> bytes:
    path = root / REAL_PLAY_PROVENANCE
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"model": "real_play_v1", "records": [], "schema": "scrubbots.real_play_provenance.v1"}
    known = {record.get("levelId") for record in data["records"]}
    data["records"] = [*data["records"], *(record for record in records if record["levelId"] not in known)]
    # Same bytes as the game's JSON.stringify(..., "\\t", true) writer.
    return (json.dumps(data, indent="\\t", sort_keys=True, ensure_ascii=False) + "\\n").encode("utf-8")


def publish_level('''
rep("\n\ndef publish_level(", HELPERS)

# publish_level: attach the record built from the staged plan copy.
rep('''    return {"disposition": "PUBLISHED", "game_project": str(root), "level_id": level_id, "order": order, "paths"''',
    '''    record = real_play_record(pipeline, level_id, order, paths["supply_plan"])
    return {"disposition": "PUBLISHED", "game_project": str(root), "level_id": level_id, "order": order, "real_play_record": record, "paths"''')

# publish_batch: write the merged provenance with the catalog commit (and roll it back with it).
rep('''        _validate_proposed_catalog(stage)
        relatives = []''', '''        _validate_proposed_catalog(stage)
        provenance_path = root / REAL_PLAY_PROVENANCE
        original_provenance = provenance_path.read_bytes() if provenance_path.is_file() else None
        provenance_bytes = _provenance_with(root, [item["real_play_record"] for item in staged_results])
        relatives = []''')
rep('''            # The catalog is the batch visibility/commit point.
            staged_catalog = stage / "data/levels/catalog/production_catalog_v1.json"''', '''            # Real-play provenance first, then the catalog (the batch visibility/commit point).
            provenance_tmp = root / ".lfx-real-play-provenance.tmp"
            provenance_tmp.parent.mkdir(parents=True, exist_ok=True)
            provenance_tmp.write_bytes(provenance_bytes)
            provenance_path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(provenance_tmp, provenance_path)
            staged_catalog = stage / "data/levels/catalog/production_catalog_v1.json"''')
rep('''            if catalog_path.read_bytes() != original_catalog:''', '''            if original_provenance is not None and provenance_path.read_bytes() != original_provenance:
                restore_provenance = root / ".lfx-provenance-rollback.tmp"
                restore_provenance.write_bytes(original_provenance); os.replace(restore_provenance, provenance_path)
            elif original_provenance is None:
                provenance_path.unlink(missing_ok=True)
            if catalog_path.read_bytes() != original_catalog:''')
p.write_text(s, encoding="utf-8")
print("ok")
