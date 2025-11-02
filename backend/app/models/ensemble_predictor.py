"""
Ensemble Ionospheric Storm Predictor

Combines climatology baseline with V2.1 neural network model to leverage
the strengths of both approaches:

- Climatology: Captures regular seasonal/diurnal patterns reliably
- V2.1 Model: Captures storm dynamics and non-linear effects

Default weighting: 70% climatology + 30% V2.1 model
Based on validation showing climatology's strong baseline performance.
"""
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from app.models.storm_predictor_v2 import EnhancedStormPredictor
from app.db.database import AsyncSessionLocal, init_db
from app.db.repository import HistoricalDataRepository

logger = logging.getLogger(__name__)


class EnsembleStormPredictor:
    """
    Ensemble predictor combining climatology and neural network forecasts.
    """

    def __init__(
        self,
        model_path: Optional[str] = "models/v2/best_model.keras",
        climatology_weight: float = 0.7,
        model_weight: float = 0.3
    ):
        """
        Initialize ensemble predictor.

        Args:
            model_path: Path to trained V2.1 model
            climatology_weight: Weight for climatology forecast (default 0.7)
            model_weight: Weight for V2.1 model forecast (default 0.3)
        """
        # Validate weights
        if not np.isclose(climatology_weight + model_weight, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {climatology_weight + model_weight}")

        self.climatology_weight = climatology_weight
        self.model_weight = model_weight

        # Initialize V2.1 model
        self.v2_predictor = EnhancedStormPredictor()
        if model_path:
            try:
                self.v2_predictor.load_model(model_path)
                logger.info(f"Loaded V2.1 model from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load model from {model_path}: {e}")
                logger.warning("V2.1 predictions will be unavailable, using climatology only")

        # Climatology table: (day_of_year, kp_bin) -> avg_tec
        self.climatology_table = {}
        self.climatology_loaded = False

    async def load_climatology(self, train_years: Optional[List[int]] = None):
        """
        Build climatology table from historical data.

        Args:
            train_years: Years to use for climatology (default: 2015-2022)
        """
        if train_years is None:
            train_years = list(range(2015, 2023))  # 2015-2022

        logger.info(f"Building climatology from years {min(train_years)}-{max(train_years)}...")

        await init_db()
        async with AsyncSessionLocal() as session:
            start_date = datetime(min(train_years), 1, 1)
            end_date = datetime(max(train_years), 12, 31)

            measurements = await HistoricalDataRepository.get_measurements_by_time_range(
                session, start_date, end_date
            )

            # Bin by day-of-year and Kp level
            bins = defaultdict(list)
            for m in measurements:
                doy = m.timestamp.timetuple().tm_yday  # Day of year (1-365)
                kp_bin = int(m.kp_index)  # Bin Kp to integer (0-9)
                bins[(doy, kp_bin)].append(m.tec_mean)

            # Calculate averages
            for key, values in bins.items():
                self.climatology_table[key] = np.mean(values)

            # Fill missing bins with global average
            global_avg = np.mean([m.tec_mean for m in measurements])
            for doy in range(1, 366):
                for kp_bin in range(10):
                    if (doy, kp_bin) not in self.climatology_table:
                        self.climatology_table[(doy, kp_bin)] = global_avg

            self.climatology_loaded = True
            logger.info(f"Climatology table built: {len(self.climatology_table)} bins, "
                       f"global avg: {global_avg:.2f} TECU")

    def get_climatology_forecast(self, timestamp: datetime, kp_index: float) -> float:
        """
        Get climatology forecast for given conditions.

        Args:
            timestamp: Forecast timestamp
            kp_index: Current Kp index

        Returns:
            TEC forecast in TECU
        """
        if not self.climatology_loaded:
            logger.warning("Climatology not loaded, returning default value")
            return 15.0  # Default mid-range value

        doy = timestamp.timetuple().tm_yday
        kp_bin = int(kp_index)

        return self.climatology_table.get(
            (doy, kp_bin),
            np.mean(list(self.climatology_table.values()))
        )

    async def predict_storm(self, historical_data: List[Dict]) -> Dict:
        """
        Generate ensemble storm prediction.

        Args:
            historical_data: List of data dictionaries for the past 24+ hours

        Returns:
            Enhanced prediction dictionary with ensemble TEC forecast
        """
        # Get V2.1 model prediction
        try:
            v2_prediction = await self.v2_predictor.predict_storm(historical_data)
            v2_available = True
        except Exception as e:
            logger.warning(f"V2.1 prediction failed: {e}, using climatology only")
            v2_available = False
            v2_prediction = {}

        # Extract current conditions from latest data point
        latest_data = historical_data[-1]
        current_kp = latest_data.get('kp_index', 3.0)
        current_timestamp = datetime.fromisoformat(latest_data['timestamp'])

        # Generate forecast timestamps (24 hours ahead)
        forecast_times = [current_timestamp + timedelta(hours=h) for h in range(1, 25)]

        # Get climatology forecasts for each hour
        climatology_forecasts = []
        for forecast_time in forecast_times:
            clim_forecast = self.get_climatology_forecast(forecast_time, current_kp)
            climatology_forecasts.append(clim_forecast)

        # Combine forecasts
        if v2_available:
            v2_tec_forecast = v2_prediction.get('tec_forecast_24h', climatology_forecasts)

            # Ensemble weighted average
            ensemble_forecast = []
            for clim, v2 in zip(climatology_forecasts, v2_tec_forecast):
                ensemble = self.climatology_weight * clim + self.model_weight * v2
                ensemble_forecast.append(round(ensemble, 2))

            # Calculate ensemble metrics
            ensemble_mean = np.mean(ensemble_forecast)
            ensemble_std = np.std(ensemble_forecast)
            ensemble_min = np.min(ensemble_forecast)
            ensemble_max = np.max(ensemble_forecast)

            # Use V2.1 storm probabilities (ensemble doesn't change these)
            result = v2_prediction.copy()
            result['tec_forecast_24h'] = ensemble_forecast
            result['ensemble_method'] = f'Climatology ({self.climatology_weight:.0%}) + V2.1 Model ({self.model_weight:.0%})'
            result['climatology_forecast'] = [round(c, 2) for c in climatology_forecasts]
            result['v2_forecast'] = [round(v, 2) for v in v2_tec_forecast]
            result['ensemble_stats'] = {
                'mean': round(ensemble_mean, 2),
                'std': round(ensemble_std, 2),
                'min': round(ensemble_min, 2),
                'max': round(ensemble_max, 2)
            }

        else:
            # Fallback to climatology only
            result = {
                'timestamp': datetime.utcnow().isoformat(),
                'storm_probability_24h': 0.0,  # Climatology doesn't predict storms
                'storm_probability_48h': 0.0,
                'hourly_probabilities': [0.0] * 24,
                'tec_forecast_24h': [round(c, 2) for c in climatology_forecasts],
                'uncertainty_24h': 0.5,
                'uncertainty_48h': 0.6,
                'risk_level_24h': 'low',
                'risk_level_48h': 'low',
                'max_probability': 0.0,
                'average_probability': 0.0,
                'confidence_24h': 0.5,
                'confidence_48h': 0.4,
                'model_version': 'Climatology-Only (V2.1 unavailable)',
                'ensemble_method': 'Climatology (100%)',
                'climatology_forecast': [round(c, 2) for c in climatology_forecasts]
            }

        return result

    async def predict_with_components(self, historical_data: List[Dict]) -> Dict:
        """
        Generate prediction with all component forecasts exposed.

        Returns separate climatology, V2.1, and ensemble forecasts for analysis.

        Args:
            historical_data: List of data dictionaries for the past 24+ hours

        Returns:
            Dictionary with separate forecasts and metadata
        """
        # Get ensemble prediction (includes all components)
        ensemble_result = await self.predict_storm(historical_data)

        # Add metadata about weighting
        ensemble_result['weights'] = {
            'climatology': self.climatology_weight,
            'v2_model': self.model_weight
        }

        return ensemble_result
