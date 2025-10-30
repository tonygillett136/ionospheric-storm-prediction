from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from datetime import datetime, timedelta
from typing import List, Optional
from app.db.models import HistoricalMeasurement

class HistoricalDataRepository:
    """Repository for historical measurement data operations."""

    @staticmethod
    async def create_measurement(
        session: AsyncSession,
        timestamp: datetime,
        kp_index: float,
        dst_index: float,
        solar_wind_speed: float,
        solar_wind_density: float,
        solar_wind_temperature: Optional[float],
        imf_bz: float,
        f107_flux: float,
        tec_mean: float,
        tec_std: float,
        tec_max: Optional[float] = None,
        tec_min: Optional[float] = None,
        storm_probability: Optional[float] = None,
        risk_level: Optional[int] = None
    ) -> HistoricalMeasurement:
        """Create a new historical measurement record."""
        measurement = HistoricalMeasurement(
            timestamp=timestamp,
            kp_index=kp_index,
            dst_index=dst_index,
            solar_wind_speed=solar_wind_speed,
            solar_wind_density=solar_wind_density,
            solar_wind_temperature=solar_wind_temperature,
            imf_bz=imf_bz,
            f107_flux=f107_flux,
            tec_mean=tec_mean,
            tec_std=tec_std,
            tec_max=tec_max,
            tec_min=tec_min,
            storm_probability=storm_probability,
            risk_level=risk_level
        )
        session.add(measurement)
        await session.commit()
        await session.refresh(measurement)
        return measurement

    @staticmethod
    async def get_measurements_by_time_range(
        session: AsyncSession,
        start_time: datetime,
        end_time: datetime
    ) -> List[HistoricalMeasurement]:
        """Get all measurements within a time range, ordered by timestamp ascending."""
        result = await session.execute(
            select(HistoricalMeasurement)
            .where(and_(
                HistoricalMeasurement.timestamp >= start_time,
                HistoricalMeasurement.timestamp <= end_time
            ))
            .order_by(HistoricalMeasurement.timestamp)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_latest_measurements(
        session: AsyncSession,
        limit: int = 100
    ) -> List[HistoricalMeasurement]:
        """Get the most recent measurements."""
        result = await session.execute(
            select(HistoricalMeasurement)
            .order_by(desc(HistoricalMeasurement.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_measurement_by_timestamp(
        session: AsyncSession,
        timestamp: datetime
    ) -> Optional[HistoricalMeasurement]:
        """Get a specific measurement by timestamp."""
        result = await session.execute(
            select(HistoricalMeasurement)
            .where(HistoricalMeasurement.timestamp == timestamp)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def measurement_exists(
        session: AsyncSession,
        timestamp: datetime
    ) -> bool:
        """Check if a measurement exists for a given timestamp."""
        measurement = await HistoricalDataRepository.get_measurement_by_timestamp(session, timestamp)
        return measurement is not None

    @staticmethod
    async def get_measurements_last_n_hours(
        session: AsyncSession,
        hours: int
    ) -> List[HistoricalMeasurement]:
        """Get measurements from the last N hours."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        return await HistoricalDataRepository.get_measurements_by_time_range(
            session, start_time, end_time
        )

    @staticmethod
    async def count_measurements(session: AsyncSession) -> int:
        """Get total count of measurements in database."""
        result = await session.execute(
            select(HistoricalMeasurement)
        )
        return len(list(result.scalars().all()))

    @staticmethod
    async def delete_old_measurements(
        session: AsyncSession,
        before_date: datetime
    ) -> int:
        """Delete measurements older than specified date. Returns count of deleted records."""
        result = await session.execute(
            select(HistoricalMeasurement)
            .where(HistoricalMeasurement.timestamp < before_date)
        )
        measurements = result.scalars().all()
        count = len(list(measurements))

        for measurement in measurements:
            await session.delete(measurement)

        await session.commit()
        return count
