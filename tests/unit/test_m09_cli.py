import importlib
import json
from pathlib import Path

from scrubbots_pixel_factory.cli import main as cli_main

cli_module = importlib.import_module("scrubbots_pixel_factory.cli.main")


def test_omitted_generate_seed_is_controlled_and_recorded(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli_module.secrets, "randbits", lambda bits: 4242)
    assert cli_main(["generate", "--difficulty", "EASY", "--mode", "MASK", "--width", "20", "--height", "20", "--output", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert 'seed_selected={"type":"int","value":4242}' in output
    metadata = next(tmp_path.rglob("metadata.json"))
    value = json.loads(metadata.read_text(encoding="utf-8"))
    assert value["generation"]["request"]["seed"] == {"type": "int", "value": 4242}
    assert value["generation"]["seed"] == {"type": "int", "value": 4242}


def test_seed_parser_keeps_noncanonical_decimal_as_string() -> None:
    from scrubbots_pixel_factory.cli.main import _canonical_seed

    assert _canonical_seed("42") == 42
    assert _canonical_seed("-42") == -42
    assert _canonical_seed("042") == "042"
    assert _canonical_seed("seed-42") == "seed-42"


def test_options_json_and_local_exemplar_loader_reject_remote_paths(tmp_path) -> None:
    from scrubbots_pixel_factory.cli.main import CLIError, _load_exemplars, _options_from_json

    try:
        _options_from_json(Path("https://example.invalid/options.json"), "mask")
    except CLIError as exc:
        assert "local filesystem path" in str(exc)
    else:
        raise AssertionError("remote options path was accepted")
    try:
        _load_exemplars(Path("https://example.invalid/exemplar.json"))
    except CLIError as exc:
        assert "local filesystem path" in str(exc)
    else:
        raise AssertionError("remote exemplar path was accepted")


def test_help_is_available_from_module() -> None:
    from scrubbots_pixel_factory.cli.main import _parser

    help_text = _parser().format_help()
    assert "generate" in help_text and "reproduce" in help_text and "batch" in help_text
