"""Immutable, builder-only Git publication evidence; never task-state authority."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum

BUILDER_RECEIPT_VERSION = "1.0"
_SHA = re.compile(r"^[a-f0-9]{40}$")
_TASK = re.compile(r"^SB-CP00-00[3-9]-C001$")


class ParityResult(StrEnum):
    VERIFIED_EQUAL = "VERIFIED_EQUAL"
    DIVERGED = "DIVERGED"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True, slots=True)
class BuilderTestSummary:
    focused_passed: int
    focused_failed: int
    focused_skipped: int
    full_passed: int
    full_failed: int
    full_skipped: int
    compileall_exit_code: int
    diff_check_exit_code: int

    def to_dict(self) -> dict[str, int]:
        return {
            "focused_passed": self.focused_passed,
            "focused_failed": self.focused_failed,
            "focused_skipped": self.focused_skipped,
            "full_passed": self.full_passed,
            "full_failed": self.full_failed,
            "full_skipped": self.full_skipped,
            "compileall_exit_code": self.compileall_exit_code,
            "diff_check_exit_code": self.diff_check_exit_code,
        }


@dataclass(frozen=True, slots=True)
class PublicationParity:
    result: ParityResult
    execution_sha: str
    origin_main_sha: str
    ahead: int
    behind: int

    def to_dict(self) -> dict[str, object]:
        return {
            "result": self.result.value if isinstance(self.result, ParityResult) else ParityResult.UNVERIFIED.value,
            "execution_sha": self.execution_sha if _SHA.fullmatch(self.execution_sha or "") else "",
            "origin_main_sha": self.origin_main_sha if _SHA.fullmatch(self.origin_main_sha or "") else "",
            "ahead": self.ahead if type(self.ahead) is int and self.ahead >= 0 else -1,
            "behind": self.behind if type(self.behind) is int and self.behind >= 0 else -1,
        }


@dataclass(frozen=True, slots=True)
class BuilderPublicationReceipt:
    """Fixed fact record with no mutable status, audit, or acceptance field."""

    schema_version: str
    task_id: str
    prompt_path: str
    builder_log_path: str
    repository_owner: str
    repository_name: str
    branch: str
    base_sha: str
    implementation_sha: str
    builder_log_sha: str
    final_sha: str
    test_summary: BuilderTestSummary
    publication_parity: PublicationParity

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "prompt_path": self.prompt_path,
            "builder_log_path": self.builder_log_path,
            "repository": {"owner": self.repository_owner, "name": self.repository_name},
            "branch": self.branch,
            "base_sha": self.base_sha,
            "implementation_sha": self.implementation_sha,
            "builder_log_sha": self.builder_log_sha,
            "final_sha": self.final_sha,
            "test_summary": self.test_summary.to_dict() if isinstance(self.test_summary, BuilderTestSummary) else {},
            "publication_parity": self.publication_parity.to_dict() if isinstance(self.publication_parity, PublicationParity) else {},
        }


class ReceiptReasonCode(StrEnum):
    VALID_RECEIPT = "VALID_RECEIPT"
    INVALID_RECEIPT = "INVALID_RECEIPT"
    INVALID_IDENTITY = "INVALID_IDENTITY"
    INVALID_PATH = "INVALID_PATH"
    INVALID_SHA = "INVALID_SHA"
    INVALID_TEST_FACTS = "INVALID_TEST_FACTS"
    INVALID_PARITY_FACTS = "INVALID_PARITY_FACTS"


@dataclass(frozen=True, slots=True)
class ReceiptValidationResult:
    valid: bool
    reason_code: ReceiptReasonCode


def validate_builder_receipt(receipt: object) -> ReceiptValidationResult:
    """Validate canonical repository facts and publication parity without status authority."""
    if not isinstance(receipt, BuilderPublicationReceipt):
        return ReceiptValidationResult(False, ReceiptReasonCode.INVALID_RECEIPT)
    if receipt.schema_version != BUILDER_RECEIPT_VERSION or not _TASK.fullmatch(receipt.task_id or ""):
        return ReceiptValidationResult(False, ReceiptReasonCode.INVALID_RECEIPT)
    if (
        receipt.repository_owner != "Sekiph82"
        or receipt.repository_name != "ScrubBots-Level-Factory"
        or receipt.branch != "main"
    ):
        return ReceiptValidationResult(False, ReceiptReasonCode.INVALID_IDENTITY)
    if (
        not isinstance(receipt.prompt_path, str)
        or not re.fullmatch(r"\.hiveai/prompts/SB-CP00-00[3-9]-C001_[A-Z0-9_-]+_PROMPT\.md", receipt.prompt_path)
        or not isinstance(receipt.builder_log_path, str)
        or not re.fullmatch(r"\.hiveai/codex-logs/SB-CP00-00[3-9]-C001_[A-Z0-9_-]+_CODEX_LOG\.md", receipt.builder_log_path)
    ):
        return ReceiptValidationResult(False, ReceiptReasonCode.INVALID_PATH)
    if not all(isinstance(value, str) and _SHA.fullmatch(value) for value in (
        receipt.base_sha, receipt.implementation_sha, receipt.builder_log_sha, receipt.final_sha,
    )):
        return ReceiptValidationResult(False, ReceiptReasonCode.INVALID_SHA)
    summary = receipt.test_summary
    if not isinstance(summary, BuilderTestSummary) or any(
        type(value) is not int or value < 0
        for value in (
            summary.focused_passed, summary.focused_failed, summary.focused_skipped,
            summary.full_passed, summary.full_failed, summary.full_skipped,
            summary.compileall_exit_code, summary.diff_check_exit_code,
        )
    ):
        return ReceiptValidationResult(False, ReceiptReasonCode.INVALID_TEST_FACTS)
    parity = receipt.publication_parity
    if (
        not isinstance(parity, PublicationParity)
        or not isinstance(parity.result, ParityResult)
        or not isinstance(parity.execution_sha, str) or not _SHA.fullmatch(parity.execution_sha)
        or not isinstance(parity.origin_main_sha, str) or not _SHA.fullmatch(parity.origin_main_sha)
        or type(parity.ahead) is not int or parity.ahead < 0
        or type(parity.behind) is not int or parity.behind < 0
    ):
        return ReceiptValidationResult(False, ReceiptReasonCode.INVALID_PARITY_FACTS)
    if parity.result is ParityResult.VERIFIED_EQUAL and not (
        parity.execution_sha == parity.origin_main_sha == receipt.final_sha
        and parity.ahead == parity.behind == 0
    ):
        return ReceiptValidationResult(False, ReceiptReasonCode.INVALID_PARITY_FACTS)
    if parity.result is ParityResult.DIVERGED and parity.execution_sha == parity.origin_main_sha and parity.ahead == parity.behind == 0:
        return ReceiptValidationResult(False, ReceiptReasonCode.INVALID_PARITY_FACTS)
    return ReceiptValidationResult(True, ReceiptReasonCode.VALID_RECEIPT)


def serialize_builder_receipt(receipt: BuilderPublicationReceipt) -> str:
    if not validate_builder_receipt(receipt).valid:
        raise ValueError("invalid builder publication receipt")
    return json.dumps(receipt.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


__all__ = [
    "BUILDER_RECEIPT_VERSION", "BuilderPublicationReceipt", "BuilderTestSummary",
    "ParityResult", "PublicationParity", "ReceiptReasonCode", "ReceiptValidationResult",
    "serialize_builder_receipt", "validate_builder_receipt",
]
