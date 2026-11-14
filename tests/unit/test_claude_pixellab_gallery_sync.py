"""Owner request 2026-11-14: a Studio button imports the newest PixelLab gallery sheets
that never reached the Factory (the 10:09 desert sheet was charged but lost when the
Studio closed). Only free reads; known sheets are recognised by their atlas hash."""
import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts"))
import factory_core_launcher as launcher  # noqa: E402
from scrubbots_pixel_factory import studio_extensions as se  # noqa: E402


def test_sync_imports_only_unknown_sheets(tmp_path, monkeypatch):
    transactions = tmp_path / "data" / "output" / "Pixellab" / "Transactions"
    transactions.mkdir(parents=True)
    known, new = b"\x89PNG known", b"\x89PNG new"
    (transactions / f"pixellab-atlas-{hashlib.sha256(known).hexdigest()}.json").write_text("{}")
    monkeypatch.setattr(launcher, "_repository_root", lambda: tmp_path)
    imported: list[bytes] = []
    monkeypatch.setattr(launcher, "_semantic_import_pixellab_pro_4x4",
                        lambda request: imported.append(Path(request["path"]).read_bytes()) or {"pass_count": 16, "source_ids": ["s"] * 16, "atlas_path": "A"})
    sheets = [{"asset_id": "a", "png": known}, {"asset_id": "b", "png": new}, {"asset_id": "c", "skipped": "64 frames"}]

    result = launcher._pixellab_gallery_sync({"limit": 10}, sheets=sheets)

    assert imported == [new]
    assert result["counts"] == {"IMPORTED": 1, "ALREADY_IN_FACTORY": 1, "SKIPPED": 1, "IMPORT_FAILED": 0}
    assert result["new_sources"] == 16


def test_gallery_fetch_uses_only_free_reads_and_skips_non_4x4():
    calls = []
    listing = {"content": [{"type": "text", "text": "  gallery:aaa | Pixel art style: desert | 56x56, 16 frames | 2026-11-14\n"
                                                    "  gallery:bbb | portrait | 128x128, 1 frames | 2026-11-14\n"}]}

    def call_tool(name, arguments):
        calls.append(name)
        return listing if name == "list_images" else {"structuredContent": {"download_url": "https://x/aaa/image.png"}}

    sheets = se.pixellab_recent_gallery_sheets(10, call_tool=call_tool, download=lambda url, **kw: b"PNG" + str(kw["expected_size"]).encode())

    assert calls == ["list_images", "get_image"]
    assert sheets[0]["png"] == b"PNG(224, 224)" and "skipped" in sheets[1]
    assert se.PIXELLAB_GALLERY_SYNC_TOOLS == {"list_images", "get_image", "get_balance"}  # free reads only


def test_balance_reads_remaining_generations_with_a_free_call():
    calls = []
    text = ("credits: $0.00\ngenerations_remaining: 790\ngenerations_used: 1210\ngenerations_total: 2000\n"
            "subscription: active (Tier 1: Pixel Apprentice)\ngenerations_reset: 2026-11-20\n")

    def call_tool(name, arguments):
        calls.append(name)
        return {"content": [{"type": "text", "text": text}]}

    balance = se.pixellab_balance(call_tool=call_tool)

    assert calls == ["get_balance"] and "get_balance" in se.PIXELLAB_GALLERY_SYNC_TOOLS
    assert balance["generations_remaining"] == 790 and balance["generations_total"] == 2000
    assert balance["generations_reset"] == "2026-11-20"
