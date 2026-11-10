import sys

import pytest


@pytest.fixture(autouse=True)
def unload_m03_modules_after_each_test():
    yield
    for name in list(sys.modules):
        if name == "scrubbots_pixel_factory.generators" or name.startswith("scrubbots_pixel_factory.generators."):
            del sys.modules[name]


_REAL_CHECKOUT = __import__("pathlib").Path(__file__).resolve().parents[1]

# Content-pipeline tests import scrubbots_content_pipeline directly; make that
# independent of which other test happened to extend sys.path first.
if str(_REAL_CHECKOUT / "content_pipeline" / "src") not in sys.path:
    sys.path.append(str(_REAL_CHECKOUT / "content_pipeline" / "src"))

# 2026-11-10: a test cleanup deleted every folder in the owner's real
# data/Level Factory/Imported. While a test runs, any delete, rename or write
# under the real checkout's data/ folder now fails that test instead.
_REAL_DATA_PREFIX = __import__("os").path.normcase(str(_REAL_CHECKOUT / "data")) + __import__("os").sep
_guard_owner_data = False
_WRITE_FLAGS = 0
for _flag in ("O_WRONLY", "O_RDWR", "O_CREAT", "O_APPEND", "O_TRUNC"):
    _WRITE_FLAGS |= getattr(__import__("os"), _flag, 0)


def _is_real_data_path(value) -> bool:
    import os

    if isinstance(value, bytes):
        value = os.fsdecode(value)
    if not isinstance(value, (str, os.PathLike)):
        return False
    try:
        return os.path.normcase(os.path.abspath(os.fspath(value))).startswith(_REAL_DATA_PREFIX)
    except (TypeError, ValueError):
        return False


def _owner_data_audit(event: str, args: tuple) -> None:
    if not _guard_owner_data:
        return
    if event in {"os.remove", "os.rmdir", "shutil.rmtree", "os.truncate"}:
        targets = args[:1]
    elif event in {"os.rename", "os.replace"}:
        targets = args[:2]
    elif event == "open" and len(args) >= 3:
        mode, flags = args[1], args[2]
        writes = (isinstance(mode, str) and any(ch in mode for ch in "wax+")) or (
            isinstance(flags, int) and bool(flags & _WRITE_FLAGS))
        targets = args[:1] if writes else ()
    else:
        return
    for target in targets:
        if _is_real_data_path(target):
            raise PermissionError(f"test attempted {event} on the owner's real data: {target}")


sys.addaudithook(_owner_data_audit)


_GODOT_SUBPROCESS_TIMEOUT_SECONDS = 900


@pytest.fixture(autouse=True)
def bound_godot_subprocesses(monkeypatch):
    """2026-11-10: a headless Godot suite without a timeout hung the run for 3 h.

    Any Godot child started through subprocess.run without its own timeout now
    fails that one test with TimeoutExpired instead of blocking the session.
    """
    import subprocess

    original_run = subprocess.run

    def bounded_run(args, *positional, **keywords):
        text = " ".join(str(part) for part in args) if isinstance(args, (list, tuple)) else str(args)
        if "timeout" not in keywords and ("godot" in text.lower() or "--headless" in text):
            keywords["timeout"] = _GODOT_SUBPROCESS_TIMEOUT_SECONDS
        return original_run(args, *positional, **keywords)

    monkeypatch.setattr(subprocess, "run", bounded_run)
    yield


@pytest.fixture(autouse=True)
def forbid_owner_data_mutation():
    global _guard_owner_data
    _guard_owner_data = True
    try:
        yield
    finally:
        _guard_owner_data = False


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

    original_archive = owner_art_storage.archive_pixellab_export

    def guarded_archive(*args, repository_root=None, **kwargs):
        root = Path(repository_root) if repository_root is not None else owner_art_storage.factory_repository_root()
        if Path(root).resolve() == _REAL_CHECKOUT:
            # Never write the owner's real Final/Grid Files: run against a
            # throw-away root so input validation still behaves normally.
            import tempfile

            repository_root = Path(tempfile.mkdtemp(prefix="guarded-owner-art-"))
        return original_archive(*args, repository_root=repository_root, **kwargs)

    monkeypatch.setattr(owner_art_storage, "archive_pixellab_export", guarded_archive)
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


@pytest.fixture(autouse=True)
def forbid_real_pixellab_network(monkeypatch):
    """No test may reach the paid PixelLab API with the owner's stored token.

    2026-11-10: tests patched the retired generate_pixellab_pro_4x4_frames while
    the launcher calls generate_pixellab_pro_4x4_atlas_mcp, and faked
    "credentials configured", so they could reach the real MCP endpoint.
    """
    try:
        from scrubbots_pixel_factory import studio_extensions
    except ImportError:
        yield
        return

    def blocked(*_args, **_kwargs):
        raise RuntimeError("test attempted a real PixelLab network request; patch the provider transport")

    monkeypatch.setattr(studio_extensions, "urlopen", blocked, raising=False)
    yield


@pytest.fixture
def isolated_studio_repository(tmp_path, monkeypatch):
    """A throw-away repository in the canonical data layout for Studio tests.

    Every repository-root resolver points at it, so candidates, Imported
    sources, reviews and evidence never touch the owner's real data.
    """
    from scrubbots_pixel_factory import owner_art_storage, owner_upload, studio_extensions

    repository = tmp_path / "repository"
    (repository / "data" / "Level Factory" / "Imported").mkdir(parents=True)
    (repository / "data" / "Level Factory" / "Workspace" / "Candidates").mkdir(parents=True)
    monkeypatch.setattr(owner_art_storage, "factory_repository_root", lambda *_args, **_kwargs: repository)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda *_args, **_kwargs: repository)
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda *_args, **_kwargs: repository)
    return repository
