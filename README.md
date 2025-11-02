# Ionospheric Storm Prediction System

A sophisticated real-time ionospheric storm prediction application that collects live space weather data and uses deep learning to forecast ionospheric disturbances up to 24 hours in advance.

## Overview

This system provides critical space weather forecasting for applications in:
- **Aviation** - GPS navigation and HF communications
- **Maritime** - Vessel positioning and safety systems
- **Satellite Operations** - Orbit determination and communications
- **Power Grid Management** - GIC warnings and protection
- **Survey & Mapping** - High-precision GNSS positioning
- **Telecommunications** - HF radio propagation forecasting

## Features

### 🌍 Real-Time Data Collection
- **NOAA SWPC** - Kp index, solar wind, magnetic field, F10.7 flux
- **NASA CDDIS** - Global TEC measurements
- Live updates every 5 minutes
- WebSocket streaming for instant updates

### 🤖 Advanced ML Prediction
- **Ensemble Model** - Combines climatology and neural network strengths (default: 70% climatology + 30% V2.1)
- **Enhanced BiLSTM-Attention** architecture with multi-head attention (V2.1)
- **24 physics-informed features** including:
  - Magnetic latitude coordinates (AACGM-v2)
  - Rate-of-change detection (Kp, Dst, TEC trends)
  - Solar cycle phase
  - Temporal encoding (daytime, season, high-latitude zones)
  - Traditional space weather indices
- **3.88M parameters** for state-of-the-art accuracy (8x larger than V1)
- **Multi-task learning** with 4 output heads:
  - Storm binary prediction (24h ahead)
  - Hourly storm probabilities (24 hours)
  - TEC forecasting (24 hours)
  - Uncertainty estimation
- **Risk classification** (Low/Moderate/Elevated/High/Severe)
- **Rigorous validation** - Climatology provides strong baseline (16.18 TECU RMSE)
- **Model versioning** - V1 (CNN-LSTM), V2.1 (BiLSTM-Attention), Ensemble (Climatology + V2.1)

### 📊 Interactive Visualizations
- **3D Globe** - Real-time TEC distribution on photo-realistic Earth
- **Storm Gauge** - Current storm probability with risk indicators
- **Timeline Charts** - 24-hour probability and TEC forecasts
- **Historical Trends** - View patterns over 24h/week/month/year/10 years
- **Live Parameters** - Kp index, solar wind, IMF Bz, F10.7 flux

### 💾 Real Observational Data
- **NASA OMNI Database** - 10 years of real measurements (2015-2025, 87,600+ hours)
- **Real Storm Events** - Actual geomagnetic storms including major events
- **SQLite Storage** - Professional database with Alembic migrations
- **Fast Queries** - Indexed retrieval across any time range
- **Authoritative Sources** - GFZ Potsdam (Kp), Kyoto WDC (Dst), NASA spacecraft

### 📚 Educational Content
- Comprehensive current conditions dashboard
- Detailed glossary of 25+ technical terms
- Expandable information panels
- Contextual tooltips throughout the interface

## Quick Start

### Backend
\`\`\`bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Recommended: Download 10 years of real NASA OMNI data (~5-10 minutes)
python fetch_real_historical_data.py

# Alternative: Use synthetic test data (for development only)
# python seed_historical_data.py

python main.py
\`\`\`

### Frontend
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

Open http://localhost:5173

## Technology Stack

**Backend:** Python 3.13, FastAPI, TensorFlow 2.20+, NumPy, Pandas, SQLAlchemy
**Frontend:** React 18.3, Vite, Three.js, Recharts
**ML:** BiLSTM-Attention neural network (V2) with multi-head attention, residual connections
**Database:** SQLite with Alembic migrations

## Documentation

See full documentation in `/docs` folder

## License

MIT
