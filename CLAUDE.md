# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SolarPilot is a German-language PV monitoring system for a Solplanet ASW015K-TH inverter with asymmetric East/West solar array (15.575 kWp total: 6.23 kWp East, 9.345 kWp West). The system runs on Raspberry Pi 4 as a Docker stack and collects live data every 30 seconds from a local Ai-Dongle.

**Current Status:** Phase 1 (Foundation) - Live data collection, basic dashboard, no forecasting yet.

## Architecture

### Docker Stack (4 Containers)
```
nginx (port 80) → frontend (port 3000)
                 → backend (port 8080) → SQLite (/app/data/solarpilot.db)
```

**Backend:** FastAPI (async-first) + SQLAlchemy (async) + aiohttp
**Frontend:** React 18 + Vite + TailwindCSS (German UI)
**Database:** SQLite with live_data table (30-second polling intervals)

### Key Components

**`backend/app/services/solplanet_collector.py`** - Most critical component
- Polls 3 Dongle endpoints in parallel every 30 seconds:
  - Device 2: Inverter (MPPT data)
  - Device 3: Smartmeter (grid power)
  - Device 4: Battery (SOC, power)
- Calculates East/West split based on MPPT mapping in .env
- Computes house consumption: `PV + Battery + Grid`
- **⚠️ JSON keys are placeholders** - must be adapted to real Dongle API structure

**`backend/app/config.py`** - Configuration management
- MPPT mapping: `MPPT_EAST` and `MPPT_WEST` (comma-separated, e.g., "1" and "2,3")
- Parses to lists via `mppt_east_list` and `mppt_west_list` properties

**`frontend/src/components/EnergyFlowDiagram.jsx`** - Main UI component
- Shows 4 blocks: Solar (with East/West), Battery, House, Grid
- Updates every 30 seconds via `useLiveData` hook

### Energy Balance Formula

**Critical:** Sign conventions must be correct:
```
House Consumption = PV_total + Battery_power + Grid_power

Where:
- Battery_power: positive = charging (energy IN), negative = discharging (energy OUT)
- Grid_power: positive = import (energy IN), negative = export (energy OUT)
```

If the house consumption calculation seems wrong, check sign conventions in the Dongle API response.

## Development Commands

### Local Development (with Hot-Reload)
```bash
# Start dev containers
docker-compose -f docker-compose.dev.yml up --build

# Access points:
# - Frontend: http://localhost:3000
# - Backend API docs: http://localhost:8080/docs
# - Health check: http://localhost:8080/api/health

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend

# Stop containers
docker-compose -f docker-compose.dev.yml down
```

### Production Deployment (Raspberry Pi)
```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f
docker-compose logs -f backend  # Backend only

# Restart after code changes
docker-compose down
docker-compose up -d --build

# Health check
curl http://localhost/api/health
```

### Database Inspection
```bash
# Enter backend container
docker exec -it solarpilot-app bash

# Open SQLite
sqlite3 /app/data/solarpilot.db

# View recent data
SELECT timestamp, pv_total_power, pv_east_power, pv_west_power,
       battery_soc, grid_power, house_consumption
FROM live_data
ORDER BY timestamp DESC
LIMIT 10;

# Exit
.exit
exit
```

### Testing Dongle API
```bash
# Required before first run to identify correct JSON keys
curl "http://192.168.10.113:8484/getdevdata.cgi?device=2&sn=UR015K6052540222"  # Inverter
curl "http://192.168.10.113:8484/getdevdata.cgi?device=3&sn=UR015K6052540222"  # Smartmeter
curl "http://192.168.10.113:8484/getdevdata.cgi?device=4&sn=UR015K6052540222"  # Battery
```

## Critical Implementation Details

### 1. Dongle API Parsing (⚠️ Must Be Adapted)

The JSON keys in `solplanet_collector.py` are **placeholders**. Before first deployment:

1. Test Dongle API endpoints (commands above)
2. Identify real keys for:
   - MPPT data: Likely `vpv1`, `ipv1`, `ppv1` (voltage, current, power) or similar
   - Battery: `soc`, `pb`, `vb`, `ib`, `temp` or similar
   - Grid: `pac`, `fac` or similar
3. Update `parse_live_data()` method in `solplanet_collector.py`

Search for `# ⚠️ PLACEHOLDER` or `# ⚠️ TODO` comments in the file.

### 2. MPPT East/West Mapping

The inverter has 3 MPPT inputs. Configuration in `.env` maps them to East/West:

```bash
# Example: MPPT1 = East (14 modules), MPPT2+3 = West (21 modules)
MPPT_EAST=1
MPPT_WEST=2,3
```

**Validation method:**
- Morning (8-10am): East MPPT should dominate
- Afternoon (2-4pm): West MPPTs should dominate

If values appear swapped, exchange the mapping in `.env` and restart backend.

### 3. Pushover Configuration

iOS push notifications require:
```bash
PUSHOVER_APP_TOKEN=<from pushover.net>
PUSHOVER_USER_KEY=<from pushover.net>
```

Backend checks `settings.pushover_enabled` property. If false, notifications are skipped with warning.

### 4. Database Schema

**`live_data` table** (main data storage):
- Populated every 30 seconds by collector
- Size: ~100 KB/day
- Auto-cleanup: Records older than 90 days (not yet implemented in Phase 1)

**`daily_summary` table** (for future use):
- Not populated in Phase 1
- Reserved for Phase 3 (reports)

## File Modification Guidelines

### When Changing Collector Logic

If modifying `backend/app/services/solplanet_collector.py`:
1. Update `parse_live_data()` for new fields
2. Update `backend/app/models/database.py` (LiveData model) if schema changes
3. Update `backend/app/models/schemas.py` (LiveDataResponse) for API contract
4. Restart backend container to apply changes

### When Changing Frontend UI

Frontend uses Auto-update every 30 seconds:
1. Modify components in `frontend/src/components/`
2. Changes are hot-reloaded in dev mode
3. For production: rebuild frontend container

### When Changing Docker Configuration

After modifying Dockerfiles or docker-compose files:
```bash
# Rebuild specific service
docker-compose up -d --build backend

# Or rebuild all
docker-compose down
docker-compose up -d --build
```

## System Specifics

### PV System Configuration
- **Modules:** Trina Solar Vertex S+ TSM-NEG9RC.27 (445W each)
- **Total:** 35 modules = 15.575 kWp
- **East:** 14 modules = 6.23 kWp (~40%), Azimuth -90°
- **West:** 21 modules = 9.345 kWp (~60%), Azimuth 90°
- **Inverter:** Solplanet ASW015K-TH (3 MPPT inputs)
- **Battery:** Ai-HB G2 (7 modules)

### Dongle Configuration
- **Local IP:** 192.168.10.113:8484
- **Serial Number:** UR015K6052540222
- **No authentication required** (local network only)
- **Device IDs:** 2 (Inverter), 3 (Smartmeter), 4 (Battery)

### Network Architecture
- All components run in local network (192.168.10.x)
- **No ports exposed to internet** (security requirement)
- Raspberry Pi and Dongle must be on same network
- Frontend accessible via Pi's IP address on port 80

## Troubleshooting

### Backend won't start
1. Check `.env` exists: `cp .env.example .env`
2. Check Pushover credentials in `.env`
3. View logs: `docker-compose logs backend`

### No data in dashboard
1. Check Dongle reachable: `curl http://192.168.10.113:8484/getdevdata.cgi?device=2&sn=UR015K6052540222`
2. Check backend health: `curl http://localhost/api/health`
3. Inspect database: `docker exec -it solarpilot-app sqlite3 /app/data/solarpilot.db "SELECT COUNT(*) FROM live_data;"`
4. Most likely: JSON parsing failed → check collector logs for errors

### East/West values seem swapped
1. Edit `.env`: swap `MPPT_EAST` and `MPPT_WEST` values
2. Restart: `docker-compose restart backend`
3. Verify in dashboard after 30 seconds

### House consumption shows negative values
Energy balance formula error - check sign conventions in `parse_live_data()`:
- Ensure Battery: + = charging, - = discharging
- Ensure Grid: + = import, - = export
- May need to invert signs from Dongle API

## Phase 2 Preview (Not Implemented)

Future phases will add:
- **Phase 2:** Dual-Forecast (Open-Meteo + Google Solar API)
- **Phase 3:** Device recommendations (washing machine, dryer timing)
- **Phase 4:** Automation and learning

Do not implement forecast features unless explicitly requested.

## Version Information

- **Current Version:** 1.0.0 (Phase 1 - Foundation)
- **Backend:** Python 3.13 (Docker), FastAPI 0.115.0
- **Frontend:** Node 22 (Docker), React 18.3.1, Vite 5.4.11
- **Database:** SQLite (aiosqlite 0.20.0, SQLAlchemy 2.0.36)
