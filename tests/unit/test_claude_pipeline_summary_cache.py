"""A verified Release Pool read must not re-parse every pipeline record each time (P0-P, 2026-11-17)."""
import json

from scrubbots_pixel_factory.supply_pipeline import release_pool


class _Studio:
    class StudioExtensionError(Exception):
        pass

    def __init__(self):
        self.reads = 0

    def _read_json(self, path):
        self.reads += 1
        return json.loads(path.read_text(encoding="utf-8"))


def test_latest_ready_index_parses_each_record_once_until_it_changes(tmp_path, monkeypatch):
    monkeypatch.setattr(release_pool, "_PIPELINE_SUMMARIES", {})
    paths = []
    for n, (cid, created) in enumerate([("c1", "2026-11-17T01"), ("c1", "2026-11-17T02"), ("c2", "2026-11-17T01")]):
        p = tmp_path / f"pipeline-{n}.json"
        p.write_text(json.dumps({"disposition": "READY", "primary": {"state": "READY"}, "candidate_id": cid,
                                 "run_id": f"pipeline-{n}", "created_at": created}), encoding="utf-8")
        paths.append(p)
    studio = _Studio()

    first = release_pool._latest_ready_pipeline_index(paths, studio)
    second = release_pool._latest_ready_pipeline_index(paths, studio)

    assert first == second and first["c1"]["run_id"] == "pipeline-1" and first["c2"]["run_id"] == "pipeline-2"
    assert studio.reads == 3  # second listing read nothing
    paths[0].write_text(json.dumps({"disposition": "FAILED", "candidate_id": "c1"}) + " ", encoding="utf-8")
    release_pool._latest_ready_pipeline_index(paths, studio)
    assert studio.reads == 4  # only the changed record was read again
