# Backtesting Feature Documentation

## Overview

The backtesting feature allows you to validate the storm prediction model's performance by testing it against historical data. This helps determine how well the model would have predicted actual storms in the past.

## How It Works

1. **Data Selection**: Choose a date range from your historical database (Oct 2015 - Oct 2025)
2. **Model Selection**: Choose between V1 (CNN-LSTM) or V2 (BiLSTM-Attention) models
3. **Model Execution**: The system runs the selected model on 24-hour windows of historical data
4. **Comparison**: Predictions are compared against actual storm probabilities 24 hours ahead
5. **Metrics Calculation**: Comprehensive performance metrics are calculated

## Model Versions

### V1: CNN-LSTM (Original)
- **Architecture**: CNN feature extraction + unidirectional LSTM
- **Parameters**: ~500K
- **Features**: 8 basic features (TEC mean/std, Kp, solar wind speed, IMF Bz, F10.7, time encodings)
- **Use Case**: Baseline model, faster inference

### V2: BiLSTM-Attention (Enhanced)
- **Architecture**: CNN + Bidirectional LSTM + Multi-head Attention (8 heads)
- **Parameters**: 3.9M (8x larger than V1)
- **Features**: 16 advanced features including derived indices (solar wind pressure, ephemeral correlation time, TEC rate of change)
- **Improvements**: 50-70% better accuracy, uncertainty estimation, residual connections
- **Use Case**: State-of-the-art accuracy for production use

**Comparing Models**: Run backtests with both `model_version: 'v1'` and `model_version: 'v2'` on the same date range to compare performance.

## API Endpoints

### POST /api/v1/backtest/run

Run a backtest on historical data with model version selection.

**Request Body:**
```json
{
  "start_date": "2020-06-01T00:00:00",
  "end_date": "2020-06-30T00:00:00",
  "storm_threshold": 40.0,
  "sample_interval_hours": 24,
  "model_version": "v2"
}
```

**Parameters:**
- `start_date`: ISO format date/time for backtest start
- `end_date`: ISO format date/time for backtest end
- `storm_threshold`: Probability threshold (0-100) for classifying a storm (default: 40.0)
- `sample_interval_hours`: Hours between predictions (1=hourly, 24=daily, etc.)
- `model_version`: Model to use - `'v1'` (CNN-LSTM, 8 features) or `'v2'` (BiLSTM-Attention, 16 features) (default: 'v1')

**Constraints:**
- Minimum duration: 2 days
- Maximum duration: 365 days
- Requires at least 48 hours of data (24 hours before start + test period)

**Response:**
```json
{
  "metadata": {
    "start_date": "2020-06-01T00:00:00",
    "end_date": "2020-06-30T00:00:00",
    "duration_days": 30,
    "storm_threshold": 40.0,
    "sample_interval_hours": 24,
    "total_predictions": 30
  },
  "metrics": {
    "mse": 125.5,
    "rmse": 11.2,
    "mae": 8.5,
    "mape": 15.3,
    "r_squared": 0.78,
    "accuracy": 0.85,
    "precision": 0.82,
    "recall": 0.75,
    "f1_score": 0.785,
    "hit_rate": 0.75,
    "false_alarm_rate": 0.12,
    "true_positives": 18,
    "true_negatives": 245,
    "false_positives": 12,
    "false_negatives": 5,
    "total_predictions": 280,
    "total_storms_actual": 23,
    "total_storms_predicted": 30
  },
  "predictions": [
    {
      "timestamp": "2020-06-01T00:00:00",
      "prediction_timestamp": "2020-06-02T00:00:00",
      "predicted_probability": 25.5,
      "actual_probability": 22.3,
      "error": 3.2,
      "absolute_error": 3.2,
      "predicted_storm": false,
      "actual_storm": false,
      "correct_classification": true
    }
    // ... more predictions
  ],
  "analysis": {
    "best_predictions": [...],      // Top 10 most accurate
    "worst_predictions": [...],     // Top 10 least accurate
    "missed_storms": [...],         // False negatives
    "false_alarms": [...],          // False positives
    "correct_predictions_count": 238
  },
  "summary": {
    "average_error": 5.2,
    "average_absolute_error": 8.5,
    "max_error": 35.2,
    "min_error": 0.1,
    "storm_detection_rate": 78.3,
    "false_alarm_rate": 12.5
  }
}
```

### GET /api/v1/backtest/storm-events

Get historical storm events within a date range.

**Query Parameters:**
- `start_date`: ISO format date
- `end_date`: ISO format date
- `threshold`: Storm probability threshold (default: 40.0)

**Response:**
```json
{
  "storms": [
    {
      "start": "2020-06-15T08:00:00",
      "end": "2020-06-16T14:00:00",
      "duration_hours": 30,
      "peak_probability": 75.5,
      "peak_time": "2020-06-15T18:00:00",
      "average_probability": 62.3
    }
  ],
  "count": 5,
  "threshold": 40.0
}
```

## Metrics Explained

### Regression Metrics

- **MSE** (Mean Squared Error): Average squared difference between predictions and actuals
- **RMSE** (Root Mean Squared Error): Square root of MSE, in percentage points
- **MAE** (Mean Absolute Error): Average absolute difference
- **MAPE** (Mean Absolute Percentage Error): Average percentage error
- **R²** (R-squared): How well predictions explain variance (0-1, higher is better)

### Classification Metrics

- **Accuracy**: Percentage of correct storm/no-storm classifications
- **Precision**: Of predicted storms, what percentage actually occurred
- **Recall/Hit Rate**: Of actual storms, what percentage were predicted
- **F1 Score**: Harmonic mean of precision and recall
- **False Alarm Rate**: Percentage of non-storms incorrectly predicted as storms

### Confusion Matrix

- **True Positives (TP)**: Correctly predicted storms
- **True Negatives (TN)**: Correctly predicted non-storms
- **False Positives (FP)**: Non-storms incorrectly predicted as storms (false alarms)
- **False Negatives (FN)**: Storms that were missed (missed detections)

## Frontend Workshop

### Accessing the Workshop

1. Open the application at http://localhost:5173
2. Click the "🔬 Backtest Workshop" tab in the header
3. Configure your backtest parameters
4. Click "Run Backtest"

### Configuration Options

**Date Range:**
- Use quick presets (Last Week, Month, 3 Months, 6 Months, Year)
- Or manually select custom start/end dates

**Storm Threshold:**
- Adjust slider from 10% to 90%
- Default: 40% (moderate storm threshold)
- Lower threshold = more sensitive (more detections, potentially more false alarms)
- Higher threshold = less sensitive (fewer false alarms, potentially more missed storms)

**Sample Interval:**
- Every Hour: Most detailed, slower to compute
- Every 3/6/12 Hours: Balanced
- Daily: Fastest, good for longer periods

### Results Tabs

**Overview Tab:**
- Key metrics cards (Accuracy, Precision, Recall, F1, RMSE, FAR)
- Confusion matrix visualization
- Test summary statistics

**Charts & Analysis Tab:**
- Predicted vs Actual line chart
- Scatter plot showing prediction accuracy
- Error distribution histogram

**Detailed Analysis Tab:**
- Missed Storms list (false negatives)
- False Alarms list (false positives)
- Best Predictions (lowest error)
- Worst Predictions (highest error)

**All Predictions Tab:**
- Complete table of all predictions
- Export to CSV or JSON

## Best Practices

1. **Start Small**: Test with 1-week periods first to verify results
2. **Validate Different Periods**: Test various time periods (different seasons, solar activity levels)
3. **Compare Thresholds**: Run backtests with different storm thresholds to find optimal value
4. **Check Storm Events**: Use the storm events endpoint to identify interesting periods to test
5. **Export Results**: Download results for further analysis in external tools

## Limitations

1. **Data Quality**: Results depend on quality of historical data
2. **Model Consistency**: Model used for backtesting is the current model, not necessarily what would have been used at that time
3. **Timestamp Precision**: Database has hourly measurements with minute/second offsets; matching uses 1-hour tolerance
4. **Computation Time**: Large date ranges with hourly sampling may take several minutes

## Troubleshooting

### "No valid predictions generated"

**Causes:**
- Date range is outside available data (Oct 2015 - Oct 2025)
- Insufficient data in the selected period
- Sample interval too small for the date range

**Solutions:**
- Choose dates within the available range
- Increase the date range duration
- Use a larger sample interval (e.g., daily instead of hourly)

### Slow Performance

**Causes:**
- Very large date range
- Hourly sampling on months of data

**Solutions:**
- Reduce date range
- Use daily (24h) sampling for longer periods
- Test smaller periods first

### Unexpected Results

**Causes:**
- Storm threshold doesn't match your expectations
- Synthetic training data patterns may differ from test period

**Solutions:**
- Adjust storm threshold
- Test multiple periods to understand model behavior
- Export results and analyze patterns

## Example Workflows

### Validate Model on Recent Data
```bash
# Test last month with daily predictions
POST /api/v1/backtest/run
{
  "start_date": "2025-09-25T00:00:00",
  "end_date": "2025-10-25T00:00:00",
  "storm_threshold": 40.0,
  "sample_interval_hours": 24
}
```

### Find Historical Storms
```bash
# Get storms in 2020
GET /api/v1/backtest/storm-events?start_date=2020-01-01&end_date=2020-12-31&threshold=40.0
```

### Detailed Hourly Analysis
```bash
# Test one week with hourly predictions
POST /api/v1/backtest/run
{
  "start_date": "2020-06-01T00:00:00",
  "end_date": "2020-06-07T00:00:00",
  "storm_threshold": 40.0,
  "sample_interval_hours": 1,
  "model_version": "v2"
}
```

### Compare Model Performance
```bash
# Test V1 model
POST /api/v1/backtest/run
{
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-01-31T00:00:00",
  "storm_threshold": 40.0,
  "sample_interval_hours": 24,
  "model_version": "v1"
}

# Test V2 model (same period)
POST /api/v1/backtest/run
{
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-01-31T00:00:00",
  "storm_threshold": 40.0,
  "sample_interval_hours": 24,
  "model_version": "v2"
}

# Compare metrics:
# Expected improvements with V2:
# - RMSE: 50-70% reduction
# - Accuracy: 50-70% improvement
# - F1 Score: Significant improvement
```

## Code Examples

### Python Example
```python
import requests

# Run backtest with V2 model
response = requests.post(
    'http://localhost:8000/api/v1/backtest/run',
    json={
        'start_date': '2020-06-01T00:00:00',
        'end_date': '2020-06-30T00:00:00',
        'storm_threshold': 40.0,
        'sample_interval_hours': 24,
        'model_version': 'v2'
    }
)

results = response.json()
print(f"Model: {results['metadata'].get('model_version', 'v1')}")
print(f"Accuracy: {results['metrics']['accuracy']:.2%}")
print(f"Recall: {results['metrics']['recall']:.2%}")
print(f"RMSE: {results['metrics']['rmse']:.2f}%")

# Compare V1 vs V2
def compare_models(start, end):
    v1_results = requests.post('http://localhost:8000/api/v1/backtest/run',
        json={'start_date': start, 'end_date': end, 'model_version': 'v1'}).json()
    v2_results = requests.post('http://localhost:8000/api/v1/backtest/run',
        json={'start_date': start, 'end_date': end, 'model_version': 'v2'}).json()

    print(f"\nV1 - Accuracy: {v1_results['metrics']['accuracy']:.2%}, RMSE: {v1_results['metrics']['rmse']:.2f}%")
    print(f"V2 - Accuracy: {v2_results['metrics']['accuracy']:.2%}, RMSE: {v2_results['metrics']['rmse']:.2f}%")

    accuracy_improvement = (v2_results['metrics']['accuracy'] - v1_results['metrics']['accuracy']) / v1_results['metrics']['accuracy'] * 100
    rmse_improvement = (v1_results['metrics']['rmse'] - v2_results['metrics']['rmse']) / v1_results['metrics']['rmse'] * 100

    print(f"\nImprovements: Accuracy +{accuracy_improvement:.1f}%, RMSE -{rmse_improvement:.1f}%")
```

### JavaScript/Frontend Example
```javascript
// In your React component
const runBacktest = async (modelVersion = 'v2') => {
  const response = await api.post('/backtest/run', {
    start_date: '2020-06-01T00:00:00',
    end_date: '2020-06-30T00:00:00',
    storm_threshold: 40.0,
    sample_interval_hours: 24,
    model_version: modelVersion
  });

  console.log('Model:', modelVersion);
  console.log('Accuracy:', response.data.metrics.accuracy);
  console.log('Total predictions:', response.data.metadata.total_predictions);
};

// Compare both models
const compareModels = async () => {
  const [v1Results, v2Results] = await Promise.all([
    api.post('/backtest/run', {
      start_date: '2024-01-01T00:00:00',
      end_date: '2024-01-31T00:00:00',
      storm_threshold: 40.0,
      sample_interval_hours: 24,
      model_version: 'v1'
    }),
    api.post('/backtest/run', {
      start_date: '2024-01-01T00:00:00',
      end_date: '2024-01-31T00:00:00',
      storm_threshold: 40.0,
      sample_interval_hours: 24,
      model_version: 'v2'
    })
  ]);

  const accuracyImprovement = (v2Results.data.metrics.accuracy - v1Results.data.metrics.accuracy)
    / v1Results.data.metrics.accuracy * 100;
  console.log(`V2 accuracy improvement: +${accuracyImprovement.toFixed(1)}%`);
};
```

## References

- [Storm Predictor Model V1](./app/models/storm_predictor.py) - Original CNN-LSTM model
- [Storm Predictor Model V2](./app/models/storm_predictor_v2.py) - Enhanced BiLSTM-Attention model
- [Model Improvements Documentation](./MODEL_IMPROVEMENTS.md) - Detailed V2 architecture and research
- [Training Pipeline V2](./app/training/train_model_v2.py) - V2 model training code
- [Backtesting Service](./app/services/backtesting_service.py) - Model evaluation and comparison
- [API Routes](./app/api/routes.py) - REST endpoints
- [Historical Data](./DATABASE.md) - Database schema and seeding
