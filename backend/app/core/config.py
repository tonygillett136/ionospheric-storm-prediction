"""
Configuration settings for the Ionospheric Storm Prediction System
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Ionospheric Storm Prediction System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Data Sources
    NOAA_SWPC_BASE_URL: str = "https://services.swpc.noaa.gov"
    NASA_CDDIS_BASE_URL: str = "https://cddis.nasa.gov"

    # Update intervals (seconds)
    DATA_UPDATE_INTERVAL: int = 300  # 5 minutes
    PREDICTION_UPDATE_INTERVAL: int = 3600  # 1 hour

    # Model settings
    MODEL_PATH: str = "ml_models/saved_models"
    PREDICTION_HORIZON_HOURS: int = 24

    # Data retention
    MAX_HISTORICAL_DAYS: int = 30

    # Thresholds for storm classification
    STORM_THRESHOLD_MINOR: float = 0.3
    STORM_THRESHOLD_MODERATE: float = 0.5
    STORM_THRESHOLD_SEVERE: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
