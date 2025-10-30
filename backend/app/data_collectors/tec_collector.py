"""
Total Electron Content (TEC) Data Collector
Collects TEC data from multiple sources for ionospheric monitoring
"""
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class TECCollector:
    """Collector for Total Electron Content data"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        # NOAA USTEC/GloTEC endpoint
        self.glotec_base = "https://www.ngdc.noaa.gov/stp/iono/ustec"

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_realtime_tec_estimate(self) -> Dict:
        """
        Generate synthetic real-time TEC data based on empirical models
        In production, this would fetch from actual TEC sources

        Returns: Dictionary with TEC values on a global grid
        """
        try:
            # Create a synthetic global TEC map (2.5° x 5° grid)
            # Latitude: -87.5 to 87.5 (71 points)
            # Longitude: -180 to 175 (72 points)

            lats = np.arange(-87.5, 88, 2.5)
            lons = np.arange(-180, 176, 5)

            # Generate realistic TEC distribution
            # Higher TEC at equator, lower at poles
            # Add some noise for variability
            tec_grid = []

            # Get current hour for diurnal variation
            current_hour = datetime.utcnow().hour

            for lat in lats:
                tec_row = []
                for lon in lons:
                    # Base TEC depends on latitude
                    base_tec = self._calculate_base_tec(lat, lon, current_hour)

                    # Add some random variation
                    noise = np.random.normal(0, 2)
                    tec_value = max(0, base_tec + noise)

                    tec_row.append(round(tec_value, 2))
                tec_grid.append(tec_row)

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "latitudes": lats.tolist(),
                "longitudes": lons.tolist(),
                "tec_values": tec_grid,
                "units": "TECU",
                "source": "empirical_model"
            }
        except Exception as e:
            logger.error(f"Error generating TEC estimate: {e}")
            return {}

    def _calculate_base_tec(self, lat: float, lon: float, hour: int) -> float:
        """
        Calculate base TEC value using simplified empirical model
        """
        # Latitudinal dependence - peak at equator
        lat_factor = np.cos(np.radians(lat * 1.5))

        # Longitudinal/time dependence - peak around 14:00 LT
        local_hour = (hour + lon / 15) % 24
        time_factor = 1 + 0.5 * np.cos(np.radians((local_hour - 14) * 15))

        # Base TEC (typical range 5-50 TECU)
        base_tec = 15 + 25 * lat_factor * time_factor

        return base_tec

    async def get_tec_statistics(self, tec_data: Dict) -> Dict:
        """
        Calculate statistics from TEC data
        """
        try:
            if not tec_data or "tec_values" not in tec_data:
                return {}

            tec_array = np.array(tec_data["tec_values"])

            return {
                "mean": float(np.mean(tec_array)),
                "median": float(np.median(tec_array)),
                "std": float(np.std(tec_array)),
                "min": float(np.min(tec_array)),
                "max": float(np.max(tec_array)),
                "percentile_95": float(np.percentile(tec_array, 95))
            }
        except Exception as e:
            logger.error(f"Error calculating TEC statistics: {e}")
            return {}

    async def calculate_roti(self, tec_timeseries: List[float], sampling_interval: int = 30) -> float:
        """
        Calculate Rate of TEC Index (ROTI) for scintillation monitoring

        Args:
            tec_timeseries: List of TEC values over time
            sampling_interval: Sampling interval in seconds

        Returns: ROTI value
        """
        try:
            if len(tec_timeseries) < 2:
                return 0.0

            # Calculate ROT (Rate of TEC change)
            rot_values = []
            for i in range(1, len(tec_timeseries)):
                rot = (tec_timeseries[i] - tec_timeseries[i-1]) / sampling_interval
                rot_values.append(rot)

            # ROTI is the standard deviation of ROT
            roti = float(np.std(rot_values)) if rot_values else 0.0

            return roti
        except Exception as e:
            logger.error(f"Error calculating ROTI: {e}")
            return 0.0

    async def detect_anomalies(self, current_tec: Dict, historical_mean: float,
                              historical_std: float) -> Dict:
        """
        Detect TEC anomalies that might indicate ionospheric disturbances

        Args:
            current_tec: Current TEC data
            historical_mean: Historical mean TEC
            historical_std: Historical standard deviation

        Returns: Anomaly detection results
        """
        try:
            stats = await self.get_tec_statistics(current_tec)

            if not stats:
                return {"anomaly_detected": False}

            current_mean = stats["mean"]

            # Calculate deviation from historical norm (in standard deviations)
            deviation = abs(current_mean - historical_mean) / historical_std

            # Threshold for anomaly: > 2 standard deviations
            anomaly_detected = deviation > 2.0

            return {
                "anomaly_detected": anomaly_detected,
                "deviation_sigma": round(deviation, 2),
                "current_mean_tec": round(current_mean, 2),
                "historical_mean_tec": round(historical_mean, 2),
                "severity": self._classify_anomaly_severity(deviation)
            }
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {"anomaly_detected": False}

    def _classify_anomaly_severity(self, deviation: float) -> str:
        """Classify anomaly severity based on deviation"""
        if deviation < 2.0:
            return "normal"
        elif deviation < 3.0:
            return "minor"
        elif deviation < 4.0:
            return "moderate"
        else:
            return "severe"

    async def get_regional_tec(self, tec_data: Dict, lat_range: tuple,
                              lon_range: tuple) -> Optional[np.ndarray]:
        """
        Extract TEC data for a specific geographic region

        Args:
            tec_data: Global TEC data
            lat_range: (min_lat, max_lat)
            lon_range: (min_lon, max_lon)

        Returns: Regional TEC array
        """
        try:
            if not tec_data or "tec_values" not in tec_data:
                return None

            lats = np.array(tec_data["latitudes"])
            lons = np.array(tec_data["longitudes"])
            tec_values = np.array(tec_data["tec_values"])

            # Find indices within range
            lat_mask = (lats >= lat_range[0]) & (lats <= lat_range[1])
            lon_mask = (lons >= lon_range[0]) & (lons <= lon_range[1])

            # Extract regional data
            regional_tec = tec_values[lat_mask][:, lon_mask]

            return regional_tec
        except Exception as e:
            logger.error(f"Error extracting regional TEC: {e}")
            return None
