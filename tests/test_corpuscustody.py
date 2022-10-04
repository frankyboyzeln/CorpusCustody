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


class CompatTests(unittest.TestCase):
    def _records(self, name):
        return manifest.parse_file(os.path.join(SAMPLES, name))

    def test_purpose_validation(self):
        with self.assertRaises(compat.PurposeError):
            compat.check_purpose("nonsense")
        self.assertEqual(compat.check_purpose("Commercial"), "commercial")

    def test_permissive_clear_for_commercial(self):
        recs = self._records("permissive.manifest")
        result = compat.evaluate(recs, "commercial")
        self.assertTrue(result.clear)
        self.assertEqual(result.findings, [])

    def test_sharealike_blocks_commercial(self):
        recs = self._records("sharealike.manifest")
        result = compat.evaluate(recs, "commercial")
        self.assertFalse(result.clear)
        obligations = {i.obligation for i in result.findings}
        self.assertIn("share_alike", obligations)
        self.assertIn("non_commercial", obligations)

    def test_sharealike_clear_for_internal(self):
        recs = self._records("sharealike.manifest")
        result = compat.evaluate(recs, "internal")
        self.assertTrue(result.clear)

    def test_unknown_blocks_every_purpose(self):
        recs = self._records("unknown.manifest")
        for purpose in compat.PURPOSES:
            result = compat.evaluate(recs, purpose)
            self.assertFalse(result.clear, purpose)
            self.assertTrue(
                any(i.obligation == "unknown" for i in result.findings), purpose
            )


class GateTests(unittest.TestCase):
    def _records(self, name):
        return manifest.parse_file(os.path.join(SAMPLES, name))

    def test_permissive_passes(self):
        g = gate.decide(self._records("permissive.manifest"), "commercial")
        self.assertEqual(g.decision, gate.PASS)
        self.assertFalse(g.refused)

    def test_unknown_refuses(self):
        g = gate.decide(self._records("unknown.manifest"), "internal")
        self.assertEqual(g.decision, gate.REFUSE)
        self.assertTrue(g.refused)

    def test_cleared_manifest_lines_deterministic(self):
        recs = self._records("permissive.manifest")
        a = gate.cleared_manifest_lines(recs, "commercial")
        b = gate.cleared_manifest_lines(recs, "commercial")
        self.assertEqual(a, b)
        self.assertTrue(a[0].startswith("# corpuscustody cleared manifest"))

    def test_write_cleared_manifest(self):
        recs = self._records("permissive.manifest")
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "cleared.manifest")
            gate.write_cleared_manifest(out, recs, "commercial")
            with open(out, "r", encoding="utf-8", newline="") as handle:
                data = handle.read()
            self.assertIn("rec-0001 | MIT | commercial", data)
            self.assertNotIn("\r\n", data)


class ReportTests(unittest.TestCase):
    def _records(self, name):
        return manifest.parse_file(os.path.join(SAMPLES, name))

    def test_license_counts(self):
        counts = report.license_counts(self._records("unknown.manifest"))
        self.assertEqual(counts["UNKNOWN"], 2)
        self.assertEqual(counts["MIT"], 1)

    def test_render_resolve_lines(self):
        lines = report.render_resolve(self._records("permissive.manifest"))
        self.assertEqual(lines[0], "records: 5")


class CliTests(unittest.TestCase):
    def _run(self, argv):
        import contextlib

        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        return code, out.getvalue(), err.getvalue()
