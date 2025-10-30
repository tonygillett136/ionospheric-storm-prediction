"""
NOAA Space Weather Prediction Center Data Collector
Collects real-time space weather data including Kp, Dst, solar wind parameters
"""
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class NOAASWPCCollector:
    """Collector for NOAA SWPC data"""

    def __init__(self, base_url: str = "https://services.swpc.noaa.gov"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_planetary_k_index(self) -> List[Dict]:
        """
        Get the Planetary K-index (Kp) data
        Returns: List of Kp index values with timestamps
        """
        try:
            url = f"{self.base_url}/products/noaa-planetary-k-index.json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully retrieved {len(data)} Kp index records")
                    return data
                else:
                    logger.error(f"Failed to retrieve Kp index: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error retrieving Kp index: {e}")
            return []

    async def get_geomagnetic_storms(self) -> List[Dict]:
        """
        Get current geomagnetic storm probabilities
        Returns: Storm probability data
        """
        try:
            url = f"{self.base_url}/products/noaa-geomagnetic-forecast.json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Successfully retrieved geomagnetic storm forecast")
                    return data
                else:
                    logger.error(f"Failed to retrieve storm forecast: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error retrieving storm forecast: {e}")
            return []

    async def get_solar_wind(self) -> List[Dict]:
        """
        Get real-time solar wind data (speed, density, temperature)
        Returns: Solar wind parameters
        """
        try:
            url = f"{self.base_url}/products/solar-wind/plasma-7-day.json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully retrieved {len(data)} solar wind records")
                    return data
                else:
                    logger.error(f"Failed to retrieve solar wind data: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error retrieving solar wind data: {e}")
            return []

    async def get_mag_field(self) -> List[Dict]:
        """
        Get real-time magnetic field data (IMF Bz component)
        Returns: Magnetic field data including Bz component
        """
        try:
            url = f"{self.base_url}/products/solar-wind/mag-7-day.json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully retrieved {len(data)} magnetic field records")
                    return data
                else:
                    logger.error(f"Failed to retrieve magnetic field data: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error retrieving magnetic field data: {e}")
            return []

    async def get_f107_solar_flux(self) -> List[Dict]:
        """
        Get F10.7 cm solar flux data
        Returns: Solar flux measurements
        """
        try:
            url = f"{self.base_url}/products/summary/10cm-flux.json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Successfully retrieved F10.7 solar flux data")
                    return data
                else:
                    logger.error(f"Failed to retrieve solar flux data: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error retrieving solar flux data: {e}")
            return []

    async def get_all_data(self) -> Dict:
        """
        Collect all space weather data in one call
        Returns: Dictionary containing all data types
        """
        try:
            kp_data = await self.get_planetary_k_index()
            storm_data = await self.get_geomagnetic_storms()
            solar_wind = await self.get_solar_wind()
            mag_field = await self.get_mag_field()
            f107_flux = await self.get_f107_solar_flux()

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "kp_index": kp_data,
                "storm_forecast": storm_data,
                "solar_wind": solar_wind,
                "magnetic_field": mag_field,
                "f107_flux": f107_flux
            }
        except Exception as e:
            logger.error(f"Error collecting all NOAA data: {e}")
            return {}

    def parse_latest_kp(self, kp_data: List[Dict]) -> Optional[float]:
        """
        Parse the latest Kp value from the dataset
        """
        if not kp_data or len(kp_data) < 2:
            return None
        try:
            # Skip header row and get the most recent value
            latest = kp_data[-1]
            if isinstance(latest, list) and len(latest) > 1:
                return float(latest[1])
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"Error parsing Kp value: {e}")
        return None

    def parse_solar_wind_params(self, solar_wind: List[Dict]) -> Optional[Dict]:
        """
        Parse the latest solar wind parameters
        """
        if not solar_wind or len(solar_wind) < 2:
            return None
        try:
            latest = solar_wind[-1]
            if isinstance(latest, list) and len(latest) >= 4:
                return {
                    "timestamp": latest[0],
                    "density": float(latest[1]) if latest[1] else None,
                    "speed": float(latest[2]) if latest[2] else None,
                    "temperature": float(latest[3]) if latest[3] else None
                }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"Error parsing solar wind parameters: {e}")
        return None

    def parse_mag_field_bz(self, mag_data: List[Dict]) -> Optional[float]:
        """
        Parse the Bz component of the magnetic field
        """
        if not mag_data or len(mag_data) < 2:
            return None
        try:
            latest = mag_data[-1]
            if isinstance(latest, list) and len(latest) >= 4:
                # Bz is typically the 4th column
                return float(latest[3]) if latest[3] else None
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"Error parsing Bz value: {e}")
        return None
