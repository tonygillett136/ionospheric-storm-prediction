"""
Test prediction accuracy at different time horizons (24h, 48h, 72h, 5 days, 7 days)

This helps determine if longer-range storm predictions are feasible and useful.
"""
import asyncio
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys
import logging
import json

sys.path.append(str(Path(__file__).parent))

from app.db.database import AsyncSessionLocal, init_db
from app.db.repository import HistoricalDataRepository
from app.models.storm_predictor_v2 import EnhancedStormPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_prediction_horizon(
    predictor,
    measurements,
    start_idx,
    horizon_hours,
    storm_threshold=40.0
):
    """
    Test prediction accuracy for a specific time horizon.

    Args:
        predictor: Model predictor instance
        measurements: List of historical measurements
        start_idx: Starting index in measurements
        horizon_hours: Hours ahead to predict (24, 48, 72, 120, 168)
        storm_threshold: Threshold for storm classification

    Returns:
        Dict with prediction results
    """
    # Need 24 hours of input data
    if start_idx < 24:
        return None

    # Need data at target horizon
    target_idx = start_idx + horizon_hours
    if target_idx >= len(measurements):
        return None

    # Prepare input features (24 hours before current time)
    input_data = measurements[start_idx - 24:start_idx]

    features = []
    for m in input_data:
        data_dict = {
            'tec_statistics': {'mean': m.tec_mean, 'std': m.tec_std},
            'kp_index': m.kp_index,
            'dst_index': m.dst_index,
            'solar_wind_params': {
                'speed': m.solar_wind_speed,
                'density': m.solar_wind_density
            },
            'imf_bz': m.imf_bz,
            'f107_flux': m.f107_flux,
            'timestamp': m.timestamp.isoformat()
        }
        feat = predictor.prepare_enhanced_features(data_dict)
        feat = predictor.normalize_features(feat)
        features.append(feat)

    input_features = np.array([features], dtype=np.float32)

    # Run prediction
    prediction_output = predictor.model.predict(input_features, verbose=0)
    predicted_prob = float(prediction_output['storm_binary'][0][0] * 100)

    # Get actual at target horizon
    actual_measurement = measurements[target_idx]
    actual_prob = actual_measurement.storm_probability

    return {
        'prediction_time': measurements[start_idx].timestamp.isoformat(),
        'target_time': actual_measurement.timestamp.isoformat(),
        'horizon_hours': horizon_hours,
        'predicted_probability': predicted_prob,
        'actual_probability': actual_prob,
        'error': predicted_prob - actual_prob,
        'absolute_error': abs(predicted_prob - actual_prob),
        'predicted_storm': predicted_prob >= storm_threshold,
        'actual_storm': actual_prob >= storm_threshold,
        'correct_classification': (predicted_prob >= storm_threshold) == (actual_prob >= storm_threshold)
    }


def calculate_horizon_metrics(predictions, horizon_hours):
    """Calculate performance metrics for a specific horizon."""
    if not predictions:
        return None

    predicted_probs = np.array([p['predicted_probability'] for p in predictions])
    actual_probs = np.array([p['actual_probability'] for p in predictions])

    # Regression metrics
    mse = np.mean((predicted_probs - actual_probs) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(predicted_probs - actual_probs))

    # Classification metrics
    correct = sum(1 for p in predictions if p['correct_classification'])
    accuracy = correct / len(predictions)

    # Storm-specific metrics
    true_positives = sum(1 for p in predictions if p['predicted_storm'] and p['actual_storm'])
    false_positives = sum(1 for p in predictions if p['predicted_storm'] and not p['actual_storm'])
    true_negatives = sum(1 for p in predictions if not p['predicted_storm'] and not p['actual_storm'])
    false_negatives = sum(1 for p in predictions if not p['predicted_storm'] and p['actual_storm'])

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    far = false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) > 0 else 0

    return {
        'horizon_hours': horizon_hours,
        'horizon_days': horizon_hours / 24,
        'total_predictions': len(predictions),
        'rmse': rmse,
        'mae': mae,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'false_alarm_rate': far,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'true_negatives': true_negatives,
        'false_negatives': false_negatives,
        'actual_storms': true_positives + false_negatives,
        'predicted_storms': true_positives + false_positives
    }


async def run_horizon_analysis():
    """Main analysis function."""
    logger.info("Starting prediction horizon analysis")

    # Initialize
    await init_db()

    # Test period: Q1 2024 (3 months of data)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)

    logger.info(f"Loading data from {start_date} to {end_date}")

    async with AsyncSessionLocal() as session:
        measurements = await HistoricalDataRepository.get_measurements_by_time_range(
            session, start_date, end_date
        )

    logger.info(f"Loaded {len(measurements)} measurements")

    # Sort by timestamp
    measurements.sort(key=lambda m: m.timestamp)

    # Load V2 model
    model_path = Path('models/v2/best_model.keras')
    if not model_path.exists():
        logger.error(f"Model not found at {model_path}")
        return

    predictor = EnhancedStormPredictor(model_path=str(model_path))
    logger.info("Model loaded")

    # Test different horizons
    horizons = [
        24,   # 1 day (current)
        48,   # 2 days
        72,   # 3 days
        120,  # 5 days
        168   # 7 days (1 week)
    ]

    results = {}

    for horizon_hours in horizons:
        logger.info(f"\nTesting {horizon_hours}-hour ({horizon_hours/24:.1f}-day) predictions...")

        predictions = []

        # Sample every 6 hours to speed up analysis
        for i in range(24, len(measurements) - horizon_hours, 6):
            try:
                result = await test_prediction_horizon(
                    predictor,
                    measurements,
                    i,
                    horizon_hours,
                    storm_threshold=40.0
                )

                if result:
                    predictions.append(result)

                if len(predictions) % 100 == 0:
                    logger.info(f"  Processed {len(predictions)} predictions for {horizon_hours}h horizon")

            except Exception as e:
                logger.error(f"Error at index {i}: {e}")
                continue

        # Calculate metrics
        metrics = calculate_horizon_metrics(predictions, horizon_hours)

        if metrics:
            results[f"{horizon_hours}h"] = metrics

            logger.info(f"\n{horizon_hours}-hour ({horizon_hours/24:.1f}-day) Results:")
            logger.info(f"  Total predictions: {metrics['total_predictions']}")
            logger.info(f"  RMSE: {metrics['rmse']:.2f}%")
            logger.info(f"  MAE: {metrics['mae']:.2f}%")
            logger.info(f"  Accuracy: {metrics['accuracy']*100:.2f}%")
            logger.info(f"  F1 Score: {metrics['f1_score']*100:.2f}%")
            logger.info(f"  Recall (Detection Rate): {metrics['recall']*100:.2f}%")
            logger.info(f"  False Alarm Rate: {metrics['false_alarm_rate']*100:.2f}%")
            logger.info(f"  Actual storms: {metrics['actual_storms']}")

    # Save results
    output_file = Path('horizon_analysis_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n✅ Results saved to {output_file}")

    # Summary comparison
    logger.info("\n" + "="*80)
    logger.info("SUMMARY: Prediction Accuracy vs Time Horizon")
    logger.info("="*80)
    logger.info(f"{'Horizon':<12} {'Accuracy':<12} {'F1 Score':<12} {'RMSE':<12} {'Detection Rate':<15} {'False Alarms':<15}")
    logger.info("-"*80)

    for horizon_hours in horizons:
        key = f"{horizon_hours}h"
        if key in results:
            m = results[key]
            logger.info(
                f"{m['horizon_days']:.1f} days    "
                f"{m['accuracy']*100:>5.1f}%       "
                f"{m['f1_score']*100:>5.1f}%       "
                f"{m['rmse']:>5.1f}%       "
                f"{m['recall']*100:>5.1f}%          "
                f"{m['false_alarm_rate']*100:>5.1f}%"
            )

    logger.info("="*80)

    # Analysis and recommendation
    logger.info("\nANALYSIS:")

    # Compare 24h vs 168h (1 week)
    if '24h' in results and '168h' in results:
        acc_24h = results['24h']['accuracy']
        acc_168h = results['168h']['accuracy']
        f1_24h = results['24h']['f1_score']
        f1_168h = results['168h']['f1_score']

        acc_drop = (acc_24h - acc_168h) / acc_24h * 100
        f1_drop = (f1_24h - f1_168h) / f1_24h * 100

        logger.info(f"\n1-day vs 7-day comparison:")
        logger.info(f"  Accuracy drop: {acc_drop:.1f}%")
        logger.info(f"  F1 Score drop: {f1_drop:.1f}%")

        # Recommendation
        logger.info("\nRECOMMENDATION:")
        if acc_168h >= 0.5 and f1_168h >= 0.3:
            logger.info("  ✅ 7-day predictions show useful accuracy")
            logger.info(f"  ✅ 7-day predictions achieve {acc_168h*100:.1f}% accuracy and {f1_168h*100:.1f}% F1 score")
            logger.info("  ✅ WORTH ADDING to the app with appropriate confidence intervals")
        elif acc_168h >= 0.4:
            logger.info("  ⚠️  7-day predictions show marginal accuracy")
            logger.info(f"  ⚠️  7-day predictions achieve {acc_168h*100:.1f}% accuracy")
            logger.info("  ⚠️  Consider adding with STRONG uncertainty warnings")
        else:
            logger.info("  ❌ 7-day predictions are too unreliable")
            logger.info(f"  ❌ 7-day predictions only achieve {acc_168h*100:.1f}% accuracy")
            logger.info("  ❌ NOT RECOMMENDED for production use")

        # Sweet spot analysis
        logger.info("\nSWEET SPOT:")
        best_horizon = None
        best_balance = 0

        for horizon_hours in horizons:
            key = f"{horizon_hours}h"
            if key in results:
                m = results[key]
                # Balance between horizon length and accuracy
                balance_score = (horizon_hours / 24) * m['accuracy'] * m['f1_score']

                if balance_score > best_balance:
                    best_balance = balance_score
                    best_horizon = m

        if best_horizon:
            logger.info(f"  Optimal prediction horizon: {best_horizon['horizon_days']:.1f} days")
            logger.info(f"  Accuracy: {best_horizon['accuracy']*100:.1f}%")
            logger.info(f"  F1 Score: {best_horizon['f1_score']*100:.1f}%")

    return results


if __name__ == "__main__":
    asyncio.run(run_horizon_analysis())
