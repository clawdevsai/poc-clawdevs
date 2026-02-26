import unittest
from unittest.mock import MagicMock, patch
from orchestrator.gateway.gateway import (
    Gateway,
    TokenBucket,
    EfficiencyDegradation,
    ContextTruncator,
    DegradationBudget,
    HeadblessClusterWatchdog,
    VFMScore,
)
import time


class TestGateway(unittest.TestCase):
    def setUp(self):
        self.mock_r = MagicMock()

    def test_token_bucket(self):
        bucket = TokenBucket(self.mock_r, limit=2)
        pipeline = self.mock_r.pipeline.return_value
        pipeline.execute.return_value = [0, 1]
        self.assertTrue(bucket.allow())

        pipeline.execute.return_value = [0, 2]
        self.assertFalse(bucket.allow())

    def test_efficiency_degradation(self):
        eff = EfficiencyDegradation(self.mock_r, min_ratio=0.5)
        # Sequence of calls to self.r.get inside is_degraded and get_model_for_ceo
        # Each check calls get twice if not degraded, once if degraded?
        # is_degraded: total = get(IDEAS), app = get(APPROVED). (4/10 = 0.4 < 0.5 -> True)
        self.mock_r.get.side_effect = ["10", "4", "10", "4"]
        self.assertTrue(eff.is_degraded())
        self.assertEqual(eff.get_model_for_ceo(), "phi3:mini")

        self.mock_r.get.side_effect = ["10", "6", "10", "6"]
        self.assertFalse(eff.is_degraded())
        self.assertIn("gemini", eff.get_model_for_ceo().lower())

    def test_context_truncator(self):
        trunc = ContextTruncator(max_tokens=10)
        payload = "a" * 100
        truncated, was_truncated = trunc.truncate(payload)
        self.assertTrue(was_truncated)
        self.assertIn("[... CONTEÚDO TRUNCADO", truncated)

        payload_with_criteria = (
            "Normal <!-- CRITERIOS_ACEITE -->Do this<!-- /CRITERIOS_ACEITE --> End"
        )
        clean, criteria = trunc.protect_acceptance_criteria(payload_with_criteria)
        self.assertEqual(criteria, "Do this")
        self.assertIn("[CRITERIOS_PROTEGIDOS]", clean)

    def test_vfm_score_logic(self):
        vfm = VFMScore("evt1", 100, 1.0, 0.01, 10.0, 5.0, 0.0)
        self.assertTrue(vfm.approved)
        d = vfm.to_dict()
        self.assertEqual(d["event_id"], "evt1")

        vfm_from = VFMScore.from_json(d)
        self.assertEqual(vfm_from.event_id, "evt1")

    def test_gateway_flow(self):
        with patch("orchestrator.gateway.gateway._get_redis", return_value=self.mock_r):
            gw = Gateway()
            gw.token_bucket.allow = MagicMock(return_value=True)

            # VFM Rejected
            event_rejection = {
                "vfm_score": {
                    "event_id": "e1",
                    "estimated_tokens_cost": 100,
                    "estimated_hours_saved": 1.0,
                    "estimated_dollar_cost": 0.01,
                    "benefit_score": 10.0,
                    "net_score": -1.0,
                    "threshold": 0.0,
                }
            }
            self.assertIsNone(gw.process_strategy_event(event_rejection))

            # Full success
            event_ok = {
                "event_id": "evt1",
                "payload": "Small <!-- CRITERIOS_ACEITE -->Criteria<!-- /CRITERIOS_ACEITE -->",
                "vfm_score": {
                    "event_id": "evt1",
                    "estimated_tokens_cost": 100,
                    "estimated_hours_saved": 1.0,
                    "estimated_dollar_cost": 0.01,
                    "benefit_score": 10.0,
                    "net_score": 5.0,
                    "threshold": 0.0,
                },
            }
            res = gw.process_strategy_event(event_ok)
            self.assertIsNotNone(res)
            self.assertEqual(res["acceptance_criteria"], "Criteria")

            gw.process_po_approval("task1")
            gw.process_fifth_strike("task1", "Too slow")
            self.mock_r.get.return_value = "1"
            self.assertTrue(gw.is_brake_active())


class TestWatchdog(unittest.TestCase):
    def setUp(self):
        self.mock_r = MagicMock()
        self.watch = HeadblessClusterWatchdog(self.mock_r, timeout_seconds=1)

    def test_watchdog_loop_recovery_trigger(self):
        # last_cmd is old -> elapsed > timeout
        self.mock_r.get.side_effect = [
            str(int(time.time()) - 10),
            None,
        ]  # None for RECOVERY_ACTIVE

        with patch("time.sleep"):

            def side_effect(*args):
                self.watch._running = False

            with patch.object(
                self.watch, "_trigger_headless_failsafe", side_effect=side_effect
            ) as mock_fail:
                self.watch._running = True
                self.watch._watch_loop()
                self.assertTrue(mock_fail.called)

    def test_watchdog_loop_resume_trigger(self):
        self.mock_r.get.side_effect = [
            str(int(time.time())),
            "1",  # cycle 1
            str(int(time.time())),
            "1",  # cycle 2
            str(int(time.time())),
            "1",  # cycle 3
            str(int(time.time())),
            "1",  # cycle 4
        ]

        with patch("time.sleep"):

            def stop_loop():
                if self.watch.consecutive_stable >= 2:
                    self.watch._running = False

            self.watch._trigger_auto_resume = MagicMock(side_effect=stop_loop)
            self.watch._running = True
            self.watch._watch_loop()
            self.assertTrue(self.watch._trigger_auto_resume.called)

    def test_efficiency_degradation_record(self):
        eff = EfficiencyDegradation(self.mock_r)
        eff.record_ceo_idea()
        self.mock_r.incr.assert_called_with(eff.RATIO_KEY)
        eff.record_po_approved()
        self.mock_r.incr.assert_called_with(eff.APPROVED_KEY)

    def test_degradation_budget_flow(self):
        budget = DegradationBudget(self.mock_r)
        budget.record_fifth_strike()
        self.mock_r.incr.assert_called_with(budget.FIFTH_STRIKE_KEY)
        budget.record_cosmetic_approval()
        self.mock_r.incr.assert_called_with(budget.COSMETIC_APPROVAL_KEY)
        budget.record_task_completed()
        self.mock_r.incr.assert_called_with(budget.SPRINT_TOTAL_KEY)

    def test_failsafe_trigger(self):
        self.watch._trigger_headless_failsafe()
        self.mock_r.set.assert_any_call(self.watch.RECOVERY_ACTIVE_KEY, "1")
        self.assertTrue(self.mock_r.xadd.called)


if __name__ == "__main__":
    unittest.main()
