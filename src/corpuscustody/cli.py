"""Command line interface for corpuscustody.

Subcommands:
  resolve   parse a manifest and print each record's resolved license
  gate      run the pass or refuse decision for a declared purpose
  report    print the combined resolve and gate report
  version   print the version

Exit codes:
  0  clean, gate passed, or informational command succeeded
  1  gate refused (findings present)
  2  usage error or bad input
"""

import argparse
import sys
from typing import List, Optional

from . import __version__
from .compat import PurposeError, PURPOSES
from .gate import decide, write_cleared_manifest
from .manifest import ManifestError, parse_file
from .report import render_gate, render_report, render_resolve

USAGE_ERROR = 2
REFUSED = 1
OK = 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="corpuscustody",
        description="Training-data license and provenance gate.",
    )
    sub = parser.add_subparsers(dest="command")

    p_resolve = sub.add_parser(
        "resolve", help="parse a manifest and resolve each record's license"
    )
    p_resolve.add_argument("manifest", help="path to a dataset manifest")

    p_gate = sub.add_parser(
        "gate", help="run the pass or refuse decision for a declared purpose"
    )
    p_gate.add_argument("manifest", help="path to a dataset manifest")
    p_gate.add_argument(
        "--purpose",
        required=True,
        choices=PURPOSES,
        help="declared purpose for the combined set",
    )
    p_gate.add_argument(
        "--out",
        default=None,
        help="write a cleared manifest to this path on pass",
    )

    p_report = sub.add_parser(
        "report", help="print the combined resolve and gate report"
    )
    p_report.add_argument("manifest", help="path to a dataset manifest")
    p_report.add_argument(
        "--purpose",
        required=True,
        choices=PURPOSES,
        help="declared purpose for the combined set",
    )

    sub.add_parser("version", help="print the version")
    return parser


def _emit(lines: List[str]) -> None:
    for line in lines:
        print(line)


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return USAGE_ERROR

    if args.command == "version":
        print("corpuscustody {0}".format(__version__))
        return OK

    try:
        records = parse_file(args.manifest)
    except FileNotFoundError:
        print("error: manifest not found: {0}".format(args.manifest), file=sys.stderr)
        return USAGE_ERROR
    except ManifestError as exc:
        print("error: {0}".format(exc), file=sys.stderr)
        return USAGE_ERROR

    if args.command == "resolve":
        _emit(render_resolve(records))
