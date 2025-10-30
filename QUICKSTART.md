# Quick Start Guide

Get the Ionospheric Storm Prediction System running in under 10 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python --version

# Check Node.js version (need 18+)
node --version

# Check npm
npm --version
```

If any are missing, install them first.

## 5-Minute Setup

### 1. Install Backend Dependencies (2 minutes)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 2. Install Frontend Dependencies (2 minutes)

```bash
cd frontend
npm install
cd ..
```

### 3. Configure Environment (30 seconds)

```bash
cp .env.example .env
```

That's it! No configuration changes needed for local development.

## Running the System

### Option 1: Two Terminal Windows

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

Wait for: `System fully operational!`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Wait for: `Local: http://localhost:5173/`

### Option 2: macOS/Linux One-Liner

```bash
# In one terminal, run both (requires tmux or use separate terminals)
cd backend && source venv/bin/activate && python main.py &
cd frontend && npm run dev
```

## Access the Application

Open your browser to:
```
http://localhost:5173
```

You should see:
- ✅ A rotating 3D Earth with TEC visualization
- ✅ A storm probability gauge
- ✅ Real-time parameter cards
- ✅ A 24-hour forecast timeline
- ✅ "Live" status indicator (green dot)

## First Steps

1. **Explore the Globe**: Click and drag to rotate, scroll to zoom
2. **Check the Gauge**: See the current 24h storm probability
3. **View Parameters**: Monitor Kp index, solar wind, and other metrics
4. **Study Timeline**: See hour-by-hour forecasts for the next 24 hours
5. **Watch Updates**: The system updates automatically every 5 minutes

## API Access

While the app is running, you can also access:

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **Current Prediction**: http://localhost:8000/api/v1/prediction

## Troubleshooting

### Port Already in Use

**Backend (port 8000):**
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Frontend (port 5173):**
```bash
# macOS/Linux
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Module Not Found

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### npm Install Errors

```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### No Data Showing

1. Check backend terminal for errors
2. Verify backend is running: http://localhost:8000/api/v1/health
3. Check browser console (F12) for errors
4. Wait 5 minutes for initial data collection

## What's Happening Behind the Scenes?

When you start the system:

1. **Backend starts** and initializes the ML model
2. **Data collectors connect** to NOAA SWPC APIs
3. **Initial data collection** fetches space weather parameters
4. **First prediction** is generated using the CNN-LSTM model
5. **WebSocket server** opens for real-time updates
6. **Frontend connects** via WebSocket for live data
7. **Automatic updates** begin every 5 minutes (data) and 1 hour (predictions)

## Next Steps

- 📖 Read [SETUP.md](SETUP.md) for detailed installation instructions
- 🔧 See [TECHNICAL_OVERVIEW.md](TECHNICAL_OVERVIEW.md) for architecture details
- 📡 Check [API_REFERENCE.md](API_REFERENCE.md) for API documentation
- 🚀 Explore the code in `backend/` and `frontend/` directories

## Stopping the System

1. Press `Ctrl+C` in the frontend terminal
2. Press `Ctrl+C` in the backend terminal
3. Type `deactivate` in the backend terminal to exit the virtual environment

## Getting Help

If something isn't working:
1. Check the terminal logs for error messages
2. Review the troubleshooting section above
3. See [SETUP.md](SETUP.md) for detailed help
4. Check the browser console (F12 → Console tab)

## System Requirements

**Minimum:**
- Python 3.9+
- Node.js 18+
- 4 GB RAM
- 2 GB free disk space
- Internet connection

**Works on:**
- ✅ macOS (Intel/Apple Silicon)
- ✅ Linux (Ubuntu, Debian, Fedora, etc.)
- ✅ Windows 10/11

---

**Enjoy exploring ionospheric storms!** 🌍⚡
