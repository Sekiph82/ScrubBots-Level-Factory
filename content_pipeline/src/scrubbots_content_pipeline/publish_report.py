"""Deterministic, secret-free machine and human reports for publisher attempts."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from .candidate_manifest import CandidateManifestBuildResult
from .config import PRODUCTION_TARGET
from .current_main_replay import AUTHORITY_SOURCE_PATHS, CurrentMainReplayReceipt, REPOSITORY
from .one_command_publisher import PublisherRunReport, PublisherStage
from .production_manifest_activation import ProductionManifestReasonCode
from .production_promotion import ProductionPromotionReport, PromotionReasonCode
from .staging_download_verify import StagingDownloadVerificationReport
from .staging_manifest_publish import StagingManifestPublishReport
from .staging_pack_upload import StagingPackUploadReport

PUBLISH_REPORT_SCHEMA = "scrubbots.content.publish-report.v1"
PUBLISH_REPORT_SCHEMA_VERSION = 1
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SAFE_CODE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SAFE_KEY_PART = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UTC = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")


@dataclass(frozen=True, slots=True)
class PublishReport:
    """Immutable canonical machine report; human output derives from its bytes."""

    report_digest: str
    canonical_json_bytes: bytes

    def to_dict(self) -> dict[str, object]:
        value = json.loads(self.canonical_json_bytes.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("invalid canonical report")
        return value

    def to_json_bytes(self) -> bytes:
        return self.canonical_json_bytes

    def render_human(self) -> str:
        return render_publish_report(self)


def build_publish_report(
    run: PublisherRunReport,
    *,
    level_factory_commit_sha: str,
    report_timestamp_utc: str | None = None,
) -> PublishReport:
    """Bind typed publish evidence into canonical JSON with an explicit digest rule."""
    if not isinstance(run, PublisherRunReport) or not isinstance(level_factory_commit_sha, str) or not _GIT_SHA.fullmatch(level_factory_commit_sha):
        raise ValueError("invalid report source identity")
    if report_timestamp_utc is not None and not _valid_timestamp(report_timestamp_utc):
        raise ValueError("invalid explicit UTC report timestamp")
    payload: dict[str, object] = {
        "schema": PUBLISH_REPORT_SCHEMA,
        "schema_version": PUBLISH_REPORT_SCHEMA_VERSION,
        "level_factory_commit_sha": level_factory_commit_sha,
        "report_timestamp_utc": report_timestamp_utc,
        "mode": run.mode.value,
        "accepted": run.accepted is True,
        "terminal_stage": run.terminal_stage.value,
        "reason_code": _code(run.reason_code),
        "failure": None if run.accepted else {
            "stage": run.terminal_stage.value, "reason_code": _code(run.reason_code),
        },
        "candidate_manifest": _candidate(run.candidate),
        "validation_only_outcome": _validation(run),
        "staging": _staging(run),
        "current_main_replay": _current_main(run.current_main_replay),
        "owner_approval_state": _owner_approval_state(run),
        "production": _production(run),
        "release_state": _release_state(run),
        "production_mutated": _production_mutated(run),
        "production_mutation_state": _production_mutation_state(run),
        "production_manifest_mutated": _production_manifest_mutated(run),
        "production_manifest_mutation_state": _production_manifest_mutation_state(run),
        "journal": [
            {"sequence": _positive_int(item.sequence), "stage": item.stage.value,
             "accepted": item.accepted is True, "reason_code": _code(item.reason_code),
             "evidence_sha256": _digest(item.evidence_sha256)}
            for item in run.journal
        ],
    }
    digest = hashlib.sha256(_canonical(payload)).hexdigest()
    final = dict(payload)
    final["report_digest"] = digest
    return PublishReport(digest, _canonical(final))


def serialize_publish_report(report: PublishReport) -> bytes:
    if not isinstance(report, PublishReport):
        raise TypeError("report must be a PublishReport")
    document = report.to_dict()
    digest = document.pop("report_digest", None)
    if digest != report.report_digest or hashlib.sha256(_canonical(document)).hexdigest() != digest:
        raise ValueError("publish report digest mismatch")
    return report.canonical_json_bytes


def render_publish_report(report: PublishReport) -> str:
    """Render stable Markdown using only fields in the canonical machine report."""
    doc = report.to_dict()
    lines = [
        "# Content publish report", "",
        f"- Report digest: {doc['report_digest']}",
        f"- Schema: {doc['schema']} v{doc['schema_version']}",
        f"- Level Factory commit: {doc['level_factory_commit_sha']}",
        f"- Mode/result: {doc['mode']} / {'ACCEPTED' if doc['accepted'] else 'REJECTED'}",
        f"- Terminal stage/reason: {doc['terminal_stage']} / {doc['reason_code']}",
        f"- Production mutated: {str(doc['production_mutated']).lower()} ({doc['production_mutation_state']})",
        f"- Production manifest mutated: {str(doc['production_manifest_mutated']).lower()} ({doc['production_manifest_mutation_state']})",
        "", "## Candidate manifest",
    ]
    candidate = doc["candidate_manifest"]
    if candidate is None:
        lines.append("- Not produced")
    else:
        lines.extend([
            f"- SHA-256: {candidate['sha256']}",
            f"- Content version: {candidate['content_version']}",
            f"- Minimum game version: {candidate['minimum_game_version']}",
        ])
        for pack in candidate["packs"]:
            levels = ", ".join(pack["level_ids"])
            lines.append(
                f"- Pack {pack['pack_id']} v{pack['pack_version']}: {pack['sha256']} "
                f"({pack['byte_length']} bytes; levels {levels})"
            )
    lines.extend(["", "## Gate outcomes"])
    for name, value in (
        ("Validation-only", doc["validation_only_outcome"]),
        ("STAGING", doc["staging"]),
        ("Current-main replay", doc["current_main_replay"]),
        ("Owner approval", doc["owner_approval_state"]),
        ("PRODUCTION", doc["production"]),
    ):
        lines.append(f"- {name}: {_human_status(value)}")
    replay = doc["current_main_replay"]
    lines.extend(["", "## Current-main evidence"])
    authority = replay["game_authority"]
    if authority is None:
        lines.append(f"- Replay: {replay['reason_code']}")
    else:
        lines.append(f"- ScrubBots main commit: {authority['commit']}")
        lines.append(f"- Replay manifest SHA-256: {replay['manifest_sha256']}")
        for path, digest in sorted(authority["source_sha256"].items()):
            lines.append(f"- Authority {path}: {digest}")
        for pack in replay["packs"]:
            for level in pack["levels"]:
                lines.append(
                    f"- Level {level['level_id']}: {level['solver_status']}; "
                    f"replay_ok={str(level['replay_ok']).lower()}; "
                    f"replay_solved={str(level['replay_solved']).lower()}; "
                    f"final_active={level['final_active']}; unresolved={level['unresolved']}; "
                    f"supply_exhausted={str(level['supply_exhausted']).lower()}"
                )
    production = doc["production"]
    identity = production["resulting_identity"]
    lines.extend(["", "## Production identity"])
    if identity is None:
        lines.append("- No verified resulting production identity")
    else:
        lines.append(f"- Manifest SHA-256: {identity['manifest_sha256']}")
        lines.append(f"- Content version: {identity['content_version']}")
        lines.append(f"- Target: {identity['production_target_id']}")
        lines.append(f"- Promoted event digest: {identity['production_promoted_event_digest']}")
    lines.extend(["", "## Release-state events"])
    if not doc["release_state"]["events"]:
        lines.append("- None")
    else:
        for event in doc["release_state"]["events"]:
            lines.append(
                f"- {event['sequence']} {event['environment']} {event['state']}: "
                f"{event['event_digest']} (content {event['content_digest']})"
            )
    if doc["failure"] is not None:
        lines.append(f"- Failure: {doc['failure']['stage']} / {doc['failure']['reason_code']}")
    return "\n".join(lines) + "\n"


def _candidate(candidate: CandidateManifestBuildResult | None) -> dict[str, object] | None:
    if candidate is None:
        return None
    manifest = candidate.manifest
    levels_by_pack: dict[str, list[str]] = {pack.pack_id: [] for pack in manifest.packs}
    for level in manifest.levels:
        levels_by_pack[level.pack_id].append(_id(level.level_id))
    return {
        "sha256": _digest(candidate.manifest_sha256),
        "content_version": _positive_int(manifest.content_version),
        "minimum_game_version": _version(manifest.minimum_game_version),
        "packs": [
            {"pack_id": _id(pack.pack_id), "pack_version": _positive_int(pack.pack_version),
             "object_key": _object_key(pack.object_key), "sha256": _digest(pack.sha256),
             "byte_length": _nonnegative_int(pack.byte_length),
             "level_ids": sorted(levels_by_pack[pack.pack_id])}
            for pack in manifest.packs
        ],
    }


def _validation(run: PublisherRunReport) -> dict[str, object]:
    value = run.validation
    if value is None:
        return {"accepted": False, "reason_code": "NOT_RUN", "environment": None, "target_id": None}
    return {
        "accepted": value.accepted is True,
        "reason_code": "VALID" if value.accepted is True else "CONFIG_REJECTED",
        "schema_version": _version(value.schema_version),
        "environment": _code(value.environment.upper()),
        "target_id": _optional_target_id(value.target_id),
        "target_version": _optional_id(value.target_version),
    }


def _stage(run: PublisherRunReport, stage: PublisherStage) -> dict[str, object]:
    entry = next((item for item in run.journal if item.stage is stage), None)
    if entry is None:
        return {"accepted": False, "reason_code": "NOT_RUN"}
    return {"accepted": entry.accepted is True, "reason_code": _code(entry.reason_code)}


def _staging(run: PublisherRunReport) -> dict[str, object]:
    return {
        "upload": _upload(run.staging_upload),
        "integrity": _stage(run, PublisherStage.STAGING_OBJECT_INTEGRITY),
        "manifest": _manifest_publish(run.staging_publish),
        "download_verification": _download(run.staging_download),
    }


def _upload(report: StagingPackUploadReport | None) -> dict[str, object]:
    if report is None:
        return {"accepted": False, "reason_code": "NOT_RUN", "packs": []}
    return {
        "accepted": report.accepted is True, "reason_code": _code(report.reason_code.value),
        "manifest_sha256": _optional_digest(report.manifest_sha256),
        "manifest_write_authorized": report.manifest_write_authorized is True,
        "object_write_attempted": report.object_write_attempted is True,
        "packs": [
            {"pack_id": _id(item.pack_id), "object_key": _object_key(item.object_key),
             "sha256": _digest(item.sha256), "byte_length": _nonnegative_int(item.byte_length)}
            for item in report.uploaded_packs
        ],
    }


def _manifest_publish(report: StagingManifestPublishReport | None) -> dict[str, object]:
    if report is None:
        return {"accepted": False, "reason_code": "NOT_RUN", "manifest_write_attempted": False}
    receipt = report.receipt
    return {
        "accepted": report.accepted is True, "reason_code": _code(report.reason_code.value),
        "manifest_write_attempted": report.manifest_write_attempted is True,
        "references_revalidated": report.references_revalidated is True,
        "manifest_sha256": _optional_digest(receipt.manifest_sha256 if receipt else None),
        "content_version": _positive_int(receipt.content_version) if receipt else None,
    }


def _download(report: StagingDownloadVerificationReport | None) -> dict[str, object]:
    if report is None:
        return {"accepted": False, "reason_code": "NOT_RUN", "manifest_read": False, "packs": []}
    receipt = report.receipt
    return {
        "accepted": report.accepted is True, "reason_code": _code(report.reason_code.value),
        "manifest_read": report.manifest_read is True,
        "manifest_sha256": _optional_digest(receipt.manifest_sha256 if receipt else None),
        "content_version": _positive_int(receipt.content_version) if receipt else None,
        "packs": [
            {"pack_id": _id(item.pack_id), "object_key": _object_key(item.object_key),
             "sha256": _digest(item.sha256), "byte_length": _nonnegative_int(item.byte_length),
             "level_ids": sorted(_id(level_id) for level_id in item.level_ids)}
            for item in receipt.packs
        ] if receipt else [],
    }


def _current_main(receipt: CurrentMainReplayReceipt | None) -> dict[str, object]:
    if receipt is None:
        return {"accepted": False, "reason_code": "NOT_RUN", "manifest_sha256": None,
                "game_authority": None, "packs": []}
    authority = None
    commit = receipt.game_commit if _GIT_SHA.fullmatch(receipt.game_commit or "") else None
    if receipt.game_repository == REPOSITORY and receipt.game_branch == "main" and commit is not None:
        source = receipt.authority_source_sha256
        if isinstance(source, Mapping) and set(source) == set(AUTHORITY_SOURCE_PATHS):
            source_hashes = {key: _digest(source[key]) for key in sorted(AUTHORITY_SOURCE_PATHS)}
            authority = {"repository": REPOSITORY, "branch": "main", "commit": commit,
                         "source_sha256": source_hashes}
    packs = []
    for row in receipt.pack_results:
        if not isinstance(row, Mapping):
            raise ValueError("invalid replay report evidence")
        raw_levels = row.get("levels", ())
        if not isinstance(raw_levels, (tuple, list)):
            raise ValueError("invalid replay level evidence")
        levels = []
        for level in raw_levels:
            if not isinstance(level, Mapping):
                raise ValueError("invalid replay level evidence")
            levels.append({
                "level_id": _id(level.get("level_id")),
                "level_sha256": _optional_digest(level.get("level_sha256")),
                "plan_sha256": _optional_digest(level.get("plan_sha256")),
                "fifo_columns": _fifo_columns(level.get("fifo_columns")),
                "solver_state_sha256": _optional_digest(level.get("solver_state_sha256")),
                "solver_evidence_sha256": _optional_digest(level.get("solver_evidence_sha256")),
                "accepted": level.get("accepted") is True,
                "solver_status": _optional_code(level.get("solver_status")),
                "replay_ok": level.get("replay_ok") is True,
                "replay_solved": level.get("replay_solved") is True,
                "final_active": _nonnegative_int(level.get("final_active")),
                "unresolved": _nonnegative_int(level.get("unresolved")),
                "supply_exhausted": level.get("supply_exhausted") is True,
            })
        packs.append({"pack_id": _id(row.get("pack_id")), "pack_sha256": _digest(row.get("pack_sha256")),
                      "levels": sorted(levels, key=lambda item: item["level_id"])})
    return {
        "accepted": receipt.accepted is True, "reason_code": _code(receipt.reason_code),
        "manifest_sha256": _optional_digest(receipt.manifest_sha256),
        "game_authority": authority, "packs": sorted(packs, key=lambda item: item["pack_id"]),
    }


def _owner_approval_state(run: PublisherRunReport) -> str:
    if run.mode.value != "PRODUCTION":
        return "NOT_REQUIRED"
    promotion = run.production_promotion
    if promotion is None:
        return "REQUIRED_NOT_PROVIDED_OR_INVALID" if run.reason_code == "EXPLICIT_PRODUCTION_AUTHORITY_REQUIRED" else "NOT_REACHED"
    if promotion.reason_code is PromotionReasonCode.OWNER_APPROVAL_REQUIRED:
        return "REQUIRED_NOT_PROVIDED_OR_INVALID"
    if promotion.reason_code is PromotionReasonCode.OWNER_APPROVAL_LOST:
        return "NOT_CURRENT"
    if promotion.reason_code in {
        PromotionReasonCode.STAGING_NOT_VERIFIED,
        PromotionReasonCode.REPLAY_NOT_ACCEPTED,
        PromotionReasonCode.MANIFEST_PRECONDITION_FAILED,
    }:
        return "NOT_REACHED"
    return "ACCEPTED_BY_PROMOTION_GATE"


def _production(run: PublisherRunReport) -> dict[str, object]:
    promotion, activation = run.production_promotion, run.production_activation
    return {
        "pack_promotion": _promotion(promotion),
        "manifest_activation": _activation(activation),
        "cas": {
            "promotion_manifest_write_attempted": promotion.manifest_write_attempted is True if promotion else False,
            "activation_manifest_write_attempted": activation.manifest_write_attempted is True if activation else False,
            "activation_reason_code": _code(activation.reason_code.value) if activation else "NOT_RUN",
        },
        "resulting_identity": _production_identity(run),
    }


def _promotion(report: ProductionPromotionReport | None) -> dict[str, object]:
    if report is None:
        return {"accepted": False, "reason_code": "NOT_RUN", "manifest_write_attempted": False, "packs": []}
    return {
        "accepted": report.accepted is True, "reason_code": _code(report.reason_code.value),
        "manifest_write_attempted": report.manifest_write_attempted is True,
        "manifest_sha256": _optional_digest(report.manifest_sha256),
        "packs": [
            {"pack_id": _id(item.pack_id), "source_object_key": _object_key(item.source_object_key),
             "production_object_key": _object_key(item.production_object_key), "sha256": _digest(item.sha256),
             "byte_length": _nonnegative_int(item.byte_length), "verified": item.verified is True}
            for item in report.promoted_objects
        ],
    }


def _activation(report: object) -> dict[str, object]:
    if report is None:
        return {"accepted": False, "reason_code": "NOT_RUN", "manifest_write_attempted": False}
    receipt = report.receipt
    return {
        "accepted": report.accepted is True, "reason_code": _code(report.reason_code.value),
        "manifest_write_attempted": report.manifest_write_attempted is True,
        "manifest_sha256": _optional_digest(receipt.manifest_sha256 if receipt else None),
        "content_version": _positive_int(receipt.content_version) if receipt else None,
    }


def _production_identity(run: PublisherRunReport) -> dict[str, object] | None:
    activation = run.production_activation
    receipt = activation.receipt if activation is not None else None
    if receipt is None:
        if not (
            activation is not None and activation.accepted is True
            and activation.reason_code is ProductionManifestReasonCode.ALREADY_CURRENT
            and run.candidate is not None and activation.release_event is not None
        ):
            return None
        production_packs = {
            item.pack_id: item for item in (
                run.production_promotion.promoted_objects if run.production_promotion is not None else ()
            )
        }
        if (
            len(production_packs) != len(run.candidate.manifest.packs)
            or run.staging_publish is None or run.staging_publish.receipt is None
        ):
            return None
        return {
            "confirmation": "ALREADY_CURRENT",
            "manifest_sha256": _digest(run.candidate.manifest_sha256),
            "content_version": _positive_int(run.candidate.manifest.content_version),
            "production_target_id": _optional_target_id(PRODUCTION_TARGET.logical_target_id),
            "manifest_object_key": _object_key(run.staging_publish.receipt.manifest_object_key),
            "game_commit": (
                run.current_main_replay.game_commit
                if run.current_main_replay is not None and _GIT_SHA.fullmatch(run.current_main_replay.game_commit or "")
                else None
            ),
            "production_promoted_event_digest": _digest(activation.release_event.event_digest),
            "history_tip_sha256": None,
            "packs": [
                {
                    "pack_id": _id(pack.pack_id),
                    "object_key": _object_key(
                        production_packs[pack.pack_id].production_object_key
                    ),
                    "sha256": _digest(pack.sha256),
                    "byte_length": _nonnegative_int(pack.byte_length),
                    "verified_before_write": True,
                    "verified_after_write": True,
                }
                for pack in run.candidate.manifest.packs
            ],
        }
    return {
        "manifest_sha256": _digest(receipt.manifest_sha256),
        "content_version": _positive_int(receipt.content_version),
        "production_target_id": _optional_target_id(receipt.production_target_id),
        "manifest_object_key": _object_key(receipt.manifest_object_key),
        "game_commit": receipt.game_commit if _GIT_SHA.fullmatch(receipt.game_commit) else None,
        "production_promoted_event_digest": _digest(receipt.production_promoted_event.event_digest),
        "history_tip_sha256": _digest(receipt.history_tip_sha256),
        "packs": [
            {"pack_id": _id(item.pack_id), "object_key": _object_key(item.object_key),
             "sha256": _digest(item.sha256), "byte_length": _nonnegative_int(item.byte_length),
             "verified_before_write": item.verified_before_write is True,
             "verified_after_write": item.verified_after_write is True}
            for item in receipt.packs
        ],
    }


def _release_state(run: PublisherRunReport) -> dict[str, object]:
    events = []
    if run.staging_publish is not None:
        events.extend(run.staging_publish.appended_release_events)
    if run.production_promotion is not None:
        events.extend(run.production_promotion.release_events)
    if run.production_activation is not None and run.production_activation.release_event is not None:
        events.append(run.production_activation.release_event)
    return {
        "events": [
            {"sequence": _positive_int(event.sequence), "environment": _code(event.environment.value.upper()),
             "state": _code(event.to_state.value), "event_digest": _digest(event.event_digest),
             "content_digest": _digest(event.content_digest)}
            for event in events
        ],
        "resulting_production_identity": _production_identity(run),
    }


def _production_mutated(run: PublisherRunReport) -> bool:
    if _production_manifest_mutated(run):
        return True
    promotion = run.production_promotion
    return bool(promotion is not None and (promotion.promoted_objects or promotion.release_events))


def _production_manifest_mutated(run: PublisherRunReport) -> bool:
    activation = run.production_activation
    return bool(activation is not None and activation.accepted is True
                and activation.reason_code is ProductionManifestReasonCode.ACTIVATED
                and activation.receipt is not None)


def _production_mutation_state(run: PublisherRunReport) -> str:
    activation = run.production_activation
    if _production_mutated(run):
        return "CONFIRMED"
    if (activation is not None and activation.accepted
            and activation.reason_code is ProductionManifestReasonCode.ALREADY_CURRENT):
        return "ALREADY_CURRENT"
    if activation is None or not activation.manifest_write_attempted:
        promotion = run.production_promotion
        if promotion is None or promotion.reason_code in {
            PromotionReasonCode.STAGING_NOT_VERIFIED,
            PromotionReasonCode.REPLAY_NOT_ACCEPTED,
            PromotionReasonCode.MANIFEST_PRECONDITION_FAILED,
            PromotionReasonCode.OWNER_APPROVAL_REQUIRED,
            PromotionReasonCode.OWNER_APPROVAL_LOST,
            PromotionReasonCode.GAME_AUTHORITY_STALE,
            PromotionReasonCode.INVALID_HISTORY,
            PromotionReasonCode.INVALID_PROVIDER,
            PromotionReasonCode.CAPABILITY_REJECTED,
        }:
            return "NO_NEW_MUTATION_CONFIRMED"
        return "UNCONFIRMED_AFTER_PRODUCTION_ATTEMPT"
    return "UNCONFIRMED_AFTER_WRITE_ATTEMPT"


def _production_manifest_mutation_state(run: PublisherRunReport) -> str:
    activation = run.production_activation
    if _production_manifest_mutated(run):
        return "CONFIRMED"
    if (activation is not None and activation.accepted
            and activation.reason_code is ProductionManifestReasonCode.ALREADY_CURRENT):
        return "ALREADY_CURRENT"
    if activation is None or not activation.manifest_write_attempted:
        return "NO_NEW_MANIFEST_MUTATION_CONFIRMED"
    return "UNCONFIRMED_AFTER_WRITE_ATTEMPT"


def _human_status(value: object) -> str:
    if isinstance(value, Mapping):
        if "accepted" in value:
            return "ACCEPTED" if value.get("accepted") is True else str(value.get("reason_code", "REJECTED"))
        return "; ".join(f"{key}: {_human_status(nested)}" for key, nested in sorted(value.items()))
    return str(value)


def _code(value: object) -> str:
    result = str(value)
    if not _SAFE_CODE.fullmatch(result):
        raise ValueError("unsafe or unbounded reason code")
    return result


def _optional_code(value: object) -> str | None:
    return _code(value) if isinstance(value, str) and _SAFE_CODE.fullmatch(value) else None


def _id(value: object) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        raise ValueError("invalid report identifier")
    return value


def _optional_id(value: object) -> str | None:
    return _id(value) if value is not None else None


def _optional_target_id(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > 128 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", value):
        raise ValueError("invalid logical target identifier")
    return value


def _object_key(value: object) -> str:
    if not isinstance(value, str) or len(value) > 512 or "://" in value or "\\" in value or value.startswith("/"):
        raise ValueError("invalid provider-neutral object key")
    parts = value.split("/")
    if any(part in {"", ".", ".."} or not _SAFE_KEY_PART.fullmatch(part) for part in parts):
        raise ValueError("invalid provider-neutral object key")
    return value


def _version(value: object) -> str:
    if not isinstance(value, str) or len(value) > 64 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+_-]*", value):
        raise ValueError("invalid version text")
    return value


def _digest(value: object) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ValueError("invalid SHA-256 evidence")
    return value


def _optional_digest(value: object) -> str | None:
    return _digest(value) if value is not None else None


def _nonnegative_int(value: object) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("invalid nonnegative integer evidence")
    return value


def _fifo_columns(value: object) -> list[list[dict[str, object]]]:
    if not isinstance(value, (tuple, list)) or not value or len(value) > 4096:
        raise ValueError("invalid FIFO conservation evidence")
    columns = []
    for column in value:
        if not isinstance(column, (tuple, list)) or not column or len(column) > 4096:
            raise ValueError("invalid FIFO conservation evidence")
        entries = []
        for entry in column:
            if not isinstance(entry, Mapping) or set(entry) != {"batchId", "cid", "robots"}:
                raise ValueError("invalid FIFO conservation evidence")
            entries.append({
                "batchId": _id(entry.get("batchId")),
                "cid": _id(entry.get("cid")),
                "robots": _positive_int(entry.get("robots")),
            })
        columns.append(entries)
    return columns


def _positive_int(value: object) -> int:
    if type(value) is not int or value < 1:
        raise ValueError("invalid positive integer evidence")
    return value


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not _UTC.fullmatch(value):
        return False
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%dT%H:%M:%SZ") == value
    except ValueError:
        return False


def _canonical(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"


__all__ = [
    "PUBLISH_REPORT_SCHEMA", "PUBLISH_REPORT_SCHEMA_VERSION", "PublishReport",
    "build_publish_report", "render_publish_report", "serialize_publish_report",
]
