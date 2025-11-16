# Project State Document

**Generated:** November 16, 2025
**Purpose:** Comprehensive snapshot of current system architecture, features, and technical details
**For:** Future development sessions and onboarding

---

## Executive Summary

The Ionospheric Storm Prediction System is a real-time ML-powered forecasting application that predicts geomagnetic storms up to 48 hours in advance. The system uses an ensemble model (70% climatology + 30% neural network) and provides both global and regional TEC predictions with storm-aware risk assessment.

**Current Version:** 2.1.0+
**Status:** Fully functional, local development
**Key Achievement:** Regional predictions now use ensemble ML model with storm enhancements

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React + Vite)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ 3D Globe │  │  Gauges  │  │  Charts  │  │  Tables  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                          │                                   │
│                   REST API + WebSocket                       │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│              Backend (FastAPI + Python)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │        Ensemble Storm Predictor (Default)              │ │
│  │    70% Climatology + 30% V2.1 BiLSTM-Attention         │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Regional │  │   Data   │  │  NOAA    │  │ WebSocket│   │
│  │ Ensemble │  │ Service  │  │Collector │  │ Manager  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                    Data Layer                                │
│  ┌───────────────────┐  ┌──────────────────────────────┐   │
│  │  SQLite Database  │  │   External Data Sources      │   │
│  │  (87,600+ hours)  │  │   - NOAA SWPC                │   │
│  │  2015-2025 data   │  │   - NASA OMNI                │   │
│  └───────────────────┘  └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.13
- FastAPI (async web framework)
- TensorFlow 2.20+ (ML model inference)
- SQLAlchemy (database ORM)
- Uvicorn (ASGI server)
- NumPy, Pandas (data processing)

**Frontend:**
- React 18.3
- Vite (build tool)
- Three.js + react-three-fiber (3D globe)
- Recharts (time-series charts)
- Axios (API client)

**Database:**
- SQLite with Alembic migrations
- 1GB+ database with real NASA OMNI data
- Indexed for fast time-range queries

---

## Core Features

### 1. Ensemble Storm Prediction (Default)

**File:** `backend/app/models/ensemble_predictor.py`

**Configuration:**
- 70% Climatology baseline
- 30% V2.1 BiLSTM-Attention neural network
- Configurable via API parameters

**Outputs:**
- 24h and 48h storm probabilities
- Hourly storm probabilities (24 hours)
- TEC forecasts (24 hours)
- Risk level classification (Low/Moderate/Elevated/High/Severe)
- Confidence estimates

**API Endpoint:** `GET /api/v1/prediction` (default uses ensemble)

### 2. Regional Predictions (ML-Enhanced)

**Files:**
- `backend/app/services/regional_ensemble_service.py`
- `backend/app/api/routes.py` (regional endpoint)

**Key Innovation (Nov 16, 2025):** Regional predictions now use the same ensemble ML model as the main dashboard

**Features:**
- **5 Geographic Regions:** Equatorial, Mid-Latitude, Auroral, Polar, Global
- **ML Integration:** Calls ensemble predictor first, infers forecasted Kp
- **Storm Enhancement System:**
  - Auroral zones: 1.65x enhancement during storms
  - Mid-latitude: 1.35x enhancement
  - Equatorial: 1.15x enhancement
- **Kp-Aware Risk Assessment:**
  - Regional sensitivity factors (Auroral: 2.0x, Mid-lat: 1.5x, Equatorial: 1.0x)
  - Storm severity boost based on G-scale (G1-G5)

**Key Functions:**
- `_infer_kp_from_storm_probability()` - Maps ML storm probability to forecasted Kp
- `_apply_storm_enhancement()` - Applies geographic storm response factors
- `assess_risk()` - Kp-aware risk assessment with regional sensitivity

**API Endpoint:** `GET /api/v1/prediction/regional`

### 3. Real Historical Data

**Source:** NASA OMNI Database (2015-2025)

**Data Points:**
- 87,600+ hourly measurements
- Kp index (GFZ Potsdam)
- Dst index (Kyoto WDC)
- Solar wind parameters (NASA spacecraft)
- F10.7 solar flux
- TEC measurements

**Storage:** SQLite database (`backend/data/ionospheric.db`)

**Fetch Script:** `backend/fetch_real_historical_data.py`

### 4. Educational Features

#### Climatology Explorer
**Files:** `frontend/src/components/ClimatologyExplorer.jsx`

**Features:**
- Time series visualization (30 days to 2 years)
- Kp comparison across activity levels
- Seasonal pattern analysis
- Extended forecasting

#### Storm Gallery
**Files:** `frontend/src/components/StormGallery.jsx`, `backend/storm_events.py`

**Content:**
- 6 major storms (2015-2025)
- Mother's Day 2024 G5-Extreme storm
- Real measurement data and impact stories

### 5. Interactive Visualizations

**3D Globe:** Photo-realistic Earth with live TEC overlay (Three.js)

**Storm Gauges:** Speedometer-style probability displays (24h, 48h)

**Timeline Charts:** Hourly forecasts with risk levels (Recharts)

**Historical Trends:** View data over multiple time ranges

### 6. UI Enhancements (Nov 16, 2025)

**Sticky Condensing Header:**
- Position becomes fixed when scrolling past 50px
- Title shrinks from 32px → 22px
- Subtitle fades out
- Navigation buttons condense
- Smooth 0.3s transitions
- Backdrop blur effect

**Fixed Speedometer Overlaps:**
- Percentage labels moved down 15px in both StormGauge and DualHorizonForecast components

---

## ML Model Architecture

### Ensemble Predictor

**Default Weights:**
- Climatology: 70%
- V2.1 Model: 30%

**Performance:**
- Expected RMSE: ~14-15 TECU
- Improvement over climatology: ~3-5%

### Climatology Component

**Table Structure:**
- 365 days × 10 Kp levels = 3,650 bins
- Trained on 2015-2022 data
- Captures seasonal and geomagnetic patterns

### V2.1 BiLSTM-Attention Model

**Architecture:**
- 3.88M parameters (8x larger than V1)
- Multi-head attention mechanism
- Residual connections
- 24 physics-informed features

**Features:**
- Magnetic latitude (AACGM-v2)
- Rate-of-change detection
- Solar cycle phase
- Temporal encoding

**Multi-Task Outputs:**
- Storm binary prediction
- Hourly storm probabilities (24 hours)
- TEC forecasting (24 hours)
- Uncertainty estimation

**Performance:**
- Validation RMSE: 9.87 TECU
- Issue: Under-confident (narrow prediction range)
- Reason for ensemble: Combines with climatology for reliability

---

## API Endpoints

### Core Prediction

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/prediction` | GET | Main prediction (ensemble default) |
| `/api/v1/prediction/ensemble` | GET | Custom ensemble weighting |
| `/api/v1/prediction/regional` | GET | Regional forecasts (ML-enhanced) |
| `/api/v1/current` | GET | Current conditions |
| `/api/v1/health` | GET | Health check |

### Analysis Tools

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/backtest/run` | GET | Run historical validation |
| `/api/v1/impact-assessment` | GET | Real-world impact analysis |
| `/api/v1/trends/{hours}` | GET | Historical trends |

### Educational

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/climatology/explore` | GET | Time series data |
| `/api/v1/climatology/heatmap` | GET | Complete climatology table |
| `/api/v1/storms/gallery` | GET | All storm events |
| `/api/v1/storms/{storm_id}` | GET | Detailed storm measurements |

### WebSocket

| Endpoint | Protocol | Purpose |
|----------|----------|---------|
| `/api/v1/ws` | WebSocket | Real-time updates |

**Message Types:**
- `initial_data` - Full state on connection
- `data_update` - New measurements
- `prediction_update` - New forecast
- `periodic_update` - Summary metrics
- `heartbeat` - Keep-alive

---

## Frontend Navigation

### Main Tabs (7 Total)

1. **📊 Dashboard** - Main prediction view with 3D globe
2. **🔬 Backtest Workshop** - Historical model validation
3. **🎯 Impact Assessment** - Real-world impact analysis
4. **📍 Regional Forecast** - Location-specific predictions (ML-enhanced)
5. **🔮 Ensemble Model** - Climatology + V2.1 comparison
6. **📚 Climatology Explorer** - Educational TEC exploration
7. **⚡ Storm Gallery** - Historical major storms

---

## Key Files Reference

### Backend Core

```
backend/
├── app/
│   ├── api/
│   │   └── routes.py              # All API endpoints, regional ML integration
│   ├── models/
│   │   ├── ensemble_predictor.py  # Ensemble storm predictor
│   │   └── storm_predictor.py     # V2.1 neural network wrapper
│   ├── services/
│   │   ├── data_service.py        # Data collection orchestrator
│   │   ├── regional_ensemble_service.py  # Regional predictions with ML + storm enhancements
│   │   └── noaa_collector.py      # NOAA SWPC data collection
│   └── database/
│       ├── models.py              # SQLAlchemy models
│       └── session.py             # Database session management
├── models/v2/
│   └── best_model.keras           # V2.1 BiLSTM-Attention model
├── data/
│   └── ionospheric.db             # SQLite database (1GB+)
├── storm_events.py                # Storm gallery metadata
├── fetch_real_historical_data.py  # NASA OMNI data fetcher
└── main.py                        # Application entry point
```

### Frontend Core

```
frontend/
├── src/
│   ├── components/
│   │   ├── App.jsx                      # Main app with sticky header
│   │   ├── StormGauge.jsx               # 24h probability gauge (fixed overlap)
│   │   ├── DualHorizonForecast.jsx      # 24h+48h gauges (fixed overlap)
│   │   ├── RegionalPredictions.jsx      # Regional forecasts UI
│   │   ├── EarthGlobe.jsx               # 3D Earth visualization
│   │   ├── ClimatologyExplorer.jsx      # Educational climatology
│   │   ├── StormGallery.jsx             # Historical storms
│   │   └── ...
│   ├── services/
│   │   └── api.js                       # API client methods
│   └── styles/
│       └── ...
└── package.json
```

### Documentation

```
Root Directory:
├── README.md                           # Main project documentation (updated Nov 16)
├── CHANGELOG.md                        # Version history (updated Nov 16)
├── SESSION_CONTINUITY.md               # Development state tracking (updated Nov 16)
├── PROJECT_STATE.md                    # This file
├── TECHNICAL_OVERVIEW.md               # Technical architecture (OUTDATED)
├── ENSEMBLE_MODEL.md                   # Ensemble model documentation
├── CLIMATOLOGY_EXPLORER.md             # Climatology feature docs
├── STORM_GALLERY.md                    # Storm gallery docs
└── ... (25+ total .md files)
```

---

## Recent Changes (November 16, 2025)

### Commits (6 total)

1. `1541c4b` - Add storm enhancement factors to regional predictions
2. `041b4f9` - Make regional risk assessment Kp-aware during storms
3. `658c34e` - Integrate ML ensemble forecast into regional predictions
4. `ae07c08` - Fix speedometer needle overlapping with percentage label
5. `1fd0cd2` - Implement sticky condensing header with smooth scroll transitions
6. `e73dabf` - Update regional predictions UI to reflect ensemble ML model

### Key Changes Summary

**Backend:**
- Regional predictions now call ensemble predictor first
- Infer forecasted Kp from ML storm probability
- Apply storm enhancements based on geographic response factors
- Kp-aware risk assessment with regional sensitivity

**Frontend:**
- Fixed speedometer needle overlaps in gauges
- Implemented sticky condensing header
- Updated regional predictions validation note

**Documentation:**
- Updated README.md to reflect ML-enhanced regional predictions
- Updated CHANGELOG.md with November 16 session
- Updated SESSION_CONTINUITY.md with latest state

---

## Current System Status

### What's Running

**Backend:** http://localhost:8000
- Process: Background (multiple instances may exist)
- Auto-reload: ✅ Enabled
- Status check: `curl http://localhost:8000/api/v1/health`

**Frontend:** http://localhost:5173
- Vite dev server with hot reload
- Status check: Open in browser

**Database:** `backend/data/ionospheric.db`
- Size: ~1GB
- Records: 87,600+ hours (2015-2025)

### Git Status

- **Branch:** main
- **Remote:** https://github.com/tonygillett136/ionospheric-storm-prediction
- **Latest commit:** e73dabf
- **Status:** All changes committed and pushed ✅

---

## Known Issues & Limitations

### Current Issues

**None identified** - System is stable and fully functional

### Warnings (Non-blocking)

- Pydantic model namespace warnings in backtest models
- Some background bash processes may accumulate (harmless)

### Limitations

1. **Production deployment:** Still local development only
2. **TECHNICAL_OVERVIEW.md:** Outdated, doesn't reflect ensemble model or recent changes
3. **Model under-confidence:** V2.1 model has narrow prediction range (reason for ensemble approach)

---

## Development Workflow

### Making Backend Changes

1. Edit files in `backend/app/`
2. Uvicorn auto-reloads (watch terminal)
3. Test with curl or browser
4. Commit when satisfied

### Making Frontend Changes

1. Edit files in `frontend/src/`
2. Vite hot-reloads automatically
3. Check browser for changes
4. Commit when satisfied

### Git Workflow

```bash
# Check status
git status
git log --oneline -5

# Make changes and commit
git add <files>
git commit -m "Description

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote
git push origin main
```

---

## Testing & Validation

### Quick Tests

```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Main prediction
curl http://localhost:8000/api/v1/prediction

# Regional prediction
curl http://localhost:8000/api/v1/prediction/regional

# Current conditions
curl http://localhost:8000/api/v1/current
```

### Full System Test

1. Open http://localhost:5173
2. Check all 7 tabs render correctly
3. Verify 3D globe rotates smoothly
4. Check storm gauges display probabilities
5. Test regional predictions show data
6. Verify sticky header works on scroll
7. Check speedometer needles don't overlap labels

---

## Future Roadmap

### High Priority
1. Test regional ML integration thoroughly
2. Verify storm enhancements during active conditions
3. Update TECHNICAL_OVERVIEW.md

### Medium Priority
4. Add more storms to gallery
5. Implement location presets for regional forecast
6. CSV export for climatology data
7. "Share this prediction" button

### Low Priority
8. Production deployment (cloud hosting)
9. CI/CD pipeline
10. Comprehensive testing suite
11. Alert system frontend UI

---

## External Resources

**Data Sources:**
- NOAA SWPC: https://www.swpc.noaa.gov/
- NASA OMNI: https://omniweb.gsfc.nasa.gov/

**Documentation:**
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Three.js: https://threejs.org/

**Repository:**
- GitHub: https://github.com/tonygillett136/ionospheric-storm-prediction
- Local: `/Users/tonygillett/code/ionospheric_prediction`

---

## For AI Assistants

### Context Preservation

This document provides:
- Complete system architecture
- All key files and their purposes
- Recent changes and current state
- Known issues and limitations
- Development workflows

**Before starting work:**
1. Read this document for current state
2. Check `git log --oneline -10` for recent commits
3. Run `git status` for uncommitted changes
4. Verify backend/frontend are running

### Typical Development Flow

1. User requests feature/fix
2. Design approach (backend, frontend, or both)
3. Implement backend changes (if needed)
   - Modify `backend/app/api/routes.py` or services
   - Add/update API endpoints
4. Implement frontend changes (if needed)
   - Add API methods to `frontend/src/services/api.js`
   - Create/modify React components
   - Add styling
5. Test locally
6. Update documentation
7. Commit with descriptive message
8. Push to repository
9. Update SESSION_CONTINUITY.md

### Documentation Standards

- Create .md file for major features
- Update README.md for user-facing changes
- Update CHANGELOG.md for all changes
- Update SESSION_CONTINUITY.md at end of session
- Update PROJECT_STATE.md for major architectural changes

---

**Last Updated:** November 16, 2025
**Next Review:** After next major feature or architectural change
