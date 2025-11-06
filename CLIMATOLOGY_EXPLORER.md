# Climatology Explorer Feature

## Overview

The **Climatology Explorer** is a new feature that allows users to explore and understand ionospheric Total Electron Content (TEC) climatology patterns. Unlike predictions that focus on specific storm events, climatology represents long-term average conditions based on historical data from 2015-2022.

This feature is designed to be educational, helping users understand:
- What climatology is and how it differs from predictions
- Seasonal patterns in ionospheric TEC
- How geomagnetic activity (Kp index) affects TEC values
- Why climatology forms the foundation of our ensemble prediction system

## Features

### 1. Time Series View
- **Purpose**: Visualize climatology data over any date range up to 2 years into the future
- **Key Features**:
  - Adjustable time ranges (30 days to 2 years)
  - Multiple Kp scenarios (quiet, moderate, storm, or current conditions)
  - Hourly or daily resolution
  - Statistical summaries (mean, range, standard deviation)
  - Interactive area chart with tooltips

### 2. Kp Comparison View
- **Purpose**: Compare how TEC varies across different geomagnetic activity levels
- **Key Features**:
  - Multi-line chart showing TEC patterns for different Kp levels throughout the year
  - Interactive Kp level selection (0-9)
  - Color-coded Kp indicators
  - Statistical table showing mean, std dev, and range for each Kp level

### 3. Seasonal Patterns View
- **Purpose**: Understand how TEC varies by season
- **Key Features**:
  - Seasonal breakdown (Winter, Spring, Summer, Autumn)
  - Statistical analysis by season
  - Visual comparison of seasonal variations

## Educational Value

The Climatology Explorer includes extensive educational content:

- **What is Climatology**: Explains the difference between "climate" and "weather" in the context of ionospheric prediction
- **Seasonal Patterns**: Describes how TEC varies naturally throughout the year
- **Geomagnetic Effects**: Shows how Kp index correlates with TEC patterns
- **Role in Predictions**: Explains how climatology forms 70% of the ensemble prediction system

## Technical Implementation

### Backend API Endpoints

#### 1. GET `/api/v1/climatology/explore`

Generates climatology data for any date range, including future dates.

**Parameters**:
- `start_date` (optional): ISO format start date (default: today)
- `end_date` (optional): ISO format end date (default: start_date + days)
- `days` (optional): Number of days to project (default: 365, max: 730)
- `kp_scenario` (optional): Geomagnetic activity scenario
  - `current` - Use current Kp index (default)
  - `quiet` - Use Kp=2
  - `moderate` - Use Kp=5
  - `storm` - Use Kp=7
  - `specific` - Use custom kp_value
- `kp_value` (optional): Specific Kp value when kp_scenario='specific' (0-9)
- `hourly_resolution` (optional): If true, return hourly data points (default: false)

**Response**:
```json
{
  "metadata": {
    "start_date": "2025-11-06T00:00:00",
    "end_date": "2026-11-06T00:00:00",
    "duration_days": 365,
    "kp_scenario": "moderate",
    "kp_value": 5.0,
    "hourly_resolution": false,
    "data_points": 365,
    "description": "Climatological TEC forecast based on 2015-2022 historical patterns"
  },
  "statistics": {
    "mean": 15.23,
    "std": 2.45,
    "min": 10.12,
    "max": 22.67,
    "median": 15.01
  },
  "data": [
    {
      "timestamp": "2025-11-06T12:00:00",
      "tec_mean": 15.23,
      "day_of_year": 310,
      "kp_index": 5.0
    },
    ...
  ]
}
```

#### 2. GET `/api/v1/climatology/heatmap`

Returns the complete climatology table formatted as a heatmap (day-of-year × Kp index).

**Parameters**: None

**Response**:
```json
{
  "metadata": {
    "total_bins": 3650,
    "days": 365,
    "kp_levels": 10,
    "data_source": "Historical measurements 2015-2022",
    "description": "Complete climatology table showing TEC patterns by day-of-year and Kp index"
  },
  "heatmap": [
    {
      "day_of_year": 1,
      "date_example": "2025-01-01T00:00:00",
      "kp_values": {
        "kp_0": 14.5,
        "kp_1": 14.8,
        "kp_2": 15.1,
        ...
        "kp_9": 18.9
      }
    },
    ...
  ],
  "statistics": {
    "by_kp_level": {
      "kp_0": {
        "mean": 14.52,
        "std": 2.31,
        "min": 10.0,
        "max": 20.1
      },
      ...
    },
    "by_season": {
      "winter": {
        "mean": 13.45,
        "std": 2.12,
        "min": 9.8,
        "max": 19.2
      },
      ...
    }
  }
}
```

### Frontend Implementation

#### New Components

1. **ClimatologyExplorer.jsx** (`frontend/src/components/ClimatologyExplorer.jsx`)
   - Main component for the climatology exploration feature
   - Manages state for view selection, controls, and data loading
   - Renders three different views (time series, Kp comparison, seasonal)
   - Includes educational content and explanations

2. **ClimatologyExplorer.css** (`frontend/src/styles/ClimatologyExplorer.css`)
   - Comprehensive styling for all climatology explorer views
   - Responsive design for mobile and desktop
   - Color-coded Kp indicators
   - Gradient backgrounds for educational sections

#### API Service Updates

Added two new methods to `api.js`:

```javascript
async exploreClimatology(params = {}) {
  const response = await this.axiosInstance.get('/climatology/explore', { params });
  return response.data;
}

async getClimatologyHeatmap() {
  const response = await this.axiosInstance.get('/climatology/heatmap');
  return response.data;
}
```

#### Navigation Integration

Added new tab to `App.jsx`:
- Tab label: "📚 Climatology Explorer"
- View state: `activeView === 'climatology'`
- Renders `<ClimatologyExplorer />` component

## Data Science Background

### Climatology Table Structure

The climatology table is a lookup dictionary with:
- **Keys**: `(day_of_year, kp_bin)` tuples
- **Values**: Average TEC in TECU (Total Electron Content Units)
- **Bins**: 365 days × 10 Kp levels = 3,650 total bins
- **Training Data**: Historical measurements from 2015-2022 (8 years)

### Why Climatology Works

Validation testing showed that climatology provides:
- **Strong baseline performance**: 16.18 TECU RMSE
- **Reliable seasonal patterns**: Captures regular variations throughout the year
- **Stable predictions**: Less susceptible to model overfitting
- **Complementary to neural networks**: Provides foundation while neural networks capture storm dynamics

### Ensemble Integration

The system uses climatology as 70% of the ensemble prediction:
```
Ensemble Prediction = 0.7 × Climatology + 0.3 × V2.1 Neural Network
```

This weighting was determined through validation testing and represents the optimal balance between:
- **Climatology**: Captures regular patterns reliably
- **Neural Network**: Captures storm dynamics and non-linear effects

## Use Cases

### 1. Educational Understanding
- Learn what "typical" ionospheric conditions look like
- Understand seasonal variations in TEC
- See how geomagnetic storms affect the ionosphere

### 2. Planning and Analysis
- Project expected TEC values for future dates
- Compare expected conditions under different Kp scenarios
- Analyze long-term patterns for research

### 3. Baseline Comparison
- Compare current conditions against climatological normals
- Identify when conditions deviate from typical patterns
- Understand the context of predictions

## Future Enhancements

Potential improvements for future versions:

1. **Regional Climatology**: Different climatology patterns by latitude/longitude
2. **Anomaly Detection**: Highlight when current conditions deviate significantly from climatology
3. **Export Functionality**: Allow users to download climatology data as CSV/JSON
4. **Custom Date Ranges**: More flexible date range selection with calendar picker
5. **Comparison Mode**: Overlay actual TEC data on climatology to show deviations
6. **Solar Cycle Effects**: Account for 11-year solar cycle in climatology patterns

## Performance Considerations

- **Backend**: Climatology table is pre-computed at startup (no runtime computation)
- **API Response Times**: Typically < 100ms for explore endpoint, < 500ms for heatmap
- **Frontend**: Recharts library handles visualization efficiently
- **Data Transfer**: Hourly resolution for periods > 90 days may result in larger payloads
- **Caching**: Browser caches API responses for 5 minutes to reduce server load

## Testing

To test the climatology explorer feature:

1. **Start the backend**:
   ```bash
   cd backend
   python -m app.main
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Navigate to the Climatology Explorer tab**

4. **Test different scenarios**:
   - Change time ranges
   - Try different Kp scenarios
   - Switch between views
   - Check statistics and charts

## API Examples

### Example 1: Get 30 days of climatology for quiet conditions

```bash
curl "http://localhost:8000/api/v1/climatology/explore?days=30&kp_scenario=quiet"
```

### Example 2: Get 1 year with hourly resolution for storm conditions

```bash
curl "http://localhost:8000/api/v1/climatology/explore?days=365&kp_scenario=storm&hourly_resolution=true"
```

### Example 3: Get complete heatmap data

```bash
curl "http://localhost:8000/api/v1/climatology/heatmap"
```

## Files Modified/Created

### Backend Files
- **Modified**: `backend/app/api/routes.py` - Added two new endpoints
- **No changes to**: `backend/app/models/ensemble_predictor.py` (used existing climatology functionality)

### Frontend Files
- **Created**: `frontend/src/components/ClimatologyExplorer.jsx`
- **Created**: `frontend/src/styles/ClimatologyExplorer.css`
- **Modified**: `frontend/src/App.jsx` - Added new tab and view
- **Modified**: `frontend/src/services/api.js` - Added two new API methods

### Documentation Files
- **Created**: `CLIMATOLOGY_EXPLORER.md` (this file)

## Troubleshooting

### Issue: "Climatology data not loading"
**Solution**: Ensure the backend server is running and the database contains historical measurements from 2015-2022.

### Issue: "Charts not rendering"
**Solution**: Check browser console for errors. Ensure recharts dependency is installed (`npm install recharts`).

### Issue: "API returns 500 error"
**Solution**: Check backend logs. Ensure numpy is installed and climatology table is properly loaded.

### Issue: "Heatmap takes long to load"
**Solution**: This is expected on first load as it processes 3,650 bins. Consider implementing caching on the backend.

## References

- **Ensemble Model Documentation**: `ENSEMBLE_MODEL.md`
- **API Reference**: `API_REFERENCE.md`
- **Main README**: `README.md`

## Credits

Developed as part of the Ionospheric Storm Prediction System. The climatology approach is based on standard meteorological and space weather forecasting techniques, adapted for Total Electron Content (TEC) prediction.
