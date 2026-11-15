"""Owner 2026-11-15: PixelLab ignored no_background=True for atlases 118-120 and drew a
white card behind every frame; they entered Final as normal sources. Such an atlas is
now rejected at intake and its slices get a REJECTED Release Pool status."""
import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts"))
import factory_core_launcher as launcher  # noqa: E402
from scrubbots_pixel_factory.pixellab_pro_atlas import inspect_atlas  # noqa: E402


def _atlas(card: bool) -> bytes:
    atlas = Image.new("RGBA", (224, 224), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)
    for index in range(16):
        x, y = (index % 4) * 56, (index // 4) * 56
        if card:
            draw.rectangle((x + 2, y + 2, x + 53, y + 53), fill=(255, 255, 255, 255))
        draw.rectangle((x + 14, y + 14, x + 41, y + 41), fill=(0, 0, 0, 255))
        draw.rectangle((x + 18, y + 18, x + 37, y + 37), fill=(255, 56, 129, 255))
        draw.rectangle((x + 22, y + 22, x + 22 + index % 4, y + 33), fill=(81, 82, 82, 255))
    out = io.BytesIO()
    atlas.save(out, "PNG")
    return out.getvalue()


def test_white_card_atlas_is_rejected_and_clean_atlas_is_not():
    _, card = inspect_atlas(_atlas(True), max_colors=12)
    _, clean = inspect_atlas(_atlas(False), max_colors=12)
    assert all("OPAQUE_BACKGROUND" in record["reasons"] and record["intake_status"] == "REJECTED" for record in card)
    assert not any("OPAQUE_BACKGROUND" in record["reasons"] for record in clean)


def test_background_atlas_slices_get_a_rejected_status(monkeypatch):
    calls = []
    import scrubbots_pixel_factory.owner_release_library as library
    monkeypatch.setattr(library, "list_records", lambda: {"records": [{"source_id": "owner-upload-" + "b" * 64}]})
    monkeypatch.setattr(library, "transition", lambda source_id, status, **kwargs: calls.append((source_id, status)))
    monkeypatch.setattr(launcher, "_pixellab_final_slice_path", lambda catalog, frame: Path("Final") / f"LF-{frame['index']:06d}.png")
    manifest = {"frames": [{"index": 1, "sha256": "a" * 64, "reasons": ["OPAQUE_BACKGROUND"]},
                           {"index": 2, "sha256": "b" * 64, "reasons": ["OPAQUE_BACKGROUND"]}]}

    assert launcher._reject_background_atlas_frames({"atlas_path": "PX-ATLAS-000999.png"}, manifest) == 1
    assert calls == [("owner-upload-" + "a" * 64, "REJECTED")]
    assert launcher._reject_background_atlas_frames({}, {"frames": [{"index": 1, "sha256": "c" * 64, "reasons": []}]}) == 0
