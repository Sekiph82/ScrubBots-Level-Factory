"""Two different owner PNGs with the same basename (e.g. a/same.png, b/same.png).

Release Pool names status artwork by the source basename. Before 2026-11-12 the
second source failed with "owner release artwork projection collides with an
unverified status record" (aborting a whole batch import), and a later status
move of one source could unlink the other source's readable artwork.
"""
import hashlib
from io import BytesIO
from pathlib import Path

from PIL import Image

from scrubbots_pixel_factory import owner_release_library


def _source(folder: Path, color) -> tuple[str, str, Path]:
    folder.mkdir(parents=True)
    image = BytesIO()
    Image.new("RGBA", (8, 8), color).save(image, format="PNG")
    path = folder / "same.png"
    path.write_bytes(image.getvalue())
    digest = hashlib.sha256(image.getvalue()).hexdigest()
    return "owner-upload-" + digest, digest, path


def _pending(root: Path, source) -> dict:
    source_id, digest, path = source
    return owner_release_library.transition(
        source_id, "PENDING", source_sha256=digest, provider="OWNER_UPLOAD",
        original_source_path=str(path), repository_root=root)


def test_same_basename_sources_both_enter_pending_and_keep_their_artwork(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    (root / "TASKS.md").write_text("# isolated test repository", encoding="utf-8")
    (root / ".git").write_text("gitdir: none", encoding="utf-8")
    first = _source(tmp_path / "in" / "a", (200, 20, 20, 255))
    second = _source(tmp_path / "in" / "b", (20, 20, 200, 255))

    _pending(root, first)
    _pending(root, second)

    pending = root / "data" / "Release Pool" / "Pending"
    pngs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in pending.glob("*.png")}
    assert sorted(pngs.values()) == sorted([first[1], second[1]]), pngs
    assert pngs["same.png"] == first[1]

    # Moving the second source must not touch the first source's readable artwork.
    owner_release_library.transition(
        second[0], "REJECTED", source_sha256=second[1], provider="OWNER_UPLOAD",
        original_source_path=str(second[2]), reason="test", repository_root=root)
    assert hashlib.sha256((pending / "same.png").read_bytes()).hexdigest() == first[1]
    assert [path.name for path in pending.glob("*.png")] == ["same.png"]
    rejected = root / "data" / "Release Pool" / "Rejected"
    assert [hashlib.sha256(path.read_bytes()).hexdigest() for path in rejected.glob("*.png")] == [second[1]]

    # A third transition of the first source still verifies cleanly.
    owner_release_library.transition(
        first[0], "REJECTED", source_sha256=first[1], provider="OWNER_UPLOAD",
        original_source_path=str(first[2]), reason="test", repository_root=root)
    assert sorted(hashlib.sha256(path.read_bytes()).hexdigest() for path in rejected.glob("*.png")) == sorted(
        [first[1], second[1]])
    assert owner_release_library.list_records(repository_root=root)["counts"]["REJECTED"] == 2
