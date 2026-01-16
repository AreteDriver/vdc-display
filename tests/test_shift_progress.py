"""Tests for shift progress calculations."""

import pytest
from datetime import date, datetime
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.shift_progress import (
    get_current_shift,
    calculate_shift_workload,
    get_demo_data,
)


class TestGetCurrentShift:
    """Tests for get_current_shift function."""

    @patch('modules.shift_progress.datetime')
    def test_day_shift_morning(self, mock_datetime):
        """6 AM should be day shift."""
        mock_datetime.now.return_value = datetime(2026, 1, 16, 6, 0, 0)
        assert get_current_shift() == "day"

    @patch('modules.shift_progress.datetime')
    def test_day_shift_afternoon(self, mock_datetime):
        """12 PM should be day shift."""
        mock_datetime.now.return_value = datetime(2026, 1, 16, 12, 0, 0)
        assert get_current_shift() == "day"

    @patch('modules.shift_progress.datetime')
    def test_day_shift_end(self, mock_datetime):
        """5:59 PM should still be day shift."""
        mock_datetime.now.return_value = datetime(2026, 1, 16, 17, 59, 0)
        assert get_current_shift() == "day"

    @patch('modules.shift_progress.datetime')
    def test_night_shift_evening(self, mock_datetime):
        """6 PM should be night shift."""
        mock_datetime.now.return_value = datetime(2026, 1, 16, 18, 0, 0)
        assert get_current_shift() == "night"

    @patch('modules.shift_progress.datetime')
    def test_night_shift_midnight(self, mock_datetime):
        """Midnight should be night shift."""
        mock_datetime.now.return_value = datetime(2026, 1, 16, 0, 0, 0)
        assert get_current_shift() == "night"

    @patch('modules.shift_progress.datetime')
    def test_night_shift_early_morning(self, mock_datetime):
        """5 AM should be night shift."""
        mock_datetime.now.return_value = datetime(2026, 1, 16, 5, 0, 0)
        assert get_current_shift() == "night"


class TestGetDemoData:
    """Tests for demo data fallback."""

    def test_demo_data_structure(self):
        """Demo data should have all required fields."""
        data = get_demo_data()

        required_fields = [
            'shift', 'date', 'new_hours', 'carryover_hours',
            'total_hours', 'completed_hours', 'percent_complete',
            'vehicles_total', 'vehicles_completed'
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_demo_data_types(self):
        """Demo data should have correct types."""
        data = get_demo_data()

        assert isinstance(data['shift'], str)
        assert isinstance(data['date'], str)
        assert isinstance(data['new_hours'], (int, float))
        assert isinstance(data['carryover_hours'], (int, float))
        assert isinstance(data['total_hours'], (int, float))
        assert isinstance(data['completed_hours'], (int, float))
        assert isinstance(data['percent_complete'], int)
        assert isinstance(data['vehicles_total'], int)
        assert isinstance(data['vehicles_completed'], int)

    def test_demo_data_math(self):
        """Demo data math should be consistent."""
        data = get_demo_data()

        # Total hours = new + carryover
        assert data['total_hours'] == data['new_hours'] + data['carryover_hours']

        # Percent complete should match hours
        expected_percent = int(data['completed_hours'] / data['total_hours'] * 100)
        assert data['percent_complete'] == expected_percent

    def test_demo_data_shift_valid(self):
        """Demo shift should be 'day' or 'night'."""
        data = get_demo_data()
        assert data['shift'] in ('day', 'night')

    def test_demo_data_vehicles_valid(self):
        """Completed vehicles should not exceed total."""
        data = get_demo_data()
        assert data['vehicles_completed'] <= data['vehicles_total']


class TestCalculateShiftWorkload:
    """Tests for calculate_shift_workload with mocked database."""

    @patch('modules.shift_progress.query_one')
    def test_empty_database(self, mock_query):
        """Should handle empty database gracefully."""
        mock_query.return_value = None

        result = calculate_shift_workload('day', date(2026, 1, 16))

        assert result['total_hours'] == 0
        assert result['completed_hours'] == 0
        assert result['percent_complete'] == 0

    @patch('modules.shift_progress.query_one')
    def test_zero_total_hours(self, mock_query):
        """Should handle zero total hours without division error."""
        mock_query.side_effect = [
            {'total_vehicles': 0, 'total_hours': 0, 'completed_vehicles': 0},
            {'completed_hours': 0},
            None  # No carryover
        ]

        result = calculate_shift_workload('day', date(2026, 1, 16))

        assert result['percent_complete'] == 0  # No division by zero

    @patch('modules.shift_progress.query_one')
    def test_with_carryover(self, mock_query):
        """Should include carryover hours in total."""
        mock_query.side_effect = [
            {'total_vehicles': 10, 'total_hours': 100, 'completed_vehicles': 5},
            {'completed_hours': 50},
            {'carryover_hours': 20}
        ]

        result = calculate_shift_workload('day', date(2026, 1, 16))

        assert result['new_hours'] == 100
        assert result['carryover_hours'] == 20
        assert result['total_hours'] == 120
