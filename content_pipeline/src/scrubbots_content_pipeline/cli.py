"""Command-line entry point restricted to local validation-only execution."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .config import Environment, PipelineConfig
from .scrubpack_inspection import extract_scrubpack, inspect_scrubpack
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
    parser.add_argument("--inspect-pack", metavar="PATH", help="inspect one local .scrubpack without writing")
    parser.add_argument("--extract-pack", metavar="PATH", help="validate and safely extract one local .scrubpack")
    parser.add_argument("--destination", metavar="DIR", help="new destination directory for --extract-pack")
    parser.add_argument(
        "--output-format",
        choices=("human", "json"),
        default="human",
        help="inspect/extract result format",
    )
    args = parser.parse_args()
    selected_modes = sum(bool(value) for value in (args.validate_only, args.dry_run, args.inspect_pack, args.extract_pack))
    if selected_modes > 1:
        parser.error("choose one command mode")
    if args.inspect_pack and args.destination:
        parser.error("--destination is only valid with --extract-pack")
    if args.extract_pack and not args.destination:
        parser.error("--extract-pack requires --destination")
    if args.destination and not args.extract_pack:
        parser.error("--destination requires --extract-pack")
    if args.inspect_pack:
        report = inspect_scrubpack(args.inspect_pack)
        print(json.dumps(report.to_dict(), sort_keys=True, separators=(",", ":")) if args.output_format == "json" else report.render_human())
        return 0 if report.accepted else 1
    if args.extract_pack:
        report = extract_scrubpack(args.extract_pack, args.destination)
        print(json.dumps(report.to_dict(), sort_keys=True, separators=(",", ":")) if args.output_format == "json" else report.render_human())
        return 0 if report.accepted else 1
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
