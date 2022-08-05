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
        self.assertEqual(ids, sorted(ids))
        self.assertIn("MIT", ids)


class ManifestTests(unittest.TestCase):
    def test_parse_line_ok(self):
        rec = manifest.parse_line(1, "rec-1 | MIT | src")
        self.assertEqual(rec.record_id, "rec-1")
        self.assertEqual(rec.spdx_id, "MIT")
        self.assertEqual(rec.source, "src")

    def test_wrong_field_count_raises(self):
        with self.assertRaises(manifest.ManifestError):
            manifest.parse_line(1, "rec-1 | MIT")

    def test_empty_record_id_raises(self):
        with self.assertRaises(manifest.ManifestError):
            manifest.parse_line(1, " | MIT | src")

    def test_comments_and_blanks_ignored(self):
        text = "# comment\n\nrec-1 | MIT | s\n"
        recs = manifest.parse_text(text)
        self.assertEqual(len(recs), 1)

    def test_empty_license_field_preserved(self):
        rec = manifest.parse_line(1, "rec-1 |  | src")
        self.assertEqual(rec.spdx_id, "")
