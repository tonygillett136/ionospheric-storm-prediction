# Changelog

All notable changes to the Ionospheric Storm Prediction System.

## [Unreleased]

## [2.1.0] - 2025-11-06

### Added - Storm Gallery Feature
- **Historical Storm Gallery** with 6 curated major geomagnetic storms (2015-2025)
  - Grid view with interactive storm cards
  - Detailed storm view with real measurement data
  - Time series charts (Kp Index, TEC, Solar Wind Speed)
  - Real-world impact stories
  - Links to NOAA official reports
  - Severity badges (G1-G5 color-coded)
  - Notable event indicators
- Featured storms include:
  - St. Patrick's Day Storm 2015 (G4-Severe)
  - September 2017 Storm Series (G4-Severe)
  - **Mother's Day Storm 2024 (G5-Extreme)** - First G5 since 2003
- New backend endpoints:
  - `GET /api/v1/storms/gallery` - Get all storm events
  - `GET /api/v1/storms/{storm_id}` - Get detailed measurements
- New frontend components:
  - `StormGallery.jsx` (434 lines)
  - `StormGallery.css` (476 lines)
- Storm metadata database: `backend/storm_events.py`
- Documentation: `STORM_GALLERY.md`

### Added - Climatology Explorer Feature
- **Climatology Explorer** for educational TEC pattern exploration
  - Three interactive views:
    - Time Series: Visualize climatology over adjustable date ranges (30 days to 2 years)
    - Kp Comparison: Compare TEC patterns across geomagnetic activity levels (Kp 0-9)
    - Seasonal Patterns: Understand seasonal TEC variations with envelope charts
  - Extended forecasting up to 2 years into the future
  - Multiple Kp scenarios (quiet, moderate, storm, current, specific)
  - Hourly or daily resolution options
  - Statistical summaries and analysis
  - Educational content explaining climatology
- New backend endpoints:
  - `GET /api/v1/climatology/explore` - Generate climatology time series
  - `GET /api/v1/climatology/heatmap` - Complete climatology table (365×10 bins)
- New frontend components:
  - `ClimatologyExplorer.jsx` (623 lines)
  - `ClimatologyExplorer.css` (584 lines)
- Documentation: `CLIMATOLOGY_EXPLORER.md`

### Fixed
- **Climatology Explorer**: Fixed seasonal patterns chart to show meaningful data
  - Changed from flat mean-only line to full range visualization (min, mean, max)
  - Added educational explanation of equinoctial effect
  - Created envelope chart showing seasonal variability
- **Backend**: Added missing `numpy` import in `routes.py`
  - Fixed 500 error in climatology endpoints

### Documentation
- Created `STORM_GALLERY.md` - Comprehensive storm gallery documentation
- Created `CLIMATOLOGY_EXPLORER.md` - Climatology feature documentation
- Created `SESSION_CONTINUITY.md` - Session continuity guide for development
- Created `docs/LOCAL_DEPLOYMENT.md` - Local development deployment guide
- Updated `README.md` - Added new features to feature list

### Changed
- Updated main navigation to include 7 tabs (was 5):
  - Added "📚 Climatology Explorer" tab
  - Added "⚡ Storm Gallery" tab
- Extended API service with 4 new methods:
  - `exploreClimatology()`
  - `getClimatologyHeatmap()`
  - `getStormGallery()`
  - `getStormDetails()`

## [2.0.0] - 2025-11-02

### Added - Ensemble Model (Default)
- **Ensemble Storm Predictor** combining climatology (70%) and V2.1 model (30%)
  - Improved baseline performance: 16.18 TECU RMSE
  - Configurable weighting via API parameters
  - Separate forecasts exposed (climatology, V2.1, ensemble)
- Climatology table with 9,493 bins (365 days × 10 Kp levels)
  - Built from 2015-2022 historical data
  - Captures seasonal and geomagnetic patterns
- New `/prediction/ensemble` endpoint with custom weighting
- **Ensemble Model tab** in UI for comparison view
- Documentation: `ENSEMBLE_MODEL.md`

### Changed
- **Default prediction** now uses ensemble method (was V2.1 only)
- Updated UI subtitle to reflect "Powered by Ensemble Model"
- Modified `/prediction` endpoint to return ensemble by default
  - Use `?use_ensemble=false` for V2.1-only predictions

## [1.5.0] - 2025-11-01

### Added - Advanced Features
- **Regional Prediction Service**
  - Location-specific forecasts with latitude/longitude parameters
  - Magnetic latitude adjustments
  - High-latitude amplification factors
- **Impact Assessment Service**
  - GPS accuracy degradation estimates
  - HF radio propagation predictions
  - Satellite operation risk levels
  - Power grid GIC risk assessment
- **Alert System** (backend only)
  - Create/manage custom storm alerts
  - Threshold-based notifications
  - Alert history tracking
  - API endpoints for alert management

### Added - Analysis Tools
- **Backtesting Workshop UI**
  - Historical model validation
  - Threshold optimization
  - Storm event detection
  - Performance metrics visualization
- **Impact Dashboard**
  - Real-world impact translations
  - Sector-specific risk assessments
- **Regional Forecast Tab**
  - Interactive location selection
  - Regional prediction display

## [1.4.0] - 2025-10-31

### Added - Model V2.1 Enhancements
- **Enhanced BiLSTM-Attention architecture**
  - Multi-head attention mechanism
  - 3.88M parameters (8x larger than V1)
  - Residual connections
  - Advanced regularization
- **24 physics-informed features**:
  - Magnetic latitude (AACGM-v2)
  - Rate-of-change detection
  - Solar cycle phase
  - Temporal encoding (daytime, season, high-latitude)
- **Multi-task learning** with 4 output heads
- Performance: 9.87 TECU RMSE on validation
- Documentation: `MODEL_V2.1_ENHANCEMENTS.md`, `V2.1_VALIDATION_REPORT.md`

## [1.3.0] - 2025-10-25

### Added - Real Data Integration
- **NASA OMNI Database** integration
  - 10 years of measurements (2015-2025)
  - 87,600+ hourly records
  - Authoritative data sources (GFZ, Kyoto WDC, NASA)
- **Historical Trends Component**
  - View data over multiple time ranges (24h to 10 years)
  - Interactive charts
- **Real storm events** in database
- SQLite database with Alembic migrations
- Data fetching script: `fetch_real_historical_data.py`
- Documentation: `REAL_DATA_STATUS.md`, `backend/DATABASE.md`

## [1.2.0] - 2025-10-20

### Added - Enhanced UI
- **3D Globe Visualization**
  - Photo-realistic Earth texture
  - Real-time TEC distribution overlay
  - Interactive camera controls
  - Day/night terminator
- **Multi-tab Navigation**
  - Dashboard (main view)
  - Backtest Workshop
  - Impact Assessment
  - Regional Forecast
- **Current Conditions Dashboard**
- **Glossary Component** with 25+ terms
- **Expandable Information Panels**

## [1.1.0] - 2025-10-15

### Added - Core Prediction Features
- **Storm Gauge** visualization
- **Dual Horizon Forecast** (24h and 48h)
- **Timeline Charts** for hourly probabilities
- **Risk Level Classification** (Low/Moderate/Elevated/High/Severe)
- **Confidence Estimates**
- **Parameter Cards** for space weather indices

### Changed
- Improved prediction visualization
- Enhanced user experience with tooltips
- Better error handling

## [1.0.0] - 2025-10-10

### Added - Initial Release
- **FastAPI Backend**
  - REST API with async support
  - WebSocket for real-time updates
  - Health monitoring
- **React Frontend**
  - Vite build system
  - Responsive design
  - Dark theme with gradient backgrounds
- **ML Model V1** (CNN-LSTM)
  - Storm probability prediction
  - TEC forecasting
- **Data Collection**
  - NOAA SWPC integration
  - Live Kp index, solar wind, IMF Bz, F10.7 flux
  - Automatic data updates
- **Database**
  - SQLite storage
  - Historical data management
- **Documentation**
  - README, QUICKSTART, SETUP
  - API documentation
  - Technical overview

## Version Numbering

Format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes, major feature additions
- **MINOR**: New features, significant enhancements
- **PATCH**: Bug fixes, minor improvements

## Links

- **Repository**: https://github.com/tonygillett136/ionospheric-storm-prediction
- **Documentation**: See `/docs` folder and root `.md` files
- **Issues**: https://github.com/tonygillett136/ionospheric-storm-prediction/issues

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details
