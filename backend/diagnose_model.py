"""
Diagnostic Script for V2.1 Model Anomalies

Investigates:
1. NaN correlation issue
2. Positive bias (+5.26 TECU over-prediction)
3. High MAE (10.84 vs 8.13 climatology)
"""
import numpy as np
import asyncio
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from app.db.database import AsyncSessionLocal, init_db
from app.db.repository import HistoricalDataRepository
from app.models.storm_predictor_v2 import EnhancedStormPredictor


async def diagnose_predictions():
    """Diagnose model prediction issues."""
    print("=" * 80)
    print("V2.1 MODEL DIAGNOSTIC ANALYSIS")
    print("=" * 80)

    # Load model
    print("\n🔄 Loading V2.1 model...")
    predictor = EnhancedStormPredictor()
    model_path = "models/v2/best_model.keras"
    predictor.load_model(model_path)
    print("   ✓ Model loaded successfully\n")

    # Load test data
    print("📊 Loading test data (2023-2024)...")
    await init_db()

    async with AsyncSessionLocal() as session:
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 12, 31)

        test_data = await HistoricalDataRepository.get_measurements_by_time_range(
            session, start_date, end_date
        )

    print(f"   Loaded {len(test_data)} test measurements\n")

    # Make predictions on sample
    print("🧪 Generating predictions on sample...")

    model_predictions = []
    actual_values = []
    timestamps_list = []

    n_samples = min(1000, len(test_data) - 48)  # Sample 1000 predictions
    indices = np.linspace(24, len(test_data) - 25, n_samples, dtype=int)

    for i in indices:
        # Get 24h historical sequence
        historical_sequence = test_data[i - 23:i + 1]
        future = test_data[i + 24]

        # Prepare data
        data_sequence = []
        for measurement in historical_sequence:
            data_dict = {
                'tec_statistics': {'mean': measurement.tec_mean, 'std': measurement.tec_std},
                'kp_index': measurement.kp_index,
                'dst_index': measurement.dst_index,
                'solar_wind_params': {
                    'speed': measurement.solar_wind_speed,
                    'density': measurement.solar_wind_density
                },
                'imf_bz': measurement.imf_bz,
                'f107_flux': measurement.f107_flux,
                'timestamp': measurement.timestamp.isoformat(),
                'latitude': 45.0,
                'longitude': 0.0
            }
            data_sequence.append(data_dict)

        # Get prediction
        try:
            prediction = await predictor.predict_storm(data_sequence)
            tec_forecast_array = prediction.get('tec_forecast_24h', [20.0])
            tec_forecast = tec_forecast_array[0]  # Already denormalized

            model_predictions.append(tec_forecast)
            actual_values.append(future.tec_mean)
            timestamps_list.append(future.timestamp)
        except Exception as e:
            print(f"   Error on sample {len(model_predictions)}: {e}")
            continue

    model_predictions = np.array(model_predictions)
    actual_values = np.array(actual_values)

    print(f"   Generated {len(model_predictions)} predictions\n")

    # ============================================================================
    # ANALYSIS 1: Distribution Statistics
    # ============================================================================
    print("=" * 80)
    print("ANALYSIS 1: PREDICTION DISTRIBUTIONS")
    print("=" * 80)

    print(f"\nModel Predictions:")
    print(f"  Mean:       {np.mean(model_predictions):.2f} TECU")
    print(f"  Std Dev:    {np.std(model_predictions):.2f} TECU")
    print(f"  Min:        {np.min(model_predictions):.2f} TECU")
    print(f"  Max:        {np.max(model_predictions):.2f} TECU")
    print(f"  Range:      {np.max(model_predictions) - np.min(model_predictions):.2f} TECU")
    print(f"  Median:     {np.median(model_predictions):.2f} TECU")
    print(f"  Q1/Q3:      {np.percentile(model_predictions, 25):.2f} / {np.percentile(model_predictions, 75):.2f} TECU")

    print(f"\nActual Values:")
    print(f"  Mean:       {np.mean(actual_values):.2f} TECU")
    print(f"  Std Dev:    {np.std(actual_values):.2f} TECU")
    print(f"  Min:        {np.min(actual_values):.2f} TECU")
    print(f"  Max:        {np.max(actual_values):.2f} TECU")
    print(f"  Range:      {np.max(actual_values) - np.min(actual_values):.2f} TECU")
    print(f"  Median:     {np.median(actual_values):.2f} TECU")
    print(f"  Q1/Q3:      {np.percentile(actual_values, 25):.2f} / {np.percentile(actual_values, 75):.2f} TECU")

    # ============================================================================
    # ANALYSIS 2: Correlation Issue
    # ============================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS 2: CORRELATION DIAGNOSTICS")
    print("=" * 80)

    # Check variance
    pred_var = np.var(model_predictions)
    actual_var = np.var(actual_values)

    print(f"\nVariance:")
    print(f"  Predictions: {pred_var:.4f}")
    print(f"  Actuals:     {actual_var:.4f}")

    if pred_var < 0.01:
        print("\n⚠️  WARNING: Prediction variance near zero!")
        print("   → Model is predicting nearly constant values")
        print("   → This explains the NaN correlation")

    # Try to compute correlation
    try:
        correlation = np.corrcoef(model_predictions, actual_values)[0, 1]
        print(f"\nCorrelation: {correlation:.4f}")
    except:
        print(f"\n❌ Correlation: NaN (zero variance detected)")

    # ============================================================================
    # ANALYSIS 3: Bias Analysis
    # ============================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS 3: BIAS DIAGNOSTICS")
    print("=" * 80)

    errors = model_predictions - actual_values
    bias = np.mean(errors)
    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(np.mean(errors ** 2))

    print(f"\nError Statistics:")
    print(f"  Bias (mean error):  {bias:+.2f} TECU")
    print(f"  MAE:                {mae:.2f} TECU")
    print(f"  RMSE:               {rmse:.2f} TECU")

    positive_errors = np.sum(errors > 0)
    negative_errors = np.sum(errors < 0)

    print(f"\nError Distribution:")
    print(f"  Over-predictions:  {positive_errors} ({100*positive_errors/len(errors):.1f}%)")
    print(f"  Under-predictions: {negative_errors} ({100*negative_errors/len(errors):.1f}%)")

    if bias > 3:
        print(f"\n⚠️  WARNING: Significant positive bias detected!")
        print(f"   → Model systematically over-predicts by {bias:.2f} TECU")

    # ============================================================================
    # ANALYSIS 4: Raw Model Output Investigation
    # ============================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS 4: RAW MODEL OUTPUT INSPECTION")
    print("=" * 80)

    # Get a single raw prediction to inspect
    sample_sequence = test_data[24:48]
    data_sequence = []
    for measurement in sample_sequence:
        data_dict = {
            'tec_statistics': {'mean': measurement.tec_mean, 'std': measurement.tec_std},
            'kp_index': measurement.kp_index,
            'dst_index': measurement.dst_index,
            'solar_wind_params': {
                'speed': measurement.solar_wind_speed,
                'density': measurement.solar_wind_density
            },
            'imf_bz': measurement.imf_bz,
            'f107_flux': measurement.f107_flux,
            'timestamp': measurement.timestamp.isoformat(),
            'latitude': 45.0,
            'longitude': 0.0
        }
        data_sequence.append(data_dict)

    raw_prediction = await predictor.predict_storm(data_sequence)

    print("\nRaw Model Output (single sample):")
    print(f"  Storm probability 24h: {raw_prediction.get('storm_probability_24h', 0):.4f}")
    print(f"  Storm probability 48h: {raw_prediction.get('storm_probability_48h', 0):.4f}")
    print(f"  Risk level 24h:        {raw_prediction.get('risk_level_24h', 'Unknown')}")
    print(f"  Risk level 48h:        {raw_prediction.get('risk_level_48h', 'Unknown')}")

    tec_forecast_array = raw_prediction.get('tec_forecast_24h', [])
    if len(tec_forecast_array) > 0:
        print(f"\n  TEC Forecast (already in TECU, denormalized by model):")
        print(f"    First hour:  {tec_forecast_array[0]:.2f} TECU")
        print(f"    Mean (24h):  {np.mean(tec_forecast_array):.2f} TECU")
        print(f"    Std (24h):   {np.std(tec_forecast_array):.2f} TECU")
        print(f"    Range:       {np.min(tec_forecast_array):.2f} - {np.max(tec_forecast_array):.2f} TECU")

    # Check if values are in a reasonable range
    if len(tec_forecast_array) > 0:
        mean_tec = np.mean(tec_forecast_array)
        if mean_tec < 1.0 or mean_tec > 100.0:
            print(f"\n⚠️  WARNING: TEC values in unusual range!")
            print(f"   → Expected ~5-50 TECU, got {mean_tec:.2f} TECU")
            print(f"   → Model output may need investigation")

    # ============================================================================
    # ANALYSIS 5: Check Training Normalization
    # ============================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS 5: NORMALIZATION CHECK")
    print("=" * 80)

    # Sample actual TEC values from training period
    async with AsyncSessionLocal() as session:
        train_start = datetime(2015, 1, 1)
        train_end = datetime(2022, 12, 31)

        train_data = await HistoricalDataRepository.get_measurements_by_time_range(
            session, train_start, train_end
        )

    train_tec_values = [m.tec_mean for m in train_data[:10000]]  # Sample

    print(f"\nTraining Data TEC Statistics (sample):")
    print(f"  Mean:  {np.mean(train_tec_values):.2f} TECU")
    print(f"  Std:   {np.std(train_tec_values):.2f} TECU")
    print(f"  Range: {np.min(train_tec_values):.2f} - {np.max(train_tec_values):.2f} TECU")

    if len(tec_forecast_array) > 0:
        model_mean = np.mean(tec_forecast_array)
        expected_mean = np.mean(train_tec_values)

        print(f"\nModel Output Consistency Check:")
        print(f"  Model prediction mean:  {model_mean:.2f} TECU")
        print(f"  Training data mean:     {expected_mean:.2f} TECU")

        if abs(model_mean - expected_mean) > 10.0:
            print(f"\n⚠️  MISMATCH: Model output differs significantly from training data")
            print(f"   → Difference: {abs(model_mean - expected_mean):.2f} TECU")
        else:
            print(f"\n✅ Model output is in reasonable range (diff: {abs(model_mean - expected_mean):.2f} TECU)")

    # ============================================================================
    # SUMMARY
    # ============================================================================
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)

    issues_found = []

    if pred_var < 0.01:
        issues_found.append("Low prediction variance (explains NaN correlation)")

    if bias > 3:
        issues_found.append(f"Significant positive bias (+{bias:.2f} TECU)")

    if mae > 10:
        issues_found.append(f"High MAE ({mae:.2f} TECU)")

    if len(tec_forecast_array) > 0:
        mean_tec = np.mean(tec_forecast_array)
        if mean_tec < 1.0 or mean_tec > 100.0:
            issues_found.append(f"Unusual TEC output range ({mean_tec:.2f} TECU)")

    if len(issues_found) > 0:
        print("\n⚠️  Issues Identified:")
        for idx, issue in enumerate(issues_found, 1):
            print(f"   {idx}. {issue}")
    else:
        print("\n✅ No obvious issues detected")

    print("\n" + "=" * 80)

    # Save diagnostic plots
    print("\n📊 Generating diagnostic plots...")

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: Prediction vs Actual scatter
    axes[0, 0].scatter(actual_values, model_predictions, alpha=0.3, s=10)
    axes[0, 0].plot([0, 100], [0, 100], 'r--', label='Perfect prediction')
    axes[0, 0].set_xlabel('Actual TEC (TECU)')
    axes[0, 0].set_ylabel('Predicted TEC (TECU)')
    axes[0, 0].set_title('Prediction vs Actual')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Plot 2: Error distribution
    axes[0, 1].hist(errors, bins=50, edgecolor='black', alpha=0.7)
    axes[0, 1].axvline(0, color='r', linestyle='--', label='Zero error')
    axes[0, 1].axvline(bias, color='g', linestyle='--', label=f'Mean error ({bias:.2f})')
    axes[0, 1].set_xlabel('Prediction Error (TECU)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Error Distribution')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Plot 3: Prediction distribution
    axes[1, 0].hist(model_predictions, bins=50, edgecolor='black', alpha=0.7, label='Predictions')
    axes[1, 0].hist(actual_values, bins=50, edgecolor='black', alpha=0.5, label='Actuals')
    axes[1, 0].set_xlabel('TEC (TECU)')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Value Distributions')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Plot 4: Time series (first 200 samples)
    n_plot = min(200, len(model_predictions))
    axes[1, 1].plot(range(n_plot), actual_values[:n_plot], 'b-', label='Actual', alpha=0.7)
    axes[1, 1].plot(range(n_plot), model_predictions[:n_plot], 'r-', label='Predicted', alpha=0.7)
    axes[1, 1].set_xlabel('Sample')
    axes[1, 1].set_ylabel('TEC (TECU)')
    axes[1, 1].set_title('Time Series (first 200 samples)')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('diagnostic_plots.png', dpi=150)
    print("   ✓ Saved diagnostic_plots.png")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(diagnose_predictions())
