import sys

import pytest


@pytest.fixture(autouse=True)
def unload_m03_modules_after_each_test():
    yield
    for name in list(sys.modules):
        if name == "scrubbots_pixel_factory.generators" or name.startswith("scrubbots_pixel_factory.generators."):
            del sys.modules[name]


_REAL_CHECKOUT = __import__("pathlib").Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def forbid_writes_to_owner_release_pool(monkeypatch):
    """Tests must never append events to the owner's real data/Release Pool.

    2026-11-09 a unit test without an isolated root wrote nine synthetic
    `owner-upload-000...0001..0009` FAILED records into the canonical checkout;
    Factory Studio then showed them as owner Batch Issues. Every Release Pool
    status write goes through `owner_release_library.transition`.
    """
    from pathlib import Path

    try:
        from scrubbots_pixel_factory import owner_art_storage, owner_release_library
    except ImportError:
        yield
        return
    original = owner_release_library.transition

    def guarded(*args, repository_root=None, **kwargs):
        root = Path(repository_root) if repository_root is not None else owner_art_storage.factory_repository_root()
        if Path(root).resolve() == _REAL_CHECKOUT:
            raise RuntimeError("test attempted to write the owner's real data/Release Pool; pass an isolated repository_root")
        return original(*args, repository_root=repository_root, **kwargs)

    monkeypatch.setattr(owner_release_library, "transition", guarded)
    yield


_OWNER_DATA_WATCH = ("data/Release Pool", "data/Level Factory/Batches", "data/Level Factory/Imported",
                     "data/output/Pixellab/Final", "data/output/Pixellab/Grid Files")


def _owner_data_snapshot():
    from pathlib import Path

    snapshot = {}
    for relative in _OWNER_DATA_WATCH:
        root = _REAL_CHECKOUT / relative
        if root.exists():
            for path in root.rglob("*"):
                if path.is_file() and ".locks" not in path.parts:
                    stat = path.stat()
                    snapshot[str(path.relative_to(_REAL_CHECKOUT))] = (stat.st_mtime_ns, stat.st_size)
    return snapshot


def pytest_sessionstart(session):
    session.config._owner_data_before = _owner_data_snapshot()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    before = getattr(config, "_owner_data_before", None)
    if before is None:
        return
    after = _owner_data_snapshot()
    changed = sorted(set(after) ^ set(before) | {k for k in after if k in before and after[k] != before[k]})
    if changed:
        terminalreporter.write_sep("!", "OWNER DATA CHANGED DURING TESTS (a test may lack an isolated root, or Factory Studio was running)")
        for name in changed[:40]:
            terminalreporter.write_line(name)
