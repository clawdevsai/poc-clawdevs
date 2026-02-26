import unittest
from unittest.mock import MagicMock, patch
from scripts.gpu_lock import GPULock, _compute_ttl
import os


class TestGPULock(unittest.TestCase):
    def setUp(self):
        self.mock_r = MagicMock()
        # Mocking redis.get to return a default as bytes
        self.mock_r.get.return_value = b"test-agent"
        self.pod_patch = patch.dict(os.environ, {"POD_NAME": "test-agent"})
        self.pod_patch.start()
        self.redis_patch = patch(
            "scripts.gpu_lock._get_redis", return_value=self.mock_r
        )
        self.redis_patch.start()
        self.lock = GPULock(event_key="test-key", poll_interval=0.1)

    def tearDown(self):
        self.redis_patch.stop()
        self.pod_patch.stop()

    def test_get_redis_fail(self):
        # Stop the global patch to use the real function
        self.redis_patch.stop()
        try:
            with patch.dict("sys.modules", {"redis": None}):
                from scripts.gpu_lock import _get_redis

                with self.assertRaises(RuntimeError):
                    _get_redis()
        finally:
            self.redis_patch.start()

    def test_compute_ttl_error(self):
        self.mock_r.get.side_effect = Exception("Redis error")
        self.assertEqual(_compute_ttl(self.mock_r, "key"), 60)
        self.mock_r.get.side_effect = None  # Reset side effect

        # Small payload
        self.mock_r.get.return_value = b"line1\nline2"
        self.assertEqual(_compute_ttl(self.mock_r, "key"), 60)

        # Large payload
        self.mock_r.get.return_value = b"line\n" * 600
        self.assertEqual(_compute_ttl(self.mock_r, "key"), 120)

    def test_acquire_and_release(self):
        # First call fails, second succeeds
        self.mock_r.set.side_effect = [False, True]
        self.mock_r.get.return_value = b"test-agent"

        self.lock.acquire()
        self.assertTrue(self.lock._acquired)
        self.assertEqual(self.mock_r.set.call_count, 2)

        self.lock.release()
        self.assertFalse(self.lock._acquired)
        self.mock_r.delete.assert_called_with("gpu_active_lock")

    def test_context_manager(self):
        self.mock_r.set.return_value = True
        self.mock_r.get.return_value = b"test-agent"

        with GPULock(event_key="test-key") as lock:
            self.assertTrue(lock._acquired)

        self.mock_r.delete.assert_called_with("gpu_active_lock")


if __name__ == "__main__":
    unittest.main()
