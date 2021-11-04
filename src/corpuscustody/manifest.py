"""Dataset manifest parsing, line oriented.

A manifest is a UTF-8 text file, one record per line. Blank lines and lines
whose first non-space character is `#` are ignored, so manifests can carry
comments and stay diffable.

Each record line has three tab-separated or pipe-separated fields:

    record_id  <sep>  spdx_id  <sep>  source

The separator is a single pipe `|`. Surrounding whitespace on each field is
stripped. `record_id` and `source` are free text. `spdx_id` is looked up in the
offline SPDX table at resolve time; it is not validated here beyond being read.

An empty spdx_id field is preserved as an empty string, which the resolver maps
to UNKNOWN. This keeps parsing and license policy in separate modules.
"""

from dataclasses import dataclass
from typing import List


class ManifestError(ValueError):
    """Raised when a manifest line cannot be parsed into a record."""


@dataclass(frozen=True)
class Record:
    """One dataset record drawn from a manifest line."""

    line_no: int
    record_id: str
    spdx_id: str
    source: str


def parse_line(line_no: int, raw: str) -> Record:
    """Parse a single non-comment, non-blank line into a Record.

