"""
Impact Assessment Service

Translates ionospheric storm predictions into actionable impact assessments
for GPS, HF radio, satellites, and power grids.
"""
import math
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ImpactAssessmentService:
    """
    Service for calculating real-world impacts of ionospheric storms.

    Based on research from:
    - Klobuchar ionospheric model
    - NOAA Space Weather Prediction Center guidelines
    - ITU radio propagation models
    """

    def assess_impacts(
        self,
        probability_24h: float,
        probability_48h: float,
        kp_index: float,
        tec_mean: float,
        dst_index: float = 0,
        latitude: float = 45.0  # Default mid-latitude
    ) -> Dict:
        """
        Calculate comprehensive impact assessment.

        Args:
            probability_24h: Storm probability (0-1) for 24h horizon
            probability_48h: Storm probability (0-1) for 48h horizon
            kp_index: Current Kp index (0-9)
            tec_mean: Mean TEC value in TECU
            dst_index: Disturbance storm time index
            latitude: Geographic latitude for regional effects

        Returns:
            Dictionary with impact assessments for different systems
        """
        try:
            # Convert probabilities to percentages
            prob_24h_pct = probability_24h * 100
            prob_48h_pct = probability_48h * 100

            # Calculate GPS impact
            gps_impact = self._assess_gps_impact(
                prob_24h_pct, kp_index, tec_mean, latitude
            )

            # Calculate HF radio impact
            radio_impact = self._assess_radio_impact(
                prob_24h_pct, kp_index, tec_mean
            )

            # Calculate satellite impact
            satellite_impact = self._assess_satellite_impact(
                prob_24h_pct, kp_index, dst_index
            )

            # Calculate power grid impact (high-latitude regions)
            power_grid_impact = self._assess_power_grid_impact(
                prob_24h_pct, kp_index, latitude
            )

            # Overall severity score (1-10)
            overall_severity = self._calculate_overall_severity(
                prob_24h_pct, kp_index, tec_mean
            )

            return {
                "gps": gps_impact,
                "radio": radio_impact,
                "satellite": satellite_impact,
                "power_grid": power_grid_impact,
                "overall": {
                    "severity_score": overall_severity,
                    "severity_level": self._get_severity_label(overall_severity),
                    "confidence": "high" if prob_24h_pct > 50 else "medium"
                },
                "metadata": {
                    "probability_24h": round(prob_24h_pct, 2),
                    "probability_48h": round(prob_48h_pct, 2),
                    "kp_index": kp_index,
                    "tec_mean": tec_mean,
                    "latitude": latitude
                }
            }

        except Exception as e:
            logger.error(f"Error assessing impacts: {e}")
            return self._get_default_assessment()

    def _assess_gps_impact(
        self, probability: float, kp: float, tec: float, lat: float
    ) -> Dict:
        """
        Assess GPS accuracy degradation.

        GPS error scales with TEC and geomagnetic activity.
        Baseline accuracy: ~3-5m
        Storm accuracy: ~10-30m (or worse)
        """
        # Base error in meters
        base_error = 3.5

        # TEC contribution (linear approximation)
        # Normal TEC: 20 TECU, Storm TEC: 50-100 TECU
        tec_factor = tec / 20.0  # Normalize to baseline

        # Kp contribution (exponential)
        kp_factor = 1.0 + (kp / 3.0) ** 1.5

        # Probability multiplier
        prob_factor = 1.0 + (probability / 100.0) * 2.0

        # Latitude effect (higher impact at high latitudes)
        lat_factor = 1.0 + abs(lat) / 90.0 * 0.5

        # Calculate degraded accuracy
        degraded_error = base_error * tec_factor * kp_factor * prob_factor * lat_factor

        # Calculate impact score (1-10)
        # 3m = 1, 30m = 10
        impact_score = min(10, max(1, (degraded_error / 3.0)))

        return {
            "normal_accuracy_m": round(base_error, 1),
            "degraded_accuracy_m": round(degraded_error, 1),
            "accuracy_loss_pct": round(((degraded_error - base_error) / base_error) * 100, 1),
            "impact_score": round(impact_score, 1),
            "impact_level": self._get_impact_label(impact_score),
            "description": self._get_gps_description(impact_score),
            "recommendations": self._get_gps_recommendations(impact_score)
        }

    def _assess_radio_impact(self, probability: float, kp: float, tec: float) -> Dict:
        """
        Assess HF radio propagation impact.

        Ionospheric storms can cause:
        - Absorption (signal loss)
        - Scintillation (signal fading)
        - Complete blackouts
        """
        # Blackout probability scales with storm severity
        blackout_prob = min(95, (probability + kp * 5 + tec / 2))

        # Frequency band impacts (HF: 3-30 MHz)
        # Lower frequencies more affected
        low_freq_impact = min(10, (blackout_prob / 10))
        mid_freq_impact = min(10, (blackout_prob / 12))
        high_freq_impact = min(10, (blackout_prob / 15))

        # Overall impact score
        impact_score = (low_freq_impact + mid_freq_impact + high_freq_impact) / 3

        return {
            "blackout_probability_pct": round(blackout_prob, 1),
            "frequency_impacts": {
                "low_band_3_10_mhz": {
                    "impact_score": round(low_freq_impact, 1),
                    "status": self._get_radio_status(low_freq_impact)
                },
                "mid_band_10_20_mhz": {
                    "impact_score": round(mid_freq_impact, 1),
                    "status": self._get_radio_status(mid_freq_impact)
                },
                "high_band_20_30_mhz": {
                    "impact_score": round(high_freq_impact, 1),
                    "status": self._get_radio_status(high_freq_impact)
                }
            },
            "impact_score": round(impact_score, 1),
            "impact_level": self._get_impact_label(impact_score),
            "description": self._get_radio_description(impact_score),
            "recommendations": self._get_radio_recommendations(impact_score)
        }

    def _assess_satellite_impact(
        self, probability: float, kp: float, dst: float
    ) -> Dict:
        """
        Assess satellite operation impacts.

        Effects include:
        - Orbit perturbations (increased drag)
        - Surface charging
        - Single event upsets (SEU)
        """
        # Drag increase scales with storm severity
        # Nominal drag: 1.0x, Storm: 2-10x
        drag_multiplier = 1.0 + (probability / 100.0) * (kp / 2.0)

        # Charging risk (0-100%)
        charging_risk = min(95, probability + kp * 8)

        # SEU risk (0-100%)
        seu_risk = min(90, probability * 0.8 + kp * 7)

        # Overall impact score
        drag_score = min(10, drag_multiplier)
        charging_score = min(10, charging_risk / 10)
        seu_score = min(10, seu_risk / 10)
        impact_score = (drag_score + charging_score + seu_score) / 3

        return {
            "atmospheric_drag_multiplier": round(drag_multiplier, 2),
            "surface_charging_risk_pct": round(charging_risk, 1),
            "single_event_upset_risk_pct": round(seu_risk, 1),
            "impact_score": round(impact_score, 1),
            "impact_level": self._get_impact_label(impact_score),
            "description": self._get_satellite_description(impact_score),
            "recommendations": self._get_satellite_recommendations(impact_score)
        }

    def _assess_power_grid_impact(
        self, probability: float, kp: float, latitude: float
    ) -> Dict:
        """
        Assess power grid impact (primarily high-latitude regions).

        Geomagnetically Induced Currents (GICs) can damage transformers.
        """
        # GIC risk strongly latitude-dependent
        # Minimal risk below 45°, high risk above 60°
        if abs(latitude) < 45:
            lat_factor = 0.1
        elif abs(latitude) < 60:
            lat_factor = 0.5
        else:
            lat_factor = 1.0

        # GIC risk
        gic_risk = min(95, probability * lat_factor + kp * 10 * lat_factor)

        # Impact score (1-10)
        impact_score = min(10, gic_risk / 10)

        return {
            "gic_risk_pct": round(gic_risk, 1),
            "affected_regions": "High latitudes (>60°)" if lat_factor > 0.5 else "Minimal impact at this latitude",
            "impact_score": round(impact_score, 1),
            "impact_level": self._get_impact_label(impact_score),
            "description": self._get_power_description(impact_score, latitude),
            "recommendations": self._get_power_recommendations(impact_score)
        }

    def _calculate_overall_severity(
        self, probability: float, kp: float, tec: float
    ) -> float:
        """Calculate overall storm severity (1-10 scale)"""
        # Weighted combination
        prob_score = (probability / 100) * 10
        kp_score = (kp / 9) * 10
        tec_score = min(10, (tec / 50) * 10)  # Normalize to 50 TECU

        overall = (prob_score * 0.5 + kp_score * 0.3 + tec_score * 0.2)
        return round(overall, 1)

    # Helper methods for labels and descriptions
    def _get_severity_label(self, score: float) -> str:
        if score < 2:
            return "minimal"
        elif score < 4:
            return "low"
        elif score < 6:
            return "moderate"
        elif score < 8:
            return "high"
        else:
            return "severe"

    def _get_impact_label(self, score: float) -> str:
        return self._get_severity_label(score)

    def _get_gps_description(self, score: float) -> str:
        if score < 3:
            return "Normal GPS performance expected"
        elif score < 5:
            return "Minor GPS accuracy degradation possible"
        elif score < 7:
            return "Moderate GPS errors likely (5-15m)"
        elif score < 9:
            return "Significant GPS degradation (15-30m)"
        else:
            return "Severe GPS disruption possible (>30m errors)"

    def _get_gps_recommendations(self, score: float) -> list:
        if score < 5:
            return ["No special precautions needed"]
        elif score < 7:
            return [
                "Use DGPS or WAAS if available",
                "Increase position tolerance margins"
            ]
        else:
            return [
                "Avoid GPS-critical operations if possible",
                "Use alternative navigation (inertial, visual)",
                "Increase safety margins significantly"
            ]

    def _get_radio_description(self, score: float) -> str:
        if score < 3:
            return "Normal HF radio conditions"
        elif score < 5:
            return "Minor HF propagation disturbances"
        elif score < 7:
            return "Moderate HF signal degradation"
        elif score < 9:
            return "Severe HF propagation issues"
        else:
            return "HF radio blackout conditions likely"

    def _get_radio_recommendations(self, score: float) -> list:
        if score < 5:
            return ["Monitor conditions, no action needed"]
        elif score < 7:
            return [
                "Use lower frequencies when possible",
                "Increase transmit power if available",
                "Prepare backup communication methods"
            ]
        else:
            return [
                "Expect HF communication difficulties",
                "Switch to VHF/UHF or satellite communications",
                "Critical messages may not get through"
            ]

    def _get_radio_status(self, score: float) -> str:
        if score < 3:
            return "normal"
        elif score < 6:
            return "degraded"
        else:
            return "blackout_likely"

    def _get_satellite_description(self, score: float) -> str:
        if score < 3:
            return "Normal satellite operations expected"
        elif score < 5:
            return "Minor satellite impacts possible"
        elif score < 7:
            return "Moderate satellite operation challenges"
        elif score < 9:
            return "Significant satellite risks"
        else:
            return "Severe satellite environment"

    def _get_satellite_recommendations(self, score: float) -> list:
        if score < 5:
            return ["Normal operations, monitor conditions"]
        elif score < 7:
            return [
                "Increase orbit determination frequency",
                "Monitor surface charging",
                "Prepare for possible anomalies"
            ]
        else:
            return [
                "Delay non-essential maneuvers",
                "Increase telemetry monitoring",
                "Activate fault protection modes",
                "Expect increased atmospheric drag"
            ]

    def _get_power_description(self, score: float, latitude: float) -> str:
        if abs(latitude) < 45:
            return "Minimal power grid risk at this latitude"
        elif score < 5:
            return "Low GIC risk for power infrastructure"
        elif score < 7:
            return "Moderate GIC risk - monitor transformers"
        else:
            return "High GIC risk - potential transformer damage"

    def _get_power_recommendations(self, score: float) -> list:
        if score < 5:
            return ["Normal grid operations"]
        elif score < 7:
            return [
                "Monitor transformer temperatures",
                "Prepare for possible voltage fluctuations",
                "Have backup power ready for critical systems"
            ]
        else:
            return [
                "Consider reducing grid load if possible",
                "Closely monitor all transformers",
                "Prepare for potential localized outages",
                "Alert emergency services"
            ]

    def _get_default_assessment(self) -> Dict:
        """Return default assessment on error"""
        return {
            "gps": {"impact_score": 0, "impact_level": "unknown"},
            "radio": {"impact_score": 0, "impact_level": "unknown"},
            "satellite": {"impact_score": 0, "impact_level": "unknown"},
            "power_grid": {"impact_score": 0, "impact_level": "unknown"},
            "overall": {
                "severity_score": 0,
                "severity_level": "unknown",
                "confidence": "low"
            },
            "error": "Impact assessment failed"
        }
