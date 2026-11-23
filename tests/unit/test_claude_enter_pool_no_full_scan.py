"""A just-finished READY pipeline enters the Release Pool without re-reading every pipeline record.

Owner 2026-11-23: each READY PNG spent ~150 s and ~3.5 GB re-parsing all ~3500 pipeline
records (and every candidate) after its solve, which paged the 16 GB machine.
"""
from __future__ import annotations

import pytest

from scrubbots_pixel_factory import studio_extensions as studio
from scrubbots_pixel_factory.supply_pipeline import release_pool

CID = "candidate-owner-" + "c" * 48


def test_enter_with_given_ready_pipeline_skips_the_pipeline_scan(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    pipeline = {"run_id": "pipeline-1", "candidate_id": CID, "disposition": "READY", "primary": {"state": "READY"}}
    candidate = {"candidate_id": CID, "artwork_sha256": "a" * 64}
    entry = {"pipeline_run_id": "pipeline-1", "entry_digest": "d"}
    reads = {"entries": 0}

    def no_scan():
        raise AssertionError("every pipeline record was re-read")

    def entries(candidate_id, verify=False):
        reads["entries"] += 1
        return [] if reads["entries"] == 1 else [entry]

    monkeypatch.setattr(studio, "_pipeline_paths", no_scan)
    monkeypatch.setattr(studio, "_latest_review", lambda *_args, **_kw: None)
    monkeypatch.setattr(release_pool, "release_entries", entries)
    monkeypatch.setattr(release_pool, "enter_release_pool", lambda c, p, r=None: dict(entry))

    # Act
    result = studio._enter_candidate_release_pool(candidate, pipeline=pipeline)

    # Assert
    assert result["readback_verified"] is True and result["pipeline_run_id"] == "pipeline-1"
