"""Thin repository-local launcher for the canonical Python Factory Core CLI."""

from pathlib import Path
import sys


def _main() -> int:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root / "src"))
    from scrubbots_pixel_factory.cli.main import main as canonical_main

    return canonical_main()


if __name__ == "__main__":
    raise SystemExit(_main())
