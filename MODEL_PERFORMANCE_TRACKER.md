# Model Performance Tracker

## Overview

The **Model Performance Tracker** is a feature that catalogs recent geomagnetic storms (up to 1 year back) and evaluates how well the prediction model performed on each storm. This provides transparency into model accuracy and helps users understand real-world prediction performance.

## Purpose

- **Accountability**: Show actual model performance on real recent storms
- **Transparency**: Demonstrate prediction accuracy with concrete examples
- **Analysis**: Identify patterns in model strengths and weaknesses
- **Trust Building**: Help users understand when to trust predictions

## Features

### Storm Detection and Cataloging

**Automatic Detection:**
- Scans historical data for storm events based on Kp index threshold (default: Kp ≥ 5.0)
- Groups consecutive storm hours into storm events
- Filters out NASA OMNI fill values for data quality
- Detects storms from last 30 days up to 1 year back

**Storm Metadata:**
- Start time, end time, peak time
- Duration in hours
- Peak Kp index reached
- Average Kp during storm
- Maximum and average TEC values
- Severity classification (G1-G5 NOAA scale)

### Model Performance Analysis

**For Each Storm:**
- **Detection**: Did the model predict this storm?
- **Lead Time**: How many hours in advance was it detected?
- **Accuracy Metrics**:
  - RMSE (Root Mean Square Error) during storm period
  - MAE (Mean Absolute Error) during storm period
  - Detection Rate: % of storm duration correctly predicted
- **Prediction Time Series**: Predicted vs actual values over time

### Interactive UI

**Main View:**
- Table of recent storms with key metrics
- Sortable and filterable storm list
- Severity badges (color-coded G1-G5)
- Summary statistics (total storms, average duration, strongest storm)
- Severity distribution chart

**Storm Details (Expandable):**
- Full storm timeline (start, peak, end times)
- TEC response during storm
- Model performance metrics with visual indicators
- Success/failure indicators for detection

**Controls:**
- Time period selector (30/90/180/365 days)
- Performance analysis toggle (on-demand for faster loading)
- Refresh button

## Technical Implementation

### Backend

**Service:** `backend/app/services/recent_storm_performance_service.py`

Key classes and methods:
```python
class RecentStormPerformanceService:
    async def detect_storms()  # Detect storm events from historical data
    async def analyze_storm_performance()  # Run model retrospectively
    async def get_recent_storm_catalog()  # Get full catalog
```

**API Endpoints:** `backend/app/api/routes.py`

1. **`GET /api/v1/storms/recent`**
   - Query parameters:
     - `days_back`: How many days to look back (default: 365, max: 365)
     - `kp_threshold`: Kp threshold for detection (default: 5.0)
     - `analyze_performance`: Run performance analysis (default: false)
     - `model_version`: Model to use ('v1' or 'v2', default: 'v2')
   - Returns: Storm catalog with metadata and optional performance metrics

2. **`GET /api/v1/storms/recent/{storm_id}/performance`**
   - Path parameters:
     - `storm_id`: Storm identifier (format: storm_YYYYMMDD_HHMM)
   - Query parameters:
     - `model_version`: Model version ('v1' or 'v2', default: 'v2')
   - Returns: Detailed performance analysis for specific storm

### Frontend

**Component:** `frontend/src/components/RecentStormPerformance.jsx`

Features:
- React hooks for state management
- Expandable storm rows for details
- Lazy loading of performance data
- Loading states and error handling
- Responsive design

**Styling:** `frontend/src/styles/RecentStormPerformance.css`
- Modern dark theme
- Color-coded severity indicators
- Animated loading states
- Mobile-responsive layout

**API Integration:** `frontend/src/services/api.js`
```javascript
async getRecentStorms(params)  // Get storm catalog
async getStormPerformance(stormId, modelVersion)  // Get specific storm performance
```

## Storm Detection Algorithm

**Detection Criteria:**
1. Kp index ≥ threshold (default 5.0 for G1 minor storms)
2. Consecutive hours of elevated Kp grouped into single event
3. Minimum duration: 3 hours (configurable)
4. Fill values filtered out (Kp > 9.0 excluded)

**Severity Classification (NOAA G-Scale):**
- **G1 (Minor)**: Kp 5
- **G2 (Moderate)**: Kp 6
- **G3 (Strong)**: Kp 7
- **G4 (Severe)**: Kp 8
- **G5 (Extreme)**: Kp 9

## Model Performance Evaluation

### How It Works

1. **Retrospective Prediction**:
   - For each detected storm, run the model with data available 24 hours before storm onset
   - Generate predictions every 3 hours during storm period
   - Compare predictions to actual measurements

2. **Metrics Calculated**:
   - **Binary Detection**: Did model predict storm would occur? (yes/no)
   - **Detection Lead Time**: Hours between first detection and storm onset
   - **RMSE**: Prediction error magnitude during storm
   - **MAE**: Average absolute prediction error
   - **Detection Rate**: Percentage of storm duration model correctly predicted

3. **Analysis Period**:
   - Predictions start 24 hours before storm
   - Continue through storm duration
   - Include 6-hour recovery period after storm

### Performance Interpretation

**Good Performance:**
- Storm detected: ✓ Yes
- Lead time: 12-24 hours
- RMSE: < 15%
- Detection rate: > 70%

**Poor Performance:**
- Storm detected: ✗ No (missed)
- Lead time: < 6 hours or none
- RMSE: > 30%
- Detection rate: < 40%

## Use Cases

### 1. Model Validation
Verify the model performs well on recent data, not just historical test sets.

### 2. Confidence Building
Show users concrete examples of successful predictions.

### 3. Failure Analysis
Identify types of storms the model struggles with (e.g., sudden onset, specific Kp ranges).

### 4. Comparison
Compare V1 vs V2 model performance on same recent storms.

### 5. Research
Study patterns in model performance across different storm characteristics.

## API Examples

### Get Recent Storms (Last 90 Days, No Performance Analysis)
```bash
curl "http://localhost:8000/api/v1/storms/recent?days_back=90&analyze_performance=false"
```

Response:
```json
{
  "period": {
    "start_date": "2025-08-09T...",
    "end_date": "2025-11-07T...",
    "days": 90
  },
  "storm_count": 36,
  "severity_distribution": {
    "G5": 23,
    "G2": 4,
    "G1": 3
  },
  "statistics": {
    "total_storm_hours": 1377,
    "avg_storm_duration_hours": 38.2
  },
  "storms": [...]
}
```

### Get Storms with Performance Analysis
```bash
curl "http://localhost:8000/api/v1/storms/recent?days_back=30&analyze_performance=true&model_version=v2"
```

Note: Performance analysis is slower as it runs the model retrospectively on each storm.

### Get Specific Storm Performance
```bash
curl "http://localhost:8000/api/v1/storms/recent/storm_20250914_1800/performance?model_version=v2"
```

Response:
```json
{
  "storm_id": "storm_20250914_1800",
  "storm_info": {
    "start_time": "2025-09-14T18:00:00",
    "peak_kp": 8.5,
    "duration_hours": 20,
    "severity": "G4 - Severe"
  },
  "model_performance": {
    "storm_detected": true,
    "detection_lead_hours": 18.5,
    "storm_rmse": 12.4,
    "storm_mae": 9.8,
    "detection_rate": 85.0
  }
}
```

## Frontend Usage

1. **Navigate** to "📊 Model Performance" tab
2. **Select** time period (30/90/180/365 days)
3. **Toggle** "Analyze model performance" for detailed metrics (slower)
4. **Click "Refresh"** to load storm catalog
5. **View** summary statistics and severity distribution
6. **Click** on any storm row to expand details
7. **Review** model performance metrics for each storm

## Performance Considerations

**Without Performance Analysis:**
- Fast (< 1 second)
- Shows storm catalog only
- Good for browsing recent activity

**With Performance Analysis:**
- Slower (10-60 seconds depending on storm count)
- Runs model retrospectively on each storm
- Calculates detailed accuracy metrics
- Recommended for detailed analysis of specific periods

**Optimization Tips:**
- Start with `analyze_performance=false` to browse storms
- Enable performance analysis only when needed
- Use shorter time periods for faster results
- Cache results on frontend to avoid re-analysis

## Files

**Backend:**
- `backend/app/services/recent_storm_performance_service.py` (334 lines)
- `backend/app/api/routes.py` (+148 lines for endpoints)

**Frontend:**
- `frontend/src/components/RecentStormPerformance.jsx` (365 lines)
- `frontend/src/styles/RecentStormPerformance.css` (338 lines)
- `frontend/src/services/api.js` (+21 lines for API methods)
- `frontend/src/App.jsx` (+18 lines for integration)

**Total:** ~1,224 lines of new code

## Future Enhancements

**Potential improvements:**

1. **Advanced Filtering**:
   - Filter by severity level (show only G3+ storms)
   - Filter by detection success/failure
   - Date range picker

2. **Visualizations**:
   - Time series charts showing predicted vs actual
   - Performance trend over time
   - Comparison charts for different model versions

3. **Export**:
   - Download storm catalog as CSV
   - Export performance metrics for analysis
   - Generate performance reports

4. **Alerts**:
   - Notify when model performance degrades
   - Flag storms with poor predictions

5. **Model Comparison**:
   - Side-by-side V1 vs V2 performance
   - Ensemble vs individual models

6. **Statistical Analysis**:
   - Correlation between storm characteristics and prediction accuracy
   - Performance by season, solar cycle phase

## Troubleshooting

### Issue: No storms detected
**Cause**: No Kp ≥ 5 events in selected period, or data missing
**Solution**: Try longer time period or lower Kp threshold

### Issue: Performance analysis timing out
**Cause**: Too many storms to analyze
**Solution**: Reduce time period or analyze storms individually

### Issue: High RMSE values
**Cause**: Model predictions significantly different from actual
**Solution**: This indicates model struggled with these storms - normal behavior to document

### Issue: Storm ID not found
**Cause**: Storm ID format incorrect or storm not in database
**Solution**: Verify storm ID format (storm_YYYYMMDD_HHMM)

## Related Documentation

- `ENSEMBLE_MODEL.md` - Model architecture and design
- `V2.1_VALIDATION_REPORT.md` - Validation methodology
- `BACKTESTING.md` - General backtesting capabilities
- `API_REFERENCE.md` - Complete API documentation

## Credits

Model Performance Tracker feature implemented November 2025.
Builds on existing backtesting infrastructure and historical data from NASA OMNI database (2015-2025).
