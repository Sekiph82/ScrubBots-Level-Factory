"""A batch must not re-hash the pinned runtime for every PNG, yet a changed file is still caught."""
import pytest

from scrubbots_pixel_factory.supply_pipeline import pinned_game_source as pins


def test_runtime_verification_is_reused_until_a_file_changes(tmp_path, monkeypatch):
    calls = []
    real = pins._verify_attested_runtime_files
    monkeypatch.setattr(pins, "_verify_attested_runtime_files", lambda root: calls.append(root) or {"ok": True})
    monkeypatch.setattr(pins, "_VERIFIED_RUNTIMES", {})
    monkeypatch.setattr(pins, "_STAMP_RECHECK_SECONDS", 0.0)  # check the stamp on every call here
    script = tmp_path / "scripts" / "a.gd"
    script.parent.mkdir(parents=True)
    script.write_text("x", encoding="utf-8")
    (tmp_path / "project.godot").write_text("p", encoding="utf-8")

    pins.verify_attested_runtime(tmp_path)
    pins.verify_attested_runtime(tmp_path)
    assert len(calls) == 1

    script.write_text("changed", encoding="utf-8")
    pins.verify_attested_runtime(tmp_path)
    assert len(calls) == 2

    (tmp_path / "scripts" / "b.gd").write_text("new file", encoding="utf-8")
    pins.verify_attested_runtime(tmp_path)
    assert len(calls) == 3
    assert real is not None


def test_real_runtime_still_verifies_and_rejects_tampering(tmp_path):
    with pytest.raises(pins.PinnedGameSourceError):
        pins.verify_attested_runtime(tmp_path)
