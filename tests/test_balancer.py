import unittest
from unittest.mock import MagicMock
from orchestrator.gateway.balancer import DynamicBalancer


class TestBalancer(unittest.TestCase):
    def setUp(self):
        self.mock_r = MagicMock()
        self.balancer = DynamicBalancer(self.mock_r)

    def test_get_resource_state(self):
        self.mock_r.get.side_effect = [
            "1",
            "2.0",
            "10",
            "5",
        ]  # gpu_lock, spent, ceo_total, po_approved
        self.mock_r.xlen.return_value = 5

        state = self.balancer.get_resource_state()
        self.assertTrue(state.gpu_locked)
        self.assertEqual(state.queue_depth, 5)
        self.assertEqual(state.daily_budget_ratio, 0.4)
        self.assertEqual(state.efficiency_ratio, 0.5)

    def test_decide_placement_emergency_budget(self):
        self.mock_r.get.side_effect = [None, "6.0", "10", "5"]
        placement = self.balancer.decide_placement("CEO")
        self.assertIn(placement, ["gpu", "cpu"])

    def test_decide_placement_low_efficiency(self):
        self.mock_r.get.side_effect = [None, "1.0", "10", "1"]
        placement = self.balancer.decide_placement("CEO")
        self.assertEqual(placement, "cpu")

    def test_decide_placement_gpu_locked_queue_busy(self):
        self.mock_r.get.side_effect = ["1", "1.0", "10", "8"]
        self.mock_r.xlen.return_value = 10
        placement = self.balancer.decide_placement("Developer")
        self.assertEqual(placement, "cloud")

    def test_decide_placement_default_roles(self):
        roles = {"CEO": "cloud", "Developer": "gpu", "DevOps": "cpu"}
        for role, expected in roles.items():
            self.mock_r.get.side_effect = [None, "0.0", "1", "1"]
            self.assertEqual(self.balancer.decide_placement(role), expected)

    def test_get_model_for_tier(self):
        self.assertIn(
            "gemini-2.0-pro", self.balancer.get_model_for_tier("cloud", "CEO")
        )
        self.assertIn(
            "deepseek-coder", self.balancer.get_model_for_tier("gpu", "Developer")
        )
        self.assertEqual(
            "ollama/phi3:mini", self.balancer.get_model_for_tier("cpu", "UX")
        )


if __name__ == "__main__":
    unittest.main()
