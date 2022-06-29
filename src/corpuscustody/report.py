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


