# Getting Started

Welcome to the Ionospheric Storm Prediction System! This guide will help you get the application running quickly.

## Quick Start (5 minutes)

### Prerequisites
- **Python 3.13+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)

### Step 1: Clone Repository
```bash
git clone <your-repo-url>
cd ionospheric_prediction
```

### Step 2: Start Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: Seed 10 years of historical data (takes ~30 seconds)
python seed_historical_data.py

# Start the server
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
System fully operational!
```

### Step 3: Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

You should see:
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Step 4: Open Application
Navigate to **http://localhost:5173** in your browser

## What You'll See

### Main Dashboard
1. **3D Globe** - Real-time TEC visualization on Earth
   - Drag to rotate
   - Scroll to zoom
   - Colored points show ionospheric activity

2. **Storm Gauge** - Current 24-hour storm probability
   - Green: Low risk (<20%)
   - Yellow: Moderate (20-40%)
   - Orange: Elevated (40-60%)
   - Red: High risk (>60%)

3. **Current Conditions** - Comprehensive space weather state
   - TEC statistics
   - Geomagnetic indices
   - Solar wind parameters
   - Ionospheric conditions

4. **Live Parameters**
   - Kp Index (geomagnetic activity)
   - Solar Wind Speed
   - IMF Bz (magnetic field)
   - F10.7 Flux (solar activity)

5. **Timeline Charts** - 24-hour forecasts
   - Storm probability trend
   - TEC forecast

6. **Historical Trends** - View past storm activity from real database
   - 24 hours - hourly data
   - Week - last 7 days
   - Month - last 30 days
   - Year - last 365 days
   - 10 Years - complete historical archive (87,600 hours)

7. **Glossary** - Learn technical terms
   - Search functionality
   - Filter by category
   - Expandable definitions

## Features Walkthrough

### Interacting with the Globe
- **Rotate**: Click and drag
- **Zoom**: Scroll wheel or pinch
- **Reset**: Refresh the page

The globe shows:
- Blue dots = Low TEC (0-12 TECU)
- Cyan = Moderate TEC (12-24 TECU)
- Yellow = Elevated TEC (24-36 TECU)
- Orange = High TEC (36-48 TECU)
- Red = Very High TEC (48+ TECU)

### Understanding the Predictions
The system analyzes:
- Total Electron Content (TEC)
- Geomagnetic indices (Kp, Dst)
- Solar wind parameters
- Interplanetary magnetic field (IMF Bz)
- Solar flux (F10.7)
- Time of day and season

To predict:
- Storm probability for next 24 hours
- Hour-by-hour risk levels
- TEC forecast

### Using Historical Trends
1. Click period button (24h/Week/Month/Year)
2. View statistics cards:
   - Average probability
   - Peak probability
   - High risk periods count
   - Moderate risk periods count
3. Hover over charts for detailed values
4. Compare different time periods

### Exploring the Glossary
1. Scroll to Glossary section
2. Use search box to find terms
3. Filter by category (dropdown)
4. Click term to expand definition
5. Click again to collapse

## Understanding the Data

### Live Updates
- **Data refresh**: Every 5 minutes
- **Predictions**: Every hour
- **WebSocket**: Real-time when active

### Color Coding
**Risk Levels:**
- 🟢 Low: <20% - Normal operations
- 🟡 Moderate: 20-40% - Minor effects possible
- 🟠 Elevated: 40-60% - Noticeable impacts
- 🔴 High: 60-80% - Significant disruptions
- 🔴 Severe: >80% - Major disruptions

**Storm Impacts:**
- GPS positioning errors (meters to tens of meters)
- HF radio communication disruptions
- Satellite signal degradation
- Increased satellite drag
- Aurora visible at lower latitudes

## Educational Content

### Learn More
The app includes extensive educational content:

1. **Tooltips** - Hover over (?) icons next to parameters
2. **Expandable Panels** - Click to learn about:
   - Ionospheric Storms
   - Prediction Model
   - Applications & Use Cases
3. **Glossary** - 25+ technical terms explained

### Key Concepts

**TEC (Total Electron Content)**
- Measures electrons in ionosphere
- Higher TEC = more GPS delay
- Varies by location, time, solar activity

**Kp Index**
- Measures geomagnetic activity
- Scale 0-9
- Kp ≥5 indicates geomagnetic storm

**IMF Bz**
- North-south magnetic field component
- Negative (southward) = storm trigger
- Positive (northward) = stable conditions

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'tensorflow'"**
```bash
cd backend
pip install -r requirements.txt
```

**"Port 8000 already in use"**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
# Then restart
python main.py
```

### Frontend Issues

**"Cannot find module" errors**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Black screen or globe not showing**
- Clear browser cache (Ctrl+Shift+R)
- Check browser console for errors (F12)
- Ensure WebGL is enabled
- Try different browser

**No data showing**
- Check backend is running (http://localhost:8000/api/v1/health)
- Check browser console for API errors
- Verify network connection

## Next Steps

### Explore Features
1. Try different time periods in Historical Trends
2. Search glossary terms
3. Expand all educational panels
4. Watch the globe auto-rotate
5. Monitor live updates

### Customize
1. Modify update intervals in `backend/app/core/config.py`
2. Adjust globe settings in `frontend/src/components/Globe3D.jsx`
3. Add new parameters or visualizations

### Learn More
- Read `TECHNICAL_OVERVIEW.md` for architecture details
- See `API_REFERENCE.md` for API documentation
- Check `DEPLOYMENT.md` for production setup

## Support

For issues or questions:
1. Check this guide
2. Review documentation in `/docs`
3. Check browser console (F12)
4. Check backend logs
5. Open GitHub issue

## Development Tips

### Hot Reload
- Frontend auto-reloads on file changes
- Backend requires manual restart

### API Testing
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get prediction
curl http://localhost:8000/api/v1/prediction

# Get TEC data
curl http://localhost:8000/api/v1/tec/current
```

### Browser DevTools
- Press F12 to open
- Console tab for errors
- Network tab for API calls
- Application tab for WebSocket

## Keyboard Shortcuts

**Globe Controls:**
- Mouse drag = Rotate
- Scroll = Zoom in/out
- No keyboard shortcuts currently

**Browser:**
- Ctrl/Cmd + R = Refresh
- Ctrl/Cmd + Shift + R = Hard refresh (clear cache)
- F12 = Developer tools
- Ctrl/Cmd + F = Search page

Happy predicting! 🌍⚡
