# VDC-Display

TV Dashboard for Vehicle Distribution Center shift progress. Designed for facility floor displays showing real-time labor hours and production stage status.

## Features

- **Shift Labor Progress** — Hours complete vs total, percentage bar
- **Stage Breakdown** — Installation, PPO, Shuttle, FQA percentages
- **Carryover Display** — Shows inherited work from previous shift
- **Auto-refresh** — Updates every 10 minutes (configurable)
- **Kiosk Mode** — No user interaction required

## Display Optimization

Designed for 32-36" TVs at 15-30ft viewing distance:
- 96px numbers for primary metrics
- 48px+ for secondary values
- High contrast dark theme
- No scrolling required

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with demo data
streamlit run app.py --server.port 8503

# Run with database
DATABASE_PATH=/path/to/logistics.db streamlit run app.py --server.port 8503
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `data/logistics.db` | Path to shared SQLite database |
| `REFRESH_INTERVAL_MINUTES` | `10` | Dashboard refresh interval |

## Docker

```bash
docker run -p 8503:8503 \
  -v /data/logistics.db:/app/data/logistics.db:ro \
  -e REFRESH_INTERVAL_MINUTES=10 \
  vdc-display
```

## Architecture

```
vdc-display/
├── app.py                 # Main Streamlit dashboard
├── modules/
│   ├── database.py        # Read-only DB connection
│   ├── shift_progress.py  # Labor hours calculation
│   └── stage_breakdown.py # Per-stage percentages
└── requirements.txt
```

Part of the VDC operational intelligence suite:
- [VDC-Production](https://github.com/AreteDriver/vdc-production) — Supervisor analytics (port 8501)
- [VDC-Logistics](https://github.com/AreteDriver/vdc-logistics) — Floor team tool (port 8502)
- **VDC-Display** — TV dashboard (port 8503)

## License

MIT
