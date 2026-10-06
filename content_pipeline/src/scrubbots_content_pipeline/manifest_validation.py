"""Pure local reference validation for a versioned content manifest."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .manifest_v1 import ContentManifestV1
from .scrubpack_builder import ScrubpackBuildEvidence, ScrubpackBuildResult, verify_scrubpack_build


class ManifestReferenceReasonCode(str, Enum):
    VALID = "VALID"
    INVALID_MANIFEST = "INVALID_MANIFEST"
    INVALID_EVIDENCE_SET = "INVALID_EVIDENCE_SET"
    DUPLICATE_PACK_EVIDENCE = "DUPLICATE_PACK_EVIDENCE"
    MISSING_PACK_EVIDENCE = "MISSING_PACK_EVIDENCE"
    UNDECLARED_PACK_EVIDENCE = "UNDECLARED_PACK_EVIDENCE"
    LEVEL_PACK_NOT_DECLARED = "LEVEL_PACK_NOT_DECLARED"
    DISABLED_LEVEL_NOT_DECLARED = "DISABLED_LEVEL_NOT_DECLARED"
    SCHEDULE_TARGET_NOT_DECLARED = "SCHEDULE_TARGET_NOT_DECLARED"
    DUPLICATE_PACK_ID = "DUPLICATE_PACK_ID"
    DUPLICATE_PACK_OBJECT_KEY = "DUPLICATE_PACK_OBJECT_KEY"
    CONFLICTING_LEVEL_OWNERSHIP = "CONFLICTING_LEVEL_OWNERSHIP"
    PACK_ID_MISMATCH = "PACK_ID_MISMATCH"
    PACK_VERSION_MISMATCH = "PACK_VERSION_MISMATCH"
    PACK_SHA256_MISMATCH = "PACK_SHA256_MISMATCH"
    PACK_BYTE_LENGTH_MISMATCH = "PACK_BYTE_LENGTH_MISMATCH"
    PACK_MEMBERSHIP_MISMATCH = "PACK_MEMBERSHIP_MISMATCH"
    PACK_ARCHIVE_INVALID = "PACK_ARCHIVE_INVALID"


@dataclass(frozen=True, slots=True)
class ManifestReferenceCheck:
    check_id: str
    accepted: bool
    reason_code: ManifestReferenceReasonCode

    def to_dict(self) -> dict[str, object]:
        return {"accepted": self.accepted, "check_id": self.check_id, "reason_code": self.reason_code.value}


@dataclass(frozen=True, slots=True)
class ManifestReferenceValidationResult:
    eligible: bool
    checks: tuple[ManifestReferenceCheck, ...]

    def to_dict(self) -> dict[str, object]:
        return {"checks": [check.to_dict() for check in self.checks], "eligible": self.eligible}


def _check(check_id: str, reason_code: ManifestReferenceReasonCode) -> ManifestReferenceCheck:
    return ManifestReferenceCheck(check_id, reason_code is ManifestReferenceReasonCode.VALID, reason_code)


def validate_manifest_references(
    manifest: object, pack_builds: object
) -> ManifestReferenceValidationResult:
    """Fail closed unless local immutable M12 build evidence binds every manifest reference."""
    if not isinstance(manifest, ContentManifestV1):
        checks = (_check("manifest_contract", ManifestReferenceReasonCode.INVALID_MANIFEST),)
        return ManifestReferenceValidationResult(False, checks)

    packs = tuple(manifest.packs)
    levels = tuple(manifest.levels)
    pack_ids = {pack.pack_id.casefold() for pack in packs}
    level_ids = {level.level_id.casefold() for level in levels}
    pack_by_id = {pack.pack_id.casefold(): pack for pack in packs}

    checks: list[ManifestReferenceCheck] = [_check("manifest_contract", ManifestReferenceReasonCode.VALID)]

    declared_pack_ids = [pack.pack_id.casefold() for pack in packs]
    if len(declared_pack_ids) != len(set(declared_pack_ids)):
        pack_identity_reason = ManifestReferenceReasonCode.DUPLICATE_PACK_ID
    elif len({pack.object_key for pack in packs}) != len(packs):
        pack_identity_reason = ManifestReferenceReasonCode.DUPLICATE_PACK_OBJECT_KEY
    else:
        pack_identity_reason = ManifestReferenceReasonCode.VALID
    checks.append(_check("pack_identity_unique", pack_identity_reason))

    ownership: dict[str, set[str]] = {}
    for level in levels:
        ownership.setdefault(level.level_id.casefold(), set()).add(level.pack_id.casefold())
    ownership_reason = (
        ManifestReferenceReasonCode.CONFLICTING_LEVEL_OWNERSHIP
        if any(len(owners) > 1 for _, owners in sorted(ownership.items()))
        else ManifestReferenceReasonCode.VALID
    )
    checks.append(_check("level_ownership_unique", ownership_reason))

    level_pack_reason = (
        ManifestReferenceReasonCode.LEVEL_PACK_NOT_DECLARED
        if any(level.pack_id.casefold() not in pack_ids for level in levels)
        else ManifestReferenceReasonCode.VALID
    )
    checks.append(_check("level_pack_references", level_pack_reason))

    disabled_reason = (
        ManifestReferenceReasonCode.DISABLED_LEVEL_NOT_DECLARED
        if any(level_id.casefold() not in level_ids for level_id in manifest.disabled_levels)
        else ManifestReferenceReasonCode.VALID
    )
    checks.append(_check("disabled_level_references", disabled_reason))

    schedule_reason = ManifestReferenceReasonCode.VALID
    for schedule in manifest.schedules:
        target_exists = (
            schedule.target_id.casefold() in pack_ids
            if schedule.target_kind == "pack"
            else schedule.target_id.casefold() in level_ids
        )
        if not target_exists:
            schedule_reason = ManifestReferenceReasonCode.SCHEDULE_TARGET_NOT_DECLARED
            break
    checks.append(_check("schedule_target_references", schedule_reason))

    if not isinstance(pack_builds, (tuple, list)) or any(
        not isinstance(build, ScrubpackBuildResult)
        or type(build.archive_bytes) is not bytes
        or not isinstance(build.evidence, ScrubpackBuildEvidence)
        or not isinstance(build.evidence.pack_id, str)
        for build in pack_builds
    ):
        checks.append(_check("pack_evidence_set", ManifestReferenceReasonCode.INVALID_EVIDENCE_SET))
        builds: tuple[ScrubpackBuildResult, ...] = ()
    else:
        builds = tuple(pack_builds)

    grouped_builds: dict[str, list[ScrubpackBuildResult]] = {}
    for build in builds:
        grouped_builds.setdefault(build.evidence.pack_id.casefold(), []).append(build)
    duplicate_evidence = any(len(group) > 1 for _, group in sorted(grouped_builds.items()))
    missing_evidence = any(pack.pack_id.casefold() not in grouped_builds for pack in packs)
    undeclared_evidence = any(pack_id not in pack_by_id for pack_id in grouped_builds)
    if "pack_evidence_set" not in {check.check_id for check in checks}:
        if duplicate_evidence:
            evidence_set_reason = ManifestReferenceReasonCode.DUPLICATE_PACK_EVIDENCE
        elif missing_evidence:
            evidence_set_reason = ManifestReferenceReasonCode.MISSING_PACK_EVIDENCE
        elif undeclared_evidence:
            evidence_set_reason = ManifestReferenceReasonCode.UNDECLARED_PACK_EVIDENCE
        else:
            evidence_set_reason = ManifestReferenceReasonCode.VALID
        checks.append(_check("pack_evidence_set", evidence_set_reason))

    def evidence_reason(
        mismatch_reason: ManifestReferenceReasonCode,
        compare: Callable[[object, ScrubpackBuildResult], bool],
    ) -> ManifestReferenceReasonCode:
        for pack in sorted(packs, key=lambda item: item.pack_id.encode("ascii")):
            matches = grouped_builds.get(pack.pack_id.casefold(), [])
            if not matches:
                return ManifestReferenceReasonCode.MISSING_PACK_EVIDENCE
            if len(matches) != 1:
                return ManifestReferenceReasonCode.DUPLICATE_PACK_EVIDENCE
            build = matches[0]
            try:
                matches_reference = compare(pack, build)
            except (AttributeError, TypeError, ValueError):
                return ManifestReferenceReasonCode.INVALID_EVIDENCE_SET
            if not matches_reference:
                return mismatch_reason
        return ManifestReferenceReasonCode.VALID

    checks.extend(
        (
            _check(
                "pack_id_binding",
                evidence_reason(ManifestReferenceReasonCode.PACK_ID_MISMATCH, lambda pack, build: build.evidence.pack_id == pack.pack_id),
            ),
            _check(
                "pack_version_binding",
                evidence_reason(
                    ManifestReferenceReasonCode.PACK_VERSION_MISMATCH, lambda pack, build: build.evidence.pack_version == pack.pack_version
                ),
            ),
            _check(
                "pack_sha256_binding",
                evidence_reason(ManifestReferenceReasonCode.PACK_SHA256_MISMATCH, lambda pack, build: build.evidence.archive_sha256 == pack.sha256),
            ),
            _check(
                "pack_byte_length_binding",
                evidence_reason(
                    ManifestReferenceReasonCode.PACK_BYTE_LENGTH_MISMATCH, lambda pack, build: build.evidence.archive_byte_length == pack.byte_length
                ),
            ),
        )
    )

    expected_membership: dict[str, set[str]] = {pack_id: set() for pack_id in pack_ids}
    for level in levels:
        expected_membership.setdefault(level.pack_id.casefold(), set()).add(level.level_id)
    membership_reason = evidence_reason(
        ManifestReferenceReasonCode.PACK_MEMBERSHIP_MISMATCH,
        lambda pack, build: set(build.evidence.level_ids) == expected_membership.get(pack.pack_id.casefold(), set()),
    )
    checks.append(_check("pack_level_membership", membership_reason))

    archive_reason = evidence_reason(
        ManifestReferenceReasonCode.PACK_ARCHIVE_INVALID,
        lambda _pack, build: _verify_build(build),
    )
    checks.append(_check("pack_archive_integrity", archive_reason))

    ordered_checks = tuple(checks)
    return ManifestReferenceValidationResult(all(check.accepted for check in ordered_checks), ordered_checks)


__all__ = [
    "ManifestReferenceCheck",
    "ManifestReferenceReasonCode",
    "ManifestReferenceValidationResult",
    "validate_manifest_references",
]


def _verify_build(build: ScrubpackBuildResult) -> bool:
    try:
        if build.solver_identity_artifact_bytes is not None:
            from .scrubpack_solver_identity import verify_solver_proven_scrubpack

            return verify_solver_proven_scrubpack(
                build.archive_bytes, build.solver_identity_artifact_bytes, build.evidence
            )
        return verify_scrubpack_build(build.archive_bytes, build.evidence)
    except Exception:
        return False
