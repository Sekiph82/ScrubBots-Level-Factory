"""Regression 2026-11-14: restoring one selected PNG re-validated all ~1500 candidate
bundles (fresh process per Studio read), ~2 min per click, which starved the batch
progress read; the screen stayed at "8/903 done" while the batch was at 21+."""
from pathlib import Path

from scrubbots_pixel_factory import studio_extensions as se


def test_find_candidate_reads_only_the_named_bundle(tmp_path, monkeypatch):
    candidate_id = "candidate-owner-" + "a" * 48
    root = tmp_path / "Workspace" / "Candidates" / candidate_id
    root.mkdir(parents=True)
    monkeypatch.setattr("scrubbots_pixel_factory.owner_art_storage.owner_art_paths", lambda _repo: {"workspace": tmp_path / "Workspace"})
    read: list[Path] = []
    monkeypatch.setattr(se, "_candidate_row", lambda path, **_kw: read.append(path) or {"candidate_id": candidate_id, "artwork_sha256": "b" * 64})
    monkeypatch.setattr(se, "list_candidates", lambda: (_ for _ in ()).throw(AssertionError("full candidate scan")))
    monkeypatch.setattr(se, "_validated_review_chain", lambda candidate: ([{"disposition": "ACCEPT"}], []))

    assert se.find_candidate(candidate_id)["candidate_id"] == candidate_id
    assert se._latest_review(candidate_id, "b" * 64) == {"disposition": "ACCEPT"}
    assert se._latest_review(candidate_id, "c" * 64) is None
    assert read == [root.resolve()] * 3


def test_find_candidate_falls_back_to_the_full_scan_when_folder_is_absent(tmp_path, monkeypatch):
    monkeypatch.setattr("scrubbots_pixel_factory.owner_art_storage.owner_art_paths", lambda _repo: {"workspace": tmp_path})
    monkeypatch.setattr(se, "list_candidates", lambda: [{"candidate_id": "candidate-x"}])
    assert se.find_candidate("candidate-x") == {"candidate_id": "candidate-x"}


def test_find_candidate_does_not_load_the_whole_candidate_cache(tmp_path, monkeypatch):
    # 2026-11-23: find_candidate loaded the 232 MB candidate-rows cache (~2.1 GB in Python)
    # for one row; every batch child kept it, six of them paged the 16 GB machine.
    candidate_id = "candidate-owner-" + "d" * 48
    root = tmp_path / "Workspace" / "Candidates" / candidate_id
    root.mkdir(parents=True)
    monkeypatch.setattr("scrubbots_pixel_factory.owner_art_storage.owner_art_paths", lambda _repo: {"workspace": tmp_path / "Workspace"})
    monkeypatch.setattr(se, "_candidate_stamps", lambda path: ((1, 2),))
    monkeypatch.setattr(se, "_validated_candidate_row", lambda path: {"candidate_id": candidate_id})
    monkeypatch.setattr(se, "_candidate_disk_cache", lambda: (_ for _ in ()).throw(AssertionError("whole cache loaded")))
    monkeypatch.setattr(se, "_CANDIDATE_ROW_CACHE", {})

    assert se.find_candidate(candidate_id) == {"candidate_id": candidate_id}
