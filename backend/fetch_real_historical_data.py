"""
Fetch Real Historical Ionospheric Data
======================================

Downloads 10 years of REAL observational data from:
- NASA OMNI: Solar wind, IMF, Dst, Kp indices
- NOAA SWPC: F10.7 solar flux
- TEC estimates derived from space weather conditions

This replaces the synthetic data generator with actual measurements.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys
import numpy as np
from typing import Dict, List, Optional
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.db.database import AsyncSessionLocal, init_db
from app.db.repository import HistoricalDataRepository
from app.db.models import HistoricalMeasurement

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NASAOMNIFetcher:
    """
    Fetches real space weather data from NASA OMNI database
    OMNI provides 1-hour resolution data merged from multiple spacecraft
    """

    BASE_URL = "https://omniweb.gsfc.nasa.gov/cgi/nx1.cgi"

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_omni_data(self, start_date: datetime, end_date: datetime) -> str:
        """
        Fetch OMNI data for a date range
        Returns ASCII text data
        """
        params = {
            'activity': 'retrieve',
            'res': 'hour',  # Hourly resolution
            'spacecraft': 'omni2',
            'start_date': start_date.strftime('%Y%m%d'),
            'end_date': end_date.strftime('%Y%m%d'),
            'vars': [
                '1',   # Bartels rotation number (skip)
                '2',   # ID for IMF spacecraft
                '3',   # ID for SW plasma spacecraft
                '4',   # # of points in IMF averages
                '5',   # # of points in plasma averages
                '6',   # Percent interp
                '7',   # Timeshift
                '8',   # RMS timeshift
                '9',   # RMS phase front normal
                '10',  # Time btwn observations
                '11',  # Field magnitude average
                '12',  # Bx GSE
                '13',  # By GSE
                '14',  # Bz GSE
                '15',  # By GSM
                '16',  # Bz GSM
                '17',  # RMS SD B scalar
                '18',  # RMS SD field vector
                '19',  # Flow speed
                '20',  # Vx velocity
                '21',  # Vy velocity
                '22',  # Vz velocity
                '23',  # Proton density
                '24',  # Temperature
                '25',  # Flow pressure
                '26',  # Electric field
                '27',  # Plasma beta
                '28',  # Alfven mach number
                '29',  # X(s/c), GSE
                '30',  # Y(s/c), GSE
                '31',  # Z(s/c), GSE
                '32',  # BSN (x-component)
                '33',  # BSN (y-component)
                '34',  # BSN (z-component)
                '35',  # AE-index
                '36',  # AL-index
                '37',  # AU-index
                '38',  # SYM/D index
                '39',  # SYM/H index
                '40',  # ASY/D index
                '41',  # ASY/H index
                '42',  # PC(N) index
                '43',  # Magnetosonic mach number
                '44',  # Dst-index
                '45',  # ap-index
                '46',  # f10.7_index
                '47',  # AE_INDEX
                '48',  # Kp index
            ],
            'scale': '1',
            'view': '0',
            'charsize': '&charsize=10',
            'xstyle': '1',
            'ystyle': '1',
            'symbol': '3',
            'symsize': '&symsize=0.4',
            'linestyle': '1',
            'table': '0',
            'imagex': '640',
            'imagey': '480',
            'color': '1',
        }

        try:
            logger.info(f"Fetching OMNI data from {start_date} to {end_date}...")
            async with self.session.post(self.BASE_URL, data=params) as response:
                if response.status == 200:
                    text = await response.text()
                    return text
                else:
                    logger.error(f"Failed to fetch OMNI data: HTTP {response.status}")
                    return ""
        except Exception as e:
            logger.error(f"Error fetching OMNI data: {e}")
            return ""

    def parse_omni_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single line of OMNI data
        Format: YEAR DOY HOUR values...
        """
        try:
            parts = line.split()
            if len(parts) < 20:
                return None

            year = int(parts[0])
            doy = int(parts[1])  # Day of year
            hour = int(parts[2])

            # Create datetime from year, day of year, and hour
            timestamp = datetime(year, 1, 1) + timedelta(days=doy - 1, hours=hour)

            # Parse parameters (check for fill values 9999.99, 999.99, etc.)
            def parse_value(val: str, fill_values: List[float] = [9999.99, 999.99, 99.99, 9.999]) -> Optional[float]:
                try:
                    v = float(val)
                    for fill in fill_values:
                        if abs(v - fill) < 0.01:
                            return None
                    return v
                except:
                    return None

            # Extract key parameters (indices may vary based on OMNI format)
            # These are approximate indices - may need adjustment
            data = {
                'timestamp': timestamp,
                'imf_bz': parse_value(parts[16]) if len(parts) > 16 else None,  # Bz GSM
                'solar_wind_speed': parse_value(parts[21]) if len(parts) > 21 else None,
                'solar_wind_density': parse_value(parts[23]) if len(parts) > 23 else None,
                'solar_wind_temperature': parse_value(parts[24]) if len(parts) > 24 else None,
                'dst_index': parse_value(parts[40]) if len(parts) > 40 else None,
                'kp_index': parse_value(parts[38]) if len(parts) > 38 else None,
                'f107_flux': parse_value(parts[50]) if len(parts) > 50 else None,
            }

            return data
        except Exception as e:
            logger.debug(f"Error parsing line: {e}")
            return None


async def fetch_omni_data_simple(start_date: datetime, end_date: datetime) -> List[Dict]:
    """
    Simplified OMNI data fetcher using the text interface
    This is more reliable than the CGI interface
    """

    # OMNI2 data files are organized by year
    # Format: https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/omni2_YYYY.dat

    all_data = []

    async with aiohttp.ClientSession() as session:
        current_year = start_date.year
        end_year = end_date.year

        while current_year <= end_year:
            url = f"https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/omni2_{current_year}.dat"
            logger.info(f"Fetching {url}...")

            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        text = await response.text()
                        lines = text.strip().split('\n')

                        for line in lines:
                            parsed = parse_omni2_line(line)
                            if parsed and start_date <= parsed['timestamp'] <= end_date:
                                all_data.append(parsed)

                        logger.info(f"Parsed {len([l for l in lines if parse_omni2_line(l)])} records from {current_year}")
                    else:
                        logger.error(f"Failed to fetch {url}: HTTP {response.status}")
            except Exception as e:
                logger.error(f"Error fetching year {current_year}: {e}")

            current_year += 1
            await asyncio.sleep(1)  # Be nice to the server

    return all_data


def parse_omni2_line(line: str) -> Optional[Dict]:
    """
    Parse OMNI2 format line
    Format documentation: https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/omni2.text
    """
    try:
        if len(line) < 200:
            return None

        # Fixed-width format
        year = int(line[0:4])
        doy = int(line[5:8])
        hour = int(line[9:11])

        # Create timestamp
        timestamp = datetime(year, 1, 1) + timedelta(days=doy - 1, hours=hour)

        # Parse values (fixed positions)
        def parse_field(start: int, end: int, fill_value: float = 9999.99) -> Optional[float]:
            try:
                val = float(line[start:end].strip())
                if abs(val - fill_value) < 0.01 or abs(val - 999.99) < 0.01 or abs(val - 99.99) < 0.01:
                    return None
                return val
            except:
                return None

        return {
            'timestamp': timestamp,
            'kp_index': parse_field(116, 119, 99.9),  # Kp * 10 (need to divide by 10)
            'dst_index': parse_field(113, 116, 99999),
            'imf_bz': parse_field(55, 61, 9999.99),  # Bz GSM
            'solar_wind_speed': parse_field(64, 70, 9999.9),
            'solar_wind_density': parse_field(71, 77, 999.99),
            'solar_wind_temperature': parse_field(78, 84, 9999999.),
            'f107_flux': parse_field(122, 128, 999.9),
        }
    except Exception as e:
        return None


def estimate_tec_from_space_weather(
    kp: float,
    dst: float,
    solar_wind_speed: float,
    f107: float,
    hour: int
) -> Dict[str, float]:
    """
    Estimate TEC values from space weather conditions
    Uses empirical relationships when direct TEC measurements unavailable
    """

    # Base TEC from solar activity (F10.7)
    # Empirical: TEC roughly scales with sqrt(F10.7)
    if f107 is not None:
        base_tec = 5 + 0.3 * np.sqrt(max(70, f107))
    else:
        base_tec = 20.0  # Default

    # Diurnal variation (peak around 14:00 LT)
    diurnal_factor = 1 + 0.5 * np.sin(2 * np.pi * (hour - 6) / 24)

    # Storm enhancement/depletion
    storm_factor = 1.0
    if kp is not None and kp > 4:
        # Storms can enhance or deplete TEC
        storm_factor = 1 + (kp - 4) / 10

    if dst is not None and dst < -50:
        # Strong negative Dst indicates storm
        storm_factor *= (1 - dst / 400)  # Enhancement

    mean_tec = base_tec * diurnal_factor * storm_factor

    # Add realistic variation
    std_tec = mean_tec * 0.2  # 20% variation
    max_tec = mean_tec + 2 * std_tec
    min_tec = max(0, mean_tec - 2 * std_tec)

    return {
        'tec_mean': round(mean_tec, 2),
        'tec_std': round(std_tec, 2),
        'tec_max': round(max_tec, 2),
        'tec_min': round(min_tec, 2),
    }


def calculate_storm_probability(kp: float, dst: float, imf_bz: float, sw_speed: float) -> float:
    """Calculate 24-hour storm probability from space weather conditions"""
    prob = 0.0

    # Kp contribution
    if kp is not None and kp >= 5:
        prob += (kp - 4) * 15

    # Dst contribution
    if dst is not None and dst < -50:
        prob += abs(dst) / 4

    # IMF Bz contribution (southward = bad)
    if imf_bz is not None and imf_bz < -5:
        prob += abs(imf_bz) * 3

    # Solar wind speed contribution
    if sw_speed is not None and sw_speed > 450:
        prob += (sw_speed - 450) / 10

    return max(0, min(100, round(prob, 1)))


def calculate_risk_level(storm_probability: float) -> int:
    """Calculate risk level from storm probability"""
    if storm_probability < 20:
        return 0
    elif storm_probability < 40:
        return 1
    elif storm_probability < 60:
        return 2
    elif storm_probability < 80:
        return 3
    else:
        return 4


async def import_real_data():
    """
    Main function to import real historical data
    """
    logger.info("=" * 80)
    logger.info("REAL DATA IMPORT - Ionospheric Storm Prediction System")
    logger.info("=" * 80)

    # Initialize database
    logger.info("\nInitializing database...")
    await init_db()

    # Date range: Last 10 years
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365 * 10)

    logger.info(f"\nFetching REAL data from {start_date.date()} to {end_date.date()}")
    logger.info("Data sources:")
    logger.info("  - NASA OMNI: Solar wind, IMF, Kp, Dst, F10.7")
    logger.info("  - TEC: Empirically estimated from space weather conditions")
    logger.info("")

    # Fetch data from NASA OMNI
    logger.info("Downloading data from NASA OMNI (this may take several minutes)...")
    real_data = await fetch_omni_data_simple(start_date, end_date)

    logger.info(f"\nDownloaded {len(real_data)} hourly measurements")

    if len(real_data) < 1000:
        logger.error("Insufficient data retrieved. Check NASA OMNI availability.")
        return

    # Process and insert into database
    logger.info("\nProcessing and inserting into database...")

    batch_size = 1000
    measurements_batch = []
    inserted_count = 0
    skipped_count = 0

    async with AsyncSessionLocal() as session:
        for i, data_point in enumerate(real_data):
            # Check for required fields
            if data_point.get('kp_index') is None and data_point.get('dst_index') is None:
                skipped_count += 1
                continue

            # Normalize Kp if needed (OMNI stores Kp * 10)
            kp = data_point.get('kp_index')
            if kp is not None and kp > 10:
                kp = kp / 10.0

            # Fill missing values with defaults
            dst = data_point.get('dst_index') or 0.0
            imf_bz = data_point.get('imf_bz') or 0.0
            sw_speed = data_point.get('solar_wind_speed') or 400.0
            sw_density = data_point.get('solar_wind_density') or 5.0
            sw_temp = data_point.get('solar_wind_temperature') or 100000.0
            f107 = data_point.get('f107_flux') or 120.0

            # Estimate TEC
            tec_values = estimate_tec_from_space_weather(
                kp, dst, sw_speed, f107, data_point['timestamp'].hour
            )

            # Calculate storm probability
            storm_prob = calculate_storm_probability(kp, dst, imf_bz, sw_speed)
            risk = calculate_risk_level(storm_prob)

            # Create measurement
            measurement = HistoricalMeasurement(
                timestamp=data_point['timestamp'],
                kp_index=kp or 0.0,
                dst_index=dst,
                solar_wind_speed=sw_speed,
                solar_wind_density=sw_density,
                solar_wind_temperature=sw_temp,
                imf_bz=imf_bz,
                f107_flux=f107,
                tec_mean=tec_values['tec_mean'],
                tec_std=tec_values['tec_std'],
                tec_max=tec_values['tec_max'],
                tec_min=tec_values['tec_min'],
                storm_probability=storm_prob,
                risk_level=risk
            )

            measurements_batch.append(measurement)

            # Batch insert
            if len(measurements_batch) >= batch_size:
                session.add_all(measurements_batch)
                await session.commit()
                inserted_count += len(measurements_batch)
                measurements_batch = []

                progress = (i + 1) / len(real_data) * 100
                print(f"Progress: {progress:.1f}% ({inserted_count:,} records inserted)", end='\r', flush=True)

        # Insert remaining
        if measurements_batch:
            session.add_all(measurements_batch)
            await session.commit()
            inserted_count += len(measurements_batch)

    logger.info(f"\n\n{'=' * 80}")
    logger.info("✅ REAL DATA IMPORT COMPLETE!")
    logger.info(f"{'=' * 80}")
    logger.info(f"  Total records inserted: {inserted_count:,}")
    logger.info(f"  Skipped (missing data): {skipped_count:,}")
    logger.info(f"  Date range: {start_date.date()} to {end_date.date()}")
    logger.info(f"  Database: backend/data/ionospheric.db")
    logger.info(f"\nData is now ready for model training!")
    logger.info(f"Next step: python app/training/train_model_v2.py")
    logger.info(f"{'=' * 80}\n")


if __name__ == "__main__":
    asyncio.run(import_real_data())
