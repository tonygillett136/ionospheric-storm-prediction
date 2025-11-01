"""
Quick test script to verify the retrained model produces realistic predictions
"""
import asyncio
import numpy as np
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from app.models.storm_predictor_v2 import EnhancedStormPredictor
from app.db.database import AsyncSessionLocal, init_db
from app.db.repository import HistoricalDataRepository


async def test_model_predictions():
    """Test that the new model produces realistic predictions without artifacts"""

    print("=" * 80)
    print("TESTING RETRAINED V2 MODEL FOR ARTIFICIAL PATTERNS")
    print("=" * 80)

    # Initialize database
    await init_db()

    # Load the retrained model
    model_path = Path('models/v2/best_model.keras')
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        return

    print(f"\n✓ Loading model from {model_path}")
    predictor = EnhancedStormPredictor(model_path=str(model_path))

    # Get historical data
    async with AsyncSessionLocal() as session:
        measurements = await HistoricalDataRepository.get_latest_measurements(
            session, limit=24
        )
        measurements = list(reversed(measurements))

    print(f"✓ Loaded {len(measurements)} historical measurements")

    # Convert to predictor format
    historical_data = []
    for m in measurements:
        data_point = {
            'timestamp': m.timestamp.isoformat(),
            'tec_statistics': {
                'mean': m.tec_mean,
                'std': m.tec_std,
                'max': m.tec_max,
                'min': m.tec_min
            },
            'kp_index': m.kp_index,
            'dst_index': m.dst_index,
            'solar_wind_params': {
                'speed': m.solar_wind_speed,
                'density': m.solar_wind_density,
                'temperature': m.solar_wind_temperature
            },
            'imf_bz': m.imf_bz,
            'f107_flux': m.f107_flux
        }
        historical_data.append(data_point)

    # Make prediction
    print("\n✓ Generating prediction...")
    prediction = await predictor.predict_storm(historical_data)

    # Analyze hourly probabilities
    hourly_probs = prediction['hourly_probabilities']

    print("\n" + "=" * 80)
    print("PREDICTION ANALYSIS")
    print("=" * 80)

    print(f"\n24-hour Storm Probability: {prediction['storm_probability_24h']:.4f}")
    print(f"Risk Level: {prediction['risk_level']}")
    print(f"Confidence: {prediction['confidence']:.4f}")
    print(f"Model Version: {prediction['model_version']}")

    print("\n" + "-" * 80)
    print("HOURLY PROBABILITIES (Testing for Artificial Patterns)")
    print("-" * 80)

    # Print hourly probabilities
    for i in range(0, 24, 6):
        probs = [f"{p:.4f}" for p in hourly_probs[i:i+6]]
        print(f"Hours {i:2d}-{i+5:2d}: {' '.join(probs)}")

    # Statistical analysis
    print("\n" + "-" * 80)
    print("PATTERN DETECTION")
    print("-" * 80)

    # Calculate statistics for even and odd hours
    even_hours = [hourly_probs[i] for i in range(0, 24, 2)]
    odd_hours = [hourly_probs[i] for i in range(1, 24, 2)]

    mean_even = np.mean(even_hours)
    mean_odd = np.mean(odd_hours)
    std_all = np.std(hourly_probs)

    print(f"\nEven hours (0, 2, 4, ...): mean = {mean_even:.4f}")
    print(f"Odd hours  (1, 3, 5, ...): mean = {mean_odd:.4f}")
    print(f"Ratio (even/odd): {mean_even/mean_odd if mean_odd > 0 else 'N/A':.4f}")
    print(f"Overall std dev: {std_all:.4f}")

    # Check for periodicity
    ratio = mean_even / mean_odd if mean_odd > 0 else 1.0

    print("\n" + "-" * 80)
    print("VERDICT")
    print("-" * 80)

    if abs(ratio - 1.0) > 0.5:  # More than 50% difference
        print(f"\n⚠️  WARNING: Significant difference between even/odd hours (ratio: {ratio:.2f})")
        print("     This suggests an artificial 2-hour pattern may still exist.")
    else:
        print(f"\n✅ PASS: Even/odd hour ratio is {ratio:.2f} (close to 1.0)")
        print("     Predictions appear realistic with no obvious artificial patterns!")

    # Check variance
    if std_all < 0.05:
        print("\n⚠️  WARNING: Very low variance - predictions may be too uniform")
    elif std_all > 0.4:
        print("\n✅ GOOD: Healthy variance in predictions (realistic fluctuation)")
    else:
        print(f"\n✅ ACCEPTABLE: Moderate variance ({std_all:.4f})")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_model_predictions())
