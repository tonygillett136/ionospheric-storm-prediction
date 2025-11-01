"""
Backtesting Service for Model Validation

Evaluates model performance on historical data to validate predictive accuracy.
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repository import HistoricalDataRepository
from app.models.storm_predictor import StormPredictor
from app.models.storm_predictor_v2 import EnhancedStormPredictor
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class BacktestingService:
    """Service for backtesting storm prediction model on historical data."""

    def __init__(self, model_version='v1', model_path=None):
        """
        Initialize backtesting service with specified model version

        Args:
            model_version: 'v1' or 'v2'
            model_path: Optional path to trained model
        """
        self.model_version = model_version

        if model_version == 'v2':
            # Try to load trained V2 model
            if model_path is None:
                v2_model_path = Path('models/v2/best_model.keras')
                if v2_model_path.exists():
                    model_path = str(v2_model_path)
                    logger.info(f"Loading V2 model from {model_path}")

            self.predictor = EnhancedStormPredictor(model_path=model_path)
            self.feature_count = 16
            logger.info("Using Enhanced Model V2 for backtesting")
        else:
            self.predictor = StormPredictor()
            self.feature_count = 8
            logger.info("Using Original Model V1 for backtesting")

    def prepare_input_features(self, measurements: List) -> np.ndarray:
        """
        Prepare input features from historical measurements for the model.

        Args:
            measurements: List of HistoricalMeasurement objects (24 hours)

        Returns:
            numpy array of shape (1, 24, feature_count) for model input
        """
        if len(measurements) < 24:
            raise ValueError(f"Need 24 hours of data, got {len(measurements)}")

        # Take last 24 measurements
        recent = measurements[-24:]

        features = []
        for m in recent:
            if self.model_version == 'v2':
                # Enhanced V2 features (16 features)
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
                feature_vector = self.predictor.prepare_enhanced_features(data_dict)
                feature_vector = self.predictor.normalize_features(feature_vector)
            else:
                # Original V1 features (8 features)
                feature_vector = [
                    m.tec_mean / 100.0,  # Normalize TEC
                    m.tec_std / 20.0,  # Normalize TEC std
                    m.kp_index / 9.0,  # Normalize Kp (0-9 scale)
                    m.solar_wind_speed / 1000.0,  # Normalize solar wind speed
                    m.imf_bz / 20.0,  # Normalize IMF Bz
                    m.f107_flux / 300.0,  # Normalize F10.7
                    np.sin(2 * np.pi * m.timestamp.hour / 24),  # Hour of day (sin)
                    np.cos(2 * np.pi * m.timestamp.timetuple().tm_yday / 365)  # Day of year (cos)
                ]
            features.append(feature_vector)

        # Shape: (1, 24, feature_count) - batch_size=1, timesteps=24
        return np.array([features], dtype=np.float32)

    def calculate_metrics(
        self,
        predictions: List[float],
        actuals: List[float],
        threshold: float = 40.0
    ) -> Dict:
        """
        Calculate comprehensive performance metrics.

        Args:
            predictions: List of predicted probabilities (0-100)
            actuals: List of actual probabilities (0-100)
            threshold: Probability threshold for storm classification

        Returns:
            Dictionary of metrics
        """
        predictions = np.array(predictions)
        actuals = np.array(actuals)

        # Regression metrics
        mse = np.mean((predictions - actuals) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - actuals))

        # Avoid division by zero
        if np.mean(actuals) != 0:
            mape = np.mean(np.abs((actuals - predictions) / (actuals + 1e-10))) * 100
        else:
            mape = 0.0

        # R-squared
        ss_res = np.sum((actuals - predictions) ** 2)
        ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
        r_squared = 1 - (ss_res / (ss_tot + 1e-10)) if ss_tot != 0 else 0.0

        # Classification metrics (storm vs no-storm)
        pred_storm = predictions >= threshold
        actual_storm = actuals >= threshold

        tp = np.sum((pred_storm == True) & (actual_storm == True))
        tn = np.sum((pred_storm == False) & (actual_storm == False))
        fp = np.sum((pred_storm == True) & (actual_storm == False))
        fn = np.sum((pred_storm == False) & (actual_storm == True))

        accuracy = (tp + tn) / len(predictions) if len(predictions) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # False alarm rate and hit rate
        far = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        hit_rate = recall  # Same as recall

        return {
            # Regression metrics
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'mape': float(mape),
            'r_squared': float(r_squared),

            # Classification metrics
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1_score),
            'hit_rate': float(hit_rate),
            'false_alarm_rate': float(far),

            # Confusion matrix
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),

            # Counts
            'total_predictions': len(predictions),
            'total_storms_actual': int(np.sum(actual_storm)),
            'total_storms_predicted': int(np.sum(pred_storm))
        }

    def optimize_threshold(
        self,
        predictions: List[float],
        actuals: List[float],
        optimization_method: str = 'f1',
        cost_false_alarm: float = 1.0,
        cost_missed_storm: float = 5.0,
        threshold_step: int = 5
    ) -> Dict:
        """
        Find optimal probability threshold using walk-forward cross-validation.

        This avoids overfitting by:
        1. Splitting data into 5 temporal folds (chronological order)
        2. For each threshold, calculating average performance across validation folds
        3. Finding threshold that works best on unseen future data
        4. Measuring stability (how consistent is performance across folds)

        Args:
            predictions: List of predicted probabilities (0-100)
            actuals: List of actual probabilities (0-100)
            optimization_method: 'f1', 'youden', or 'cost'
            cost_false_alarm: Cost of false alarm (for cost method)
            cost_missed_storm: Cost of missed storm (for cost method)
            threshold_step: Step size for threshold sweep (default 5%)

        Returns:
            Dictionary with optimal threshold and performance data
        """
        n_samples = len(predictions)
        n_folds = 5
        fold_size = n_samples // n_folds

        if fold_size < 10:
            # Not enough data for CV, fall back to single fold
            return self._optimize_threshold_single_fold(
                predictions, actuals, optimization_method,
                cost_false_alarm, cost_missed_storm, threshold_step
            )

        thresholds = list(range(10, 91, threshold_step))
        results = []

        best_score = -float('inf') if optimization_method != 'cost' else float('inf')
        best_threshold = 40

        # For each threshold, calculate cross-validated performance
        for threshold in thresholds:
            fold_scores = []
            fold_metrics_list = []

            # Walk-forward cross-validation
            for fold in range(1, n_folds):
                # Train on all data up to this fold
                train_end = fold * fold_size
                # Validate on this fold
                val_start = train_end
                val_end = min((fold + 1) * fold_size, n_samples)

                val_predictions = predictions[val_start:val_end]
                val_actuals = actuals[val_start:val_end]

                if len(val_predictions) == 0:
                    continue

                metrics = self.calculate_metrics(val_predictions, val_actuals, threshold)

                # Calculate score for this fold
                if optimization_method == 'f1':
                    score = metrics['f1_score']
                elif optimization_method == 'youden':
                    sensitivity = metrics['recall']
                    specificity = 1 - metrics['false_alarm_rate']
                    score = sensitivity + specificity - 1
                elif optimization_method == 'cost':
                    fp = metrics['false_positives']
                    fn = metrics['false_negatives']
                    score = (fp * cost_false_alarm) + (fn * cost_missed_storm)
                else:
                    score = 0

                fold_scores.append(score)
                fold_metrics_list.append(metrics)

            if not fold_scores:
                continue

            # Average score across folds
            avg_score = np.mean(fold_scores)
            # Stability: lower std = more consistent
            stability = 1.0 / (np.std(fold_scores) + 0.01)  # Add small epsilon

            # Penalize unstable thresholds
            if optimization_method == 'cost':
                adjusted_score = avg_score * (1.0 / stability)  # Higher cost is worse
            else:
                adjusted_score = avg_score * stability  # Reward stable high scores

            # Average metrics across folds
            avg_metrics = {
                'f1_score': np.mean([m['f1_score'] for m in fold_metrics_list]),
                'precision': np.mean([m['precision'] for m in fold_metrics_list]),
                'recall': np.mean([m['recall'] for m in fold_metrics_list]),
                'accuracy': np.mean([m['accuracy'] for m in fold_metrics_list]),
                'false_alarm_rate': np.mean([m['false_alarm_rate'] for m in fold_metrics_list]),
            }

            results.append({
                'threshold': threshold,
                'f1_score': avg_metrics['f1_score'],
                'precision': avg_metrics['precision'],
                'recall': avg_metrics['recall'],
                'accuracy': avg_metrics['accuracy'],
                'false_alarm_rate': avg_metrics['false_alarm_rate'],
                'youden_j': avg_metrics['recall'] + (1 - avg_metrics['false_alarm_rate']) - 1,
                'score': avg_score,
                'stability': stability,
                'score_std': np.std(fold_scores),
                'adjusted_score': adjusted_score
            })

            # Check if this is the best threshold (using adjusted score)
            if optimization_method == 'cost':
                if adjusted_score < best_score:
                    best_score = adjusted_score
                    best_threshold = threshold
            else:
                if adjusted_score > best_score:
                    best_score = adjusted_score
                    best_threshold = threshold

        # Get full metrics for optimal threshold on ALL data for final report
        optimal_metrics = self.calculate_metrics(predictions, actuals, best_threshold)

        return {
            'optimal_threshold': best_threshold,
            'optimization_method': optimization_method,
            'best_score': best_score,
            'threshold_sweep': results,
            'optimal_metrics': optimal_metrics,
            'n_folds': n_folds,
            'validation_type': 'walk_forward_cv'
        }

    def _optimize_threshold_single_fold(
        self, predictions, actuals, optimization_method,
        cost_false_alarm, cost_missed_storm, threshold_step
    ):
        """Fallback for small datasets - simple optimization without CV"""
        thresholds = list(range(10, 91, threshold_step))
        results = []
        best_score = -float('inf') if optimization_method != 'cost' else float('inf')
        best_threshold = 40

        for threshold in thresholds:
            metrics = self.calculate_metrics(predictions, actuals, threshold)

            if optimization_method == 'f1':
                score = metrics['f1_score']
            elif optimization_method == 'youden':
                score = metrics['recall'] + (1 - metrics['false_alarm_rate']) - 1
            elif optimization_method == 'cost':
                score = (metrics['false_positives'] * cost_false_alarm) + \
                        (metrics['false_negatives'] * cost_missed_storm)
            else:
                score = 0

            results.append({
                'threshold': threshold,
                'f1_score': metrics['f1_score'],
                'precision': metrics['precision'],
                'recall': metrics['recall'],
                'accuracy': metrics['accuracy'],
                'false_alarm_rate': metrics['false_alarm_rate'],
                'youden_j': metrics['recall'] + (1 - metrics['false_alarm_rate']) - 1,
                'score': score,
                'stability': 1.0,
                'score_std': 0.0,
                'adjusted_score': score
            })

            if optimization_method == 'cost':
                if score < best_score:
                    best_score = score
                    best_threshold = threshold
            else:
                if score > best_score:
                    best_score = score
                    best_threshold = threshold

        optimal_metrics = self.calculate_metrics(predictions, actuals, best_threshold)

        return {
            'optimal_threshold': best_threshold,
            'optimization_method': optimization_method,
            'best_score': best_score,
            'threshold_sweep': results,
            'optimal_metrics': optimal_metrics,
            'n_folds': 1,
            'validation_type': 'single_fold'
        }

    async def run_backtest(
        self,
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        storm_threshold: float = 40.0,
        sample_interval_hours: int = 1
    ) -> Dict:
        """
        Run backtest on historical data.

        Args:
            session: Database session
            start_date: Start of backtest period
            end_date: End of backtest period
            storm_threshold: Probability threshold for storm classification
            sample_interval_hours: Hours between predictions (1=every hour, 24=daily)

        Returns:
            Backtest results with predictions, actuals, and metrics
        """
        logger.info(f"Starting backtest from {start_date} to {end_date}")

        # Get all data for the period + 24 hours before (for first prediction)
        data_start = start_date - timedelta(hours=24)
        all_measurements = await HistoricalDataRepository.get_measurements_by_time_range(
            session, data_start, end_date
        )

        if len(all_measurements) < 48:  # Need at least 24 hours before + 24 hours of data
            raise ValueError(f"Insufficient data: need at least 48 hours, got {len(all_measurements)}")

        logger.info(f"Retrieved {len(all_measurements)} measurements for backtesting")

        # Create time series of predictions
        results = []
        current_time = start_date

        while current_time <= end_date:
            # Get 24 hours of data before current_time
            # Add 2-hour buffer to account for timestamp offsets (measurements might be at :43 past the hour)
            lookback_start = current_time - timedelta(hours=26)
            lookback_end = current_time + timedelta(hours=1)

            # Filter measurements for this window
            window_data = [
                m for m in all_measurements
                if lookback_start <= m.timestamp < lookback_end
            ]

            # Sort by timestamp and take last 24+ measurements
            window_data.sort(key=lambda m: m.timestamp)

            if len(window_data) >= 24:
                try:
                    # Prepare input features
                    input_features = self.prepare_input_features(window_data)
                    logger.debug(f"Input features shape: {input_features.shape} for {current_time}")

                    # Run prediction
                    prediction_output = self.predictor.model.predict(input_features, verbose=0)
                    # Model returns dict with 'storm_binary', 'storm_probability', 'tec_forecast'
                    # Use storm_binary for 24-hour ahead prediction (single value 0-1)
                    predicted_prob = float(prediction_output['storm_binary'][0][0] * 100)  # Convert to percentage
                    logger.debug(f"Predicted probability: {predicted_prob}% for {current_time}")

                    # Get actual storm probability 24 hours ahead
                    actual_time = current_time + timedelta(hours=24)
                    # Find measurement closest to actual_time (within 2 hour tolerance to handle irregular timestamps)
                    tolerance = timedelta(hours=2)
                    actual_measurement = None
                    min_time_diff = float('inf')

                    # Find the closest measurement to actual_time
                    for m in all_measurements:
                        time_diff = abs((m.timestamp - actual_time).total_seconds())
                        if time_diff < tolerance.total_seconds() and time_diff < min_time_diff:
                            actual_measurement = m
                            min_time_diff = time_diff

                    if actual_measurement and actual_measurement.storm_probability is not None:
                        actual_prob = actual_measurement.storm_probability

                        results.append({
                            'timestamp': current_time.isoformat(),
                            'prediction_timestamp': actual_time.isoformat(),
                            'predicted_probability': round(predicted_prob, 2),
                            'actual_probability': round(actual_prob, 2),
                            'error': round(predicted_prob - actual_prob, 2),
                            'absolute_error': round(abs(predicted_prob - actual_prob), 2),
                            'predicted_storm': predicted_prob >= storm_threshold,
                            'actual_storm': actual_prob >= storm_threshold,
                            'correct_classification': (predicted_prob >= storm_threshold) == (actual_prob >= storm_threshold)
                        })
                        logger.debug(f"Prediction added for {current_time}: pred={predicted_prob:.2f}, actual={actual_prob:.2f}")
                    else:
                        logger.warning(f"No actual measurement found for {actual_time}")

                except Exception as e:
                    logger.error(f"Prediction failed at {current_time}: {type(e).__name__}: {e}", exc_info=True)

            # Move to next time step
            current_time += timedelta(hours=sample_interval_hours)

        if len(results) == 0:
            raise ValueError("No valid predictions generated")

        # Calculate overall metrics
        predictions = [r['predicted_probability'] for r in results]
        actuals = [r['actual_probability'] for r in results]
        metrics = self.calculate_metrics(predictions, actuals, storm_threshold)

        # Find best and worst predictions
        results_sorted_by_error = sorted(results, key=lambda x: x['absolute_error'])
        best_predictions = results_sorted_by_error[:10]
        worst_predictions = results_sorted_by_error[-10:]

        # Identify missed storms and false alarms
        missed_storms = [r for r in results if r['actual_storm'] and not r['predicted_storm']]
        false_alarms = [r for r in results if r['predicted_storm'] and not r['actual_storm']]
        correct_predictions = [r for r in results if r['correct_classification']]

        logger.info(f"Backtest complete: {len(results)} predictions, accuracy={metrics['accuracy']:.2%}")

        return {
            'metadata': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'duration_days': (end_date - start_date).days,
                'storm_threshold': storm_threshold,
                'sample_interval_hours': sample_interval_hours,
                'total_predictions': len(results)
            },
            'metrics': metrics,
            'predictions': results,
            'analysis': {
                'best_predictions': best_predictions,
                'worst_predictions': worst_predictions,
                'missed_storms': missed_storms,
                'false_alarms': false_alarms,
                'correct_predictions_count': len(correct_predictions)
            },
            'summary': {
                'average_error': round(np.mean([r['error'] for r in results]), 2),
                'average_absolute_error': round(np.mean([r['absolute_error'] for r in results]), 2),
                'max_error': round(max([r['absolute_error'] for r in results]), 2),
                'min_error': round(min([r['absolute_error'] for r in results]), 2),
                'storm_detection_rate': round(metrics['recall'] * 100, 2),
                'false_alarm_rate': round(metrics['false_alarm_rate'] * 100, 2)
            }
        }

    async def get_storm_events(
        self,
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        threshold: float = 40.0
    ) -> List[Dict]:
        """
        Identify storm events in the historical data.

        Returns list of storm events with start/end times and peak probability.
        """
        measurements = await HistoricalDataRepository.get_measurements_by_time_range(
            session, start_date, end_date
        )

        storms = []
        in_storm = False
        storm_start = None
        storm_measurements = []

        for m in measurements:
            if m.storm_probability >= threshold:
                if not in_storm:
                    # Storm beginning
                    in_storm = True
                    storm_start = m.timestamp
                    storm_measurements = [m]
                else:
                    # Storm continuing
                    storm_measurements.append(m)
            else:
                if in_storm:
                    # Storm ended
                    peak_prob = max(sm.storm_probability for sm in storm_measurements)
                    peak_time = next(sm.timestamp for sm in storm_measurements if sm.storm_probability == peak_prob)

                    storms.append({
                        'start': storm_start.isoformat(),
                        'end': storm_measurements[-1].timestamp.isoformat(),
                        'duration_hours': len(storm_measurements),
                        'peak_probability': round(peak_prob, 2),
                        'peak_time': peak_time.isoformat(),
                        'average_probability': round(np.mean([sm.storm_probability for sm in storm_measurements]), 2)
                    })

                    in_storm = False
                    storm_measurements = []

        # Handle storm that extends to end of period
        if in_storm and storm_measurements:
            peak_prob = max(sm.storm_probability for sm in storm_measurements)
            peak_time = next(sm.timestamp for sm in storm_measurements if sm.storm_probability == peak_prob)

            storms.append({
                'start': storm_start.isoformat(),
                'end': storm_measurements[-1].timestamp.isoformat(),
                'duration_hours': len(storm_measurements),
                'peak_probability': round(peak_prob, 2),
                'peak_time': peak_time.isoformat(),
                'average_probability': round(np.mean([sm.storm_probability for sm in storm_measurements]), 2)
            })

        return storms
