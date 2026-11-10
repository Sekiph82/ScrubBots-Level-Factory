"""2026-11-10: a unit test's cleanup deleted every folder in the owner's real
data/Level Factory/Imported. The conftest audit guard must block any delete,
rename or write under the real checkout's data/ while a test runs."""
import os
from pathlib import Path

import pytest

REAL_DATA = Path(__file__).resolve().parents[2] / "data"


def test_delete_under_real_data_is_blocked() -> None:
    with pytest.raises(PermissionError, match="owner's real data"):
        os.remove(REAL_DATA / "Level Factory" / "Imported" / "guard-probe-does-not-exist.png")


def test_write_and_rename_under_real_data_are_blocked(tmp_path: Path) -> None:
    with pytest.raises(PermissionError, match="owner's real data"):
        (REAL_DATA / "Level Factory" / "guard-probe-does-not-exist.json").write_text("{}", encoding="utf-8")
    scratch = tmp_path / "x.txt"
    scratch.write_text("ok", encoding="utf-8")
    with pytest.raises(PermissionError, match="owner's real data"):
        os.replace(scratch, REAL_DATA / "guard-probe-does-not-exist.txt")


def test_reads_and_tmp_writes_still_work(tmp_path: Path) -> None:
    (tmp_path / "ok.txt").write_text("ok", encoding="utf-8")
    assert (tmp_path / "ok.txt").read_text(encoding="utf-8") == "ok"
    assert REAL_DATA.is_dir()
