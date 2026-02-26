import unittest
from unittest.mock import MagicMock, patch
from orchestrator.consumers.review_pipeline import (
    PreGPUValidator,
    BatchingBuffer,
    ReviewPipeline,
)


class TestReviewPipelineComponents(unittest.TestCase):
    def test_pre_gpu_validator(self):
        validator = PreGPUValidator()
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = {
                "response": '{"valid": false, "issues": ["Syntax error"]}'
            }
            mock_post.return_value.status_code = 200

            res = validator.validate("print('hi", "python")
            self.assertFalse(res["valid"])
            self.assertIn("Syntax error", res["issues"])

    def test_batching_buffer(self):
        mock_r = MagicMock()
        buffer = BatchingBuffer(mock_r, max_batch_size=2)

        mock_r.llen.return_value = 1
        self.assertEqual(buffer.add("pr-1", "diff1"), 1)

        mock_r.llen.return_value = 2
        self.assertTrue(buffer.should_flush())

        mock_r.lpop.side_effect = ['{"pr_id": "pr-1"}', None]
        items = buffer.flush()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["pr_id"], "pr-1")


class TestReviewPipelineFlow(unittest.TestCase):
    def setUp(self):
        self.mock_r = MagicMock()
        # Mocking gpu_lock and _get_redis inside ReviewPipeline.__init__
        with patch(
            "orchestrator.consumers.base_consumer._get_redis", return_value=self.mock_r
        ):
            with patch("scripts.gpu_lock.GPULock") as mock_lock:
                self.pipeline = ReviewPipeline()
                self.mock_lock = mock_lock

    def test_run_review_full_success(self):
        # Mock PreGPU
        self.pipeline.pre_gpu.validate = MagicMock(return_value={"valid": True})

        # Mock Ollama calls for Architect, QA, CyberSec
        # architect (approved), qa (approved), cybersec (approved)
        self.pipeline._call_ollama = MagicMock(
            side_effect=[
                '{"approved": true, "comments": []}',  # Architect
                '{"approved": true, "comments": []}',  # QA
                '{"approved": true, "comments": []}',  # CyberSec
            ]
        )

        res = self.pipeline.run_review("pr-1", "some diff", "issue-1")
        self.assertTrue(res["approved"])
        self.assertEqual(self.mock_r.xadd.call_count, 1)

    def test_run_review_architect_fail(self):
        self.pipeline.pre_gpu.validate = MagicMock(return_value={"valid": True})
        self.pipeline._call_ollama = MagicMock(
            side_effect=[
                '{"approved": false, "comments": ["Refactor needed"]}',  # Architect
                '{"approved": true, "comments": []}',  # CyberSec (QA is skipped)
            ]
        )

        res = self.pipeline.run_review("pr-1", "some diff", "issue-1")
        self.assertFalse(res["approved"])
        self.assertNotIn("qa", res["reviews"])

    def test_run_review_dba_trigger(self):
        self.pipeline.pre_gpu.validate = MagicMock(return_value={"valid": True})
        self.pipeline._call_ollama = MagicMock(
            return_value='{"approved": true, "comments": []}'
        )

        diff_with_migration = "Adding new migration for schema"
        res = self.pipeline.run_review("pr-1", diff_with_migration, "issue-1")
        self.assertIn("dba", res["reviews"])


if __name__ == "__main__":
    unittest.main()
