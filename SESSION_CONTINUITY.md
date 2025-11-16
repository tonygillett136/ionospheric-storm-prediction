# Session Continuity Guide

**Last Updated:** November 16, 2025
**Purpose:** Help anyone (including AI assistants) pick up where we left off

## Current System State

### 🚀 What's Running

**Local Development Environment:**
- **Backend**: Running on http://localhost:8000 (Uvicorn/FastAPI)
  - Process: Background process (ID: d19648 or similar)
  - Auto-reload: ✅ Enabled (watches for file changes)
  - Status: http://localhost:8000/api/v1/health

- **Frontend**: Running on http://localhost:5173 (Vite dev server)
  - Auto-reload: ✅ Enabled (Hot Module Replacement)
  - Process: PID 58854 (check with `ps aux | grep vite`)

- **Database**: SQLite at `backend/data/ionospheric.db`
  - Size: ~1GB
  - Records: 87,600+ historical measurements (2015-2025)
  - No separate process needed

### 📁 Repository State

- **Branch**: `main`
- **Remote**: https://github.com/tonygillett136/ionospheric-storm-prediction.git
- **Latest Commit**: `e73dabf` - "Update regional predictions UI to reflect ensemble ML model"
- **Status**: All changes committed and pushed ✅

### 🆕 Recently Added Features (November 16, 2025 Session)

#### 1. Regional ML Integration (Completed ✅)
**Commits:**
- `1541c4b` - Add storm enhancement factors
- `041b4f9` - Make regional risk assessment Kp-aware
- `658c34e` - Integrate ML ensemble forecast into regional predictions
- `ae07c08` - Fix speedometer needle overlapping
- `1fd0cd2` - Implement sticky condensing header
- `e73dabf` - Update regional predictions UI

**Files Modified:**
- `backend/app/api/routes.py` - Added `_infer_kp_from_storm_probability()`, integrated ML into regional endpoint
- `backend/app/services/regional_ensemble_service.py` - Added `_apply_storm_enhancement()`, Kp-aware risk assessment
- `frontend/src/components/StormGauge.jsx` - Fixed label positioning
- `frontend/src/components/DualHorizonForecast.jsx` - Fixed label positioning
- `frontend/src/App.jsx` - Implemented sticky condensing header
- `frontend/src/components/RegionalPredictions.jsx` - Updated validation note

**Features:**
- **Regional forecasts now use ensemble ML model** (same as main dashboard)
- **Storm enhancement system** with geographic response factors:
  - Auroral zones: 1.65x during storms
  - Mid-latitude: 1.35x during storms
  - Equatorial: 1.15x during storms
- **Kp-aware risk assessment** with regional sensitivity
- **Forecasted Kp inference** from ML storm probability
- **UI improvements**: Fixed speedometer overlaps, sticky condensing header

## Quick Commands

### Restart Services

**Backend:**
```bash
# Kill existing
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Start new
cd backend
source venv/bin/activate
python main.py
```

**Frontend:**
```bash
# Usually already running, but if needed:
cd frontend
npm run dev
```

### Check Status

```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Frontend (should return HTML)
curl http://localhost:5173

# Check processes
ps aux | grep "python main.py"
ps aux | grep vite
```

### Test New Features

```bash
# Test climatology endpoint
curl "http://localhost:8000/api/v1/climatology/explore?days=7&kp_scenario=moderate"

# Test storm gallery
curl http://localhost:8000/api/v1/storms/gallery

# Test specific storm
curl http://localhost:8000/api/v1/storms/mothers_day_storm_2024
```

### Git Operations

```bash
# Check current state
git status
git log --oneline -5

# Pull latest (if working from different machine)
git pull origin main

# Create new feature branch (recommended for new work)
git checkout -b feature/your-feature-name
```

## Application Structure

### Current Tabs/Views

1. **📊 Dashboard** - Main prediction view with 3D globe
2. **🔬 Backtest Workshop** - Historical model validation
3. **🎯 Impact Assessment** - Real-world impact analysis
4. **📍 Regional Forecast** - Location-specific predictions
5. **🔮 Ensemble Model** - Climatology + V2.1 comparison
6. **📚 Climatology Explorer** - ⭐ NEW (added today)
7. **⚡ Storm Gallery** - ⭐ NEW (added today)

### API Endpoints

**Core:**
- `GET /api/v1/health` - Health check
- `GET /api/v1/prediction` - Storm prediction (ensemble by default)
- `GET /api/v1/current` - Current conditions

**Climatology (NEW):**
- `GET /api/v1/climatology/explore` - Time series data
- `GET /api/v1/climatology/heatmap` - Complete climatology table

**Storm Gallery (NEW):**
- `GET /api/v1/storms/gallery` - All storms
- `GET /api/v1/storms/{storm_id}` - Storm details with measurements

**Other:**
- `GET /api/v1/trends/{hours}` - Historical trends
- `GET /api/v1/backtest/run` - Run backtest
- `GET /api/v1/impact-assessment` - Impact analysis
- `GET /api/v1/prediction/location` - Regional prediction

See `API_REFERENCE.md` for complete list.

## Where We Left Off

### Completed November 16, 2025 ✅
1. ✅ Regional ML Integration - Regional predictions now use ensemble model
2. ✅ Storm Enhancement System - Geographic response factors implemented
3. ✅ Kp-Aware Risk Assessment - Regional sensitivity to geomagnetic activity
4. ✅ UI Fixes - Speedometer needle overlap fixed
5. ✅ Sticky Condensing Header - Smooth scroll transitions
6. ✅ Documentation Updates - README, CHANGELOG, SESSION_CONTINUITY updated
7. ✅ Git - All commits pushed to main (6 commits)

### Outstanding Items ⚠️
1. ❌ **Production deployment** - Still local only
2. ❌ **TECHNICAL_OVERVIEW.md** - Outdated, doesn't reflect ensemble model or recent changes

### Recommended Next Steps

**Immediate (High Priority):**
1. Test regional predictions thoroughly to verify ML integration
2. Verify storm enhancements are working during active geomagnetic conditions
3. Create production build: `cd frontend && npm run build`

**Soon (Medium Priority):**
4. Update TECHNICAL_OVERVIEW.md to reflect ensemble model and recent changes
5. Add more storms to storm_events.py database
6. Implement one of the "Quick Win" features:
   - Location presets for Regional Forecast (2-3 hours)
   - CSV export for climatology data (1-2 hours)
   - "Share this prediction" button (1-2 hours)
   - Current solar cycle phase indicator (2-3 hours)

**Future (Low Priority):**
7. Set up actual production deployment (cloud hosting)
8. Configure CI/CD pipeline
9. Add more comprehensive testing
10. Implement alert system UI (backend exists, no frontend)

## Known Issues

### Minor Issues
- **None currently identified** - Both new features working correctly

### Warnings (Non-blocking)
- Pydantic warnings about `model_version` field namespace conflicts
  - Location: `BacktestRequest` and `OptimizeThresholdRequest` models
  - Impact: None (just warnings)
  - Fix: Add `model_config['protected_namespaces'] = ()` to models

## Development Environment

### Python Version
- **Version**: 3.13
- **Location**: `/opt/homebrew/Cellar/python@3.13/3.13.2/`
- **Virtual env**: `backend/venv/`

### Node Version
- **Version**: v22.17.1
- **Location**: `/Users/tonygillett/.nvm/versions/node/v22.17.1/`

### Key Dependencies
**Backend:**
- FastAPI
- TensorFlow 2.20+
- SQLAlchemy
- NumPy, Pandas
- Uvicorn (ASGI server)

**Frontend:**
- React 18.3
- Vite
- Recharts (for charts)
- Three.js (for 3D globe)
- Axios (API calls)

## File Locations

### Important Config Files
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies
- `backend/.env` - Backend environment variables (if exists)
- `frontend/.env` - Frontend environment variables (if exists)

### Model Files
- `backend/models/v2/best_model.keras` - V2.1 neural network model
- Note: Model loading uses attention layers, may show warnings

### Database
- `backend/data/ionospheric.db` - SQLite database
- **Backup recommended** before major changes

### Documentation
- Root: Feature docs (CLIMATOLOGY_EXPLORER.md, STORM_GALLERY.md, etc.)
- `docs/`: Deployment and API docs
- `backend/`: Model and performance docs

## Accessing the Application

**Frontend:** http://localhost:5173
**Backend API:** http://localhost:8000
**API Docs (Swagger):** http://localhost:8000/docs
**Health Check:** http://localhost:8000/api/v1/health

## Common Scenarios

### Scenario: Starting Fresh After Reboot

```bash
# 1. Navigate to project
cd /Users/tonygillett/code/ionospheric_prediction

# 2. Start backend
cd backend
source venv/bin/activate
python main.py &
cd ..

# 3. Start frontend (if not already running)
cd frontend
npm run dev
```

### Scenario: Making Changes to Backend

1. Edit files in `backend/app/`
2. Save - Uvicorn will auto-reload (watch terminal)
3. Test endpoint with curl or browser
4. If satisfied, commit changes

### Scenario: Making Changes to Frontend

1. Edit files in `frontend/src/`
2. Save - Vite will hot-reload automatically
3. Check browser (should update instantly)
4. If satisfied, commit changes

### Scenario: Adding a New Storm to Gallery

1. Edit `backend/storm_events.py`
2. Add new entry to `MAJOR_STORM_EVENTS` list
3. Follow existing format
4. Save (backend will auto-reload)
5. Test: `curl http://localhost:8000/api/v1/storms/gallery`
6. Check frontend - new storm should appear

### Scenario: Database Issues

```bash
# Check database exists
ls -lh backend/data/ionospheric.db

# Check record count
sqlite3 backend/data/ionospheric.db "SELECT COUNT(*) FROM historical_measurements;"

# If corrupted, re-fetch (takes 5-10 minutes)
cd backend
python fetch_real_historical_data.py
```

## Troubleshooting Quick Reference

| Issue | Check | Fix |
|-------|-------|-----|
| Backend won't start | Port 8000 in use | `lsof -ti:8000 \| xargs kill -9` |
| Frontend won't start | Port 5173 in use | `lsof -ti:5173 \| xargs kill -9` |
| API returns 500 error | Backend logs | Check terminal where `python main.py` runs |
| Charts not rendering | Browser console | F12, check for JS errors |
| Import errors | Virtual env active? | `source backend/venv/bin/activate` |
| Database missing | File doesn't exist | Run `fetch_real_historical_data.py` |
| Git conflicts | Stale local changes | `git status`, `git stash` or commit |

## Useful Git Commands

```bash
# See what changed recently
git log --oneline --graph --all -10

# See today's commits
git log --since="today" --oneline

# Undo uncommitted changes to file
git checkout -- <file>

# See what's different from remote
git fetch origin
git log HEAD..origin/main --oneline

# Create feature branch for new work
git checkout -b feature/my-feature
```

## Production Deployment (Future)

**Current Status:** Local development only

**Options for Production:**
1. **Docker** - See `docs/DEPLOYMENT.md`
2. **Cloud Platforms:**
   - Railway
   - Render
   - Heroku
   - AWS/GCP/Azure
3. **VPS:**
   - DigitalOcean
   - Linode
   - Vultr

**Requirements:**
- SSL certificate (Let's Encrypt recommended)
- Domain name
- Environment variables configuration
- Database persistence strategy
- Static file serving (for frontend build)

See `docs/DEPLOYMENT.md` for detailed instructions.

## Contact & Resources

**GitHub Repo:** https://github.com/tonygillett136/ionospheric-storm-prediction
**Local Path:** `/Users/tonygillett/code/ionospheric_prediction`
**Owner:** Tony Gillett

**External Resources:**
- NOAA SWPC: https://www.swpc.noaa.gov/
- NASA OMNI Database: https://omniweb.gsfc.nasa.gov/
- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/

## Notes for AI Assistants

**Context Preservation:**
- This document contains the current state as of last session
- Check git log for any commits since this document was last updated
- Run `git status` to see uncommitted changes
- Check process list to see what's actually running

**Typical Workflow:**
1. User requests feature
2. Design API endpoints (backend)
3. Implement backend (`backend/app/api/routes.py` typically)
4. Add API methods to `frontend/src/services/api.js`
5. Create React component in `frontend/src/components/`
6. Create CSS in `frontend/src/styles/`
7. Integrate into `App.jsx`
8. Test locally
9. Document (create .md file in root)
10. Commit and push

**Documentation Standards:**
- Create separate .md file for major features
- Update this SESSION_CONTINUITY.md at end of session
- Update README.md for user-facing changes
- Add to CHANGELOG.md (when created)
- Include code examples and API references

**Code Style:**
- Backend: Python with type hints
- Frontend: React functional components with hooks
- Comments: Explain "why", not "what"
- Commit messages: Descriptive with emoji (🤖 Generated with Claude Code)

## Version History

- **2025-11-06**: Initial creation after adding Climatology Explorer and Storm Gallery
- **2025-11-06**: Added Storm Gallery documentation
- **2025-11-16**: Updated with Regional ML Integration session (6 commits):
  - Regional predictions now use ensemble ML model
  - Storm enhancement system implemented
  - Kp-aware risk assessment added
  - UI fixes (speedometer overlaps, sticky header)
  - Documentation updates (README, CHANGELOG, SESSION_CONTINUITY)

---

*This document should be updated at the end of each significant development session.*
