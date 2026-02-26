import unittest
from unittest.mock import MagicMock, patch
from orchestrator.consumers.circuit_breaker import (
    DraftRejectedCircuitBreaker,
    RAGHealthCheck,
)
from pathlib import Path
import tempfile
import shutil
import os


class TestCircuitBreaker(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.environ["MEMORY_BASE_DIR"] = self.test_dir
        self.mock_r = MagicMock()
        with patch(
            "orchestrator.consumers.circuit_breaker._get_redis",
            return_value=self.mock_r,
        ):
            self.cb = DraftRejectedCircuitBreaker()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        if "MEMORY_BASE_DIR" in os.environ:
            del os.environ["MEMORY_BASE_DIR"]

    def test_cb_record_rejection_limit(self):
        self.mock_r.incr.return_value = 1
        state = self.cb.record_rejection("epic-1", "Wrong architecture")
        self.assertFalse(state["circuit_open"])

        self.mock_r.incr.return_value = 3
        state = self.cb.record_rejection("epic-1", "Still wrong")
        self.assertTrue(state["circuit_open"])
        self.assertTrue(self.mock_r.set.called)

    def test_cb_escalation(self):
        self.mock_r.incr.return_value = 5
        with patch("pathlib.Path.write_text"):
            state = self.cb.record_rejection("epic-2", "Fatal error")
            self.assertTrue(state["escalated"])
            self.assertTrue(self.mock_r.xadd.called)

    def test_cb_approval_resets(self):
        self.cb.record_approval("epic-1")
        self.mock_r.delete.assert_called_with(self.cb._rejection_key("epic-1"))

    def test_cb_defrost(self):
        self.cb.defrost_epic("epic-1", "New context")
        self.assertTrue(self.mock_r.xadd.called)
        self.assertTrue(self.mock_r.delete.called)


class TestRAGHealthCheck(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.docs = Path(self.test_dir) / "docs"
        self.docs.mkdir()
        self.workspace = Path(self.test_dir) / "workspace"
        self.workspace.mkdir()
        (self.workspace / "docs").mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_rag_health_check_full(self):
        rag = RAGHealthCheck(docs_dir=self.docs, workspace_dir=self.workspace)
        with patch("subprocess.run") as mock_run:
            # Mock successful git log
            mock_run.return_value.stdout = "abc 2026-01-01 Fix docs"
            mock_run.return_value.returncode = 0

            # Create some expected directories
            (self.workspace / "orchestrator").mkdir()
            (self.workspace / "k8s").mkdir()
            (self.workspace / "scripts").mkdir()
            (self.workspace / "memory").mkdir()

            results = rag.run("epic-1")
            self.assertEqual(results["epic_id"], "epic-1")
            self.assertEqual(results["checks"]["workspace_structure"]["status"], "ok")
            self.assertEqual(results["checks"]["doc_freshness"]["status"], "ok")
            self.assertIn("Diagnóstico", results["sanitized_context"])

    def test_rag_health_check_missing_dirs(self):
        rag = RAGHealthCheck(docs_dir=self.docs, workspace_dir=self.workspace)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = ""
            # No dirs created except the ones in setUp (docs/ and workspace/docs)
            results = rag.run("epic-2")
            self.assertEqual(
                results["checks"]["workspace_structure"]["status"], "incomplete"
            )
            self.assertIn(
                "orchestrator/",
                results["checks"]["workspace_structure"]["missing_dirs"],
            )
            self.assertIn("Pastas ausentes", results["sanitized_context"])

    def test_rag_health_check_git_error(self):
        rag = RAGHealthCheck(docs_dir=self.docs, workspace_dir=self.workspace)
        with patch("subprocess.run", side_effect=Exception("git not found")):
            results = rag.run("epic-3")
            self.assertEqual(results["checks"]["doc_freshness"]["status"], "error")
            self.assertIn("git not found", results["checks"]["doc_freshness"]["error"])


if __name__ == "__main__":
    unittest.main()
