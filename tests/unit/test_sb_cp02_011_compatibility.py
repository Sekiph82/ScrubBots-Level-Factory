from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    AppContentCompatibilityReasonCode as Reason,
    check_app_content_compatibility,
)

SCHEMA = "scrubbots.content.manifest.v1"


def _check(**overrides):
    values = dict(
        current_game_version="2.4.0",
        supported_manifest_schema_versions={SCHEMA: {1, 2}},
        manifest_schema=SCHEMA,
        manifest_schema_version=1,
        minimum_game_version="2.4.0",
    )
    values.update(overrides)
    return check_app_content_compatibility(**values)


@pytest.mark.parametrize("current,minimum", [("2.4.0", "2.4.0"), ("2.5.0", "2.4.0"), ("3.0.0", "2.4.0")])
def test_supported_schema_and_equal_or_newer_game_versions_are_compatible(current, minimum) -> None:
    result = _check(current_game_version=current, minimum_game_version=minimum)
    assert result.compatible is True
    assert result.reason_code is Reason.COMPATIBLE


def test_supported_schema_version_set_and_range_are_accepted() -> None:
    supported = {SCHEMA: range(1, 4)}
    assert _check(supported_manifest_schema_versions=supported, manifest_schema_version=3).compatible is True
    assert _check(supported_manifest_schema_versions=supported, manifest_schema_version=4).reason_code is Reason.UNSUPPORTED_SCHEMA_VERSION


def test_unknown_future_schema_and_unsupported_version_fail_closed() -> None:
    assert _check(manifest_schema="scrubbots.content.manifest.v99").reason_code is Reason.UNSUPPORTED_SCHEMA_VERSION
    assert _check(manifest_schema_version=99).reason_code is Reason.UNSUPPORTED_SCHEMA_VERSION


def test_too_old_game_version_fails_closed() -> None:
    result = _check(current_game_version="2.3.99", minimum_game_version="2.4.0")
    assert result.compatible is False
    assert result.reason_code is Reason.GAME_VERSION_TOO_OLD


@pytest.mark.parametrize("current", [None, True, "02.4.0", "2.4", " 2.4.0", "2.4.0-beta"])
def test_invalid_current_app_version_fails_closed(current) -> None:
    assert _check(current_game_version=current).reason_code is Reason.INVALID_APP_VERSION


@pytest.mark.parametrize(
    "field,value",
    [
        ("manifest_schema", None),
        ("manifest_schema", ""),
        ("manifest_schema_version", True),
        ("manifest_schema_version", 0),
        ("minimum_game_version", "2.04.0"),
        ("minimum_game_version", None),
    ],
)
def test_invalid_manifest_compatibility_fields_fail_closed(field, value) -> None:
    assert _check(**{field: value}).reason_code is Reason.INVALID_MANIFEST_COMPATIBILITY_FIELDS


def test_invalid_app_supported_schema_declaration_fails_closed() -> None:
    for capability in (None, {}, {SCHEMA: set()}, {SCHEMA: (1, 1)}, {SCHEMA: (True,)}, {"": (1,)}):
        result = _check(supported_manifest_schema_versions=capability)
        assert result.compatible is False
        assert result.reason_code is Reason.INVALID_APP_CAPABILITY


def test_content_version_history_and_other_gates_remain_independent() -> None:
    compatible = _check()
    assert compatible.compatible is True
    assert not hasattr(compatible, "content_version")
    assert not hasattr(compatible, "references_valid")
    assert not hasattr(compatible, "disabled_levels_valid")
    assert not hasattr(compatible, "schedule_active")
