"""Tests for corpuscustody, stdlib unittest only."""

import io
import os
import tempfile
import unittest

from corpuscustody import __version__
from corpuscustody import cli, compat, gate, manifest, report, spdx

SAMPLES = os.path.join(os.path.dirname(__file__), os.pardir, "samples")


class SpdxTests(unittest.TestCase):
    def test_permissive_has_no_blocking_obligations(self):
        lic = spdx.resolve("MIT")
        self.assertEqual(lic.obligations(), ["attribution"])

    def test_empty_resolves_to_unknown(self):
        lic = spdx.resolve("")
        self.assertTrue(lic.unknown)
