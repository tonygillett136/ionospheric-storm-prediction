# Setup Guide - Ionospheric Storm Prediction System

This guide will help you set up and run the Ionospheric Storm Prediction System on your local machine.

## Prerequisites

- **Python 3.9+** (recommended: Python 3.11)
- **Node.js 18+** and npm
- **Git** (optional, for version control)
- At least 4GB of available RAM
- Internet connection for data collection

## Installation Steps

### 1. Backend Setup

#### Create Python Virtual Environment

```bash
cd backend
python -m venv venv
```

#### Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

#### Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastAPI for the web server
- TensorFlow for ML models
- NumPy, Pandas, SciPy for data processing
- aiohttp for async HTTP requests
- And other required packages

#### Configure Environment Variables

```bash
cd ..
cp .env.example .env
```

Edit `.env` if you want to customize settings (optional).

### 2. Frontend Setup

#### Install Node Dependencies

```bash
cd frontend
npm install
```

This will install:
- React for the UI framework
- Three.js and react-three-fiber for 3D visualization
- D3.js for data visualization
- Recharts for charting
- Axios for API communication

### 3. Directory Structure Verification

Your project should look like this:

```
ionospheric_prediction/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── data_collectors/
│   │   │   ├── noaa_swpc_collector.py
│   │   │   └── tec_collector.py
│   │   ├── models/
│   │   │   └── storm_predictor.py
│   │   └── services/
│   │       └── data_service.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Globe3D.jsx
│   │   │   ├── StormGauge.jsx
│   │   │   ├── ParameterCard.jsx
│   │   │   └── TimelineChart.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── ml_models/
    ├── training/
    ├── saved_models/
    └── data/
```

## Running the Application

### Option 1: Run Both Backend and Frontend Together

You'll need two terminal windows/tabs.

#### Terminal 1 - Start Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting Ionospheric Storm Prediction System...
INFO:     Collecting initial data...
INFO:     System fully operational!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Terminal 2 - Start Frontend

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v6.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Option 2: Access the Application

1. Open your web browser
2. Navigate to: **http://localhost:5173**
3. You should see the Ionospheric Storm Prediction System dashboard

The backend API will be available at: **http://localhost:8000**

## Verifying Installation

### Check Backend Health

Open http://localhost:8000/api/v1/health in your browser or use curl:

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "last_data_update": "2025-10-23T...",
  "last_prediction_update": "2025-10-23T...",
  "historical_points": 1
}
```

### Check Frontend Connection

In the browser, you should see:
- A 3D rotating globe with TEC data visualization
- A storm probability gauge
- Real-time parameter cards (Kp index, Solar Wind, etc.)
- A 24-hour forecast timeline
- A "Live" status indicator in the header

## Troubleshooting

### Backend Issues

**Problem: Module not found errors**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows
# Reinstall dependencies
pip install -r requirements.txt
```

**Problem: Port 8000 already in use**
```bash
# Find and kill the process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Problem: TensorFlow installation issues**
```bash
# Try installing TensorFlow separately
pip install tensorflow==2.18.0 --no-cache-dir
```

### Frontend Issues

**Problem: npm install fails**
```bash
# Clear npm cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Problem: Port 5173 already in use**

Edit `frontend/vite.config.js` and change the port:
```javascript
server: {
  port: 3000,  // Change to any available port
  ...
}
```

**Problem: WebSocket connection fails**

Check that:
1. Backend is running on port 8000
2. No firewall is blocking the connection
3. CORS settings in backend allow your frontend origin

### Data Collection Issues

**Problem: No data appearing**

The system uses empirical models to generate synthetic TEC data for demonstration. If you see empty charts:
1. Check the browser console for errors
2. Verify the backend is running and accessible
3. Check the backend logs for collection errors

## System Requirements

### Minimum:
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Storage: 2 GB free space
- Internet: Broadband connection

### Recommended:
- CPU: Quad-core 2.5 GHz+
- RAM: 8 GB+
- Storage: 5 GB free space (for ML model training)
- Internet: Stable broadband connection

## Next Steps

Once the system is running:

1. **Explore the Dashboard**: Interact with the 3D globe, view real-time parameters
2. **Monitor Predictions**: Watch the 24-hour storm probability forecasts
3. **Configure Settings**: Modify `.env` to customize update intervals
4. **Train Models**: See ML_TRAINING.md for model training instructions
5. **API Documentation**: Visit http://localhost:8000/docs for interactive API docs

## Additional Resources

- API Documentation: http://localhost:8000/docs
- System Architecture: See README.md
- Model Training: See ML_TRAINING.md (to be created)
- Contributing: See CONTRIBUTING.md (to be created)

## Getting Help

If you encounter issues:
1. Check the logs in both terminal windows
2. Review this setup guide
3. Check the browser console for frontend errors
4. Verify all dependencies are installed correctly

## Stopping the Application

To stop the application:

1. **Frontend**: Press `Ctrl+C` in the terminal running `npm run dev`
2. **Backend**: Press `Ctrl+C` in the terminal running `python main.py`
3. **Deactivate venv**: Type `deactivate` in the backend terminal
