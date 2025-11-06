# Local Development Deployment Guide

This document explains how to deploy and test changes locally, which is what we're currently doing with the Ionospheric Storm Prediction System.

## Overview

The application consists of two services:
- **Backend**: Python FastAPI server on port 8000
- **Frontend**: React/Vite dev server on port 5173

## Quick Start (Restart Services)

### Backend

```bash
# Kill any process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Navigate to backend and start server
cd backend
source venv/bin/activate
python main.py
```

The backend will:
- Start on http://0.0.0.0:8000
- Auto-reload when code changes (Uvicorn watch mode)
- Load the ML model and climatology data
- Begin collecting real-time space weather data

### Frontend

The frontend dev server is typically already running. Check with:

```bash
# Check if running
ps aux | grep "node.*vite" | grep -v grep

# If needed, start it
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

## Typical Development Workflow

### 1. Make Code Changes

Edit your files as needed. Example:
- Backend: `backend/app/api/routes.py`
- Frontend: `frontend/src/components/YourComponent.jsx`

### 2. Test Changes

**Backend**: Uvicorn will auto-reload when it detects changes
**Frontend**: Vite will hot-reload automatically

### 3. Verify API Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Test new climatology endpoint
curl "http://localhost:8000/api/v1/climatology/explore?days=7&kp_scenario=moderate"
```

### 4. Commit Changes

```bash
git add <files>
git commit -m "Your commit message

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

## Common Issues and Solutions

### Issue: Port 8000 already in use

```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or find the PID manually
lsof -i :8000
kill -9 <PID>
```

### Issue: Frontend not loading

```bash
# Check if Vite is running
ps aux | grep vite

# Restart if needed
cd frontend
npm run dev
```

### Issue: Backend import errors

```bash
# Make sure you're in the virtual environment
cd backend
source venv/bin/activate

# Check python path
which python  # Should show: .../backend/venv/bin/python

# Reinstall dependencies if needed
pip install -r requirements.txt
```

### Issue: Changes not reflected

- **Backend**: Save the file and wait ~1-2 seconds for Uvicorn to reload
- **Frontend**: Vite should hot-reload instantly; check browser console for errors

## Testing New Features

### Example: Testing Climatology Explorer

1. **Start both services** (see Quick Start above)

2. **Test backend API**:
```bash
# Test explore endpoint
curl -s "http://localhost:8000/api/v1/climatology/explore?days=30&kp_scenario=moderate" | python3 -m json.tool | head -50

# Test heatmap endpoint
curl -s "http://localhost:8000/api/v1/climatology/heatmap" | python3 -m json.tool | head -50
```

3. **Test frontend UI**:
- Open http://localhost:5173
- Navigate to "📚 Climatology Explorer" tab
- Test different views: Time Series, Kp Comparison, Seasonal
- Verify charts render correctly
- Check browser console for errors (F12)

4. **Verify data flow**:
- Open Network tab in browser DevTools
- Watch API calls to `/api/v1/climatology/*`
- Verify response data matches expected format

## Environment Configuration

### Backend (.env)

The backend uses environment variables for configuration. No `.env` file is required for local development as sensible defaults are used.

Default values:
- `API_HOST=0.0.0.0`
- `API_PORT=8000`
- `DEBUG=True`
- `CORS_ORIGINS=["http://localhost:5173"]`

### Frontend (.env)

Frontend environment variables are defined in `.env` or `.env.local`:

```bash
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1
```

## Monitoring Running Services

### Check what's running

```bash
# Backend
lsof -i :8000

# Frontend
lsof -i :5173

# All Python processes
ps aux | grep python | grep main.py

# All Node/Vite processes
ps aux | grep vite
```

### View logs

**Backend**: Logs appear in the terminal where you ran `python main.py`

**Frontend**: Logs appear in the terminal where you ran `npm run dev`, plus browser console

## Database

The application uses SQLite for historical data:

- **Location**: `backend/data/ionospheric.db`
- **Size**: ~87,600+ measurements (10 years of NASA OMNI data)
- **No separate service** needed - it's just a file

### Database operations

```bash
# Check if database exists
ls -lh backend/data/ionospheric.db

# View schema (optional)
sqlite3 backend/data/ionospheric.db ".schema"

# Count records (optional)
sqlite3 backend/data/ionospheric.db "SELECT COUNT(*) FROM historical_measurements;"
```

## Complete Restart (Clean State)

If you need to restart everything from scratch:

```bash
# 1. Kill all processes
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# 2. Pull latest code
git pull origin main

# 3. Update backend dependencies (if needed)
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..

# 4. Update frontend dependencies (if needed)
cd frontend
npm install
cd ..

# 5. Start backend
cd backend
source venv/bin/activate
python main.py &
cd ..

# 6. Start frontend
cd frontend
npm run dev
```

## Performance Tips

### Backend Startup Time

First startup takes ~5-10 seconds to:
- Load TensorFlow model (~3-4 seconds)
- Build climatology table (~2-3 seconds)
- Fetch initial space weather data (~2-3 seconds)

Subsequent requests are fast (<100ms) as data is cached in memory.

### Frontend Build

For production build (not needed for local development):

```bash
cd frontend
npm run build
# Output: dist/ folder
```

## When to "Deploy"

In this local setup, "deployment" means:

1. **Code is committed and pushed to GitHub** ✅
2. **Services are running locally** ✅
3. **Changes are accessible at http://localhost:5173** ✅

This is a **development environment**. For a true production deployment, see `docs/DEPLOYMENT.md` for:
- Docker deployment
- Nginx configuration
- SSL certificates
- Cloud hosting options

## Quick Reference

| Service | Port | URL | Auto-reload? |
|---------|------|-----|-------------|
| Backend API | 8000 | http://localhost:8000/api/v1 | Yes (Uvicorn) |
| Frontend Dev | 5173 | http://localhost:5173 | Yes (Vite HMR) |
| WebSocket | 8000 | ws://localhost:8000/api/v1/ws | Yes |
| Database | N/A | SQLite file | N/A |

## Success Indicators

Your local deployment is working when:

- ✅ Backend responds to http://localhost:8000/api/v1/health
- ✅ Frontend loads at http://localhost:5173
- ✅ No errors in backend terminal
- ✅ No errors in frontend terminal
- ✅ Browser console shows WebSocket connection
- ✅ New features (e.g., Climatology Explorer tab) are visible

## What We Did Today

1. **Created new climatology feature**:
   - Backend: 2 new endpoints (`/climatology/explore`, `/climatology/heatmap`)
   - Frontend: New `ClimatologyExplorer` component with 3 views
   - Documentation: `CLIMATOLOGY_EXPLORER.md`

2. **Found and fixed bug**:
   - Missing `numpy` import in `routes.py`
   - Fixed by adding `import numpy as np`

3. **Committed changes**:
   - Main feature commit: `7cb503d`
   - Bug fix commit: `78fd56e`
   - Pushed to GitHub `main` branch

4. **Tested locally**:
   - Backend API endpoints working ✅
   - Frontend tab added and visible ✅
   - Ready for user testing ✅

## Next Steps

**To use the new feature**:
1. Ensure both services are running (see Quick Start)
2. Open http://localhost:5173 in your browser
3. Click on "📚 Climatology Explorer" tab
4. Explore the three views: Time Series, Kp Comparison, Seasonal

**For production deployment** (if needed):
- See `docs/DEPLOYMENT.md` for cloud deployment options
- Consider Docker, Heroku, Railway, or Render
- Will require environment setup and domain configuration

## Support

If you encounter issues:

1. **Check logs**: Look at terminal output for both backend and frontend
2. **Check ports**: Use `lsof -i :8000` and `lsof -i :5173`
3. **Check git**: Ensure you're on latest commit with `git status`
4. **Restart services**: Follow "Complete Restart" section above
5. **Check browser console**: Press F12 and look for JavaScript errors

Remember: This is a **local development** environment. Changes are immediately visible after save (auto-reload), but they're only accessible on your machine until deployed to a production server.
