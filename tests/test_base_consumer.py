import unittest
from unittest.mock import MagicMock, patch
from orchestrator.consumers.base_consumer import BaseConsumer


class MockConsumer(BaseConsumer):
    AGENT_NAME = "TestAgent"

    def process(self, msg_id, data):
        if data.get("fail"):
            raise ValueError("Forced failure")
        self.processed_id = msg_id

    def stop(self):
        self._running = False

    def ack(self, msg_id):
        self.r.xack(self.stream_name, self.consumer_group, msg_id)


class TestBaseConsumer(unittest.TestCase):
    def setUp(self):
        self.mock_r = MagicMock()
        with patch(
            "orchestrator.consumers.base_consumer._get_redis", return_value=self.mock_r
        ):
            with patch("signal.signal"):
                self.consumer = MockConsumer(
                    stream_name="test-stream",
                    consumer_group="test-cg",
                    consumer_name="test-c",
                )

    def test_init(self):
        self.assertEqual(self.consumer.stream_name, "test-stream")
        self.assertEqual(self.consumer.consumer_group, "test-cg")
        self.mock_r.xgroup_create.assert_called()

    def test_ensure_group_exists(self):
        self.mock_r.xgroup_create.side_effect = Exception("BUSYGROUP")
        self.consumer._ensure_group()  # Should not raise

    def test_publish(self):
        self.mock_r.xadd.return_value = "1-0"
        res = self.consumer.publish("out", {"a": 1})
        self.assertEqual(res, "1-0")

    def test_state_management(self):
        self.consumer.set_state("k", "v")
        self.mock_r.set.assert_called_with("k", "v")

        self.mock_r.get.return_value = '"val"'
        self.assertEqual(self.consumer.get_state_json("k"), "val")

        self.consumer.set_state_json("k2", {"x": 1})
        self.mock_r.setex.assert_called()

    def test_reclaim_pending(self):
        self.mock_r.xautoclaim.return_value = ["0-0", [("1-0", {"data": 1})]]
        msgs = self.consumer._reclaim_pending()
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0][0], "1-0")

    def test_run_single_loop(self):
        # Mocking run loop
        self.mock_r.xautoclaim.return_value = [None, [("1-0", {"data": "test"})]]

        # Stop loop after one iteration
        def side_effect(*args, **kwargs):
            self.consumer._running = False
            return [None, [("1-0", {"data": "test"})]]

        self.mock_r.xautoclaim.side_effect = side_effect

        self.consumer.run()
        self.assertEqual(self.consumer.processed_id, "1-0")
        self.mock_r.xack.assert_called_with("test-stream", "test-cg", "1-0")

    def test_run_error_handling(self):
        self.mock_r.xautoclaim.return_value = [None, [("1-1", {"fail": True})]]

        def side_effect(*args, **kwargs):
            self.consumer._running = False
            return [None, [("1-1", {"fail": True})]]

        self.mock_r.xautoclaim.side_effect = side_effect

        self.consumer.run()
        # Should not call xack due to error
        self.mock_r.xack.assert_not_called()

    def test_base_consumer_ack_call(self):
        with patch(
            "orchestrator.consumers.base_consumer._get_redis", return_value=self.mock_r
        ):
            with patch("signal.signal"):
                consumer = MockConsumer(
                    stream_name="test", consumer_group="cg", consumer_name="c"
                )
                consumer.ack("msg123")
                self.mock_r.xack.assert_called()

    def test_base_consumer_stop_call(self):
        with patch("orchestrator.consumers.base_consumer._get_redis"):
            with patch("signal.signal"):
                consumer = MockConsumer(
                    stream_name="test", consumer_group="cg", consumer_name="c"
                )
                consumer.stop()
                self.assertFalse(consumer._running)


if __name__ == "__main__":
    unittest.main()
