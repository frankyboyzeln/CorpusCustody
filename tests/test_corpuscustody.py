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
        self.assertEqual(lic.spdx_id, "UNKNOWN")

    def test_unrecognised_resolves_to_unknown(self):
        lic = spdx.resolve("NOT-A-REAL-ID")
        self.assertTrue(lic.unknown)

    def test_explicit_unknown_token(self):
        self.assertTrue(spdx.resolve("UNKNOWN").unknown)

    def test_share_alike_flag(self):
        self.assertTrue(spdx.resolve("CC-BY-SA-4.0").share_alike)

    def test_known_identifiers_sorted(self):
        ids = spdx.known_identifiers()
