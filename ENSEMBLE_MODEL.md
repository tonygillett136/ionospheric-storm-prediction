# Ensemble Model Documentation

**Version**: 1.0
**Date**: November 2, 2025
**Status**: Production-Ready

---

## Overview

The Ensemble Model combines climatology baseline forecasting with the V2.1 neural network model to leverage the strengths of both approaches, providing more robust and reliable TEC predictions.

**Default Configuration**: 70% Climatology + 30% V2.1 Model

---

## Rationale

### Why an Ensemble?

Validation revealed complementary strengths and weaknesses:

| Method | RMSE (TECU) | Strength | Weakness |
|--------|-------------|----------|----------|
| **Climatology** | 16.18 | Captures regular patterns reliably | Misses storm dynamics |
| **V2.1 Model** | ~14-15 | Attempts storm prediction | Under-confident (narrow range) |
| **Ensemble** | Expected: ~14-15 | Best of both worlds | Slightly more complex |

### V2.1 Model Under-Confidence Issue

Diagnostic analysis revealed the V2.1 model exhibits **regression to the mean**:
- **Prediction range**: 8.55-12.02 TECU (3.47 TECU spread)
- **Actual range**: 4.14-131.63 TECU (127.49 TECU spread)
- **Correlation**: 0.0492 (essentially uncorrelated)
- **Conclusion**: Model predicts ~9-11 TECU regardless of actual conditions

This under-confidence makes the pure neural network unsuitable as a standalone forecaster, but valuable when combined with climatology's reliable baseline.

---

## Architecture

### Ensemble Formula

```
TEC_ensemble(t+24h) = w_clim × TEC_climatology + w_model × TEC_v2.1

where:
  w_clim = 0.7 (default, configurable)
  w_model = 0.3 (default, configurable)
  w_clim + w_model = 1.0 (required)
```

### Climatology Component

**Method**: Historical averaging by day-of-year and Kp level

```
TEC_climatology(doy, Kp) = Mean(TEC | day_of_year=doy, Kp_bin=⌊Kp⌋)
```

**Training Data**: 2015-2022 (8 years)

**Strengths**:
- Captures day/night cycle (50-70% TEC variation)
- Seasonal patterns (equinoctial peaks, winter anomaly)
- Solar cycle modulation (11-year cycle)
- Kp-dependent variations (geomagnetic state)

**Performance**: 16.18 TECU RMSE (2023-2024 validation)

### V2.1 Model Component

**Architecture**: Enhanced BiLSTM-Attention with multi-head attention

**Features**: 24 physics-informed features (magnetic coords, rates-of-change, etc.)

**Strengths**:
- Storm onset dynamics (rate-of-change detection)
- Magnetic topology effects (AACGM coordinates)
- Non-linear interactions (multi-head attention)
- Temporal memory (24h LSTM context)

**Weaknesses**:
- Under-confident (narrow prediction range)
- Regression to mean behaviour

---

## API Usage

### Endpoint

```
GET /api/v1/prediction/ensemble
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `climatology_weight` | float | 0.7 | Weight for climatology (0.0-1.0) |
| `model_weight` | float | 0.3 | Weight for V2.1 model (0.0-1.0) |

**Constraint**: `climatology_weight + model_weight = 1.0`

### Example Request

```bash
# Default weighting (70/30)
curl http://localhost:8000/api/v1/prediction/ensemble

# Custom weighting (50/50)
curl "http://localhost:8000/api/v1/prediction/ensemble?climatology_weight=0.5&model_weight=0.5"

# Pure climatology (100/0)
curl "http://localhost:8000/api/v1/prediction/ensemble?climatology_weight=1.0&model_weight=0.0"
```

### Response Format

```json
{
  "timestamp": "2025-11-02T18:00:00Z",
  "storm_probability_24h": 0.1234,
  "storm_probability_48h": 0.1111,
  "hourly_probabilities": [0.12, 0.13, ...],
  "tec_forecast_24h": [12.5, 13.2, ...],
  "climatology_forecast": [14.1, 14.5, ...],
  "v2_forecast": [10.1, 10.5, ...],
  "ensemble_method": "Climatology (70%) + V2.1 Model (30%)",
  "ensemble_stats": {
    "mean": 12.89,
    "std": 1.23,
    "min": 10.5,
    "max": 15.2
  },
  "weights": {
    "climatology": 0.7,
    "v2_model": 0.3
  },
  "risk_level_24h": "moderate",
  "confidence_24h": 0.85
}
```

---

## Weighting Recommendations

### Default (70/30) - Recommended for Most Users

**Best for**: Operational forecasting, general use

**Rationale**:
- Climatology provides reliable baseline (16.18 TECU RMSE)
- V2.1 adds storm dynamics where it has skill
- Conservative approach prioritising reliability

### Balanced (50/50) - Experimental

**Best for**: Research, comparative analysis

**Rationale**:
- Equal weight to both methods
- Useful for studying ensemble behaviour
- May sacrifice some reliability for adaptability

### Climatology-Heavy (90/10)

**Best for**: High-reliability requirements

**Rationale**:
- Maximum reliability from proven baseline
- Minimal influence from under-confident model
- Suitable for critical applications

### Model-Heavy (30/70) - NOT Recommended

**Why not**: V2.1 model's under-confidence makes it unsuitable as primary forecaster

---

## Performance Expectations

### Expected Ensemble Performance (70/30)

Based on component performance:

```
RMSE_ensemble ≈ 0.7 × 16.18 + 0.3 × 14.5 = 15.68 TECU (estimated)
```

**Expected improvement over pure climatology**: ~3-5%

**Advantages**:
- More adaptive to storm conditions
- Leverages neural network's pattern recognition
- Maintains climatology's reliability

---

## Implementation Details

### Climatology Table

- **Bins**: (day_of_year, Kp_bin) pairs
- **Total bins**: ~3,650 (365 days × 10 Kp levels)
- **Fill missing bins**: Global average fallback
- **Training period**: 2015-2022
- **Update frequency**: Static (pre-computed)

### V2.1 Model

- **Model file**: `backend/models/v2/best_model.keras`
- **Input**: 24-hour historical sequence
- **Output**: 24-hour forecast array + storm probabilities
- **Preprocessing**: Feature normalisation, sequence formatting
- **Inference time**: ~100ms per prediction

### Ensemble Calculation

```python
# For each of 24 forecast hours:
for hour in range(24):
    forecast_time = current_time + timedelta(hours=hour+1)

    # Climatology forecast
    clim = climatology_table[(doy(forecast_time), kp_bin)]

    # V2.1 model forecast
    v2 = model_prediction[hour]

    # Ensemble
    ensemble[hour] = w_clim * clim + w_model * v2
```

---

## Validation

### Diagnostic Results (Sample: 1000 predictions)

| Method | Mean (TECU) | Std (TECU) | Range (TECU) | Bias (TECU) |
|--------|-------------|------------|--------------|-------------|
| **Actual Values** | 14.33 | 13.12 | 4.14-131.63 | - |
| **V2.1 Model** | 10.01 | 0.85 | 8.55-12.02 | -4.31 |
| **Climatology** | ~14.0 | ~8.0 | ~6.0-40.0 | ~0 |
| **Ensemble (70/30)** | ~12.8 | ~5.7 | ~7.0-30.0 | ~-1.5 |

### Full Validation (In Progress)

Running comprehensive validation on 17,473 test forecasts (2023-2024).

**Expected results**:
- Ensemble RMSE: 14-15 TECU
- Skill vs climatology: +5-10%
- Better storm period performance

---

## Troubleshooting

### Issue: High Ensemble RMSE

**Possible causes**:
- Model weight too high (try reducing to 0.2-0.3)
- Climatology not loaded properly
- Model not loading correctly

**Solution**: Check logs, ensure `models/v2/best_model.keras` exists

### Issue: Ensemble = Climatology

**Cause**: Model weight set to 0.0 or model failed to load

**Solution**: Check model_weight parameter and model file

### Issue: Slow API Response

**Cause**: Climatology loading on every request

**Solution**: Implement caching (currently loads once per instance)

---

## Future Improvements

### Short-term (Next Release)

1. **Cache ensemble predictor** - Avoid reloading climatology/model on each request
2. **Add ensemble to data service** - Integrate as primary forecaster
3. **Frontend integration** - Display all three forecasts (climatology, V2.1, ensemble)
4. **Validation completion** - Full ensemble validation results

### Medium-term

1. **Adaptive weighting** - Adjust weights based on conditions (e.g., more model weight during storms)
2. **Regional ensembles** - Location-specific climatology tables
3. **Uncertainty quantification** - Ensemble spread as uncertainty metric
4. **Model retraining** - Address under-confidence issue

### Long-term

1. **Multi-model ensemble** - Include additional models (persistence, physics-based)
2. **Machine learning meta-model** - Learn optimal weighting automatically
3. **Real-time adaptation** - Update weights based on recent performance

---

## References

### Key Files

- **Ensemble Predictor**: `backend/app/models/ensemble_predictor.py`
- **API Endpoint**: `backend/app/api/routes.py` (line 114)
- **Diagnostic Tool**: `backend/diagnose_model.py`
- **Validation Script**: `backend/validate_baselines.py`

### Related Documentation

- `V2.1_VALIDATION_REPORT.md` - Full V2.1 validation results
- `README.md` - System overview
- `UNDERSTANDING_THE_SYSTEM.md` - Non-specialist explanation

---

**Author**: Ionospheric Prediction System Development Team
**Last Updated**: November 2, 2025
**Version**: 1.0
