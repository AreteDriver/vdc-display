"""Tests for stage breakdown calculations."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.stage_breakdown import get_demo_stages


class TestGetDemoStages:
    """Tests for demo stage data."""

    def test_demo_stages_not_empty(self):
        """Should return at least one stage."""
        stages = get_demo_stages()
        assert len(stages) > 0

    def test_demo_stages_structure(self):
        """Each stage should have required fields."""
        stages = get_demo_stages()

        required_fields = [
            "stage_name",
            "stage_order",
            "vehicle_count",
            "hours_remaining",
            "hours_completed",
            "percent_complete",
        ]

        for stage in stages:
            for field in required_fields:
                assert field in stage, f"Missing field: {field}"

    def test_demo_stages_order(self):
        """Stages should be in order."""
        stages = get_demo_stages()
        orders = [s["stage_order"] for s in stages]
        assert orders == sorted(orders)

    def test_demo_stages_percent_valid(self):
        """Percent complete should be 0-100."""
        stages = get_demo_stages()
        for stage in stages:
            assert 0 <= stage["percent_complete"] <= 100

    def test_demo_stages_percent_calculation(self):
        """Percent should match hours calculation."""
        stages = get_demo_stages()

        for stage in stages:
            total = stage["hours_remaining"] + stage["hours_completed"]
            if total > 0:
                expected = int(stage["hours_completed"] / total * 100)
                assert stage["percent_complete"] == expected

    def test_demo_stages_names(self):
        """Should include expected production stages."""
        stages = get_demo_stages()
        names = [s["stage_name"] for s in stages]

        # At minimum, should have these stages
        expected = ["Installation", "PPO", "FQA"]
        for exp in expected:
            assert exp in names, f"Missing stage: {exp}"

    def test_demo_stages_vehicle_count_positive(self):
        """Vehicle counts should be non-negative."""
        stages = get_demo_stages()
        for stage in stages:
            assert stage["vehicle_count"] >= 0

    def test_demo_stages_hours_non_negative(self):
        """Hours should be non-negative."""
        stages = get_demo_stages()
        for stage in stages:
            assert stage["hours_remaining"] >= 0
            assert stage["hours_completed"] >= 0
