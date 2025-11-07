"""
Recent Storm Performance Service

Catalogs recent storms (up to 1 year) and evaluates model prediction performance
for each storm event. Provides detailed analysis of how well the model predicted
each storm in advance.
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repository import HistoricalDataRepository
from app.services.backtesting_service import BacktestingService
import logging

logger = logging.getLogger(__name__)


class RecentStormPerformanceService:
    """Service for analyzing model performance on recent historical storms."""

    def __init__(self, model_version='v2'):
        """Initialize service with specified model version."""
        self.model_version = model_version
        self.backtesting_service = BacktestingService(model_version=model_version)

    async def detect_storms(
        self,
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        kp_threshold: float = 5.0,
        min_duration_hours: int = 3
    ) -> List[Dict]:
        """
        Detect storm events from historical data based on Kp index.

        Args:
            session: Database session
            start_date: Start of search period
            end_date: End of search period
            kp_threshold: Kp index threshold for storm (5.0 = G1 minor storm)
            min_duration_hours: Minimum hours to qualify as a storm event

        Returns:
            List of detected storm events with metadata
        """
        logger.info(f"Detecting storms from {start_date} to {end_date}, Kp >= {kp_threshold}")

        measurements = await HistoricalDataRepository.get_measurements_by_time_range(
            session, start_date, end_date
        )

        if not measurements:
            return []

        storms = []
        in_storm = False
        storm_start = None
        storm_measurements = []

        for m in measurements:
            # Check if we're in storm conditions (filter out NASA OMNI fill values)
            is_storm_conditions = (
                m.kp_index >= kp_threshold and
                m.kp_index < 99.0  # Filter out fill values
            )

            if is_storm_conditions:
                if not in_storm:
                    # Storm beginning
                    in_storm = True
                    storm_start = m
                    storm_measurements = [m]
                else:
                    # Storm continuing
                    storm_measurements.append(m)
            else:
                if in_storm and len(storm_measurements) >= min_duration_hours:
                    # Storm ended and meets minimum duration
                    storm_info = self._create_storm_summary(storm_start, storm_measurements)
                    storms.append(storm_info)

                    in_storm = False
                    storm_measurements = []
                elif in_storm:
                    # Storm ended but too short
                    in_storm = False
                    storm_measurements = []

        # Handle storm that extends to end of period
        if in_storm and len(storm_measurements) >= min_duration_hours:
            storm_info = self._create_storm_summary(storm_start, storm_measurements)
            storms.append(storm_info)

        logger.info(f"Detected {len(storms)} storms")
        return storms

    def _create_storm_summary(self, storm_start, storm_measurements) -> Dict:
        """Create summary information for a detected storm."""
        peak_kp = max(m.kp_index for m in storm_measurements)
        avg_kp = np.mean([m.kp_index for m in storm_measurements])
        peak_time = next(m.timestamp for m in storm_measurements if m.kp_index == peak_kp)

        # Calculate TEC response
        tec_values = [m.tec_mean for m in storm_measurements if m.tec_mean < 999.0]
        max_tec = max(tec_values) if tec_values else 0
        avg_tec = np.mean(tec_values) if tec_values else 0

        # Classify storm severity based on NOAA G-scale
        severity = self._classify_storm_severity(peak_kp)

        # Get storm duration
        duration_hours = len(storm_measurements)
        storm_end = storm_measurements[-1].timestamp

        return {
            'storm_id': f"storm_{storm_start.timestamp.strftime('%Y%m%d_%H%M')}",
            'start_time': storm_start.timestamp.isoformat(),
            'end_time': storm_end.isoformat(),
            'peak_time': peak_time.isoformat(),
            'duration_hours': duration_hours,
            'peak_kp': round(float(peak_kp), 2),
            'avg_kp': round(float(avg_kp), 2),
            'max_tec': round(float(max_tec), 2),
            'avg_tec': round(float(avg_tec), 2),
            'severity': severity['level'],
            'severity_name': severity['name'],
            'g_scale': severity['g_scale']
        }

    def _classify_storm_severity(self, kp: float) -> Dict:
        """Classify storm severity based on Kp index using NOAA G-scale."""
        if kp >= 9:
            return {'level': 5, 'name': 'Extreme', 'g_scale': 'G5'}
        elif kp >= 8:
            return {'level': 4, 'name': 'Severe', 'g_scale': 'G4'}
        elif kp >= 7:
            return {'level': 3, 'name': 'Strong', 'g_scale': 'G3'}
        elif kp >= 6:
            return {'level': 2, 'name': 'Moderate', 'g_scale': 'G2'}
        elif kp >= 5:
            return {'level': 1, 'name': 'Minor', 'g_scale': 'G1'}
        else:
            return {'level': 0, 'name': 'No Storm', 'g_scale': 'G0'}

    async def analyze_storm_performance(
        self,
        session: AsyncSession,
        storm_info: Dict,
        prediction_lead_hours: int = 24
    ) -> Dict:
        """
        Analyze model performance for a specific storm.

        Runs the model retrospectively with data available before the storm
        and compares predictions to actual storm evolution.

        Args:
            session: Database session
            storm_info: Storm metadata from detect_storms()
            prediction_lead_hours: Hours before storm to start predictions (default 24)

        Returns:
            Performance analysis for this storm
        """
        storm_start = datetime.fromisoformat(storm_info['start_time'])
        storm_end = datetime.fromisoformat(storm_info['end_time'])
        peak_time = datetime.fromisoformat(storm_info['peak_time'])

        # Get data from before storm started (for model input)
        prediction_start = storm_start - timedelta(hours=prediction_lead_hours + 24)
        prediction_end = storm_end + timedelta(hours=6)  # Include recovery phase

        logger.info(f"Analyzing performance for storm {storm_info['storm_id']}")

        try:
            # Run backtest for this storm period
            backtest_result = await self.backtesting_service.run_backtest(
                session,
                start_date=storm_start - timedelta(hours=prediction_lead_hours),
                end_date=storm_end,
                storm_threshold=40.0,
                sample_interval_hours=3  # Check every 3 hours
            )

            # Analyze prediction quality
            predictions = backtest_result['predictions']

            # Find when model first detected the storm (predicted probability >= 40%)
            storm_detected = False
            first_detection_time = None
            detection_lead_hours = 0

            for pred in predictions:
                pred_time = datetime.fromisoformat(pred['timestamp'])
                pred_target_time = datetime.fromisoformat(pred['prediction_timestamp'])

                # Check if this prediction was for a time during the storm
                if storm_start <= pred_target_time <= storm_end:
                    if pred['predicted_storm'] and not storm_detected:
                        storm_detected = True
                        first_detection_time = pred_time
                        detection_lead_hours = (storm_start - pred_time).total_seconds() / 3600

            # Find peak prediction
            peak_predictions = [p for p in predictions
                              if abs((datetime.fromisoformat(p['prediction_timestamp']) - peak_time).total_seconds()) < 7200]  # Within 2 hours

            if peak_predictions:
                peak_prediction = max(peak_predictions, key=lambda x: x['predicted_probability'])
                peak_pred_accuracy = abs(peak_prediction['predicted_probability'] - storm_info['peak_kp'] * 10)  # Rough conversion
            else:
                peak_prediction = None
                peak_pred_accuracy = None

            # Calculate storm-specific metrics
            storm_period_predictions = [
                p for p in predictions
                if storm_start <= datetime.fromisoformat(p['prediction_timestamp']) <= storm_end
            ]

            if storm_period_predictions:
                storm_rmse = np.sqrt(np.mean([p['error']**2 for p in storm_period_predictions]))
                storm_mae = np.mean([p['absolute_error'] for p in storm_period_predictions])
                detection_rate = sum(1 for p in storm_period_predictions if p['predicted_storm']) / len(storm_period_predictions)
            else:
                storm_rmse = None
                storm_mae = None
                detection_rate = 0.0

            return {
                'storm_id': storm_info['storm_id'],
                'storm_info': storm_info,
                'model_performance': {
                    'storm_detected': storm_detected,
                    'first_detection_time': first_detection_time.isoformat() if first_detection_time else None,
                    'detection_lead_hours': round(detection_lead_hours, 1) if storm_detected else None,
                    'storm_rmse': round(float(storm_rmse), 2) if storm_rmse is not None else None,
                    'storm_mae': round(float(storm_mae), 2) if storm_mae is not None else None,
                    'detection_rate': round(detection_rate * 100, 1),  # Percentage of time during storm that model predicted storm
                    'peak_prediction_accuracy': round(float(peak_pred_accuracy), 2) if peak_pred_accuracy is not None else None
                },
                'predictions': predictions,
                'overall_metrics': backtest_result['metrics'],
                'summary': backtest_result['summary']
            }

        except Exception as e:
            logger.error(f"Error analyzing storm {storm_info['storm_id']}: {e}", exc_info=True)
            return {
                'storm_id': storm_info['storm_id'],
                'storm_info': storm_info,
                'model_performance': {
                    'storm_detected': None,
                    'error': str(e)
                }
            }

    async def get_recent_storm_catalog(
        self,
        session: AsyncSession,
        days_back: int = 365,
        kp_threshold: float = 5.0,
        analyze_performance: bool = True
    ) -> Dict:
        """
        Get catalog of recent storms with optional performance analysis.

        Args:
            session: Database session
            days_back: How many days back to search (default 365)
            kp_threshold: Kp threshold for storm detection (default 5.0 = G1)
            analyze_performance: Whether to run model performance analysis (slower)

        Returns:
            Catalog of storms with metadata and optional performance analysis
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        logger.info(f"Generating storm catalog for last {days_back} days")

        # Detect storms
        storms = await self.detect_storms(
            session, start_date, end_date, kp_threshold
        )

        if not storms:
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days_back
                },
                'storm_count': 0,
                'storms': []
            }

        # Optionally analyze performance for each storm
        if analyze_performance:
            analyzed_storms = []
            for storm in storms:
                logger.info(f"Analyzing storm: {storm['storm_id']}")
                analysis = await self.analyze_storm_performance(session, storm)
                analyzed_storms.append(analysis)

            storms_data = analyzed_storms
        else:
            storms_data = [{'storm_info': storm, 'model_performance': None} for storm in storms]

        # Calculate aggregate statistics
        severity_counts = {}
        for storm in storms:
            g_scale = storm['g_scale']
            severity_counts[g_scale] = severity_counts.get(g_scale, 0) + 1

        total_storm_hours = sum(s['duration_hours'] for s in storms)
        avg_duration = total_storm_hours / len(storms) if storms else 0

        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days_back
            },
            'storm_count': len(storms),
            'severity_distribution': severity_counts,
            'statistics': {
                'total_storm_hours': total_storm_hours,
                'avg_storm_duration_hours': round(avg_duration, 1),
                'strongest_storm': max(storms, key=lambda s: s['peak_kp']),
                'longest_storm': max(storms, key=lambda s: s['duration_hours'])
            },
            'storms': storms_data,
            'model_version': self.model_version
        }
