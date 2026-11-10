"""P0-B regression: Level Factory startup blocked ~20 min because candidate_inbox()
re-validated every candidate bundle once per candidate (O(n^2))."""
from scrubbots_pixel_factory import studio_extensions


def test_candidate_inbox_reads_each_bundle_once(monkeypatch, tmp_path) -> None:
    roots = []
    for index in range(6):
        root = tmp_path / f"c{index}"
        root.mkdir()
        for name in ("metadata.json", "artwork.json", "artwork.png"):
            (root / name).write_bytes(b"x")
        roots.append(root)
    reads: list = []

    class Art:
        def __init__(self, i):
            self.candidate_id, self.grid_hash, self.width, self.height, self.cells = f"cand-{i}", "g", 4, 4, ("C01",)

    class Bundle:
        def __init__(self, root):
            self.artwork, self.artwork_png, self.metadata = Art(root.name), b"png", {"quality": {}}

    def fake_read_bundle(root):
        reads.append(root)
        return Bundle(root)

    monkeypatch.setattr(studio_extensions, "_candidate_roots", lambda: list(roots))
    monkeypatch.setattr(studio_extensions, "read_bundle", fake_read_bundle)
    monkeypatch.setattr(studio_extensions, "_relative", lambda path: str(path))
    monkeypatch.setattr(studio_extensions, "_validated_review_chain", lambda candidate: ([], []))
    monkeypatch.setattr(studio_extensions, "_CANDIDATE_ROW_CACHE", {})

    view = studio_extensions.candidate_inbox()
    assert len(view["candidates"]) == 6
    assert len(reads) == 6  # was 6 + 6*6 = 42 before the fix
    # Cached rows are returned as independent copies.
    view["candidates"][0]["quality"]["mutated"] = True
    assert "mutated" not in studio_extensions.list_candidates()[0]["quality"]
    assert len(reads) == 6
    # A changed bundle file is re-validated.
    (roots[0] / "artwork.png").write_bytes(b"changed")
    studio_extensions.list_candidates()
    assert reads[-1] == roots[0] and len(reads) == 7
