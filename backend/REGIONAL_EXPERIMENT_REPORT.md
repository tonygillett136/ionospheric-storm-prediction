# Regional Prediction Approach Experiment

## Executive Summary

**Winner:** Climatology-Primary

**Recommendation:** Climatology-Primary approach wins in 4/5 regions. Recommended for production.

## Experimental Design

### Approaches Tested

**Approach A: Climatology-Primary**
- Uses regional climatology as baseline
- Applies physics-based regional adjustment factors
- Best for: Stable conditions, regional baselines

**Approach B: V2.1 ML-Enhanced**
- Runs V2.1 neural network for global prediction
- Applies regional adjustments to ML output
- Blends with regional climatology (weight varies with Kp)
- Best for: Storm dynamics, rapid changes

### Test Parameters

- **Test Period:** 2025-08-10T00:00:00 to 2025-11-08T00:00:00
- **Duration:** 90 days
- **Total Hours:** 2160.0
- **Sample Interval:** Every 6 hours
- **Regions Tested:** 5 (Equatorial, Mid-Latitude, Auroral, Polar, Global)
- **Metrics:** MAE, RMSE, Median Error, Max Error

## Results by Region

### Equatorial

**Winner:** V2.1-Enhanced (Moderate confidence)

| Metric | Climatology-Primary | V2.1-Enhanced | Improvement |
|--------|---------------------|---------------|-------------|
| MAE (TECU) | 12.026 | 10.931 | +1.095 |
| RMSE (TECU) | 21.556 | 22.103 | -0.547 |
| Median Error | 7.025 | 4.551 | - |
| Max Error | 109.372 | 113.164 | - |
| Sample Count | 334 | 334 | - |

### Mid-Latitude

**Winner:** Climatology-Primary (High confidence)

| Metric | Climatology-Primary | V2.1-Enhanced | Improvement |
|--------|---------------------|---------------|-------------|
| MAE (TECU) | 10.462 | 10.698 | -0.236 |
| RMSE (TECU) | 22.381 | 23.561 | -1.180 |
| Median Error | 4.001 | 4.253 | - |
| Max Error | 115.488 | 118.405 | - |
| Sample Count | 334 | 334 | - |

### Auroral

**Winner:** Climatology-Primary (High confidence)

| Metric | Climatology-Primary | V2.1-Enhanced | Improvement |
|--------|---------------------|---------------|-------------|
| MAE (TECU) | 11.101 | 11.564 | -0.463 |
| RMSE (TECU) | 22.488 | 24.126 | -1.638 |
| Median Error | 4.288 | 4.464 | - |
| Max Error | 115.697 | 120.074 | - |
| Sample Count | 334 | 334 | - |

### Polar

**Winner:** Climatology-Primary (High confidence)

| Metric | Climatology-Primary | V2.1-Enhanced | Improvement |
|--------|---------------------|---------------|-------------|
| MAE (TECU) | 11.672 | 12.578 | -0.906 |
| RMSE (TECU) | 22.789 | 24.839 | -2.050 |
| Median Error | 5.067 | 5.929 | - |
| Max Error | 116.380 | 121.756 | - |
| Sample Count | 334 | 334 | - |

### Global

**Winner:** Climatology-Primary (High confidence)

| Metric | Climatology-Primary | V2.1-Enhanced | Improvement |
|--------|---------------------|---------------|-------------|
| MAE (TECU) | 10.462 | 10.698 | -0.236 |
| RMSE (TECU) | 22.381 | 23.561 | -1.180 |
| Median Error | 4.001 | 4.253 | - |
| Max Error | 115.488 | 118.405 | - |
| Sample Count | 334 | 334 | - |

## Overall Conclusion

**Winner:** Climatology-Primary

**Total Improvement:** -7.341 TECU

**Production Recommendation:**

Climatology-Primary approach wins in 4/5 regions. Recommended for production.

## Interpretation

- Positive improvement values indicate V2.1-Enhanced performs better
- Negative improvement values indicate Climatology-Primary performs better
- MAE (Mean Absolute Error): Average prediction error magnitude
- RMSE (Root Mean Square Error): Emphasizes larger errors more heavily

## Files

- **Results Data:** `REGIONAL_EXPERIMENT_RESULTS.json`
- **This Report:** `REGIONAL_EXPERIMENT_REPORT.md`
- **Backtest Service:** `backend/app/services/regional_backtest_service.py`

---

*Experiment conducted: 2025-11-08T10:06:33.469477*
