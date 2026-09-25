from __future__ import annotations

import pytest

from scrubbots_pixel_factory.qa import QAContractError, QAReportDisposition, SemanticReviewDisposition, build_qa_report


IDS = {"source_sha256": "a" * 64, "level_data_digest": "b" * 64, "logical_art_digest": "c" * 64}


def test_accepted_report_derives_disposition_and_round_trips_deterministically() -> None:
    report = build_qa_report(**IDS, stages={"STRUCTURAL": "PASS", "PRODUCTION": "PASS", "SOLVER": "PASS"}, semantic_review=SemanticReviewDisposition.ACCEPT)
    assert report.disposition is QAReportDisposition.ACCEPT
    assert report.digest() == report.digest()
    assert report.canonical_bytes() == type(report).from_dict(report.canonical_dict()).canonical_bytes()


@pytest.mark.parametrize(("stages", "semantic", "expected"), [
    ({"STRUCTURAL": "FAIL"}, SemanticReviewDisposition.ACCEPT, QAReportDisposition.REJECT),
    ({"SOLVER": "INCONCLUSIVE"}, SemanticReviewDisposition.ACCEPT, QAReportDisposition.INCONCLUSIVE),
    ({"PRODUCTION": "UNAVAILABLE"}, SemanticReviewDisposition.ACCEPT, QAReportDisposition.UNAVAILABLE),
    ({"STRUCTURAL": "PASS"}, SemanticReviewDisposition.REJECT, QAReportDisposition.REJECT),
    ({"STRUCTURAL": "PASS"}, SemanticReviewDisposition.UNREVIEWED, QAReportDisposition.INCONCLUSIVE),
])
def test_overall_disposition_is_derived_from_stage_truth(stages: dict[str, str], semantic: SemanticReviewDisposition, expected: QAReportDisposition) -> None:
    report = build_qa_report(**IDS, stages=stages, semantic_review=semantic)
    assert report.disposition is expected


def test_unknown_fields_and_caller_supplied_disposition_are_rejected() -> None:
    report = build_qa_report(**IDS, stages={"STRUCTURAL": "PASS"}, semantic_review=SemanticReviewDisposition.ACCEPT)
    with pytest.raises(QAContractError):
        type(report).from_dict({**report.canonical_dict(), "unexpected": True})
    with pytest.raises(QAContractError):
        type(report).from_dict({**report.canonical_dict(), "disposition": "REJECT"})
