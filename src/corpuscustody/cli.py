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
