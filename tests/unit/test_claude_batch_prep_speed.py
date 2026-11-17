"""Batch preparation must not re-validate every candidate (owner 2026-11-17)."""
import inspect
from pathlib import Path

from scrubbots_pixel_factory import png_batch, studio_extensions
from scrubbots_pixel_factory.supply_pipeline import release_pool


def test_candidate_cache_survives_unrelated_studio_extensions_edits():
    src = inspect.getsource(studio_extensions._candidate_validation_code_digest)
    assert '"studio_extensions.py"' not in src
    assert "getsource(_validated_candidate_row)" in src
    assert studio_extensions._candidate_validation_code_digest() == studio_extensions._candidate_validation_code_digest()


def test_ready_check_reads_only_named_candidates(monkeypatch, tmp_path):
    jobs = tmp_path / "jobs"; jobs.mkdir()
    (jobs / "png-batch-x.json").write_text("{}", encoding="utf-8")
    sha = "a" * 64
    monkeypatch.setattr(png_batch, "_root", lambda: tmp_path)
    monkeypatch.setattr(png_batch, "_read_job", lambda stem: {"items": [{
        "status": "READY", "source_sha256": sha, "source_id": "owner-upload-" + sha, "candidate_id": "cand-1"}]})

    def boom(*_a, **_k):
        raise AssertionError("full candidate projection must not run")
    monkeypatch.setattr(studio_extensions, "list_candidates", boom)
    seen = []
    monkeypatch.setattr(studio_extensions, "find_candidate", lambda cid: seen.append(("find", cid)) or None)
    monkeypatch.setattr(release_pool, "release_entries", lambda cid=None: seen.append(("entries", cid)) or [] if cid else boom())
    monkeypatch.setattr(release_pool, "entry_paths", lambda cid=None: seen.append(("paths", cid)) or [] if cid else boom())
    monkeypatch.setattr(studio_extensions, "_pipeline_paths", lambda: [])
    assert png_batch._verified_ready_sources([{"source_id": "owner-upload-" + sha, "source_sha256": sha}]) == {}
    assert ("find", "cand-1") in seen and ("entries", "cand-1") in seen and ("paths", "cand-1") in seen


def test_run_pending_batch_writes_preparation_activity():
    gd = Path("level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    assert "func _batch_prep_step(message: String)" in gd
    assert 'await _batch_prep_step("Batch worker started' in gd
    assert 'await _batch_prep_step("Batch worker is planning' in gd


def test_candidate_cache_digest_ignores_line_endings(tmp_path, monkeypatch):
    # The Git checkout (CRLF) and the installed Release copy (LF) must share one candidate cache.
    import shutil
    from pathlib import Path
    from scrubbots_pixel_factory import studio_extensions
    package = Path(studio_extensions.__file__).resolve().parent
    copies = {}
    for ending in (b"\n", b"\r\n"):
        root = tmp_path / ("crlf" if ending == b"\r\n" else "lf")
        for relative in ("output/bundle.py", "output/png.py", "quality/core.py", "contracts/palette.py"):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            text = (package / relative).read_bytes().replace(b"\r\n", b"\n")
            target.write_bytes(text.replace(b"\n", ending))
        copies[ending] = root
    digests = []
    for root in copies.values():
        monkeypatch.setattr(studio_extensions, "__file__", str(root / "studio_extensions.py"))
        digests.append(studio_extensions._candidate_validation_code_digest())
    assert digests[0] == digests[1]
