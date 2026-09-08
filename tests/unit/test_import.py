from scrubbots_pixel_factory import OFFLINE_ONLY, __version__, deterministic_digest


def test_package_imports_with_m00_metadata() -> None:
    assert __version__ == "0.1.0"
    assert OFFLINE_ONLY is True


def test_local_deterministic_computation_is_stable() -> None:
    assert deterministic_digest("scrubbots") == deterministic_digest("scrubbots")
    assert deterministic_digest("scrubbots") != deterministic_digest("different")
