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
