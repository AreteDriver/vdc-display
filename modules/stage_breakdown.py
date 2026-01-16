"""Stage breakdown calculations for TV dashboard."""

from datetime import date
from .database import query_df, query_one


def get_stage_breakdown(shift: str | None = None, target_date: date | None = None) -> list[dict]:
    """
    Get breakdown of vehicles/hours by production stage.

    Returns list of:
        {
            'stage_name': str,
            'stage_order': int,
            'vehicle_count': int,
            'hours_remaining': float,
            'hours_completed': float,
            'percent_complete': int
        }
    """
    if target_date is None:
        target_date = date.today()

    date_str = target_date.isoformat()

    query = """
        SELECT
            ps.stage_name,
            ps.stage_order,
            COUNT(v.id) as vehicle_count,
            COALESCE(SUM(
                CASE WHEN wo.status != 'complete'
                THEN wo.estimated_hours
                ELSE 0 END
            ), 0) as hours_remaining,
            COALESCE(SUM(
                CASE WHEN wo.status = 'complete'
                THEN wo.actual_hours
                ELSE 0 END
            ), 0) as hours_completed
        FROM production_stages ps
        LEFT JOIN vehicles v ON v.current_stage_id = ps.id
            AND DATE(v.arrival_time) = ?
            AND (? IS NULL OR v.shift_assigned = ?)
        LEFT JOIN work_orders wo ON wo.vehicle_id = v.id
        GROUP BY ps.id, ps.stage_name, ps.stage_order
        ORDER BY ps.stage_order
    """

    results = query_df(query, (date_str, shift, shift))

    # Calculate percentages
    for row in results:
        total = row['hours_remaining'] + row['hours_completed']
        row['percent_complete'] = int((row['hours_completed'] / total * 100) if total > 0 else 0)

    return results


def get_demo_stages() -> list[dict]:
    """Return demo stage data when database is not available."""
    return [
        {
            'stage_name': 'Installation',
            'stage_order': 1,
            'vehicle_count': 12,
            'hours_remaining': 18.5,
            'hours_completed': 42.0,
            'percent_complete': 69
        },
        {
            'stage_name': 'PPO',
            'stage_order': 2,
            'vehicle_count': 8,
            'hours_remaining': 12.0,
            'hours_completed': 24.0,
            'percent_complete': 66  # int(24/36*100) = 66
        },
        {
            'stage_name': 'Shuttle',
            'stage_order': 3,
            'vehicle_count': 6,
            'hours_remaining': 3.0,
            'hours_completed': 9.0,
            'percent_complete': 75
        },
        {
            'stage_name': 'FQA',
            'stage_order': 4,
            'vehicle_count': 10,
            'hours_remaining': 8.0,
            'hours_completed': 12.0,
            'percent_complete': 60
        }
    ]
