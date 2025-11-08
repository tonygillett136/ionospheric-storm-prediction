"""
Geographic Climatology Service

Builds and provides climatology forecasts for different geographic regions
(latitude bands) to account for the strong latitudinal dependence of TEC.
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repository import HistoricalDataRepository
import logging

logger = logging.getLogger(__name__)


class GeographicRegion:
    """Definition of geographic regions with their TEC characteristics"""

    EQUATORIAL = {
        'name': 'Equatorial',
        'code': 'equatorial',
        'lat_range': (-20, 20),
        'description': 'Equatorial region (±20°) - Highest TEC, equatorial anomaly',
        'baseline_factor': 1.4,  # Relative to global mean
        'variability_factor': 1.3
    }

    MID_LATITUDE = {
        'name': 'Mid-Latitude',
        'code': 'mid_latitude',
        'lat_range': (20, 50),
        'description': 'Mid-latitude region (20-50°) - Moderate TEC, seasonal variation',
        'baseline_factor': 1.0,
        'variability_factor': 1.0
    }

    AURORAL = {
        'name': 'Auroral',
        'code': 'auroral',
        'lat_range': (50, 70),
        'description': 'Auroral region (50-70°) - High variability, storm enhancements',
        'baseline_factor': 0.85,
        'variability_factor': 1.5
    }

    POLAR = {
        'name': 'Polar',
        'code': 'polar',
        'lat_range': (70, 90),
        'description': 'Polar region (>70°) - Lower baseline, extreme storm responses',
        'baseline_factor': 0.7,
        'variability_factor': 1.8
    }

    GLOBAL = {
        'name': 'Global',
        'code': 'global',
        'lat_range': (-90, 90),
        'description': 'Global average across all latitudes',
        'baseline_factor': 1.0,
        'variability_factor': 1.0
    }

    @classmethod
    def get_all_regions(cls) -> List[Dict]:
        """Get all defined regions"""
        return [
            cls.EQUATORIAL,
            cls.MID_LATITUDE,
            cls.AURORAL,
            cls.POLAR,
            cls.GLOBAL
        ]

    @classmethod
    def get_region_by_code(cls, code: str) -> Optional[Dict]:
        """Get region definition by code"""
        for region in cls.get_all_regions():
            if region['code'] == code:
                return region
        return None


class GeographicClimatologyService:
    """Service for building and querying geographic-specific climatology"""

    def __init__(self):
        self.regional_climatologies = {}  # {region_code: {(doy, kp_bin): tec_value}}
        self.global_avg_tec = 12.74  # TECU - baseline from historical data

    async def build_climatology(
        self,
        session: AsyncSession,
        train_years: Optional[List[int]] = None
    ) -> Dict[str, int]:
        """
        Build climatology tables for all geographic regions.

        Args:
            session: Database session
            train_years: Years to use for training (default: 2015-2022)

        Returns:
            Dictionary with bin counts per region
        """
        if train_years is None:
            train_years = list(range(2015, 2023))

        logger.info(f"Building geographic climatology from years {train_years}")

        # Get all historical measurements
        start_date = datetime(min(train_years), 1, 1)
        end_date = datetime(max(train_years), 12, 31, 23, 59, 59)

        measurements = await HistoricalDataRepository.get_measurements_by_time_range(
            session, start_date, end_date
        )

        if not measurements:
            logger.warning("No measurements found for climatology building")
            return {}

        logger.info(f"Processing {len(measurements)} measurements for geographic climatology")

        # Calculate global average for reference
        global_tec_values = [m.tec_mean for m in measurements if m.tec_mean < 999.0]
        self.global_avg_tec = np.mean(global_tec_values) if global_tec_values else 12.74

        # Build climatology for each region
        bin_counts = {}

        for region in GeographicRegion.get_all_regions():
            region_code = region['code']
            logger.info(f"Building climatology for {region['name']} region")

            # Bin measurements by (day_of_year, kp_bin)
            bins = defaultdict(list)

            for m in measurements:
                if m.tec_mean >= 999.0:  # Skip fill values
                    continue

                doy = m.timestamp.timetuple().tm_yday
                kp_bin = int(min(9, max(0, m.kp_index)))

                # Adjust TEC value for this region using regional factors
                regional_tec = self._adjust_tec_for_region(
                    m.tec_mean,
                    m.kp_index,
                    region
                )

                bins[(doy, kp_bin)].append(regional_tec)

            # Calculate average for each bin
            climatology = {}
            for key, values in bins.items():
                if values:
                    climatology[key] = float(np.mean(values))

            self.regional_climatologies[region_code] = climatology
            bin_counts[region_code] = len(climatology)

            logger.info(f"Built {len(climatology)} bins for {region['name']}")

        return bin_counts

    def _adjust_tec_for_region(
        self,
        global_tec: float,
        kp_index: float,
        region: Dict
    ) -> float:
        """
        Adjust global TEC measurement for regional characteristics.

        This uses the scientifically-based latitude factors derived from
        the empirical TEC model's latitudinal dependence.
        """
        baseline_factor = region['baseline_factor']
        variability_factor = region['variability_factor']

        # Base adjustment
        regional_tec = global_tec * baseline_factor

        # During storms (Kp > 5), apply enhanced regional variability
        if kp_index > 5:
            storm_excess = (global_tec - self.global_avg_tec) * variability_factor
            regional_tec = (self.global_avg_tec * baseline_factor) + storm_excess

        return max(0, regional_tec)

    def get_climatology_forecast(
        self,
        region_code: str,
        target_date: datetime,
        kp_scenario: float
    ) -> Optional[float]:
        """
        Get climatology-based forecast for a specific region.

        Args:
            region_code: Geographic region code
            target_date: Target forecast date
            kp_scenario: Expected Kp index

        Returns:
            Forecasted TEC value in TECU, or None if not available
        """
        if region_code not in self.regional_climatologies:
            logger.warning(f"Region {region_code} not found in climatology")
            return None

        climatology = self.regional_climatologies[region_code]

        doy = target_date.timetuple().tm_yday
        kp_bin = int(min(9, max(0, kp_scenario)))

        # Try exact match
        if (doy, kp_bin) in climatology:
            return climatology[(doy, kp_bin)]

        # Fallback: try nearby days and Kp bins
        for doy_offset in [-1, 0, 1]:
            for kp_offset in [-1, 0, 1]:
                adj_doy = ((doy + doy_offset - 1) % 365) + 1
                adj_kp = max(0, min(9, kp_bin + kp_offset))

                if (adj_doy, adj_kp) in climatology:
                    return climatology[(adj_doy, adj_kp)]

        # Last resort: return regional baseline
        region = GeographicRegion.get_region_by_code(region_code)
        return self.global_avg_tec * region['baseline_factor'] if region else None

    def get_multi_region_forecast(
        self,
        target_date: datetime,
        kp_scenario: float,
        num_days: int = 7
    ) -> Dict[str, List[Dict]]:
        """
        Get forecasts for all regions over multiple days.

        Args:
            target_date: Starting forecast date
            kp_scenario: Expected Kp index
            num_days: Number of days to forecast

        Returns:
            Dictionary mapping region codes to forecast timeseries
        """
        forecasts = {}

        for region in GeographicRegion.get_all_regions():
            region_code = region['code']
            timeseries = []

            for day_offset in range(num_days):
                forecast_date = target_date + timedelta(days=day_offset)
                tec_value = self.get_climatology_forecast(
                    region_code,
                    forecast_date,
                    kp_scenario
                )

                if tec_value is not None:
                    timeseries.append({
                        'date': forecast_date.date().isoformat(),
                        'doy': forecast_date.timetuple().tm_yday,
                        'tec': round(tec_value, 2)
                    })

            forecasts[region_code] = timeseries

        return forecasts

    def compare_regions(
        self,
        target_date: datetime,
        kp_scenario: float
    ) -> List[Dict]:
        """
        Compare TEC values across all regions for a specific date and Kp.

        Returns list of region comparisons sorted by TEC value (descending)
        """
        comparisons = []

        for region in GeographicRegion.get_all_regions():
            if region['code'] == 'global':
                continue  # Skip global for comparison

            tec_value = self.get_climatology_forecast(
                region['code'],
                target_date,
                kp_scenario
            )

            if tec_value is not None:
                comparisons.append({
                    'region': region['name'],
                    'code': region['code'],
                    'lat_range': region['lat_range'],
                    'tec': round(tec_value, 2),
                    'description': region['description']
                })

        # Sort by TEC value descending
        comparisons.sort(key=lambda x: x['tec'], reverse=True)

        return comparisons
