"""
Comparative Backtest: V1 vs V2 Model Performance

Tests both models on the same historical period to validate improvements.
"""
import asyncio
import json
from datetime import datetime
from app.db.database import AsyncSessionLocal
from app.services.backtesting_service import BacktestingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_comparison_backtest():
    """Run V1 vs V2 comparison on same test period"""

    # Test period: January 2024 (1 month)
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    end_date = datetime(2024, 1, 31, 23, 59, 59)
    storm_threshold = 40.0
    sample_interval_hours = 24  # Daily predictions for faster testing

    logger.info("=" * 80)
    logger.info("V1 vs V2 MODEL COMPARISON BACKTEST")
    logger.info("=" * 80)
    logger.info(f"Test Period: {start_date} to {end_date}")
    logger.info(f"Storm Threshold: {storm_threshold}%")
    logger.info(f"Sample Interval: {sample_interval_hours} hours")
    logger.info("")

    async with AsyncSessionLocal() as session:
        # Run V1 Model Backtest
        logger.info("-" * 80)
        logger.info("TESTING V1 MODEL (CNN-LSTM, 500K params, 8 features)")
        logger.info("-" * 80)

        try:
            v1_service = BacktestingService(model_version='v1')
            v1_results = await v1_service.run_backtest(
                session,
                start_date,
                end_date,
                storm_threshold,
                sample_interval_hours
            )

            logger.info("✓ V1 Model backtest completed")
            logger.info(f"  Total Predictions: {v1_results['metadata']['total_predictions']}")
            logger.info("")

        except Exception as e:
            logger.error(f"✗ V1 Model backtest failed: {e}")
            v1_results = None

        # Run V2 Model Backtest
        logger.info("-" * 80)
        logger.info("TESTING V2 MODEL (BiLSTM-Attention, 3.9M params, 16 features)")
        logger.info("-" * 80)

        try:
            v2_service = BacktestingService(model_version='v2')
            v2_results = await v2_service.run_backtest(
                session,
                start_date,
                end_date,
                storm_threshold,
                sample_interval_hours
            )

            logger.info("✓ V2 Model backtest completed")
            logger.info(f"  Total Predictions: {v2_results['metadata']['total_predictions']}")
            logger.info("")

        except Exception as e:
            logger.error(f"✗ V2 Model backtest failed: {e}")
            v2_results = None

    # Compare Results
    if v1_results and v2_results:
        logger.info("=" * 80)
        logger.info("PERFORMANCE COMPARISON")
        logger.info("=" * 80)
        logger.info("")

        # Metrics comparison
        v1_metrics = v1_results['metrics']
        v2_metrics = v2_results['metrics']

        def calc_improvement(v1_val, v2_val, higher_is_better=True):
            """Calculate percentage improvement"""
            if v1_val == 0:
                return 0.0
            if higher_is_better:
                return ((v2_val - v1_val) / v1_val) * 100
            else:
                return ((v1_val - v2_val) / v1_val) * 100

        # Print comparison table
        logger.info("Metric                   | V1 Model  | V2 Model  | Improvement")
        logger.info("-" * 70)

        # Regression metrics (lower is better)
        rmse_imp = calc_improvement(v1_metrics['rmse'], v2_metrics['rmse'], higher_is_better=False)
        logger.info(f"RMSE                     | {v1_metrics['rmse']:>8.2f}% | {v2_metrics['rmse']:>8.2f}% | {rmse_imp:>6.1f}%")

        mae_imp = calc_improvement(v1_metrics['mae'], v2_metrics['mae'], higher_is_better=False)
        logger.info(f"MAE                      | {v1_metrics['mae']:>8.2f}% | {v2_metrics['mae']:>8.2f}% | {mae_imp:>6.1f}%")

        mape_imp = calc_improvement(v1_metrics['mape'], v2_metrics['mape'], higher_is_better=False)
        logger.info(f"MAPE                     | {v1_metrics['mape']:>8.2f}% | {v2_metrics['mape']:>8.2f}% | {mape_imp:>6.1f}%")

        # R-squared (higher is better)
        r2_imp = calc_improvement(v1_metrics['r_squared'], v2_metrics['r_squared'], higher_is_better=True)
        logger.info(f"R² Score                 | {v1_metrics['r_squared']:>9.4f} | {v2_metrics['r_squared']:>9.4f} | {r2_imp:>6.1f}%")

        logger.info("")

        # Classification metrics (higher is better)
        acc_imp = calc_improvement(v1_metrics['accuracy'], v2_metrics['accuracy'], higher_is_better=True)
        logger.info(f"Accuracy                 | {v1_metrics['accuracy']:>8.2%} | {v2_metrics['accuracy']:>8.2%} | {acc_imp:>6.1f}%")

        prec_imp = calc_improvement(v1_metrics['precision'], v2_metrics['precision'], higher_is_better=True)
        logger.info(f"Precision                | {v1_metrics['precision']:>8.2%} | {v2_metrics['precision']:>8.2%} | {prec_imp:>6.1f}%")

        rec_imp = calc_improvement(v1_metrics['recall'], v2_metrics['recall'], higher_is_better=True)
        logger.info(f"Recall                   | {v1_metrics['recall']:>8.2%} | {v2_metrics['recall']:>8.2%} | {rec_imp:>6.1f}%")

        f1_imp = calc_improvement(v1_metrics['f1_score'], v2_metrics['f1_score'], higher_is_better=True)
        logger.info(f"F1 Score                 | {v1_metrics['f1_score']:>8.2%} | {v2_metrics['f1_score']:>8.2%} | {f1_imp:>6.1f}%")

        # False alarm rate (lower is better)
        far_imp = calc_improvement(v1_metrics['false_alarm_rate'], v2_metrics['false_alarm_rate'], higher_is_better=False)
        logger.info(f"False Alarm Rate         | {v1_metrics['false_alarm_rate']:>8.2%} | {v2_metrics['false_alarm_rate']:>8.2%} | {far_imp:>6.1f}%")

        logger.info("")
        logger.info("Confusion Matrix         | V1 Model  | V2 Model")
        logger.info("-" * 50)
        logger.info(f"True Positives           | {v1_metrics['true_positives']:>9} | {v2_metrics['true_positives']:>9}")
        logger.info(f"True Negatives           | {v1_metrics['true_negatives']:>9} | {v2_metrics['true_negatives']:>9}")
        logger.info(f"False Positives          | {v1_metrics['false_positives']:>9} | {v2_metrics['false_positives']:>9}")
        logger.info(f"False Negatives          | {v1_metrics['false_negatives']:>9} | {v2_metrics['false_negatives']:>9}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)

        # Calculate average improvement across key metrics
        key_improvements = [rmse_imp, mae_imp, acc_imp, f1_imp]
        avg_improvement = sum(key_improvements) / len(key_improvements)

        logger.info(f"Average Improvement: {avg_improvement:+.1f}%")
        logger.info("")

        if avg_improvement >= 50:
            logger.info("✓ V2 MODEL MEETS EXPECTED 50-70% IMPROVEMENT TARGET")
        elif avg_improvement >= 25:
            logger.info("~ V2 MODEL SHOWS SIGNIFICANT IMPROVEMENT (25-50%)")
        else:
            logger.info("! V2 MODEL SHOWS MODEST IMPROVEMENT (<25%)")

        logger.info("")

        # Save detailed results to JSON
        comparison_results = {
            'test_period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'duration_days': (end_date - start_date).days,
                'storm_threshold': storm_threshold,
                'sample_interval_hours': sample_interval_hours
            },
            'v1_results': v1_results,
            'v2_results': v2_results,
            'improvements': {
                'rmse': rmse_imp,
                'mae': mae_imp,
                'mape': mape_imp,
                'r_squared': r2_imp,
                'accuracy': acc_imp,
                'precision': prec_imp,
                'recall': rec_imp,
                'f1_score': f1_imp,
                'false_alarm_rate': far_imp,
                'average': avg_improvement
            }
        }

        output_file = 'models/v2/comparison_results.json'
        with open(output_file, 'w') as f:
            json.dump(comparison_results, f, indent=2)

        logger.info(f"Detailed results saved to: {output_file}")
        logger.info("")

    else:
        logger.error("Comparison failed - one or both backtests did not complete")


if __name__ == '__main__':
    asyncio.run(run_comparison_backtest())
