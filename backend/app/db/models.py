from sqlalchemy import Column, Integer, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class HistoricalMeasurement(Base):
    """
    Stores historical ionospheric and space weather measurements.
    Supports 10 years of data (87,600+ hours) with efficient querying.
    """
    __tablename__ = "historical_measurements"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True, unique=True)

    # Geomagnetic indices
    kp_index = Column(Float, nullable=False)
    dst_index = Column(Float, nullable=False)

    # Solar wind parameters
    solar_wind_speed = Column(Float, nullable=False)  # km/s
    solar_wind_density = Column(Float, nullable=False)  # particles/cm³
    solar_wind_temperature = Column(Float, nullable=True)  # K

    # Interplanetary magnetic field
    imf_bz = Column(Float, nullable=False)  # nT

    # Solar activity
    f107_flux = Column(Float, nullable=False)  # Solar flux index

    # Ionospheric measurements
    tec_mean = Column(Float, nullable=False)  # TECU
    tec_std = Column(Float, nullable=False)  # TECU
    tec_max = Column(Float, nullable=True)  # TECU
    tec_min = Column(Float, nullable=True)  # TECU

    # Predictions (if available)
    storm_probability = Column(Float, nullable=True)  # 0-100
    risk_level = Column(Integer, nullable=True)  # 0-4 (low to severe)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Create composite index for efficient time-range queries
    __table_args__ = (
        Index('idx_timestamp_desc', timestamp.desc()),
        Index('idx_timestamp_storm', timestamp, storm_probability),
    )

    def to_dict(self):
        """Convert model to dictionary for API responses."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'kp_index': self.kp_index,
            'dst_index': self.dst_index,
            'solar_wind': {
                'speed': self.solar_wind_speed,
                'density': self.solar_wind_density,
                'temperature': self.solar_wind_temperature
            },
            'imf_bz': self.imf_bz,
            'f107_flux': self.f107_flux,
            'tec': {
                'mean': self.tec_mean,
                'std': self.tec_std,
                'max': self.tec_max,
                'min': self.tec_min
            },
            'storm_probability': self.storm_probability,
            'risk_level': self.risk_level
        }

    def __repr__(self):
        return f"<HistoricalMeasurement(timestamp={self.timestamp}, kp={self.kp_index}, storm_prob={self.storm_probability})>"
