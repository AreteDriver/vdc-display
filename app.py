"""
VDC-Display: TV Dashboard for Shift Progress

Designed for 32-36" TVs at 15-30ft viewing distance.
Auto-refreshes every 10 minutes. No user interaction required.
"""

import os
import streamlit as st
from datetime import datetime

# Configure page - must be first Streamlit command
st.set_page_config(
    page_title="VDC Shift Progress",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# TV-optimized CSS
TV_STYLES = """
<style>
    /* Hide Streamlit UI elements for kiosk mode */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Dark theme with high contrast */
    .stApp {
        background-color: #1a1a2e;
        color: #ffffff;
    }

    /* Main metrics - large readable numbers */
    .big-number {
        font-size: 96px;
        font-weight: 700;
        color: #00d4ff;
        text-align: center;
        line-height: 1.1;
        margin: 0;
    }

    .medium-number {
        font-size: 64px;
        font-weight: 600;
        color: #ffffff;
        text-align: center;
        margin: 0;
    }

    .metric-label {
        font-size: 32px;
        font-weight: 400;
        color: #888888;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 8px;
    }

    /* Progress bar styling */
    .progress-container {
        background-color: #2d2d44;
        border-radius: 16px;
        height: 48px;
        margin: 24px 0;
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        border-radius: 16px;
        transition: width 0.5s ease;
    }

    .progress-good { background: linear-gradient(90deg, #00d4ff, #00ff88); }
    .progress-warning { background: linear-gradient(90deg, #ffaa00, #ff6600); }
    .progress-behind { background: linear-gradient(90deg, #ff4444, #ff0066); }

    /* Stage cards */
    .stage-card {
        background-color: #2d2d44;
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
    }

    .stage-name {
        font-size: 36px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .stage-percent {
        font-size: 48px;
        font-weight: 700;
        color: #00d4ff;
    }

    .stage-detail {
        font-size: 24px;
        color: #888888;
    }

    /* Timestamp footer */
    .timestamp {
        font-size: 24px;
        color: #666666;
        text-align: center;
        margin-top: 32px;
    }

    /* Shift header */
    .shift-header {
        font-size: 42px;
        font-weight: 600;
        color: #ffffff;
        text-align: center;
        margin-bottom: 16px;
    }

    .carryover-note {
        font-size: 28px;
        color: #ffaa00;
        text-align: center;
    }
</style>
"""

# Auto-refresh interval (milliseconds)
REFRESH_INTERVAL_MS = int(os.environ.get("REFRESH_INTERVAL_MINUTES", 10)) * 60 * 1000


def get_progress_class(percent: int) -> str:
    """Return CSS class based on progress percentage."""
    if percent >= 60:
        return "progress-good"
    elif percent >= 40:
        return "progress-warning"
    return "progress-behind"


def load_data() -> tuple[dict, list[dict]]:
    """Load shift progress and stage breakdown data."""
    try:
        from modules.shift_progress import calculate_shift_workload
        from modules.stage_breakdown import get_stage_breakdown

        shift_data = calculate_shift_workload()
        stage_data = get_stage_breakdown(shift_data['shift'])
        return shift_data, stage_data
    except Exception:
        # Fall back to demo data if database unavailable
        from modules.shift_progress import get_demo_data
        from modules.stage_breakdown import get_demo_stages

        return get_demo_data(), get_demo_stages()


def main():
    """Render the TV dashboard."""
    # Inject TV-optimized styles
    st.markdown(TV_STYLES, unsafe_allow_html=True)

    # Auto-refresh meta tag
    st.markdown(
        f'<meta http-equiv="refresh" content="{REFRESH_INTERVAL_MS // 1000}">',
        unsafe_allow_html=True
    )

    # Load data
    shift_data, stage_data = load_data()

    # Shift header
    shift_label = "Day Shift" if shift_data['shift'] == 'day' else "Night Shift"
    st.markdown(f'<div class="shift-header">📊 {shift_label} Progress</div>', unsafe_allow_html=True)

    # Carryover note (if applicable)
    if shift_data['carryover_hours'] > 0:
        st.markdown(
            f'<div class="carryover-note">'
            f'⚠️ {shift_data["total_hours"]:.0f} hours '
            f'({shift_data["new_hours"]:.0f} new + {shift_data["carryover_hours"]:.0f} carryover)'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Main progress section
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.markdown(
            f'<p class="big-number">{shift_data["completed_hours"]:.0f}</p>'
            f'<p class="metric-label">Hours Complete</p>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f'<p class="medium-number" style="color: #888888;">/</p>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f'<p class="big-number">{shift_data["total_hours"]:.0f}</p>'
            f'<p class="metric-label">Total Hours</p>',
            unsafe_allow_html=True
        )

    # Progress bar
    progress_class = get_progress_class(shift_data['percent_complete'])
    st.markdown(
        f'<div class="progress-container">'
        f'<div class="progress-bar {progress_class}" style="width: {shift_data["percent_complete"]}%;"></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Percentage display
    st.markdown(
        f'<p class="big-number" style="font-size: 120px;">{shift_data["percent_complete"]}%</p>'
        f'<p class="metric-label">Complete</p>',
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Stage breakdown
    st.markdown('<div class="shift-header" style="font-size: 36px;">Stage Breakdown</div>', unsafe_allow_html=True)

    cols = st.columns(len(stage_data)) if stage_data else []

    for i, stage in enumerate(stage_data):
        with cols[i]:
            st.markdown(
                f'<div class="stage-card">'
                f'<div class="stage-name">{stage["stage_name"]}</div>'
                f'<div class="stage-percent">{stage["percent_complete"]}%</div>'
                f'<div class="stage-detail">{stage["vehicle_count"]} vehicles</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    # Vehicles count
    st.markdown("<br>", unsafe_allow_html=True)
    vcol1, vcol2 = st.columns(2)

    with vcol1:
        st.markdown(
            f'<p class="medium-number">{shift_data["vehicles_completed"]}</p>'
            f'<p class="metric-label">Vehicles Completed</p>',
            unsafe_allow_html=True
        )

    with vcol2:
        st.markdown(
            f'<p class="medium-number">{shift_data["vehicles_total"]}</p>'
            f'<p class="metric-label">Total Vehicles</p>',
            unsafe_allow_html=True
        )

    # Timestamp
    st.markdown(
        f'<div class="timestamp">Last Updated: {datetime.now().strftime("%I:%M %p")} • '
        f'Auto-refresh every {REFRESH_INTERVAL_MS // 60000} minutes</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
