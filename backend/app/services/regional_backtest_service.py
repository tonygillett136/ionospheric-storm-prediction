"""
Regional Backtesting Service

Compares different regional prediction approaches using historical data
to scientifically determine which method provides superior accuracy.

Approaches tested:
- Approach A: Climatology-primary with regional factors
- Approach B: V2.1 ML-enhanced with regional adjustments
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repository import HistoricalDataRepository
from app.services.geographic_climatology_service import GeographicClimatologyService, GeographicRegion
from app.models.storm_predictor_v2 import EnhancedStormPredictor
import logging

logger = logging.getLogger(__name__)


class RegionalBacktestService:
    """Service for comparing regional prediction approaches"""

    def __init__(
        self,
        geographic_climatology: GeographicClimatologyService,
        model_path: str = "models/v2/best_model.keras"
    ):
        """
        Initialize backtesting service.

        Args:
            geographic_climatology: Geographic climatology service
            model_path: Path to V2.1 model
        """
        self.geographic_climatology = geographic_climatology
        self.model_path = model_path
        self.v2_model = None  # Lazy loaded

    def _ensure_model_loaded(self):
        """Load V2.1 model if not already loaded"""
        if self.v2_model is None:
            logger.info("Loading V2.1 model for backtesting...")
            self.v2_model = EnhancedStormPredictor(self.model_path)
            logger.info("V2.1 model loaded")

    def _approach_a_climatology_primary(
        self,
        region_code: str,
        target_date: datetime,
        kp: float,
        region: Dict
    ) -> float:
        """
        Approach A: Climatology-primary with regional factors.

        Uses regional climatology as baseline, applies physics-based adjustments.
        """
        # Get regional climatology forecast
        clim_forecast = self.geographic_climatology.get_climatology_forecast(
            region_code,
            target_date,
            kp
        )

        if clim_forecast is None:
            # Fallback to global average with regional factor
            clim_forecast = 12.74 * region['baseline_factor']

        return clim_forecast

    def _approach_b_v21_enhanced(
        self,
        region_code: str,
        target_date: datetime,
        kp: float,
        region: Dict,
        historical_sequence: List[Dict]
    ) -> float:
        """
        Approach B: V2.1 ML-enhanced with regional adjustments.

        Runs V2.1 model for storm dynamics, applies regional physics adjustments,
        blends with regional climatology.
        """
        self._ensure_model_loaded()

        # Get V2.1 global prediction
        try:
            # V2.1 requires 24-hour sequence
            if len(historical_sequence) < 24:
                # Not enough data, fall back to climatology
                return self._approach_a_climatology_primary(region_code, target_date, kp, region)

            # Prepare feature sequence for model
            feature_sequence = []
            for i, data_point in enumerate(historical_sequence[-24:]):
                # Get previous point for rate-of-change features
                prev = historical_sequence[-24 + i - 1] if i > 0 else None
                features = self.v2_model.prepare_enhanced_features(data_point, prev)
                normalized = self.v2_model.normalize_features(features)
                feature_sequence.append(normalized)

            # Convert to model input shape: (1, 24, 24)
            import numpy as np
            X = np.array(feature_sequence, dtype=np.float32).reshape(1, 24, 24)

            # Get V2.1 prediction using the model directly
            predictions = self.v2_model.model.predict(X, verbose=0)

            # Extract TEC forecast (first hour of 24-hour forecast)
            tec_forecast = predictions['tec_forecast'][0]  # Array of 24 values
            global_tec = float(tec_forecast[0] * 100.0)  # Denormalize (model outputs normalized TEC)

        except Exception as e:
            logger.warning(f"V2.1 prediction failed: {e}, using climatology")
            global_tec = 12.74

        # Apply regional adjustments to V2.1 output
        baseline_factor = region['baseline_factor']
        variability_factor = region['variability_factor']

        regional_tec_ml = global_tec * baseline_factor

        # During storms (Kp > 5), apply enhanced regional variability
        if kp > 5:
            global_avg = 12.74
            storm_excess = (global_tec - global_avg) * variability_factor
            regional_tec_ml = (global_avg * baseline_factor) + storm_excess

        # Get regional climatology for blending
        clim_forecast = self.geographic_climatology.get_climatology_forecast(
            region_code,
            target_date,
            kp
        )

        if clim_forecast is None:
            # No climatology, use pure ML
            return max(0, regional_tec_ml)

        # Blend ML and climatology
        # During storms: Trust ML more (60% ML, 40% climatology)
        # During quiet: Trust climatology more (30% ML, 70% climatology)
        ml_weight = 0.3 + min(0.3, kp / 10.0)  # 30-60%
        clim_weight = 1.0 - ml_weight

        blended_tec = (regional_tec_ml * ml_weight) + (clim_forecast * clim_weight)

        return max(0, blended_tec)

    async def run_regional_backtest(
        self,
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        sample_interval_hours: int = 6
    ) -> Dict:
        """
        Run backtest comparing both approaches across all regions.

        Args:
            session: Database session
            start_date: Start of test period
            end_date: End of test period
            sample_interval_hours: Hours between test points

        Returns:
            Comparison results with metrics for each approach and region
        """
        logger.info(f"Running regional backtest from {start_date} to {end_date}")

        # Get all historical data for test period
        # Need extra data before start for V2.1's 24-hour requirement
        data_start = start_date - timedelta(hours=48)
        measurements = await HistoricalDataRepository.get_measurements_by_time_range(
            session, data_start, end_date
        )

        if not measurements:
            logger.error("No measurements found for backtest period")
            return {}

        logger.info(f"Retrieved {len(measurements)} measurements for backtest")

        # Initialize results storage
        results = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'total_hours': (end_date - start_date).total_seconds() / 3600
            },
            'approaches': {
                'climatology_primary': {},
                'v21_enhanced': {}
            },
            'comparison': {}
        }

        # Test each region
        for region in GeographicRegion.get_all_regions():
            region_code = region['code']
            logger.info(f"Backtesting region: {region['name']}")

            # Storage for this region's results
            approach_a_errors = []
            approach_b_errors = []
            approach_a_predictions = []
            approach_b_predictions = []
            actual_values = []
            timestamps = []

            # Create measurement index for quick lookup
            measurement_dict = {m.timestamp: m for m in measurements}

            # Sample points for testing
            current_time = start_date
            while current_time <= end_date:
                # Get actual TEC at this time
                actual_measurement = measurement_dict.get(current_time)

                if actual_measurement and actual_measurement.tec_mean < 999.0:
                    actual_tec = actual_measurement.tec_mean
                    kp = min(9.0, max(0, actual_measurement.kp_index))

                    # Build historical sequence for V2.1 (24 hours before current time)
                    hist_sequence = []
                    for h in range(24, 0, -1):
                        hist_time = current_time - timedelta(hours=h)
                        hist_m = measurement_dict.get(hist_time)
                        if hist_m:
                            hist_sequence.append({
                                'timestamp': hist_time,
                                'tec_mean': hist_m.tec_mean if hist_m.tec_mean < 999.0 else 12.74,
                                'kp_index': min(9.0, max(0, hist_m.kp_index)),
                                'dst_index': hist_m.dst_index,
                                'solar_wind_speed': hist_m.solar_wind_speed if hist_m.solar_wind_speed < 9999.0 else 400.0,
                                'f107_flux': 100.0  # Simplified
                            })

                    # Only test if we have enough history
                    if len(hist_sequence) >= 24:
                        # Approach A: Climatology-primary
                        pred_a = self._approach_a_climatology_primary(
                            region_code,
                            current_time,
                            kp,
                            region
                        )

                        # Approach B: V2.1-enhanced
                        pred_b = self._approach_b_v21_enhanced(
                            region_code,
                            current_time,
                            kp,
                            region,
                            hist_sequence
                        )

                        # Calculate errors
                        error_a = abs(pred_a - actual_tec)
                        error_b = abs(pred_b - actual_tec)

                        approach_a_errors.append(error_a)
                        approach_b_errors.append(error_b)
                        approach_a_predictions.append(pred_a)
                        approach_b_predictions.append(pred_b)
                        actual_values.append(actual_tec)
                        timestamps.append(current_time.isoformat())

                current_time += timedelta(hours=sample_interval_hours)

            # Calculate metrics for this region
            if approach_a_errors:
                # Approach A metrics
                results['approaches']['climatology_primary'][region_code] = {
                    'region': region['name'],
                    'sample_count': len(approach_a_errors),
                    'mae': round(float(np.mean(approach_a_errors)), 3),
                    'rmse': round(float(np.sqrt(np.mean([e**2 for e in approach_a_errors]))), 3),
                    'median_error': round(float(np.median(approach_a_errors)), 3),
                    'max_error': round(float(np.max(approach_a_errors)), 3),
                    'predictions': approach_a_predictions[:10]  # Sample
                }

                # Approach B metrics
                results['approaches']['v21_enhanced'][region_code] = {
                    'region': region['name'],
                    'sample_count': len(approach_b_errors),
                    'mae': round(float(np.mean(approach_b_errors)), 3),
                    'rmse': round(float(np.sqrt(np.mean([e**2 for e in approach_b_errors]))), 3),
                    'median_error': round(float(np.median(approach_b_errors)), 3),
                    'max_error': round(float(np.max(approach_b_errors)), 3),
                    'predictions': approach_b_predictions[:10]  # Sample
                }

                # Direct comparison
                mae_diff = results['approaches']['climatology_primary'][region_code]['mae'] - \
                          results['approaches']['v21_enhanced'][region_code]['mae']

                rmse_diff = results['approaches']['climatology_primary'][region_code]['rmse'] - \
                           results['approaches']['v21_enhanced'][region_code]['rmse']

                # Positive means V2.1 is better, negative means climatology is better
                results['comparison'][region_code] = {
                    'region': region['name'],
                    'mae_improvement': round(float(mae_diff), 3),  # Positive = V2.1 better
                    'rmse_improvement': round(float(rmse_diff), 3),  # Positive = V2.1 better
                    'winner': 'V2.1-Enhanced' if (mae_diff + rmse_diff) > 0 else 'Climatology-Primary',
                    'confidence': 'High' if abs(mae_diff + rmse_diff) > 1.0 else 'Moderate' if abs(mae_diff + rmse_diff) > 0.3 else 'Low'
                }

        # Overall winner
        total_improvement = sum(
            results['comparison'][code]['mae_improvement'] + results['comparison'][code]['rmse_improvement']
            for code in results['comparison']
        )

        results['overall_winner'] = {
            'approach': 'V2.1-Enhanced' if total_improvement > 0 else 'Climatology-Primary',
            'total_improvement': round(float(total_improvement), 3),
            'recommendation': self._generate_recommendation(results)
        }

        return results

    def _generate_recommendation(self, results: Dict) -> str:
        """Generate human-readable recommendation based on results"""
        comparison = results.get('comparison', {})

        v21_wins = sum(1 for c in comparison.values() if c['winner'] == 'V2.1-Enhanced')
        clim_wins = sum(1 for c in comparison.values() if c['winner'] == 'Climatology-Primary')

        if v21_wins > clim_wins:
            return f"V2.1-Enhanced approach wins in {v21_wins}/{len(comparison)} regions. Recommended for production."
        elif clim_wins > v21_wins:
            return f"Climatology-Primary approach wins in {clim_wins}/{len(comparison)} regions. Recommended for production."
        else:
            return "Approaches perform similarly. Consider hybrid approach based on conditions."
