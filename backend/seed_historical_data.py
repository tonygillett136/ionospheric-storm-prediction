"""
Seed historical ionospheric data for the past 10 years.

Generates realistic synthetic data patterns based on:
- Solar cycle variations (11-year cycle)
- Seasonal variations
- Daily variations
- Random storm events
- Correlation between parameters
"""

import asyncio
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal, init_db
from app.db.repository import HistoricalDataRepository

# Constants
YEARS = 10
HOURS_PER_YEAR = 8760
TOTAL_HOURS = YEARS * HOURS_PER_YEAR  # 87,600 hours

def generate_solar_cycle_component(day_of_cycle: int, cycle_length: int = 4018) -> float:
    """
    Generate solar cycle component (11-year cycle = ~4018 days).
    Returns value between 0.5 and 1.5 representing solar activity level.
    """
    phase = (day_of_cycle % cycle_length) / cycle_length
    # Solar cycle is roughly sinusoidal
    return 1.0 + 0.5 * np.sin(2 * np.pi * phase)

def generate_seasonal_component(day_of_year: int) -> float:
    """
    Generate seasonal variation (higher activity around equinoxes).
    Returns value between 0.8 and 1.2.
    """
    # Peak activity around day 80 (March equinox) and day 266 (September equinox)
    equinox1 = abs(day_of_year - 80)
    equinox2 = abs(day_of_year - 266)
    min_dist = min(equinox1, equinox2)
    # Higher near equinoxes, lower near solstices
    return 0.8 + 0.4 * (1 - min_dist / 90)

def generate_daily_component(hour: int) -> float:
    """
    Generate daily variation (higher TEC during daytime).
    Returns value between 0.6 and 1.4.
    """
    # Peak around 14:00 local time
    return 1.0 + 0.4 * np.sin(2 * np.pi * (hour - 6) / 24)

def generate_storm_events(total_hours: int, avg_storms_per_year: int = 20) -> set:
    """
    Generate random storm events.
    Returns set of hour indices where storms occur.
    """
    total_storms = avg_storms_per_year * YEARS
    storm_hours = set()

    for _ in range(total_storms):
        # Random storm start
        storm_start = np.random.randint(0, total_hours)
        # Storm duration: 6-72 hours
        storm_duration = np.random.randint(6, 73)

        # Add all hours during storm
        for h in range(storm_start, min(storm_start + storm_duration, total_hours)):
            storm_hours.add(h)

    return storm_hours

def calculate_kp_index(
    solar_component: float,
    seasonal_component: float,
    is_storm: bool,
    base_noise: float
) -> float:
    """Calculate Kp index (0-9 scale)."""
    if is_storm:
        # During storm: Kp 4-9
        kp = 4.0 + np.random.exponential(1.5)
        kp = min(kp, 9.0)
    else:
        # Quiet conditions: Kp 0-4
        kp = 1.5 * solar_component * seasonal_component + base_noise
        kp = max(0.0, min(kp, 4.0))

    return round(kp, 1)

def calculate_dst_index(kp: float, is_storm: bool) -> float:
    """Calculate Dst index (typically -400 to +50 nT)."""
    if is_storm:
        # Storm: Negative Dst, stronger with higher Kp
        dst = -20 - (kp - 4) * 30 + np.random.normal(0, 15)
        dst = max(dst, -400)
    else:
        # Quiet: Near zero to slightly positive
        dst = np.random.normal(0, 10)
        dst = min(dst, 50)

    return round(dst, 1)

def calculate_solar_wind_speed(solar_component: float, is_storm: bool) -> float:
    """Calculate solar wind speed (km/s, typically 300-800)."""
    if is_storm:
        # Fast solar wind during storms
        speed = 500 + np.random.exponential(100)
        speed = min(speed, 800)
    else:
        # Normal solar wind
        speed = 350 + solar_component * 50 + np.random.normal(0, 30)
        speed = max(speed, 300)

    return round(speed, 1)

def calculate_solar_wind_density(solar_component: float) -> float:
    """Calculate solar wind density (particles/cm³, typically 1-20)."""
    density = 3 + solar_component * 2 + np.random.exponential(2)
    density = max(1.0, min(density, 20.0))
    return round(density, 2)

def calculate_solar_wind_temperature(speed: float) -> float:
    """Calculate solar wind temperature (K, typically 50000-500000)."""
    # Higher speed correlates with higher temperature
    temp = 50000 + (speed - 300) * 800 + np.random.normal(0, 30000)
    temp = max(50000, min(temp, 500000))
    return round(temp, 0)

def calculate_imf_bz(is_storm: bool) -> float:
    """Calculate IMF Bz component (nT, typically -20 to +20)."""
    if is_storm:
        # Negative (southward) Bz triggers storms
        bz = -15 + np.random.normal(0, 5)
        bz = max(bz, -20)
    else:
        # Random, slightly positive bias
        bz = np.random.normal(2, 5)
        bz = max(-20, min(bz, 20))

    return round(bz, 2)

def calculate_f107_flux(solar_component: float) -> float:
    """Calculate F10.7 solar flux (typically 70-300 sfu)."""
    flux = 100 + solar_component * 80 + np.random.normal(0, 15)
    flux = max(70, min(flux, 300))
    return round(flux, 1)

def calculate_tec_values(
    solar_component: float,
    seasonal_component: float,
    daily_component: float,
    is_storm: bool,
    kp: float
) -> tuple:
    """Calculate TEC mean, std, max, min (TECU)."""
    # Base TEC influenced by solar cycle, season, and time of day
    base_tec = 20 * solar_component * seasonal_component * daily_component

    if is_storm:
        # Enhanced TEC during storms
        mean_tec = base_tec * (1 + kp / 10) + np.random.normal(0, 5)
        std_tec = 5 + kp
    else:
        mean_tec = base_tec + np.random.normal(0, 3)
        std_tec = 2 + np.random.exponential(2)

    mean_tec = max(5, min(mean_tec, 100))
    std_tec = max(1, min(std_tec, 20))

    # Max and min based on mean and std
    max_tec = mean_tec + 2 * std_tec
    min_tec = max(0, mean_tec - 2 * std_tec)

    return (
        round(mean_tec, 2),
        round(std_tec, 2),
        round(max_tec, 2),
        round(min_tec, 2)
    )

def calculate_storm_probability(kp: float, imf_bz: float, solar_wind_speed: float) -> float:
    """Calculate 24-hour storm probability (0-100)."""
    # Higher Kp, negative Bz, fast wind = higher probability
    prob = 0.0

    # Kp contribution
    if kp >= 5:
        prob += (kp - 4) * 15

    # IMF Bz contribution (negative = bad)
    if imf_bz < 0:
        prob += abs(imf_bz) * 2

    # Solar wind speed contribution
    if solar_wind_speed > 450:
        prob += (solar_wind_speed - 450) / 10

    # Add some noise
    prob += np.random.normal(0, 5)

    return max(0, min(round(prob, 1), 100))

def calculate_risk_level(storm_probability: float) -> int:
    """Calculate risk level (0-4) based on storm probability."""
    if storm_probability < 20:
        return 0  # Low
    elif storm_probability < 40:
        return 1  # Moderate
    elif storm_probability < 60:
        return 2  # Elevated
    elif storm_probability < 80:
        return 3  # High
    else:
        return 4  # Severe

async def seed_data():
    """Generate and insert 10 years of historical data."""
    print(f"Initializing database...")
    await init_db()

    print(f"Generating {TOTAL_HOURS:,} hours ({YEARS} years) of historical data...")
    print("This may take a few minutes...\n")

    # Generate storm events
    storm_hours = generate_storm_events(TOTAL_HOURS)
    print(f"Generated {len(storm_hours):,} storm hours ({len(storm_hours) / TOTAL_HOURS * 100:.1f}% of time)")

    # Starting point: 10 years ago
    start_time = datetime.utcnow() - timedelta(days=YEARS * 365)

    # We'll use the start date to calculate solar cycle position
    # Assume we're currently mid-cycle
    current_day_in_cycle = 2000  # Mid-point of 11-year cycle

    batch_size = 1000
    measurements_batch = []
    inserted_count = 0

    async with AsyncSessionLocal() as session:
        for hour_offset in range(TOTAL_HOURS):
            timestamp = start_time + timedelta(hours=hour_offset)

            # Calculate components
            days_since_start = hour_offset // 24
            day_in_cycle = current_day_in_cycle + days_since_start
            day_of_year = timestamp.timetuple().tm_yday
            hour_of_day = timestamp.hour

            solar_component = generate_solar_cycle_component(day_in_cycle)
            seasonal_component = generate_seasonal_component(day_of_year)
            daily_component = generate_daily_component(hour_of_day)

            is_storm = hour_offset in storm_hours
            base_noise = np.random.normal(0, 0.3)

            # Calculate all parameters
            kp = calculate_kp_index(solar_component, seasonal_component, is_storm, base_noise)
            dst = calculate_dst_index(kp, is_storm)
            sw_speed = calculate_solar_wind_speed(solar_component, is_storm)
            sw_density = calculate_solar_wind_density(solar_component)
            sw_temp = calculate_solar_wind_temperature(sw_speed)
            imf_bz = calculate_imf_bz(is_storm)
            f107 = calculate_f107_flux(solar_component)
            tec_mean, tec_std, tec_max, tec_min = calculate_tec_values(
                solar_component, seasonal_component, daily_component, is_storm, kp
            )
            storm_prob = calculate_storm_probability(kp, imf_bz, sw_speed)
            risk = calculate_risk_level(storm_prob)

            # Create measurement
            measurement = HistoricalMeasurement(
                timestamp=timestamp,
                kp_index=kp,
                dst_index=dst,
                solar_wind_speed=sw_speed,
                solar_wind_density=sw_density,
                solar_wind_temperature=sw_temp,
                imf_bz=imf_bz,
                f107_flux=f107,
                tec_mean=tec_mean,
                tec_std=tec_std,
                tec_max=tec_max,
                tec_min=tec_min,
                storm_probability=storm_prob,
                risk_level=risk
            )

            measurements_batch.append(measurement)

            # Batch insert every 1000 records
            if len(measurements_batch) >= batch_size:
                session.add_all(measurements_batch)
                await session.commit()
                inserted_count += len(measurements_batch)
                measurements_batch = []

                # Progress update
                progress = (hour_offset + 1) / TOTAL_HOURS * 100
                print(f"Progress: {progress:.1f}% ({inserted_count:,} / {TOTAL_HOURS:,} records)", end='\r')

        # Insert remaining records
        if measurements_batch:
            session.add_all(measurements_batch)
            await session.commit()
            inserted_count += len(measurements_batch)

    print(f"\n\nSeeding complete! Inserted {inserted_count:,} historical records.")
    print(f"Data spans from {start_time} to {start_time + timedelta(hours=TOTAL_HOURS - 1)}")

if __name__ == "__main__":
    # Import here to avoid circular imports
    from app.db.models import HistoricalMeasurement

    asyncio.run(seed_data())
