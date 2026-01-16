"""Shift progress calculations for TV dashboard."""

from datetime import datetime, date
from .database import query_one


def get_current_shift() -> str:
    """Determine current shift based on time of day."""
    hour = datetime.now().hour
    # Day shift: 6 AM - 6 PM, Night shift: 6 PM - 6 AM
    return "day" if 6 <= hour < 18 else "night"


def calculate_shift_workload(
    shift: str | None = None, target_date: date | None = None
) -> dict:
    """
    Calculate shift workload metrics.

    Returns:
        {
            'shift': 'day' or 'night',
            'date': date string,
            'new_hours': float,
            'carryover_hours': float,
            'total_hours': float,
            'completed_hours': float,
            'percent_complete': int,
            'vehicles_total': int,
            'vehicles_completed': int
        }
    """
    if shift is None:
        shift = get_current_shift()
    if target_date is None:
        target_date = date.today()

    date_str = target_date.isoformat()

    # Get vehicles assigned to this shift
    vehicles_query = """
        SELECT
            COUNT(*) as total_vehicles,
            COALESCE(SUM(estimated_labor_hours), 0) as total_hours,
            COUNT(CASE WHEN status = 'delivered' THEN 1 END) as completed_vehicles
        FROM vehicles
        WHERE shift_assigned = ?
        AND DATE(arrival_time) = ?
    """
    vehicle_stats = query_one(vehicles_query, (shift, date_str))

    if not vehicle_stats:
        vehicle_stats = {"total_vehicles": 0, "total_hours": 0, "completed_vehicles": 0}

    # Get completed work hours from work orders
    completed_query = """
        SELECT COALESCE(SUM(actual_hours), 0) as completed_hours
        FROM work_orders wo
        JOIN vehicles v ON wo.vehicle_id = v.id
        WHERE v.shift_assigned = ?
        AND DATE(v.arrival_time) = ?
        AND wo.status = 'complete'
    """
    completed_stats = query_one(completed_query, (shift, date_str))
    completed_hours = completed_stats["completed_hours"] if completed_stats else 0

    # Get carryover from previous shift
    carryover_query = """
        SELECT COALESCE(carryover_hours, 0) as carryover_hours
        FROM shift_summaries
        WHERE shift_date = ?
        AND shift_type = ?
        ORDER BY created_at DESC
        LIMIT 1
    """
    carryover_stats = query_one(carryover_query, (date_str, shift))
    carryover_hours = carryover_stats["carryover_hours"] if carryover_stats else 0

    new_hours = float(vehicle_stats["total_hours"])
    total_hours = new_hours + carryover_hours

    percent_complete = int(
        (completed_hours / total_hours * 100) if total_hours > 0 else 0
    )

    return {
        "shift": shift,
        "date": date_str,
        "new_hours": new_hours,
        "carryover_hours": carryover_hours,
        "total_hours": total_hours,
        "completed_hours": completed_hours,
        "percent_complete": percent_complete,
        "vehicles_total": vehicle_stats["total_vehicles"],
        "vehicles_completed": vehicle_stats["completed_vehicles"],
    }


def get_demo_data() -> dict:
    """Return demo data when database is not available."""
    return {
        "shift": get_current_shift(),
        "date": date.today().isoformat(),
        "new_hours": 126.0,
        "carryover_hours": 6.0,
        "total_hours": 132.0,
        "completed_hours": 87.0,
        "percent_complete": 65,  # int(87/132*100) = 65
        "vehicles_total": 48,
        "vehicles_completed": 32,
    }
