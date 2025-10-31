"""
Data Service - Orchestrates data collection and storage
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque

from app.data_collectors.noaa_swpc_collector import NOAASWPCCollector
from app.data_collectors.tec_collector import TECCollector
from app.models.storm_predictor_v2 import EnhancedStormPredictor
from app.db.database import get_db
from app.db.repository import HistoricalDataRepository
from pathlib import Path

logger = logging.getLogger(__name__)


class DataService:
    """
    Service to manage data collection, processing, and predictions
    """

    def __init__(self, max_history_size: int = 168):  # 7 days of hourly data
        self.noaa_collector = None
        self.tec_collector = None

        # Use V2 model if available, otherwise fall back to V1
        v2_model_path = Path('models/v2/best_model.keras')
        if v2_model_path.exists():
            logger.info("Loading Enhanced Model V2 for production use")
            self.predictor = EnhancedStormPredictor(model_path=str(v2_model_path))
            self.model_version = 'v2'
        else:
            logger.warning("V2 model not found, using V1 baseline model")
            from app.models.storm_predictor import StormPredictor
            self.predictor = StormPredictor()
            self.model_version = 'v1'

        # Store historical data in memory (deque for efficient append/pop)
        self.historical_data = deque(maxlen=max_history_size)

        # Latest data cache
        self.latest_data: Optional[Dict] = None
        self.latest_prediction: Optional[Dict] = None

        # Update tracking
        self.last_data_update: Optional[datetime] = None
        self.last_prediction_update: Optional[datetime] = None

    async def initialize(self):
        """Initialize data collectors and load historical data"""
        self.noaa_collector = NOAASWPCCollector()
        await self.noaa_collector.__aenter__()

        self.tec_collector = TECCollector()
        await self.tec_collector.__aenter__()

        # Load historical data from database
        await self._load_historical_data_from_db()

        logger.info("Data service initialized")

    async def shutdown(self):
        """Cleanup resources"""
        if self.noaa_collector:
            await self.noaa_collector.__aexit__(None, None, None)
        if self.tec_collector:
            await self.tec_collector.__aexit__(None, None, None)

        logger.info("Data service shutdown")

    async def _load_historical_data_from_db(self):
        """Load historical data from database to initialize prediction context"""
        try:
            # Get database session
            async for session in get_db():
                # Load most recent 24 measurements from database
                # (Use latest_measurements instead of time range to handle gaps in data)
                measurements = await HistoricalDataRepository.get_latest_measurements(
                    session, limit=24
                )

                # Reverse to get chronological order (oldest to newest)
                measurements = list(reversed(measurements))

                # Convert database records to predictor format
                for measurement in measurements:
                    data_point = {
                        'timestamp': measurement.timestamp.isoformat(),
                        'tec_statistics': {
                            'mean': measurement.tec_mean,
                            'std': measurement.tec_std,
                            'max': measurement.tec_max,
                            'min': measurement.tec_min
                        },
                        'kp_index': measurement.kp_index,
                        'dst_index': measurement.dst_index,
                        'solar_wind_params': {
                            'speed': measurement.solar_wind_speed,
                            'density': measurement.solar_wind_density,
                            'temperature': measurement.solar_wind_temperature
                        },
                        'imf_bz': measurement.imf_bz,
                        'f107_flux': measurement.f107_flux
                    }
                    self.historical_data.append(data_point)

                logger.info(f"Loaded {len(measurements)} historical data points from database")
                break  # Exit after first iteration
        except Exception as e:
            logger.warning(f"Could not load historical data from database: {e}")
            logger.info("Starting with empty historical data - will accumulate over time")

    async def collect_all_data(self) -> Dict:
        """
        Collect all available data from various sources
        """
        try:
            # Collect NOAA space weather data
            noaa_data = await self.noaa_collector.get_all_data()

            # Collect TEC data
            tec_data = await self.tec_collector.get_realtime_tec_estimate()
            tec_stats = await self.tec_collector.get_tec_statistics(tec_data)

            # Parse key parameters
            kp_index = self.noaa_collector.parse_latest_kp(noaa_data.get('kp_index', []))
            solar_wind_params = self.noaa_collector.parse_solar_wind_params(
                noaa_data.get('solar_wind', [])
            )
            imf_bz = self.noaa_collector.parse_mag_field_bz(noaa_data.get('magnetic_field', []))

            # Combine all data
            combined_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "tec_data": tec_data,
                "tec_statistics": tec_stats,
                "kp_index": kp_index or 0,
                "solar_wind_params": solar_wind_params or {},
                "imf_bz": imf_bz or 0,
                "f107_flux": 100,  # Placeholder - would parse from NOAA data
                "raw_noaa_data": noaa_data
            }

            # Store in historical data
            self.historical_data.append(combined_data)
            self.latest_data = combined_data
            self.last_data_update = datetime.utcnow()

            logger.info("Successfully collected all data")
            return combined_data

        except Exception as e:
            logger.error(f"Error collecting data: {e}")
            return {}

    async def update_prediction(self) -> Dict:
        """
        Generate new storm prediction using collected data
        """
        try:
            if len(self.historical_data) == 0:
                logger.warning("No historical data available for prediction")
                return {}

            # Convert deque to list for prediction
            historical_list = list(self.historical_data)

            # Generate prediction
            prediction = await self.predictor.predict_storm(historical_list)

            self.latest_prediction = prediction
            self.last_prediction_update = datetime.utcnow()

            logger.info(f"Updated prediction - Risk level: {prediction.get('risk_level')}")
            return prediction

        except Exception as e:
            logger.error(f"Error updating prediction: {e}")
            return {}

    async def get_current_status(self) -> Dict:
        """
        Get current system status with latest data and predictions
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "latest_data": self.latest_data,
            "latest_prediction": self.latest_prediction,
            "last_data_update": self.last_data_update.isoformat() if self.last_data_update else None,
            "last_prediction_update": self.last_prediction_update.isoformat() if self.last_prediction_update else None,
            "historical_data_points": len(self.historical_data)
        }

    async def get_historical_trends(self, hours: int = 24) -> Dict:
        """
        Get historical trends for the specified time period
        """
        try:
            historical_list = list(self.historical_data)

            # Filter to requested time range
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            filtered_data = [
                d for d in historical_list
                if datetime.fromisoformat(d['timestamp']) > cutoff_time
            ]

            # Extract time series
            timestamps = [d['timestamp'] for d in filtered_data]
            kp_values = [d.get('kp_index', 0) for d in filtered_data]
            tec_means = [d.get('tec_statistics', {}).get('mean', 0) for d in filtered_data]

            solar_wind_speeds = [
                d.get('solar_wind_params', {}).get('speed', 0)
                for d in filtered_data
            ]

            return {
                "timestamps": timestamps,
                "kp_index": kp_values,
                "tec_mean": tec_means,
                "solar_wind_speed": solar_wind_speeds,
                "data_points": len(filtered_data)
            }

        except Exception as e:
            logger.error(f"Error getting historical trends: {e}")
            return {}

    async def start_periodic_updates(self, data_interval: int = 300,
                                     prediction_interval: int = 3600):
        """
        Start periodic data collection and prediction updates

        Args:
            data_interval: Data collection interval in seconds (default 5 min)
            prediction_interval: Prediction update interval in seconds (default 1 hour)
        """
        async def data_update_loop():
            while True:
                try:
                    await self.collect_all_data()
                    await asyncio.sleep(data_interval)
                except Exception as e:
                    logger.error(f"Error in data update loop: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute on error

        async def prediction_update_loop():
            while True:
                try:
                    await self.update_prediction()
                    await asyncio.sleep(prediction_interval)
                except Exception as e:
                    logger.error(f"Error in prediction update loop: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes on error

        # Run both loops concurrently
        await asyncio.gather(
            data_update_loop(),
            prediction_update_loop()
        )
