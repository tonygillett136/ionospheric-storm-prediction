# Model V2.1 Training - In Progress

**Started**: November 2, 2025
**Model**: Enhanced BiLSTM-Attention V2.1 (24 features)
**Status**: 🔄 TRAINING IN PROGRESS

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

## Expected Timeline

- **Sequence generation**: ~30 min (COMPLETE)
- **Training**: 2-4 hours (IN PROGRESS)
- **Validation**: 30 min (pending)
- **Baseline comparison**: 30 min (pending)
- **Total**: 3-5 hours

---

## Next Steps (After Training)

1. Load trained model
2. Run `validate_baselines.py` with V2.1 model
3. Compare:
   - Persistence RMSE: 18.74 TECU
   - Climatology RMSE: 16.17 TECU
   - V2.1 RMSE: ???
4. Calculate skill scores
5. Generate final report
6. Determine production readiness

---

## Progress Log

**10:24 UTC**: Training started
- Model built with 3,879,986 parameters ✓
- Sequence generation started ✓
- Magnetic coordinate warnings (non-critical, using geographic fallback) ⚠️
- Training epochs will begin shortly...

---

## Monitoring

Training log: `backend/training_v2.1.log`
Model checkpoints: `backend/models/v2/`

Check progress:
```bash
tail -f backend/training_v2.1.log
```

---

**Status will be updated as training progresses...**
