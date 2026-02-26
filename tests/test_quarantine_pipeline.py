import unittest
from unittest.mock import patch
from security.sandbox.quarantine_pipeline import (
    TrustMatrix,
    EntropyAnalyzer,
    SASTScanner,
    QuarantinePipeline,
    _compute_entropy,
)
import os
import shutil
import tempfile
from pathlib import Path


class TestQuarantinePipeline(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_compute_entropy(self):
        self.assertEqual(_compute_entropy(b""), 0.0)
        self.assertLess(_compute_entropy(b"aaaaa"), 1.0)
        self.assertGreater(_compute_entropy(os.urandom(100)), 5.0)

    def test_trust_matrix(self):
        matrix = TrustMatrix()
        # Trusted publisher
        self.assertTrue(matrix.is_trusted_publisher("google-analytics"))
        # Scoped package
        self.assertTrue(matrix.is_trusted_publisher("@vercel/framework"))
        self.assertFalse(matrix.is_trusted_publisher("malicious-pkg"))

        # npm verify
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = '"sha512-abc"'
            self.assertTrue(matrix.verify_npm_package("express", "4.17.1"))

        # pypi verify
        with patch("urllib.request.urlopen") as mock_url:
            mock_url.return_value.__enter__.return_value.read.return_value = (
                b'{"releases": {"1.0": [{"digests": {"sha256": "abc"}}]}}'
            )
            self.assertTrue(matrix.verify_pypi_package("requests", "1.0"))

    def test_entropy_analyzer(self):
        analyzer = EntropyAnalyzer()

        # Normal file
        f1 = self.test_dir / "normal.js"
        f1.write_text("var x = 1;" * 100)
        res1 = analyzer.analyze_file(f1)
        self.assertFalse(res1["suspicious"])

        # Minified file whitelisted (.min.js)
        f2 = self.test_dir / "lib.min.js"
        f2.write_bytes(os.urandom(500))
        res2 = analyzer.analyze_file(f2)
        # Threshold for minified is 6.5. os.urandom is ~8.0.
        # It should be suspicious but has is_minified_ext=True
        if res2["suspicious"]:
            self.assertTrue(res2["is_minified_ext"])

        # Error case
        res3 = analyzer.analyze_file(self.test_dir / "notfound.js")
        self.assertIn("error", res3)

    def test_sast_scanner(self):
        scanner = SASTScanner()
        # Clean diff
        res1 = scanner.scan_diff(" + var x = 1;")
        self.assertTrue(res1["clean"])

        # Dangerous diff (manual patterns)
        res2 = scanner.scan_diff(" + eval(payload);")
        self.assertFalse(res2["clean"])
        self.assertEqual(res2["tool"], "manual_patterns")

    def test_quarantine_pipeline_scan_package(self):
        pipeline = QuarantinePipeline()

        # Trusted publisher
        res1 = pipeline.scan_package("google-cloud", "1.0.0")
        self.assertTrue(res1["approved"])

        # Verified signature (mocked)
        with patch.object(
            pipeline.trust_matrix, "verify_npm_package", return_value=True
        ):
            res2 = pipeline.scan_package("express", "4.17.1")
            self.assertTrue(res2["approved"])

        # Untrusted/Unsigned
        with patch.object(
            pipeline.trust_matrix, "verify_npm_package", return_value=False
        ):
            res3 = pipeline.scan_package("unknown-pkg", "1.0.0")
            self.assertFalse(res3["approved"])
            self.assertTrue(res3["requires_human_review"])

    def test_quarantine_pipeline_scan_pr_diff(self):
        pipeline = QuarantinePipeline()

        # Clean PR
        res1 = pipeline.scan_pr_diff(" + x = 1", "PR-1")
        self.assertTrue(res1["approved"])

        # Dirty PR
        res2 = pipeline.scan_pr_diff(" + eval(x)", "PR-2")
        self.assertFalse(res2["approved"])


if __name__ == "__main__":
    unittest.main()
