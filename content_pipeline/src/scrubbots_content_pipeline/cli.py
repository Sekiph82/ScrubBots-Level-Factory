"""Command-line entry point restricted to local validation-only execution."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .config import Environment, PipelineConfig
from .validation import validate_only


def main() -> int:
    parser = argparse.ArgumentParser(prog="scrubbots-content-pipeline")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="validate local configuration and print a report; no publishing occurs",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="emit a deterministic fail-closed local publication-plan report; never writes remotely",
    )
    parser.add_argument(
        "--environment",
        choices=[environment.value for environment in Environment],
        default=Environment.STAGING.value,
    )
    args = parser.parse_args()
    if args.validate_only and args.dry_run:
        parser.error("choose either --validate-only or --dry-run")
    if args.dry_run:
        report = {
            "plan_version": "1.0",
            "accepted": False,
            "complete": False,
            "target_environment": args.environment,
            "checks": [{"check_id": "required_plan_evidence", "accepted": False, "reason_code": "UNVALIDATED_PAYLOAD"}],
            "remote_mutation_performed": False,
            "reason": "descriptor_payload_release_replay_and_owner_approval_are_required_via_the_local_plan_api",
        }
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
        return 1
    if not args.validate_only:
        parser.error("only --validate-only and --dry-run are available in this milestone")
    report = validate_only(PipelineConfig(environment=Environment(args.environment)))
    print(json.dumps(asdict(report), sort_keys=True, separators=(",", ":")))
    return 0 if report.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
