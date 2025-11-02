"""
Regional Prediction Service

Provides location-specific ionospheric storm predictions based on
regional TEC extraction from global data.
"""
import math
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RegionalPredictionService:
    """
    Service for calculating location-specific ionospheric storm predictions.

    Extracts regional TEC data and adjusts global predictions based on
    local ionospheric conditions.
    """

    def __init__(self):
        """Initialize regional prediction service."""
        pass

    def get_regional_prediction(
        self,
        latitude: float,
        longitude: float,
        global_prediction: Dict,
        tec_data: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate location-specific prediction.

        Args:
            latitude: Geographic latitude (-90 to 90)
            longitude: Geographic longitude (-180 to 180)
            global_prediction: Global prediction data from main model
            tec_data: Optional global TEC grid data

        Returns:
            Dictionary with regional prediction and TEC data
        """
        try:
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise ValueError("Longitude must be between -180 and 180")

            # Extract regional TEC if available
            regional_tec = None
            if tec_data:
                regional_tec = self._extract_regional_tec(latitude, longitude, tec_data)

            # Calculate regional adjustment factor
            adjustment_factor = self._calculate_regional_adjustment(
                latitude, longitude, global_prediction
            )

            # Adjust global probabilities
            global_prob_24h = global_prediction.get('storm_probability_24h', 0)
            global_prob_48h = global_prediction.get('storm_probability_48h', 0)

            regional_prob_24h = min(1.0, global_prob_24h * adjustment_factor)
            regional_prob_48h = min(1.0, global_prob_48h * adjustment_factor)

            # Calculate risk levels
            risk_level_24h = self._calculate_risk_level(regional_prob_24h)
            risk_level_48h = self._calculate_risk_level(regional_prob_48h)

            # Determine region name
            region_name = self._get_region_name(latitude, longitude)

            return {
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "region": region_name
                },
                "regional_prediction": {
                    "storm_probability_24h": round(regional_prob_24h * 100, 2),
                    "storm_probability_48h": round(regional_prob_48h * 100, 2),
                    "risk_level_24h": risk_level_24h,
                    "risk_level_48h": risk_level_48h,
                    "adjustment_factor": round(adjustment_factor, 3)
                },
                "global_comparison": {
                    "global_probability_24h": round(global_prob_24h * 100, 2),
                    "global_probability_48h": round(global_prob_48h * 100, 2),
                    "difference_24h": round((regional_prob_24h - global_prob_24h) * 100, 2),
                    "difference_48h": round((regional_prob_48h - global_prob_48h) * 100, 2)
                },
                "regional_tec": regional_tec,
                "explanation": self._get_explanation(latitude, adjustment_factor)
            }

        except Exception as e:
            logger.error(f"Error calculating regional prediction: {e}")
            raise

    def _extract_regional_tec(
        self, latitude: float, longitude: float, tec_data: Dict
    ) -> Optional[Dict]:
        """
        Extract TEC values for a specific region.

        In a full implementation, this would:
        1. Find nearest grid points in global TEC data
        2. Interpolate TEC values
        3. Calculate regional statistics

        For now, we'll return a placeholder based on latitude bands.
        """
        try:
            # Get global TEC statistics as baseline
            tec_statistics = tec_data.get('tec_statistics', {})
            global_mean = tec_statistics.get('mean', 20.0)
            global_std = tec_statistics.get('std', 5.0)

            # Latitude-based adjustment (ionosphere varies by latitude)
            # Equator: higher TEC, Poles: lower TEC
            abs_lat = abs(latitude)

            if abs_lat < 20:  # Equatorial
                lat_factor = 1.3
            elif abs_lat < 40:  # Low latitude
                lat_factor = 1.15
            elif abs_lat < 60:  # Mid latitude
                lat_factor = 1.0
            else:  # High latitude / Polar
                lat_factor = 0.7

            regional_mean = global_mean * lat_factor
            regional_std = global_std * lat_factor

            return {
                "mean": round(regional_mean, 2),
                "std": round(regional_std, 2),
                "max": round(regional_mean + regional_std * 2, 2),
                "min": round(max(0, regional_mean - regional_std * 2), 2),
                "latitude_factor": lat_factor
            }

        except Exception as e:
            logger.error(f"Error extracting regional TEC: {e}")
            return None

    def _calculate_regional_adjustment(
        self, latitude: float, longitude: float, global_prediction: Dict
    ) -> float:
        """
        Calculate adjustment factor for regional predictions.

        Factors:
        - Latitude: High-latitude regions more susceptible to storms
        - Magnetic latitude: Auroral zones have higher risk
        - Local time: Dawn/dusk sectors more active
        """
        # Base adjustment
        adjustment = 1.0

        # Latitude effect
        abs_lat = abs(latitude)

        if abs_lat < 20:  # Equatorial
            lat_adjustment = 0.85  # Lower storm risk
        elif abs_lat < 40:  # Low latitude
            lat_adjustment = 0.95
        elif abs_lat < 60:  # Mid latitude
            lat_adjustment = 1.0
        elif abs_lat < 75:  # High latitude (auroral zone)
            lat_adjustment = 1.25  # Higher storm risk
        else:  # Polar
            lat_adjustment = 1.4  # Highest storm risk

        adjustment *= lat_adjustment

        # Magnetic latitude approximation
        # Auroral zones (60-70° magnetic lat) are most affected
        # Simplified: use geographic latitude as proxy
        if 55 <= abs_lat <= 70:
            adjustment *= 1.15  # Auroral zone enhancement

        # Ensure reasonable bounds
        adjustment = max(0.5, min(1.5, adjustment))

        return adjustment

    def _calculate_risk_level(self, probability: float) -> str:
        """Calculate risk level from probability."""
        prob_pct = probability * 100

        if prob_pct < 20:
            return 'low'
        elif prob_pct < 40:
            return 'moderate'
        elif prob_pct < 60:
            return 'elevated'
        elif prob_pct < 80:
            return 'high'
        else:
            return 'severe'

    def _get_region_name(self, latitude: float, longitude: float) -> str:
        """Get descriptive region name."""
        abs_lat = abs(latitude)
        hemisphere = "Northern" if latitude >= 0 else "Southern"

        if abs_lat < 23.5:
            zone = "Equatorial"
        elif abs_lat < 40:
            zone = "Subtropical"
        elif abs_lat < 60:
            zone = "Mid-latitude"
        elif abs_lat < 75:
            zone = "Auroral"
        else:
            zone = "Polar"

        # Rough longitude zones
        if -30 <= longitude < 60:
            sector = "Europe/Africa"
        elif 60 <= longitude < 150:
            sector = "Asia/Pacific"
        elif 150 <= longitude or longitude < -150:
            sector = "Pacific"
        elif -150 <= longitude < -60:
            sector = "Americas"
        else:
            sector = "Atlantic"

        return f"{hemisphere} {zone} ({sector})"

    def _get_explanation(self, latitude: float, adjustment_factor: float) -> str:
        """Get human-readable explanation of regional factors."""
        abs_lat = abs(latitude)

        if adjustment_factor > 1.1:
            direction = "higher"
            reason_parts = []

            if abs_lat > 60:
                reason_parts.append("high-latitude location near auroral zone")
            if 55 <= abs_lat <= 70:
                reason_parts.append("enhanced auroral activity in this region")

            reason = " and ".join(reason_parts) if reason_parts else "regional factors"

            return (
                f"Regional probability is {direction} than global average due to {reason}. "
                f"High-latitude regions experience stronger geomagnetic effects."
            )

        elif adjustment_factor < 0.9:
            direction = "lower"
            reason = "equatorial/low-latitude location" if abs_lat < 30 else "regional factors"

            return (
                f"Regional probability is {direction} than global average due to {reason}. "
                f"Lower latitudes typically experience reduced storm impacts."
            )

        else:
            return (
                "Regional probability is similar to global average. "
                "Your location experiences typical mid-latitude space weather effects."
            )
