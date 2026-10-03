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
        "--environment",
        choices=[environment.value for environment in Environment],
        default=Environment.STAGING.value,
    )
    args = parser.parse_args()
    if not args.validate_only:
        parser.error("only --validate-only is available in this milestone")
    report = validate_only(PipelineConfig(environment=Environment(args.environment)))
    print(json.dumps(asdict(report), sort_keys=True, separators=(",", ":")))
    return 0 if report.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
