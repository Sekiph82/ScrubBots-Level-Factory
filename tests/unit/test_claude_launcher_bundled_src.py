"""P0-B regression: the installed Studio imported the Desktop working-tree `src`
through the editable pip install, so uncommitted edits (a 3-tuple return) broke
the installed `png-batch-run` gate ("too many values to unpack") and Resume
Batch silently did nothing. The launcher must prefer the `src` shipped beside it."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_installed_layout_launcher_imports_its_bundled_src(tmp_path: Path) -> None:
    install = tmp_path / "Release" / "ScrubBots Factory Studio"
    scripts = install / "level_factory" / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(ROOT / "level_factory/scripts/factory_core_launcher.py", scripts / "factory_core_launcher.py")
    package = install / "src" / "scrubbots_pixel_factory"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("BUNDLED_MARKER = True\n", encoding="utf-8")
    probe = (
        "import importlib.util, sys\n"
        f"spec = importlib.util.spec_from_file_location('launcher', r'{scripts / 'factory_core_launcher.py'}')\n"
        "module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)\n"
        "import scrubbots_pixel_factory as package\n"
        "print(package.__file__, getattr(package, 'BUNDLED_MARKER', False))\n"
    )
    out = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, timeout=60, cwd=tmp_path)
    assert out.returncode == 0, out.stderr
    assert str(package) in out.stdout and "True" in out.stdout, out.stdout


def test_installed_src_copy_reads_owner_data_from_canonical_checkout(tmp_path: Path) -> None:
    """Running the bundled Release src must still read data/ from the Desktop checkout
    (palette SHA binds PixelLab digests; the attested runtime lives in data/)."""
    install = tmp_path / "Release" / "ScrubBots Factory Studio"
    shutil.copytree(ROOT / "src", install / "src", ignore=shutil.ignore_patterns("__pycache__"))
    probe = (
        "from scrubbots_pixel_factory.contracts.palette import PALETTE_DATA_PATH\n"
        "from scrubbots_pixel_factory.supply_pipeline import pinned_game_source as g\n"
        "print(PALETTE_DATA_PATH); print(g.repository_root())\n"
    )
    import os
    env = {**os.environ, "PYTHONPATH": str(install / "src"), "USERPROFILE": str(ROOT.parents[1])}
    out = subprocess.run([sys.executable, "-B", "-c", probe], capture_output=True, text=True, timeout=120, cwd=tmp_path, env=env)
    assert out.returncode == 0, out.stderr
    palette, repo = out.stdout.splitlines()[-2:]
    assert Path(palette) == ROOT / "data" / "palette" / "scrubbots_palette_v3.json"
    assert Path(repo) == ROOT
