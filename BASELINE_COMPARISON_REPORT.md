# Baseline Forecast Comparison Report

**Date**: November 2, 2025
**Analysis**: 24-hour TEC Forecasts on 2023-2024 Test Data

---

## Executive Summary

This report compares simple baseline forecasting methods for 24-hour Total Electron Content (TEC) predictions. The analysis uses proper temporal validation: trained on 2015-2022 data, tested on 2023-2024 data (17,496 forecast pairs).

### Key Findings

✅ **Climatology beats Persistence** by 13.7%
✅ **Both baselines provide measurable skill**
⚠️  **V2 Model comparison pending** (model loading issues)

---

## Baseline Methods

### 1. Persistence Forecast
**Assumption**: TEC tomorrow = TEC today

**Formula**: `TEC(t+24h) = TEC(t)`

**Results**:
- RMSE: **18.74 TECU**
- MAE: 7.95 TECU
- Correlation: 0.195
- Bias: 0.01 TECU (nearly unbiased)

### 2. Climatology Forecast
**Assumption**: TEC tomorrow = historical average for this day-of-year and Kp level

**Formula**: `TEC(t+24h) = average(TEC[doy, Kp_bin])` from 2015-2022 training data

**Results**:
- RMSE: **16.17 TECU**
- MAE: 8.13 TECU
- Correlation: 0.083
- Bias: -2.13 TECU (slight under-prediction)

---

## Performance Comparison

### Overall Performance (All Conditions)

| Method | RMSE (TECU) | MAE (TECU) | Correlation | Samples |
|--------|-------------|------------|-------------|---------|
| **Climatology** | **16.17** ⭐ | 8.13 | 0.083 | 17,496 |
| Persistence | 18.74 | **7.95** ⭐ | **0.195** ⭐ | 17,496 |

**Skill Score**: Climatology vs Persistence = **+13.7%**

### High Geomagnetic Activity (Kp ≥ 5)

| Method | RMSE (TECU) | MAE (TECU) | Correlation | Samples |
|--------|-------------|------------|-------------|---------|
| **Climatology** | **16.03** ⭐ | **8.40** ⭐ | 0.098 | 11,950 |
| Persistence | 19.97 | 8.96 | **0.215** ⭐ | 11,950 |

**Skill Score**: Climatology vs Persistence = **+19.7%** during storms

---

## Interpretation

### Why Climatology Wins

The ionosphere has **strong seasonal patterns**:
- Solar zenith angle (day/night, season)
- Equinoctial storms (spring/fall maxima)
- Solar cycle effects (F10.7 modulation)
- Geomagnetic activity levels (Kp dependence)

Climatology captures these patterns by:
1. Using day-of-year (seasonal effects)
2. Binning by Kp level (storm activity)
3. Averaging over 8 years of data (2015-2022)

**Result**: Knowing "average TEC for March 15th with Kp=3" is more informative than "TEC was X yesterday"

### Why Persistence Has Better Correlation

Despite higher RMSE, persistence shows better correlation (0.195 vs 0.083) because:
- Day-to-day TEC changes are autocorrelated
- Short-term persistence captures recent trends
- Climatology gives same answer for similar conditions (lower variance)

**Trade-off**: Persistence tracks variations better, but has higher absolute errors

### Performance During Storms

**Climatology improves more during high Kp** (19.7% vs 13.7% overall):
- Persistence struggles when TEC changes rapidly
- Climatology knows "storms typically increase TEC"
- Both still have ~20 TECU errors (TEC can change 50+ TECU during storms)

---

## Implications for Model Validation

### What the V2 Model Must Beat

To be considered useful, the V2 model must:

1. **Beat Climatology RMSE** (<16.17 TECU)
   - Minimum target: **< 16 TECU** (marginal improvement)
   - Good target: **< 13 TECU** (20% skill score)
   - Excellent target: **< 11 TECU** (30% skill score)

2. **Maintain or improve correlation** (> 0.20)
   - Shows it captures TEC variability, not just mean

3. **Excel during storms** (Kp ≥ 5)
   - This is when forecasts matter most
   - Target: **< 14 TECU** during high Kp

### Current Status

⚠️  **Model comparison incomplete** due to technical issues:
- EnhancedStormPredictor needs model weights loaded
- Requires loading from `models/storm_model_v2.h5` or similar
- Will be addressed in follow-up analysis

### What Good Performance Would Look Like

```
Method                RMSE (TECU)    Skill vs Climatology
------------------------------------------------------------
Climatology           16.17          baseline
Persistence           18.74          -15.9% (worse)
V2 Model (target)     11.00          +32.0% (excellent!)
```

A 30% skill score would indicate the model is **production-ready**.

---

## Recommendations

### Immediate Next Steps

1. **Fix Model Loading**: Enable V2 model to make predictions in validation script
2. **Add Model Results**: Re-run validation with working model
3. **Compare Skill Scores**: Calculate V2 skill vs both baselines

### If Model Beats Climatology

- Add to operational dashboard with confidence
- Highlight skill score in documentation
- Compare to NOAA operational forecasts

### If Model Doesn't Beat Climatology

- **Don't panic** - this is valuable information
- Investigate why:
  - Insufficient training data?
  - Model overfitting?
  - Missing key features?
- Consider simpler models (linear regression, gradient boosting)
- Add features identified in earlier review:
  - Magnetic latitude
  - Local time
  - Seasonal features
  - Rate-of-change features

---

## Data Quality

### Training Set (2015-2022)
- **62,751 measurements** (~87% of data)
- 9,063 unique climatology bins (DOY × Kp)
- Global TEC average: 12.7 TECU
- Proper temporal separation from test set

### Test Set (2023-2024)
- **17,496 valid forecast pairs** (24h apart)
- 11,950 samples with Kp ≥ 5 (68% high activity)
- No overlap with training period
- True out-of-sample validation

---

## Technical Notes

### Skill Score Formula

```
Skill = (RMSE_baseline - RMSE_model) / RMSE_baseline
```

- Skill > 0: Model better than baseline
- Skill > 0.3: Significantly better
- Skill > 0.5: Substantially better
- Skill < 0: Worse than baseline (problem!)

### Why RMSE?

RMSE penalizes large errors more than MAE:
- During storms, TEC can change 100+ TECU
- Large forecast errors are much worse than small ones
- GPS/satellite operators care most about missing big events

---

## Conclusion

**Climatology is a strong baseline** (16.17 TECU RMSE), especially during storms (+19.7% vs persistence).

The V2 model must demonstrate **significant skill (>20%) vs climatology** to justify its complexity (3.9M parameters, BiLSTM-Attention architecture).

This analysis provides the **objective standard** for model validation. Without beating climatology, the model would be:
- Academically interesting ✓
- Production-ready ✗

**Next Action**: Load V2 model weights and complete comparison.

---

**Generated**: 2025-11-02
**Test Period**: 2023-2024 (17,496 samples)
**Train Period**: 2015-2022 (62,751 samples)
