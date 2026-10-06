"""Deterministic local candidate-manifest assembly from exact M12 pack evidence."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .compatibility import AppContentCompatibilityResult, check_app_content_compatibility
from .manifest_parser import ManifestParseError, parse_content_manifest_v1
from .manifest_v1 import (
    ContentManifestError,
    ContentManifestV1,
    ManifestLevelV1,
    ManifestPackV1,
    ManifestScheduleV1,
    ManifestSuccessorResult,
    check_manifest_successor,
)
from .manifest_validation import ManifestReferenceValidationResult, validate_manifest_references
from .scrubpack_builder import ScrubpackBuildEvidence, ScrubpackBuildResult


class CandidateManifestError(ValueError):
    """Raised when explicit candidate-manifest inputs are malformed."""


@dataclass(frozen=True, slots=True)
class CandidateManifestBuildResult:
    """Immutable exact candidate bytes plus independent local eligibility results."""

    manifest: ContentManifestV1
    manifest_bytes: bytes
    manifest_sha256: str
    pack_builds: tuple[ScrubpackBuildResult, ...]
    strict_round_trip_valid: bool
    references: ManifestReferenceValidationResult
    compatibility: AppContentCompatibilityResult
    successor: ManifestSuccessorResult | None

    @property
    def publishable(self) -> bool:
        return (
            self.strict_round_trip_valid
            and self.references.eligible
            and self.compatibility.compatible
            and (self.successor is None or self.successor.accepted)
        )


def build_candidate_manifest(
    pack_builds: Sequence[ScrubpackBuildResult],
    *,
    content_version: int,
    minimum_game_version: str,
    object_keys: Mapping[str, str],
    current_game_version: str,
    supported_manifest_schema_versions: Mapping[str, object],
    disabled_levels: Sequence[str] = (),
    schedules: Sequence[ManifestScheduleV1] = (),
    prior_accepted_content_version: int | None = None,
) -> CandidateManifestBuildResult:
    """Assemble one local manifest and fail closed across all M13 eligibility gates.

    Pack records derive identity and exact archive hash/length from the supplied
    immutable M12 build results. Provider-neutral object keys, manifest version,
    minimum game version, optional M13 metadata, and app capability are explicit
    caller inputs. This function has no filesystem, clock, network, or provider
    access.
    """
    if isinstance(pack_builds, (str, bytes)) or not isinstance(pack_builds, Sequence):
        raise CandidateManifestError("pack_builds must be an explicit sequence")
    builds = tuple(pack_builds)
    if not builds or any(
        not isinstance(build, ScrubpackBuildResult)
        or type(build.archive_bytes) is not bytes
        or not isinstance(build.evidence, ScrubpackBuildEvidence)
        for build in builds
    ):
        raise CandidateManifestError("at least one valid immutable M12 pack build is required")
    if not isinstance(object_keys, Mapping):
        raise CandidateManifestError("provider-neutral object_keys mapping is required")
    pack_ids = tuple(build.evidence.pack_id for build in builds)
    if any(not isinstance(pack_id, str) for pack_id in pack_ids) or set(object_keys) != set(pack_ids):
        raise CandidateManifestError("object_keys must explicitly and exactly cover the supplied packs")
    if isinstance(disabled_levels, (str, bytes)) or not isinstance(disabled_levels, Sequence):
        raise CandidateManifestError("disabled_levels must be an explicit sequence")
    if isinstance(schedules, (str, bytes)) or not isinstance(schedules, Sequence):
        raise CandidateManifestError("schedules must be an explicit sequence")

    try:
        packs = tuple(
            ManifestPackV1(
                pack_id=build.evidence.pack_id,
                pack_version=build.evidence.pack_version,
                object_key=object_keys[build.evidence.pack_id],
                sha256=hashlib.sha256(build.archive_bytes).hexdigest(),
                byte_length=len(build.archive_bytes),
            )
            for build in builds
        )
        levels = tuple(
            ManifestLevelV1(level_id=level_id, pack_id=build.evidence.pack_id)
            for build in builds
            for level_id in build.evidence.level_ids
        )
        manifest = ContentManifestV1(
            packs=packs,
            levels=levels,
            content_version=content_version,
            minimum_game_version=minimum_game_version,
            disabled_levels=tuple(disabled_levels),
            schedules=tuple(schedules),
        )
    except (ContentManifestError, KeyError, TypeError) as exc:
        raise CandidateManifestError("explicit candidate manifest inputs violate M13 contracts") from exc

    manifest_bytes = manifest.to_json_bytes()
    try:
        parsed = parse_content_manifest_v1(manifest_bytes)
        round_trip_valid = parsed == manifest and parsed.to_json_bytes() == manifest_bytes
    except ManifestParseError:
        round_trip_valid = False

    references = validate_manifest_references(manifest, builds)
    compatibility = check_app_content_compatibility(
        current_game_version=current_game_version,
        supported_manifest_schema_versions=supported_manifest_schema_versions,
        manifest_schema=manifest.schema,
        manifest_schema_version=manifest.schema_version,
        minimum_game_version=manifest.minimum_game_version,
    )
    successor = (
        None
        if prior_accepted_content_version is None
        else check_manifest_successor(prior_accepted_content_version, manifest.to_dict())
    )
    return CandidateManifestBuildResult(
        manifest=manifest,
        manifest_bytes=manifest_bytes,
        manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        pack_builds=builds,
        strict_round_trip_valid=round_trip_valid,
        references=references,
        compatibility=compatibility,
        successor=successor,
    )


__all__ = ["CandidateManifestBuildResult", "CandidateManifestError", "build_candidate_manifest"]
