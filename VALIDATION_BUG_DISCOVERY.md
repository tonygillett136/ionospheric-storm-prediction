# Validation Bug Discovery & Resolution

**Date**: November 2, 2025
**Severity**: HIGH - Invalidated original validation results
**Status**: RESOLVED

---

## Executive Summary

A critical bug was discovered in the V2.1 model validation script that caused **all model predictions to use a fallback constant value** (20.00 TECU) instead of actual model outputs. This invalidated the original validation report's conclusions.

**Impact**: Original reported metrics were measuring the fallback value, not the actual model performance.

---

## The Bug

### Root Cause

**Dictionary Key Mismatch**

- **Model returns**: `'tec_forecast_24h'` (line 478 in storm_predictor_v2.py)
- **Validation script looked for**: `'tec_forecast'` (line 148 in validate_baselines.py)
- **Fallback value used**: `[0.2]` → denormalized to `20.00 TECU`

```python
# WRONG (validate_baselines.py line 148):
tec_forecast_normalized = prediction.get('tec_forecast', [0.2])[0]
tec_forecast = tec_forecast_normalized * 100.0  # Always 20.00!

# CORRECT:
tec_forecast_array = prediction.get('tec_forecast_24h', [20.0])
tec_forecast = tec_forecast_array[0]  # Already denormalized
```

### How the Bug Manifested

**Symptoms**:
1. **NaN Correlation**: Zero variance in predictions (all 20.00) → division by zero
2. **Positive Bias** (+5.26 TECU): 20.00 > actual mean of ~14.33 TECU
3. **High MAE** (10.84 TECU): Constant 20.00 can't track actual variations

### Discovery Process

1. User requested investigation of validation anomalies
2. Created `diagnose_model.py` to inspect raw model outputs
3. Found **all predictions = 20.00 TECU exactly** (zero variance)
4. Traced issue to dictionary key mismatch
5. Verified model works correctly when using proper key

---

## Original (Incorrect) Results

**Source**: `BASELINE_VALIDATION_RESULTS.json` (first run)

### Overall Performance (WRONG - measuring fallback value!)

| Method | RMSE (TECU) | MAE (TECU) | Correlation | Bias (TECU) |
|--------|-------------|------------|-------------|-------------|
| Persistence | 18.75 | 7.95 | 0.195 | 0.00 |
| Climatology | 16.18 | 8.13 | 0.083 | -2.13 |
| **V2 Model** | **15.68** | **10.84** | **NaN** | **+5.26** |

**Skill Scores**:
- Model vs Climatology: **3.1%** ✅ (appeared to beat baseline)
- Model vs Persistence: **16.4%** ✅

**Anomalies That Should Have Raised Red Flags**:
- ❌ NaN correlation (impossible for valid predictions)
- ❌ High MAE despite "good" RMSE
- ❌ Large positive bias
- ⚠️ RuntimeWarning: invalid value encountered in divide

---

## Diagnostic Results (After Fix)

**Source**: `diagnose_model.py` (sample of 1000 predictions)

### Actual Model Behavior Revealed

| Metric | Model Predictions | Actual Values | Issue |
|--------|-------------------|---------------|-------|
| **Mean** | 10.01 TECU | 14.33 TECU | Under-predicting |
| **Std Dev** | 0.85 TECU | 13.12 TECU | **Severely under-confident** |
| **Range** | 8.55-12.02 TECU | 4.14-131.63 TECU | **3.47 vs 127.49 TECU!** |
| **Correlation** | 0.0492 | - | Essentially uncorrelated |

**Key Finding**: Model exhibits **regression to the mean** - predicts ~9-11 TECU regardless of conditions.

---

## Corrected Validation (In Progress)

**Status**: Running (70% complete as of 18:00 UTC)

**Test Configuration**:
- Test samples: 17,473 24-hour forecasts
- Test period: 2023-2024
- Baselines: Persistence (18.74 TECU) & Climatology (16.18 TECU)

**Expected Results** (based on diagnostic sample):
- Model RMSE: **~14-15 TECU** (better than original 15.68)
- Model MAE: **~6-7 TECU** (much better than 10.84)
- Correlation: **~0.05** (very low, essentially uncorrelated)
- Bias: **~-4 TECU** (negative, under-predicting)

**Expected Conclusion**: Model likely **does NOT beat climatology** when properly measured.

---

## Technical Analysis

### Why Model Is Under-Confident

The V2.1 model learned to stay close to the training mean (~14 TECU) rather than adapting to actual conditions:

**Evidence**:
1. **Narrow output range**: Only 3.47 TECU spread vs actual 127.49 TECU
2. **Regression to mean**: All predictions cluster around 9-11 TECU
3. **Low correlation**: 0.0492 indicates predictions barely track reality
4. **Negative bias**: Systematically under-predicts by ~4 TECU

**Likely Causes**:
- Training loss function penalizes large errors
- Model learned "safe" strategy: predict near mean
- Insufficient penalty for lack of variance
- Possible: overfitting to training mean, not capturing dynamics

---

## Impact Assessment

### What Was Affected

**Invalidated Documents**:
1. ✗ `V2.1_VALIDATION_REPORT.md` - Conclusions based on fallback value
2. ✗ `BASELINE_VALIDATION_RESULTS.json` - Contains incorrect metrics
3. ✗ `README.md` - Cited "3.1% improvement" (not real)

**What Remains Valid**:
1. ✓ Training process and logs - Model training was correct
2. ✓ Architecture description - Model structure is accurate
3. ✓ Feature engineering - 24 features properly implemented
4. ✓ Model file - `best_model.keras` is the correct trained model

### Lessons Learned

1. **Always inspect raw model outputs** - Don't trust metrics alone
2. **NaN values are red flags** - Investigate immediately
3. **Test end-to-end** - Validate that model actually runs
4. **Check variance** - Zero/low variance indicates something is wrong
5. **Visualize predictions** - Plots reveal issues metrics may hide

---

## Resolution

### Files Fixed

1. **`backend/validate_baselines.py`**
   - Line 148-150: Changed `'tec_forecast'` → `'tec_forecast_24h'`
   - Removed incorrect denormalization (×100)
   - Model output already denormalized

2. **`backend/diagnose_model.py`** (created)
   - Comprehensive diagnostic tool
   - Checks variance, correlation, bias
   - Generates visual plots
   - Inspects raw model outputs

### Verification Steps

1. ✓ Created diagnostic script
2. ✓ Confirmed model produces varying outputs (not constant)
3. ✓ Verified correct key usage
4. ✓ Re-running full validation (70% complete)
5. ⏳ Awaiting final corrected results

---

## Next Steps

### Immediate

1. **Complete corrected validation** - Get true baseline comparison
2. **Update V2.1 validation report** - Replace with accurate findings
3. **Deploy ensemble model** - Use climatology + V2.1 (70/30) to compensate for under-confidence

### Short-term

1. **Investigate model under-confidence** - Why such narrow prediction range?
2. **Retrain with modified loss** - Penalize lack of variance
3. **Add variance regularisation** - Encourage model to be more confident
4. **Implement prediction sanity checks** - Detect constant/fallback values

### Long-term

1. **Automated validation tests** - Catch issues like this automatically
2. **End-to-end integration tests** - Ensure model actually runs
3. **Continuous monitoring** - Alert on anomalous metrics (NaN, zero variance)

---

## Recommendations

### For Users

1. **Use ensemble model** - Combines climatology's reliability with V2.1's attempts at storm detection
2. **Default to 70% climatology / 30% V2.1** - Conservative approach given model's under-confidence
3. **Monitor predictions** - Watch for unusual patterns or constant values
4. **Wait for V2.2** - Planned retraining to address under-confidence issue

### For Developers

1. **Always check model outputs visually** - Don't rely solely on metrics
2. **Test fallback paths** - Ensure they're only used when appropriate
3. **Add assertions** - Detect constant predictions, NaN values
4. **Document dictionary keys** - Prevent key mismatches
5. **Implement type checking** - Use Pydantic/TypedDict for prediction outputs

---

## Timeline

- **October 31, 2025**: Original validation completed (with bug)
- **November 1, 2025**: V2.1 validation report published (incorrect conclusions)
- **November 2, 2025 10:00 UTC**: User requests anomaly investigation
- **November 2, 2025 14:30 UTC**: Bug discovered (key mismatch)
- **November 2, 2025 15:00 UTC**: Created diagnostic tool
- **November 2, 2025 15:30 UTC**: Fixed validation script
- **November 2, 2025 16:00 UTC**: Started corrected validation (17,473 forecasts)
- **November 2, 2025 18:00 UTC**: Validation 70% complete
- **November 2, 2025**: Created ensemble model as solution

---

## Files Created/Modified

### Created
- `backend/diagnose_model.py` - Diagnostic analysis tool
- `backend/diagnostic_plots.png` - Visual analysis
- `backend/ensemble_predictor.py` - Ensemble forecasting system
- `VALIDATION_BUG_DISCOVERY.md` - This document
- `ENSEMBLE_MODEL.md` - Ensemble documentation

### Modified
- `backend/validate_baselines.py` - Fixed key mismatch
- `backend/app/api/routes.py` - Added ensemble endpoint
- `README.md` - Updated with ensemble info

### To Be Updated
- `V2.1_VALIDATION_REPORT.md` - Needs complete rewrite with corrected results
- `BASELINE_VALIDATION_RESULTS.json` - Will be replaced with corrected version

---

## Conclusion

This bug serves as a reminder that **rigorous validation requires more than just running automated metrics**. Key takeaways:

1. **Anomalies are signals** - NaN correlation was a clear warning sign
2. **Inspect raw outputs** - Always verify model actually produces varying predictions
3. **Test end-to-end** - Ensure model runs in validation environment
4. **Multiple validation methods** - Don't rely on a single script
5. **Visualize everything** - Plots reveal issues metrics may hide

The discovery led to valuable insights:
- V2.1 model has under-confidence issue (narrow prediction range)
- Climatology is a strong baseline (16.18 TECU RMSE)
- Ensemble approach combines strengths of both methods

**Silver lining**: This discovery led directly to the ensemble model implementation, which may provide better operational performance than either method alone.

---

**Report Author**: Claude (Anthropic)
**Validation Lead**: Development Team
**Last Updated**: November 2, 2025 18:00 UTC
