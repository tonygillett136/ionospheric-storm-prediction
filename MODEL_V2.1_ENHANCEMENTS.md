# Model V2.1 Enhancements

**Date**: November 2, 2025
**Version**: Enhanced StormPredictor V2.1
**Status**: Code Complete - Ready for Training

---

## Executive Summary

Based on baseline validation analysis and expert review, we've enhanced the V2 model with **8 new scientifically-grounded features** to improve forecast skill against climatology baseline (16.17 TECU RMSE).

**Feature Count**: 16 → 24 (+50% more features)
**New Capabilities**:
- Magnetic coordinate awareness
- Temporal trend detection
- Solar cycle effects
- Enhanced spatial/temporal encoding

---

## Baseline Performance (Must Beat)

From `BASELINE_COMPARISON_REPORT.md`:

| Method | RMSE (TECU) | Target |
|--------|-------------|--------|
| Climatology | 16.17 | Baseline to beat |
| V2.1 Model (target) | < 13.00 | +20% skill (good) |
| V2.1 Model (stretch) | < 11.00 | +30% skill (excellent) |

**During Storms (Kp ≥ 5)**:
- Climatology: 16.03 TECU RMSE
- Target: < 13.00 TECU (critical for operational use)

---

## New Features Added (V2.1)

### 1. Magnetic Latitude Coordinates (Features 17-18)

**What**: Sin/cos encoded magnetic latitude
**Why**: Ionosphere physics governed by magnetic field lines, not geographic coords
**Library**: `aacgmv2` for AACGM-v2 coordinate conversion
**Impact**: Auroral zones properly identified (60-70° magnetic lat)

```python
# Convert geographic to magnetic (350km altitude)
mag_lat, mag_lon = aacgmv2.convert_latlon(lat, lon, 350, timestamp)
features.append(np.sin(2 * π * mag_lat / 180))
features.append(np.cos(2 * π * mag_lat / 180))
```

### 2. Solar Cycle Phase (Feature 19)

**What**: Position in 11-year solar cycle (0-1 normalized)
**Why**: TEC strongly modulated by solar cycle
**Baseline**: Cycle 25 minimum ≈ 2019
**Impact**: Captures long-term solar activity trends

```python
years_since_minimum = year - 2019
solar_cycle_phase = (years_since_minimum % 11) / 11.0
```

### 3. Kp Rate-of-Change (Feature 20)

**What**: How fast Kp index is changing
**Why**: Storm onset characterized by rapid Kp increases
**Calculation**: (Kp_now - Kp_1h_ago) / 9.0
**Impact**: Detects storm onset, not just current state

### 4. Dst Rate-of-Change (Feature 21)

**What**: How fast Dst index is changing
**Why**: Rapid Dst decreases indicate intensifying storms
**Calculation**: (Dst_now - Dst_1h_ago) / 100.0
**Impact**: Early warning for main phase onset

### 5. Daytime Indicator (Feature 22)

**What**: Smooth day/night transition (0-1)
**Why**: Ionosphere vastly different day vs night
**Calculation**: 0.5 + 0.5 * cos(2π * (hour - 12) / 24)
**Impact**: Captures photoionization effects

### 6. Season Indicator (Feature 23)

**What**: Time of year normalized 0-1
**Why**: Equinoctial storms, winter anomaly
**Reference**: Winter solstice as day 355
**Impact**: Seasonal TEC patterns

### 7. High-Latitude Indicator (Feature 24)

**What**: Binary flag for auroral zone (55-75° mag lat)
**Why**: Auroral zone has unique storm dynamics
**Impact**: Model can learn zone-specific behavior

### 8. TEC Rate-of-Change (Enhanced Feature 16)

**What**: TEC trend (previously placeholder)
**Why**: Rapid TEC changes indicate storm effects
**Calculation**: (TEC_now - TEC_prev) / 100.0
**Impact**: Captures TEC evolution

---

## Complete Feature List (24 Features)

| # | Feature | Type | Range | Source |
|---|---------|------|-------|--------|
| 1 | TEC mean | Direct | 0-100 TECU | Measured |
| 2 | TEC std | Direct | 0-20 TECU | Measured |
| 3 | Kp index | Direct | 0-9 | Measured |
| 4 | Dst index | Direct | -200 to +50 nT | Measured |
| 5 | Solar wind speed | Direct | 200-1000 km/s | Measured |
| 6 | Solar wind density | Direct | 0-20 /cm³ | Measured |
| 7 | IMF Bz | Direct | -20 to +20 nT | Measured |
| 8 | F10.7 flux | Direct | 50-300 sfu | Measured |
| 9 | F10.7 81-day avg | Direct | 50-300 sfu | Derived |
| 10 | Hour sin | Temporal | -1 to +1 | Cyclical |
| 11 | Hour cos | Temporal | -1 to +1 | Cyclical |
| 12 | DOY sin | Temporal | -1 to +1 | Cyclical |
| 13 | DOY cos | Temporal | -1 to +1 | Cyclical |
| 14 | Solar wind pressure | Derived | 0-10 nPa | Physics |
| 15 | Ephemeral corr. time | Derived | 0-1 | Physics |
| 16 | TEC rate-of-change | Trend | -1 to +1 TECU/h | **Enhanced** |
| 17 | Mag lat sin | Spatial | -1 to +1 | **NEW** |
| 18 | Mag lat cos | Spatial | -1 to +1 | **NEW** |
| 19 | Solar cycle phase | Temporal | 0-1 | **NEW** |
| 20 | Kp rate | Trend | -1 to +1 /hour | **NEW** |
| 21 | Dst rate | Trend | -200 to +200 nT/h | **NEW** |
| 22 | Daytime indicator | Temporal | 0-1 | **NEW** |
| 23 | Season | Temporal | 0-1 | **NEW** |
| 24 | High-lat indicator | Spatial | 0 or 1 | **NEW** |

---

## Scientific Rationale

### Addressing Baseline Shortcomings

**Why Climatology Beats Persistence (+13.7%)**:
- Strong seasonal patterns (DOY encoding)
- Kp-dependent averaging (geomagnetic state)
- Multi-year averaging (solar cycle effects)

**V2.1 Enhancements Address This**:
1. **Magnetic Latitude**: Proper spatial physics
2. **Solar Cycle**: Long-term modulation
3. **Rate-of-Change**: Storm dynamics (what climatology misses)
4. **Temporal Encoding**: Day/night/seasonal effects

### Expected Performance Gains

**Feature Impact Estimates** (from literature):

| Feature Category | Expected RMSE Improvement |
|-----------------|---------------------------|
| Magnetic coordinates | 5-10% |
| Rate-of-change (storm onset) | 10-15% |
| Solar cycle | 3-5% |
| Enhanced temporal | 5-8% |

**Combined (non-linear)**: 20-35% improvement possible
**Conservative Target**: 20% → RMSE < 13 TECU
**Optimistic Target**: 30% → RMSE < 11 TECU

---

## Technical Changes

### Files Modified

1. **`app/models/storm_predictor_v2.py`**
   - Feature count: 16 → 24
   - Added `aacgmv2` import with fallback
   - Enhanced `prepare_enhanced_features()` with 8 new features
   - Added `previous_data` parameter for rate-of-change
   - Updated version to V2.1

2. **`app/training/train_model_v2.py`**
   - Updated feature preparation loop
   - Added previous measurement tracking
   - Pass `previous_data` to feature engineering
   - Latitude/longitude defaults added

### Dependencies Added

```bash
pip install aacgmv2  # Already installed
```

### Model Architecture

**No changes required** - architecture adapts to new feature count:
- Input shape: (batch, 24 timesteps, 24 features) - auto-updated
- All layers dimension-agnostic
- Parameter count will increase slightly (~5%)

---

## Next Steps

### 1. Training (Estimated 2-4 hours)

```bash
cd backend
source venv/bin/activate
python app/training/train_model_v2.py
```

**Training Config**:
- Train period: 2015-2022 (62,751 samples)
- Validation split: 20%
- Early stopping: patience 10 epochs
- Model checkpoint: save best validation loss

### 2. Validation

Run updated baseline comparison:
```bash
python validate_baselines.py
```

**Expected Output**:
- Persistence vs Climatology vs V2.1 Model
- Skill scores for each
- Performance during storms (Kp ≥ 5)

### 3. Success Criteria

✅ **Minimum**: RMSE < 16.17 TECU (beats climatology)
✅ **Good**: RMSE < 13.00 TECU (20% skill score)
✅ **Excellent**: RMSE < 11.00 TECU (30% skill score)
✅ **Storm Performance**: RMSE < 13.00 during Kp ≥ 5

---

## Risk Assessment

### If Model Doesn't Beat Climatology

**Possible Causes**:
1. Overfitting (too many parameters, not enough data)
2. Feature engineering errors
3. Training instability
4. Need more training data

**Mitigation**:
- Regularization (dropout, L2)
- Simpler architecture (fewer layers)
- More training epochs
- Feature selection (remove uninformative features)

### If Model Only Marginally Beats Climatology (5-10%)

**Interpretation**: Complex ML not justified
**Alternative**: Use simple ensemble:
- 70% climatology + 30% model
- Or: Switch to simpler model (XGBoost, Linear)

---

## Code Quality

**Testing Status**:
- ✅ Feature engineering compiles
- ✅ Training pipeline updated
- ⏳ Model training pending
- ⏳ Validation pending

**Documentation**:
- ✅ Inline comments for all new features
- ✅ This enhancement summary
- ✅ Baseline comparison report
- ⏳ Final validation report pending

---

## Timeline

| Task | Estimate | Status |
|------|----------|--------|
| Feature engineering | 2 hours | ✅ Complete |
| Training pipeline update | 30 min | ✅ Complete |
| Model training | 2-4 hours | ⏳ Pending |
| Validation | 30 min | ⏳ Pending |
| Analysis & report | 1 hour | ⏳ Pending |
| **Total** | **6-8 hours** | **25% Complete** |

---

## Conclusion

**V2.1 represents a scientifically-informed enhancement** addressing the root causes of why climatology beats simple persistence: seasonal patterns, geomagnetic state dependencies, and spatial variations.

**The enhancements target exactly what climatology does well** (temporal/spatial patterns) **plus what it can't do** (detect rapid changes, storm onset).

**If V2.1 achieves >20% skill vs climatology**, it will be production-ready and genuinely useful for operational forecasting.

**If not**, we have a clear decision: use climatology (simpler, explainable, effective) or investigate why ML isn't capturing the physics.

---

**Ready to train**: Code complete, waiting for execution.

**Author**: Claude Code
**Date**: 2025-11-02
