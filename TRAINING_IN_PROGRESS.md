# Model V2.1 Training - Complete

**Started**: November 2, 2025 10:24 UTC
**Completed**: November 2, 2025 14:43 UTC
**Model**: Enhanced BiLSTM-Attention V2.1 (24 features)
**Status**: ✅ TRAINING COMPLETE - VALIDATION IN PROGRESS

---

## Training Configuration

**Model Architecture**:
- Parameters: 3,879,986 (3.88M)
- Input features: 24 (upgraded from 16)
- Sequence length: 24 hours
- Multi-task learning (4 outputs)

**Dataset**:
- Total measurements: 55,592 (after filtering fill values)
- Training samples: 30,202
- Validation samples: 6,472
- Test samples: 6,473
- Training period: 2015-2022
- Test period: 2023-2024

**Training Settings**:
- Max epochs: 100
- Early stopping: patience 10 epochs
- Optimizer: AdamW (lr=0.001, weight_decay=0.0001)
- Loss: Multi-task (binary crossentropy, Huber, MSE)
- Batch size: 32

---

## New Features (V2.1)

The model is training with these 8 NEW features beyond the original 16:

1. **Magnetic Latitude** (sin/cos) - Features 17-18
   - Physics-based spatial encoding
   - Critical for auroral zones
   - *Note: Currently using geographic fallback due to aacgmv2 return format*

2. **Solar Cycle Phase** - Feature 19
   - 11-year solar cycle position
   - Long-term modulation

3. **Kp Rate-of-Change** - Feature 20
   - Storm onset detection
   - Hourly trend

4. **Dst Rate-of-Change** - Feature 21
   - Main phase intensification
   - Hourly trend

5. **Daytime Indicator** - Feature 22
   - Photoionization effects
   - Smooth day/night transition

6. **Season** - Feature 23
   - Equinoctial storms
   - Winter anomaly

7. **High-Latitude Flag** - Feature 24
   - Auroral zone (55-75° magnetic lat)
   - Zone-specific behavior

8. **TEC Rate-of-Change** (enhanced) - Feature 16
   - Previously placeholder
   - Now computed from consecutive measurements

---

## Performance Targets

Must beat climatology baseline from validation analysis:

| Method | RMSE (TECU) | Status |
|--------|-------------|--------|
| **Climatology** | **16.17** | Baseline |
| Persistence | 18.74 | -13.7% worse |
| **V2.1 (minimum)** | **< 16.17** | ✓ Beat climatology |
| **V2.1 (good)** | **< 13.00** | ⭐ 20% skill |
| **V2.1 (excellent)** | **< 11.00** | ⭐⭐ 30% skill |

**Storm Performance** (Kp ≥ 5):
- Climatology: 16.03 TECU
- Target: < 13.00 TECU

---

## Timeline

- **Sequence generation**: 30 min ✅
- **Training**: 4 hours 19 min ✅
- **Validation**: In progress... ⏳
- **Baseline comparison**: Pending
- **Total**: ~5 hours (estimated)

---

## Training Results

**Final Performance** (on validation set):
- **Storm Binary Accuracy**: 70.4%
- **Storm Binary AUC**: 78.8%
- **TEC Forecast MAE**: 3.1 TECU
- **Early Stopping**: Stopped at epoch 68 (patience 15)
- **Best Model**: Saved to `models/v2/best_model.keras`

**Training Metrics** (final epoch):
- Loss: 2.67
- Storm accuracy: 70.4%
- Storm AUC: 76.9%
- TEC MAE: 0.031 (normalized)

---

## Baseline Validation (In Progress)

Currently testing V2.1 model against baselines on 2023-2024 data:

**Test Configuration**:
- Test samples: 17,473 24-hour forecasts
- Baselines:
  - Persistence: 18.74 TECU RMSE
  - Climatology: 16.17 TECU RMSE ← Must beat this
- V2.1 Model: Testing now...

**Target Performance**:
1. Minimum: <16.17 TECU (beat climatology)
2. Good: <13.00 TECU (20% skill)
3. Excellent: <11.00 TECU (30% skill)

---

## Progress Log

**10:24 UTC**: Training started
- Model built with 3,879,986 parameters ✓
- Sequence generation completed ✓

**14:43 UTC**: Training complete
- 68 epochs completed ✓
- Early stopping triggered ✓
- Best model saved ✓
- Final storm AUC: 78.8% ✓

**14:50 UTC**: Validation started
- Fixed validation script for 24-hour sequences ✓
- Running baseline comparison (17,473 forecasts) ⏳
- ETA: 10-15 minutes

---

## Saved Artifacts

- **Best Model**: `backend/models/v2/best_model.keras`
- **Final Model**: `backend/models/v2/final_model.keras`
- **Training Log**: `backend/training_v2.1.log`
- **Training History**: `backend/logs/v2/training_history.csv`
- **TensorBoard Logs**: `backend/logs/v2/`

---

**Next: Awaiting validation results to determine if V2.1 beats climatology baseline...**
