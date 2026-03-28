# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Unit tests for Metric model - 100% mocked, no external access.
"""

from datetime import datetime, timedelta, UTC
from uuid import UUID, uuid4


class TestMetricModel:
    """Test Metric model creation and validation - UNIT TESTS ONLY."""

    def test_metric_creation(self):
        """Test basic metric creation."""
        from app.models.metric import Metric

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            metric_type="tokens_used",
            value=1000.0,
            period_start=now,
            period_end=period_end,
        )

        assert metric.metric_type == "tokens_used"
        assert metric.value == 1000.0
        assert metric.id is not None
        assert isinstance(metric.id, UUID)

    def test_metric_with_agent(self):
        """Test metric linked to agent."""
        from app.models.metric import Metric

        agent_id = uuid4()
        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            agent_id=agent_id,
            metric_type="tasks_completed",
            value=5.0,
            period_start=now,
            period_end=period_end,
        )

        assert metric.agent_id == agent_id

    def test_metric_type_values(self):
        """Test valid metric_type values."""
        from app.models.metric import Metric

        valid_types = ["tokens_used", "tasks_completed", "approvals_issued", "errors"]

        for metric_type in valid_types:
            now = datetime.now(UTC)
            period_end = now + timedelta(hours=1)

            metric = Metric(
                metric_type=metric_type,
                value=1.0,
                period_start=now,
                period_end=period_end,
            )
            assert metric.metric_type == metric_type

    def test_metric_value_variations(self):
        """Test metric value variations (integers and decimals)."""
        from app.models.metric import Metric

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        # Integer value
        metric1 = Metric(
            metric_type="tasks_completed",
            value=10.0,
            period_start=now,
            period_end=period_end,
        )

        # Decimal value
        metric2 = Metric(
            metric_type="tokens_used",
            value=1234.56,
            period_start=now,
            period_end=period_end,
        )

        assert metric1.value == 10.0
        assert metric2.value == 1234.56

    def test_metric_period_tracking(self):
        """Test metric period tracking."""
        from app.models.metric import Metric
        from datetime import timedelta

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            metric_type="tokens_used",
            value=100.0,
            period_start=now,
            period_end=period_end,
        )

        assert metric.period_start == now
        assert metric.period_end == period_end

    def test_metric_timestamp(self):
        """Test automatic timestamp creation."""
        from app.models.metric import Metric

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            metric_type="errors",
            value=0.0,
            period_start=now,
            period_end=period_end,
        )

        assert metric.created_at is not None
        assert isinstance(metric.created_at, datetime)


class TestMetricScenarios:
    """Test common metric scenarios - UNIT TESTS ONLY."""

    def test_tokens_used_metric(self):
        """Test tokens used tracking."""
        from app.models.metric import Metric

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            metric_type="tokens_used",
            value=2500.0,
            period_start=now,
            period_end=period_end,
        )

        assert metric.metric_type == "tokens_used"
        assert metric.value == 2500.0

    def test_tasks_completed_metric(self):
        """Test tasks completed tracking."""
        from app.models.metric import Metric

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            metric_type="tasks_completed",
            value=15.0,
            period_start=now,
            period_end=period_end,
        )

        assert metric.metric_type == "tasks_completed"
        assert metric.value == 15.0

    def test_approvals_issued_metric(self):
        """Test approvals issued tracking."""
        from app.models.metric import Metric

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            metric_type="approvals_issued",
            value=8.0,
            period_start=now,
            period_end=period_end,
        )

        assert metric.metric_type == "approvals_issued"
        assert metric.value == 8.0

    def test_errors_metric(self):
        """Test errors tracking."""
        from app.models.metric import Metric

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            metric_type="errors",
            value=2.0,
            period_start=now,
            period_end=period_end,
        )

        assert metric.metric_type == "errors"
        assert metric.value == 2.0


class TestMetricEdgeCases:
    """Test edge cases for Metric model."""

    def test_metric_id_is_uuid(self):
        """Test that metric ID is UUID."""
        from app.models.metric import Metric

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            metric_type="uuid-metric",
            value=1.0,
            period_start=now,
            period_end=period_end,
        )

        assert isinstance(metric.id, UUID)
        assert len(str(metric.id)) == 36

    def test_metric_zero_values(self):
        """Test metric with zero values."""
        from app.models.metric import Metric

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            metric_type="tokens_used",
            value=0.0,
            period_start=now,
            period_end=period_end,
        )

        assert metric.value == 0.0

    def test_metric_none_values(self):
        """Test metric with None values."""
        from app.models.metric import Metric

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            metric_type="none-values-metric",
            value=1.0,
            agent_id=None,
            period_start=now,
            period_end=period_end,
        )

        assert metric.agent_id is None

    def test_metric_large_values(self):
        """Test metric with large values."""
        from app.models.metric import Metric

        now = datetime.now(UTC)
        period_end = now + timedelta(hours=1)

        metric = Metric(
            metric_type="large-values-metric",
            value=999999999.99,
            period_start=now,
            period_end=period_end,
        )

        assert metric.value == 999999999.99
