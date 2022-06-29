"""Line-oriented rendering of resolve and gate results.

All output is deterministic and free of wall-clock time. Counts are sorted by
SPDX identifier so the same input yields byte-identical output.
"""

from collections import Counter
from typing import Dict, List

from .compat import SetResult
from .gate import GateResult
from .manifest import Record
from .spdx import resolve


def license_counts(records: List[Record]) -> Dict[str, int]:
    """Count records per resolved SPDX identifier."""
    counter: Counter = Counter()
    for record in records:
        counter[resolve(record.spdx_id).spdx_id] += 1
    return dict(counter)


