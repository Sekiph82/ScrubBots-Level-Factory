from __future__ import annotations

from dataclasses import dataclass

from scrubbots_pixel_factory.qa import AuthorityIdentity, HandoffValidationReceipt, QAReportDisposition, SemanticReviewDisposition, build_main_game_handoff, build_qa_report


AUTHORITY = AuthorityIdentity("https://github.com/Sekiph82/Scrubbots", "b" * 40, "scripts/qa/acceptance.gd", "M05_MAIN_GAME_ACCEPTANCE_V1")
IDS = {"source_sha256": "a" * 64, "level_data_digest": "b" * 64, "logical_art_digest": "c" * 64}


def _report():
    return build_qa_report(**IDS, stages={"STRUCTURAL": "PASS", "PRODUCTION": "PASS", "SOLVER": "PASS"}, semantic_review=SemanticReviewDisposition.ACCEPT)


@dataclass(frozen=True)
class Provider:
    disposition: str = "PASS"

    def validate_handoff(self, handoff):
        return HandoffValidationReceipt(self.disposition, AUTHORITY, "d" * 64, "clean validation-only main-game receipt")


def _build(provider=Provider(), report=None):
    return build_main_game_handoff(level_data_sha256="1" * 64, logical_art_png_sha256="2" * 64, source_provenance_sha256="3" * 64, qa_report=report or _report(), solver_evidence_digest="4" * 64, difficulty_analysis_digest="5" * 64, semantic_evidence_digest="6" * 64, factory_schema="scrubbots-factory", factory_version=1, main_game_authority=AUTHORITY, provider=provider)


def test_valid_handoff_is_eligible_only_and_keeps_device_gates_pending() -> None:
    handoff = _build()
    assert handoff.disposition == "ELIGIBLE_FOR_MAIN_GAME_ACCEPTANCE_HANDOFF"
    assert dict(handoff.downstream_gates)["M30_COMPATIBLE"] == "PASS"
    assert dict(handoff.downstream_gates)["M47_ANDROID_DEVICE_TESTING"] == "PENDING"
    assert dict(handoff.downstream_gates)["M48_IOS_READINESS"] == "PENDING"
    assert handoff.digest() == handoff.digest()


def test_qa_not_accepted_validator_reject_and_authority_drift_never_promote() -> None:
    rejected_report = build_qa_report(**IDS, stages={"STRUCTURAL": "FAIL"}, semantic_review=SemanticReviewDisposition.ACCEPT)
    assert _build(report=rejected_report).disposition == "NOT_ELIGIBLE"
    assert _build(provider=Provider("FAIL")).disposition == "NOT_ELIGIBLE"
    drift = AuthorityIdentity(AUTHORITY.repository, "c" * 40, AUTHORITY.source_path, AUTHORITY.contract_version)

    class DriftProvider(Provider):
        def validate_handoff(self, handoff):
            return HandoffValidationReceipt("PASS", drift, "e" * 64, "drift")

    assert _build(provider=DriftProvider()).disposition == "ERROR"


def test_missing_provider_is_unavailable_and_hash_inputs_are_bound() -> None:
    handoff = _build(provider=None)
    assert handoff.disposition == "UNAVAILABLE"
    assert handoff.qa_report_digest == _report().digest()
