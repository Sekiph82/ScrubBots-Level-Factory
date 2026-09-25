"""SB-LF07-009 mandatory source-linked M05 preservation orchestration."""

from dataclasses import dataclass

from .qa.source_preservation import OwnerSourceRecord, SourcePreservationReport, verify_owner_source_preservation
from .m07_services import AttemptBudget, AttemptDisposition, AttemptReport, MutationContractError


@dataclass(frozen=True, slots=True)
class SourceLinkedMutationContext:
    record: OwnerSourceRecord
    before: SourcePreservationReport
    after: SourcePreservationReport | None = None

    @classmethod
    def establish(cls, record: OwnerSourceRecord) -> "SourceLinkedMutationContext":
        if not isinstance(record, OwnerSourceRecord):
            raise MutationContractError("source-linked orchestration requires accepted M05 OwnerSourceRecord")
        before = verify_owner_source_preservation(record)
        return cls(record, before)

    def verify_after(self, *, analysis=None, derived_artifact_paths=()) -> "SourceLinkedMutationContext":
        report = verify_owner_source_preservation(self.record, analysis=analysis, derived_artifact_paths=derived_artifact_paths)
        return SourceLinkedMutationContext(self.record, self.before, report)

    @property
    def passed(self) -> bool:
        return self.before.disposition == "PASS" and self.after is not None and self.after.disposition == "PASS"

    def require_pass(self) -> None:
        if not self.passed:
            raise MutationContractError("accepted M05 OWNER_UPLOAD preservation PASS is required before bounded success")


__all__ = ["OwnerSourceRecord", "SourceLinkedMutationContext", "SourcePreservationReport", "verify_owner_source_preservation"]
