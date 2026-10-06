"""Strict one-command composition of the independently testable M14 publisher stages."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from .candidate_manifest import CandidateManifestBuildResult, build_candidate_manifest
from .config import PRODUCTION_TARGET, STAGING_TARGET, Environment, EnvironmentTarget, PipelineConfig
from .current_main_replay import CurrentMainReplayReceipt, verify_current_main_supply_replay
from .manifest_history import ManifestHistoryV1
from .production_manifest_activation import (
    ProductionManifestActivationReport, ProductionManifestReasonCode,
    activate_versioned_production_manifest,
)
from .production_promotion import (
    OwnerPromotionApproval, ProductionManifestPrecondition, ProductionPromotionReport,
    promote_verified_staging_to_production,
)
from .provider import (
    PROVIDER_CONTRACT_VERSION, ProviderObjectBytesResult, ProviderResult,
    ProviderResultCategory,
    ProductionPromotionProvider,
)
from .publication_plan import PublicationPlan
from .publisher_validation import PublisherValidationReport, validate_publisher_candidate
from .release_state import ReleaseEvent, ReleaseReplayResult, replay_release_events
from .scrubpack_builder import ScrubpackBuildResult
from .scrubpack_solver_identity import verify_solver_proven_scrubpack
from .staging_download_verify import (
    StagingDownloadVerificationReport, verify_staged_manifest_download,
)
from .manifest_v1 import ManifestScheduleV1
from .staging_manifest_publish import (
    StagingManifestPrecondition, StagingManifestPublishReport,
    publish_candidate_manifest_to_staging,
)
from .staging_pack_upload import StagingPackUploadReport, upload_candidate_packs_to_staging
from .validation import DryRunReport, validate_only


class PublisherMode(StrEnum):
    VALIDATION_ONLY = "VALIDATION_ONLY"
    STAGING_ONLY = "STAGING_ONLY"
    PRODUCTION = "PRODUCTION"


class PublisherStage(StrEnum):
    CONFIG_VALIDATION = "CONFIG_VALIDATION"
    REQUEST_PREFLIGHT = "REQUEST_PREFLIGHT"
    FACTORY_PACK_BUILD = "FACTORY_PACK_BUILD"
    CANDIDATE_MANIFEST = "CANDIDATE_MANIFEST"
    PUBLISHER_VALIDATION = "PUBLISHER_VALIDATION"
    RELEASE_HISTORY_PREFLIGHT = "RELEASE_HISTORY_PREFLIGHT"
    STAGING_PACK_UPLOAD = "STAGING_PACK_UPLOAD"
    STAGING_OBJECT_INTEGRITY = "STAGING_OBJECT_INTEGRITY"
    STAGING_MANIFEST_PUBLISH = "STAGING_MANIFEST_PUBLISH"
    STAGING_RELEASE_STATE = "STAGING_RELEASE_STATE"
    STAGING_DOWNLOAD_VERIFY = "STAGING_DOWNLOAD_VERIFY"
    CURRENT_MAIN_REPLAY = "CURRENT_MAIN_REPLAY"
    PRODUCTION_PACK_PROMOTION = "PRODUCTION_PACK_PROMOTION"
    PRODUCTION_MANIFEST_ACTIVATION = "PRODUCTION_MANIFEST_ACTIVATION"
    CURRENT_STATE_FENCE = "CURRENT_STATE_FENCE"


@dataclass(frozen=True, slots=True)
class FactoryPackRequest:
    candidate_ids: tuple[str, ...]
    pack_id: str
    pack_version: int
    created_at_utc: str


class AcceptedFactoryPackBuilder(Protocol):
    """Explicit host adapter to the Factory current-acceptance/solver-proof builder."""

    def __call__(self, request: FactoryPackRequest, /) -> ScrubpackBuildResult: ...


@dataclass(frozen=True, slots=True)
class PublisherJournalEntry:
    sequence: int
    stage: PublisherStage
    accepted: bool
    reason_code: str
    evidence_sha256: str


@dataclass(frozen=True, slots=True)
class DownloadedPackBytes:
    pack_id: str
    object_key: str
    sha256: str
    byte_length: int
    content_bytes: bytes


@dataclass(frozen=True, slots=True)
class ProductionRunInputs:
    game_authority: Mapping[str, object]
    authority_check: Callable[[], Mapping[str, object]]
    game_runner: Callable[[Sequence[Mapping[str, object]]], Mapping[str, object]]
    owner_approval: OwnerPromotionApproval | None
    owner_approval_check: Callable[[], OwnerPromotionApproval | None]
    production_precondition: ProductionManifestPrecondition
    manifest_history: ManifestHistoryV1
    recorded_at_utc: str | datetime


@dataclass(frozen=True, slots=True)
class PublisherRunRequest:
    mode: PublisherMode
    config: PipelineConfig
    provider: ProductionPromotionProvider | None = None
    factory_pack_requests: tuple[FactoryPackRequest, ...] = ()
    factory_pack_builder: AcceptedFactoryPackBuilder | None = None
    content_version: int | None = None
    previous_content_version: int | None = None
    minimum_game_version: str | None = None
    current_game_version: str | None = None
    supported_manifest_schema_versions: Mapping[str, object] | None = None
    object_keys: Mapping[str, str] | None = None
    disabled_levels: tuple[str, ...] = ()
    schedules: tuple[ManifestScheduleV1, ...] = ()
    publication_plan: PublicationPlan | None = None
    current_target: EnvironmentTarget = STAGING_TARGET
    current_state: object | None = None
    current_content_digest: str | None = None
    owner_approved: bool = False
    staging_precondition: StagingManifestPrecondition | None = None
    release_events: tuple[ReleaseEvent, ...] = ()
    manifest_object_key: str = ""
    production: ProductionRunInputs | None = None


@dataclass(frozen=True, slots=True)
class PublisherRunReport:
    accepted: bool
    mode: PublisherMode
    reason_code: str
    terminal_stage: PublisherStage
    journal: tuple[PublisherJournalEntry, ...]
    validation: DryRunReport | None = None
    pack_builds: tuple[ScrubpackBuildResult, ...] = ()
    candidate: CandidateManifestBuildResult | None = None
    publisher_validation: PublisherValidationReport | None = None
    staging_upload: StagingPackUploadReport | None = None
    staging_publish: StagingManifestPublishReport | None = None
    staging_download: StagingDownloadVerificationReport | None = None
    replay_pack_bytes: tuple[DownloadedPackBytes, ...] = ()
    current_main_replay: CurrentMainReplayReceipt | None = None
    production_promotion: ProductionPromotionReport | None = None
    production_activation: ProductionManifestActivationReport | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "mode": self.mode.value,
            "reason_code": self.reason_code,
            "terminal_stage": self.terminal_stage.value,
            "journal": [
                {"sequence": item.sequence, "stage": item.stage.value,
                 "accepted": item.accepted, "reason_code": item.reason_code,
                 "evidence_sha256": item.evidence_sha256}
                for item in self.journal
            ],
            "candidate_manifest_sha256": self.candidate.manifest_sha256 if self.candidate else None,
            "production_manifest_sha256": (
                self.production_activation.receipt.manifest_sha256
                if self.production_activation is not None and self.production_activation.receipt is not None
                else None
            ),
        }


def run_one_command_publisher(request: PublisherRunRequest) -> PublisherRunReport:
    """Run validation, Factory pack, candidate, staging, replay, then optional production in order.

    The provider and Factory host adapter are explicit caller inputs. Production is
    available only in PRODUCTION mode and requires explicit owner approval. The
    function never selects a provider, discovers Factory candidates, or deletes data.
    """
    if not isinstance(request, PublisherRunRequest) or not isinstance(request.mode, PublisherMode):
        return _invalid_request(request)
    if not isinstance(request.config, PipelineConfig):
        return _invalid_request(request)
    journal: list[PublisherJournalEntry] = []
    evidence: dict[str, object] = {}

    dry_run = validate_only(request.config)
    evidence["validation"] = dry_run
    _record(journal, PublisherStage.CONFIG_VALIDATION, dry_run.accepted,
            "VALID" if dry_run.accepted else "CONFIG_REJECTED", (dry_run.schema_version,
            dry_run.environment, dry_run.target_id or ""))
    if not dry_run.accepted:
        return _report(request.mode, journal, PublisherStage.CONFIG_VALIDATION, "CONFIG_REJECTED", evidence)
    if request.mode is PublisherMode.VALIDATION_ONLY:
        return _report(request.mode, journal, PublisherStage.CONFIG_VALIDATION, "VALID", evidence, accepted=True)

    preflight_error = _preflight_error(request)
    _record(journal, PublisherStage.REQUEST_PREFLIGHT, preflight_error is None,
            "VALID" if preflight_error is None else preflight_error, ())
    if preflight_error is not None:
        return _report(request.mode, journal, PublisherStage.REQUEST_PREFLIGHT, preflight_error, evidence)

    assert request.factory_pack_builder is not None
    builds: list[ScrubpackBuildResult] = []
    try:
        for pack_request in request.factory_pack_requests:
            build = request.factory_pack_builder(pack_request)
            if (not isinstance(build, ScrubpackBuildResult)
                    or not _factory_output_matches_request(build, pack_request)
                    or not verify_solver_proven_scrubpack(
                        build.archive_bytes, build.solver_identity_artifact_bytes, build.evidence
                    )):
                raise ValueError("solver-proven Factory pack rejected")
            builds.append(build)
    except Exception:
        evidence["pack_builds"] = tuple(builds)
        _record(journal, PublisherStage.FACTORY_PACK_BUILD, False, "FACTORY_PACK_BUILD_FAILED",
                tuple(item.evidence.archive_sha256 for item in builds))
        return _report(request.mode, journal, PublisherStage.FACTORY_PACK_BUILD,
                       "FACTORY_PACK_BUILD_FAILED", evidence)
    pack_builds = tuple(builds)
    evidence["pack_builds"] = pack_builds
    _record(journal, PublisherStage.FACTORY_PACK_BUILD, True, "SOLVER_PROVEN_PACKS_BUILT",
            tuple(f"{item.evidence.pack_id}:{item.evidence.archive_sha256}:"
                  f"{item.evidence.solver_identity_artifact_sha256 or ''}" for item in pack_builds))

    try:
        candidate = build_candidate_manifest(
            pack_builds,
            content_version=request.content_version,
            minimum_game_version=request.minimum_game_version,
            object_keys=request.object_keys,
            current_game_version=request.current_game_version,
            supported_manifest_schema_versions=request.supported_manifest_schema_versions,
            disabled_levels=request.disabled_levels,
            schedules=request.schedules,
            prior_accepted_content_version=request.previous_content_version,
        )
    except Exception:
        _record(journal, PublisherStage.CANDIDATE_MANIFEST, False, "CANDIDATE_MANIFEST_REJECTED", ())
        return _report(request.mode, journal, PublisherStage.CANDIDATE_MANIFEST,
                       "CANDIDATE_MANIFEST_REJECTED", evidence)
    evidence["candidate"] = candidate
    _record(journal, PublisherStage.CANDIDATE_MANIFEST, candidate.publishable,
            "CANDIDATE_READY" if candidate.publishable else "CANDIDATE_NOT_PUBLISHABLE",
            (candidate.manifest_sha256,))
    if not candidate.publishable:
        return _report(request.mode, journal, PublisherStage.CANDIDATE_MANIFEST,
                       "CANDIDATE_NOT_PUBLISHABLE", evidence)

    assert request.provider is not None and request.publication_plan is not None
    replay: ReleaseReplayResult = replay_release_events(request.release_events)
    try:
        validation = validate_publisher_candidate(
            manifest_bytes=candidate.manifest_bytes,
            pack_builds=pack_builds,
            previous_content_version=request.previous_content_version,
            current_game_version=request.current_game_version,
            supported_manifest_schema_versions=request.supported_manifest_schema_versions,
            publication_plan=request.publication_plan,
            current_target=request.current_target,
            current_replay=replay,
            current_state=request.current_state,
            current_content_digest=request.current_content_digest,
            capability=request.provider.capabilities,
            owner_approved=request.owner_approved,
        )
    except Exception:
        validation = None
    evidence["publisher_validation"] = validation
    validation_ok = validation is not None and validation.accepted is True
    validation_reason = "VALID" if validation_ok else "PUBLISHER_VALIDATION_REJECTED"
    _record(journal, PublisherStage.PUBLISHER_VALIDATION, validation_ok, validation_reason,
            (candidate.manifest_sha256,))
    if not validation_ok:
        return _report(request.mode, journal, PublisherStage.PUBLISHER_VALIDATION,
                       validation_reason, evidence)

    try:
        provider_ledger = tuple(request.provider.read_release_events())
    except Exception:
        provider_ledger = ()
        ledger_ok = False
    else:
        ledger_ok = (provider_ledger == request.release_events
                     and replay_release_events(provider_ledger).accepted)
    _record(journal, PublisherStage.RELEASE_HISTORY_PREFLIGHT, ledger_ok,
            "CURRENT_RELEASE_HISTORY" if ledger_ok else "RELEASE_HISTORY_STALE_OR_INVALID",
            tuple(item.event_digest for item in provider_ledger))
    if not ledger_ok:
        return _report(request.mode, journal, PublisherStage.RELEASE_HISTORY_PREFLIGHT,
                       "RELEASE_HISTORY_STALE_OR_INVALID", evidence)

    assert request.staging_precondition is not None
    upload = upload_candidate_packs_to_staging(candidate, request.provider)  # type: ignore[arg-type]
    evidence["staging_upload"] = upload
    _record(journal, PublisherStage.STAGING_PACK_UPLOAD, upload.accepted, upload.reason_code.value,
            tuple(f"{item.pack_id}:{item.sha256}" for item in upload.uploaded_packs))
    if not upload.accepted:
        return _report(request.mode, journal, PublisherStage.STAGING_PACK_UPLOAD,
                       upload.reason_code.value, evidence)
    integrity_ok = _upload_evidence_matches(candidate, upload)
    _record(journal, PublisherStage.STAGING_OBJECT_INTEGRITY, integrity_ok,
            "EXACT_PACK_BYTES_VERIFIED" if integrity_ok else "STAGING_INTEGRITY_EVIDENCE_MISMATCH",
            tuple(item.sha256 for item in upload.uploaded_packs))
    if not integrity_ok:
        return _report(request.mode, journal, PublisherStage.STAGING_OBJECT_INTEGRITY,
                       "STAGING_INTEGRITY_EVIDENCE_MISMATCH", evidence)

    staging_publish = publish_candidate_manifest_to_staging(
        candidate=candidate,
        validation_report=validation,
        pack_upload_report=upload,
        target=request.current_target,
        precondition=request.staging_precondition,
        release_events=request.release_events,
        provider=request.provider,  # type: ignore[arg-type]
    )
    evidence["staging_publish"] = staging_publish
    staged = staging_publish.accepted is True and staging_publish.receipt is not None
    _record(journal, PublisherStage.STAGING_MANIFEST_PUBLISH, staged,
            staging_publish.reason_code.value,
            (candidate.manifest_sha256,))
    if not staged:
        return _report(request.mode, journal, PublisherStage.STAGING_MANIFEST_PUBLISH,
                       staging_publish.reason_code.value, evidence)

    appended_events = staging_publish.appended_release_events[len(provider_ledger):]
    ledger_write_ok = True
    prior_sequence = len(provider_ledger)
    prior_digest = provider_ledger[-1].event_digest if provider_ledger else "0" * 64
    for event in appended_events:
        try:
            append_result = request.provider.append_release_event(
                event, expected_prior_sequence=prior_sequence,
                expected_prior_event_digest=prior_digest,
            )
        except Exception:
            append_result = None
        if not _release_append_success(append_result, request.provider, event):
            ledger_write_ok = False
            break
        prior_sequence += 1
        prior_digest = event.event_digest
    _record(journal, PublisherStage.STAGING_RELEASE_STATE, ledger_write_ok,
            "STAGING_RELEASE_HISTORY_PERSISTED" if ledger_write_ok else "STAGING_RELEASE_HISTORY_APPEND_FAILED",
            tuple(item.event_digest for item in appended_events))
    if not ledger_write_ok:
        return _report(request.mode, journal, PublisherStage.STAGING_RELEASE_STATE,
                       "STAGING_RELEASE_HISTORY_APPEND_FAILED", evidence)

    staging_download = verify_staged_manifest_download(
        candidate=candidate, staging_receipt=staging_publish.receipt, provider=request.provider  # type: ignore[arg-type]
    )
    evidence["staging_download"] = staging_download
    _record(journal, PublisherStage.STAGING_DOWNLOAD_VERIFY, staging_download.accepted,
            staging_download.reason_code.value,
            (staging_publish.receipt.manifest_sha256,))
    if not staging_download.accepted:
        return _report(request.mode, journal, PublisherStage.STAGING_DOWNLOAD_VERIFY,
                       staging_download.reason_code.value, evidence)
    if request.mode is PublisherMode.STAGING_ONLY:
        return _report(request.mode, journal, PublisherStage.STAGING_DOWNLOAD_VERIFY,
                       "STAGING_VERIFIED", evidence, accepted=True)

    assert request.production is not None and staging_download.receipt is not None
    downloaded = _read_verified_staging_packs(request.provider, staging_download)
    if downloaded is None:
        _record(journal, PublisherStage.CURRENT_MAIN_REPLAY, False, "STAGING_PACK_READBACK_FAILED", ())
        return _report(request.mode, journal, PublisherStage.CURRENT_MAIN_REPLAY,
                       "STAGING_PACK_READBACK_FAILED", evidence)
    evidence["replay_pack_bytes"] = downloaded
    downloaded_map = {item.pack_id: item.content_bytes for item in downloaded}
    artifacts = {item.evidence.pack_id: item.solver_identity_artifact_bytes for item in pack_builds}
    build_evidence = {item.evidence.pack_id: item.evidence for item in pack_builds}
    try:
        current_main = verify_current_main_supply_replay(
            staging_report=staging_download,
            downloaded_manifest_bytes=staging_download.receipt.manifest_bytes,
            downloaded_pack_bytes=downloaded_map,
            solver_identity_artifacts=artifacts,
            pack_build_evidence=build_evidence,
            game_authority=request.production.game_authority,
            authority_check=request.production.authority_check,
            game_runner=request.production.game_runner,
        )
    except Exception:
        current_main = None
    evidence["current_main_replay"] = current_main
    replay_ok = isinstance(current_main, CurrentMainReplayReceipt) and current_main.accepted is True
    replay_reason = "VERIFIED" if replay_ok else "CURRENT_MAIN_REPLAY_REJECTED"
    _record(journal, PublisherStage.CURRENT_MAIN_REPLAY, replay_ok, replay_reason,
            (candidate.manifest_sha256,))
    if not replay_ok:
        return _report(request.mode, journal, PublisherStage.CURRENT_MAIN_REPLAY,
                       replay_reason, evidence)

    promotion = promote_verified_staging_to_production(
        staging_report=staging_download,
        downloaded_pack_bytes=downloaded_map,
        replay_receipt=current_main,
        owner_approval=request.production.owner_approval,
        owner_approval_check=request.production.owner_approval_check,
        game_authority_check=request.production.authority_check,
        target_id=PRODUCTION_TARGET.logical_target_id,
        manifest_object_key=request.manifest_object_key,
        precondition=request.production.production_precondition,
        release_events=staging_publish.appended_release_events,
        provider=request.provider,
    )
    evidence["production_promotion"] = promotion
    promoted = promotion.accepted is True and promotion.manifest_write_attempted is False
    _record(journal, PublisherStage.PRODUCTION_PACK_PROMOTION, promoted,
            promotion.reason_code.value, (candidate.manifest_sha256,))
    if not promoted:
        return _report(request.mode, journal, PublisherStage.PRODUCTION_PACK_PROMOTION,
                       promotion.reason_code.value, evidence)

    activation = activate_versioned_production_manifest(
        staging_report=staging_download,
        staging_pack_bytes=downloaded_map,
        pack_builds=pack_builds,
        promotion_report=promotion,
        replay_receipt=current_main,
        owner_approval=request.production.owner_approval,
        owner_approval_check=request.production.owner_approval_check,
        game_authority_check=request.production.authority_check,
        production_target_id=PRODUCTION_TARGET.logical_target_id,
        manifest_object_key=request.manifest_object_key,
        precondition=request.production.production_precondition,
        manifest_history=request.production.manifest_history,
        release_events=staging_publish.appended_release_events,
        recorded_at_utc=request.production.recorded_at_utc,
        current_game_version=request.current_game_version,
        supported_manifest_schema_versions=request.supported_manifest_schema_versions,
        provider=request.provider,
    )
    evidence["production_activation"] = activation
    activated = activation.accepted is True and activation.reason_code in {
        ProductionManifestReasonCode.ACTIVATED, ProductionManifestReasonCode.ALREADY_CURRENT,
    }
    _record(journal, PublisherStage.PRODUCTION_MANIFEST_ACTIVATION, activated,
            activation.reason_code.value,
            (candidate.manifest_sha256,))
    if not activated:
        return _report(request.mode, journal, PublisherStage.PRODUCTION_MANIFEST_ACTIVATION,
                       activation.reason_code.value, evidence)
    fence_reason = activation.reason_code.value
    _record(journal, PublisherStage.CURRENT_STATE_FENCE, True, fence_reason,
            (candidate.manifest_sha256,))
    return _report(request.mode, journal, PublisherStage.CURRENT_STATE_FENCE,
                   fence_reason, evidence, accepted=True)


def _preflight_error(request: PublisherRunRequest) -> str | None:
    if request.config.resolved_target != STAGING_TARGET:
        return "STAGING_TARGET_REQUIRED"
    if (request.provider is None or request.factory_pack_builder is None
            or not request.factory_pack_requests or request.content_version is None
            or not request.minimum_game_version
            or not request.current_game_version or not request.supported_manifest_schema_versions
            or not request.object_keys or request.publication_plan is None
            or request.current_content_digest is None or request.staging_precondition is None
            or not request.manifest_object_key
            or request.staging_precondition.object_key != request.manifest_object_key):
        return "REQUIRED_PUBLISH_INPUT_MISSING"
    if request.mode not in {PublisherMode.STAGING_ONLY, PublisherMode.PRODUCTION}:
        return "INVALID_PUBLISH_MODE"
    if request.mode is PublisherMode.PRODUCTION:
        production = request.production
        if (production is None or not isinstance(production.owner_approval, OwnerPromotionApproval)
                or not callable(production.owner_approval_check) or not callable(production.authority_check)
                or not callable(production.game_runner) or not isinstance(production.game_authority, Mapping)
                or not isinstance(production.production_precondition, ProductionManifestPrecondition)
                or not isinstance(production.manifest_history, ManifestHistoryV1)):
            return "EXPLICIT_PRODUCTION_AUTHORITY_REQUIRED"
    return None


def _upload_evidence_matches(candidate: CandidateManifestBuildResult,
                             upload: StagingPackUploadReport) -> bool:
    expected = {item.pack_id: (item.sha256, item.byte_length, item.object_key)
                for item in candidate.manifest.packs}
    actual = {item.pack_id: (item.sha256, item.byte_length, item.object_key)
              for item in upload.uploaded_packs}
    return upload.accepted is True and len(actual) == len(upload.uploaded_packs) == len(expected) and actual == expected


def _factory_output_matches_request(build: ScrubpackBuildResult, request: FactoryPackRequest) -> bool:
    if (build.evidence.pack_id != request.pack_id or build.evidence.pack_version != request.pack_version
            or type(build.solver_identity_artifact_bytes) is not bytes):
        return False
    try:
        document = json.loads(build.solver_identity_artifact_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    rows = document.get("levels") if isinstance(document, Mapping) else None
    if not isinstance(rows, list) or not rows:
        return False
    sources = [row.get("source") for row in rows if isinstance(row, Mapping)]
    candidate_ids = [source.get("candidate_id") for source in sources if isinstance(source, Mapping)]
    requested = request.candidate_ids
    return (
        bool(requested)
        and len(candidate_ids) == len(rows)
        and set(candidate_ids) == set(requested)
        and len(set(requested)) == len(requested)
    )


def _release_append_success(result: object, provider: ProductionPromotionProvider,
                            event: ReleaseEvent) -> bool:
    return (
        isinstance(result, ProviderResult)
        and result.result_version == PROVIDER_CONTRACT_VERSION
        and result.category is ProviderResultCategory.SUCCESS
        and result.provider_id == provider.identity.provider_id
        and result.environment is event.environment
        and result.content_digest == event.event_digest
    )


def _read_verified_staging_packs(provider: ProductionPromotionProvider,
                                 report: StagingDownloadVerificationReport) -> tuple[DownloadedPackBytes, ...] | None:
    if report.receipt is None:
        return None
    output = []
    for item in report.receipt.packs:
        try:
            result = provider.read_object_bytes(Environment.STAGING, item.object_key)
        except Exception:
            return None
        if (not isinstance(result, ProviderObjectBytesResult)
                or result.result_version != PROVIDER_CONTRACT_VERSION
                or result.category is not ProviderResultCategory.SUCCESS
                or result.provider_id != report.receipt.provider_id
                or result.environment is not Environment.STAGING or result.object_key != item.object_key
                or type(result.content_bytes) is not bytes or len(result.content_bytes) != item.byte_length
                or hashlib.sha256(result.content_bytes).hexdigest() != item.sha256):
            return None
        output.append(DownloadedPackBytes(item.pack_id, item.object_key, item.sha256,
                                          item.byte_length, result.content_bytes))
    return tuple(output)


def _record(journal: list[PublisherJournalEntry], stage: PublisherStage, accepted: bool,
            reason_code: str, evidence: Sequence[str]) -> None:
    payload = json.dumps({
        "accepted": accepted is True,
        "evidence": list(evidence),
        "reason_code": reason_code,
        "sequence": len(journal) + 1,
        "stage": stage.value,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    journal.append(PublisherJournalEntry(len(journal) + 1, stage, accepted is True,
                                         reason_code, hashlib.sha256(payload).hexdigest()))


def _report(mode: PublisherMode, journal: Sequence[PublisherJournalEntry], stage: PublisherStage,
            reason_code: str, evidence: Mapping[str, object], *, accepted: bool = False) -> PublisherRunReport:
    return PublisherRunReport(
        accepted, mode, reason_code, stage, tuple(journal),
        validation=evidence.get("validation"),
        pack_builds=evidence.get("pack_builds", ()),
        candidate=evidence.get("candidate"),
        publisher_validation=evidence.get("publisher_validation"),
        staging_upload=evidence.get("staging_upload"),
        staging_publish=evidence.get("staging_publish"),
        staging_download=evidence.get("staging_download"),
        replay_pack_bytes=evidence.get("replay_pack_bytes", ()),
        current_main_replay=evidence.get("current_main_replay"),
        production_promotion=evidence.get("production_promotion"),
        production_activation=evidence.get("production_activation"),
    )


def serialize_publisher_journal(report: PublisherRunReport) -> str:
    """Serialize the fixed deterministic journal without echoing caller inputs."""
    if not isinstance(report, PublisherRunReport):
        raise TypeError("report must be a PublisherRunReport")
    return json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")) + "\n"


def _invalid_request(request: object) -> PublisherRunReport:
    _record(journal := [], PublisherStage.REQUEST_PREFLIGHT, False, "INVALID_REQUEST_TYPE", ())
    mode = request.mode if isinstance(request, PublisherRunRequest) else PublisherMode.VALIDATION_ONLY
    return _report(mode, journal, PublisherStage.REQUEST_PREFLIGHT, "INVALID_REQUEST_TYPE", {})


__all__ = [
    "AcceptedFactoryPackBuilder", "DownloadedPackBytes", "FactoryPackRequest",
    "ProductionRunInputs", "PublisherJournalEntry", "PublisherMode", "PublisherRunReport",
    "PublisherRunRequest", "PublisherStage", "run_one_command_publisher",
    "serialize_publisher_journal",
]
