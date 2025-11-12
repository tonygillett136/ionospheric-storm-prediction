"""
Regional Prediction Service

Generates region-specific TEC predictions using the scientifically-validated
Climatology-Primary approach with regional adjustment factors.

Based on 90-day backtest experiment (REGIONAL_EXPERIMENT_REPORT.md):
- Climatology-Primary wins in 4/5 regions with high confidence
- Superior MAE and RMSE across Mid-Latitude, Auroral, Polar, and Global regions
- Uses physics-based regional factors validated by experimental data

This addresses the fundamental limitation of global predictions: a storm that's
"moderate" globally might be "extreme" in auroral zones but "mild" at the equator.
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.geographic_climatology_service import (
    GeographicClimatologyService,
    GeographicRegion
)
import logging

logger = logging.getLogger(__name__)


class RegionalRiskLevel:
    """Regional risk level definitions with region-specific thresholds"""

    # Risk thresholds by region (TEC in TECU)
    # Different regions have different baselines, so thresholds differ
    THRESHOLDS = {
        'equatorial': {
            'low': 18,      # Equatorial has high baseline
            'moderate': 25,
            'high': 35,
            'extreme': 45
        },
        'mid_latitude': {
            'low': 12,      # Mid-latitude is the reference
            'moderate': 18,
            'high': 25,
            'extreme': 35
        },
        'auroral': {
            'low': 10,      # Auroral has lower baseline but high variability
            'moderate': 15,
            'high': 22,
            'extreme': 30
        },
        'polar': {
            'low': 8,       # Polar has lowest baseline
            'moderate': 12,
            'high': 18,
            'extreme': 25
        },
        'global': {
            'low': 12,      # Global average
            'moderate': 18,
            'high': 25,
            'extreme': 35
        }
    }

    @classmethod
    def assess_risk(cls, region_code: str, tec: float) -> Dict:
        """
        Assess risk level for a region based on TEC value.

        Returns risk level, color, and description.
        """
        thresholds = cls.THRESHOLDS.get(region_code, cls.THRESHOLDS['global'])

        if tec < thresholds['low']:
            level = 'LOW'
            color = '#10b981'  # Green
            severity = 1
            description = 'Minimal ionospheric disturbance. Normal GPS and communication conditions.'
        elif tec < thresholds['moderate']:
            level = 'MODERATE'
            color = '#fbbf24'  # Yellow
            severity = 2
            description = 'Moderate ionospheric activity. Minor GPS and HF radio impacts possible.'
        elif tec < thresholds['high']:
            level = 'HIGH'
            color = '#f97316'  # Orange
            severity = 3
            description = 'Elevated ionospheric disturbance. GPS errors 3-5m, HF radio disruption likely.'
        elif tec < thresholds['extreme']:
            level = 'SEVERE'
            color = '#ef4444'  # Red
            severity = 4
            description = 'Severe ionospheric storm. Significant GPS degradation, satellite communication issues.'
        else:
            level = 'EXTREME'
            color = '#991b1b'  # Dark Red
            severity = 5
            description = 'Extreme ionospheric storm. Major GPS outages possible, widespread communication disruption.'

        return {
            'level': level,
            'severity': severity,
            'color': color,
            'description': description,
            'tec': round(float(tec), 2)
        }


class RegionalEnsembleService:
    """Service for generating region-specific predictions using Climatology-Primary approach

    This approach was scientifically validated through 90-day backtesting and proven
    to outperform ML-enhanced approaches in 4 out of 5 geographic regions.
    """

    def __init__(
        self,
        geographic_climatology: GeographicClimatologyService
    ):
        """
        Initialize regional prediction service.

        Args:
            geographic_climatology: Geographic climatology service with regional bins
        """
        self.geographic_climatology = geographic_climatology

    def generate_regional_predictions(
        self,
        current_conditions: Dict,
        forecast_hours: int = 24
    ) -> Dict:
        """
        Generate predictions for all geographic regions.

        Args:
            current_conditions: Current space weather conditions
                {
                    'kp_index': float,
                    'dst_index': float,
                    'solar_wind_speed': float,
                    'imf_bz': float,
                    'f107_flux': float
                }
            forecast_hours: Hours ahead to forecast

        Returns:
            Regional predictions with risk assessments
        """
        # Get Kp for climatology
        kp = current_conditions.get('kp_index', 3.0)

        # Use global climatology as baseline
        global_climatology_tec = self.geographic_climatology.get_climatology_forecast(
            'global',
            datetime.utcnow(),
            kp
        )

        # If no climatology available, use historical average
        global_tec = global_climatology_tec if global_climatology_tec else 12.74

        # Generate prediction for each region
        regional_predictions = {}
        regional_risks = []

        for region in GeographicRegion.get_all_regions():
            region_code = region['code']

            # CLIMATOLOGY-PRIMARY APPROACH (Experimentally Validated)
            # Get climatology forecast for this region
            climatology_forecast = self.geographic_climatology.get_climatology_forecast(
                region_code,
                datetime.utcnow(),
                kp
            )

            # Use climatology as primary forecast
            # Apply regional adjustments to global climatology if regional data unavailable
            if climatology_forecast:
                regional_tec = climatology_forecast
            else:
                # Fallback: Apply regional factors to global baseline
                regional_tec = self._adjust_for_region(
                    global_tec,
                    kp,
                    region
                )

            # Apply storm enhancement during active geomagnetic storms
            # This is critical for real-time forecasting during storm conditions
            if kp >= 5.0:
                regional_tec = self._apply_storm_enhancement(
                    regional_tec,
                    kp,
                    region_code,
                    current_conditions
                )

            # Assess risk level
            risk = RegionalRiskLevel.assess_risk(region_code, regional_tec)

            # Calculate percentage change from regional climatological normal
            if climatology_forecast and climatology_forecast > 0:
                change_pct = ((regional_tec - climatology_forecast) / climatology_forecast) * 100
            else:
                change_pct = 0

            regional_predictions[region_code] = {
                'region': region['name'],
                'code': region_code,
                'lat_range': region['lat_range'],
                'description': region['description'],
                'tec': round(float(regional_tec), 2),
                'climatology_normal': round(float(climatology_forecast), 2) if climatology_forecast else None,
                'change_percent': round(float(change_pct), 1),
                'risk': risk,
                'approach': 'Climatology-Primary',
                'validation': 'Experimentally validated (90-day backtest)'
            }

            regional_risks.append({
                'region': region['name'],
                'code': region_code,
                'severity': risk['severity'],
                'tec': regional_tec
            })

        # Identify most affected region
        most_affected = max(regional_risks, key=lambda x: x['severity'])

        # Identify region with highest TEC
        highest_tec_region = max(regional_risks, key=lambda x: x['tec'])

        # Calculate global risk based on weighted average
        global_risk_level = self._calculate_global_risk(regional_predictions)

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'forecast_hours': forecast_hours,
            'global_overview': {
                'tec': round(float(global_tec), 2),
                'risk': global_risk_level,
                'kp_index': round(float(kp), 1)
            },
            'regional_predictions': regional_predictions,
            'highlights': {
                'most_affected_region': most_affected['code'],
                'most_affected_name': most_affected['region'],
                'highest_severity': most_affected['severity'],
                'highest_tec_region': highest_tec_region['code'],
                'highest_tec_value': round(float(highest_tec_region['tec']), 2),
                'message': self._generate_highlight_message(most_affected, regional_predictions)
            }
        }

    def _adjust_for_region(
        self,
        global_tec: float,
        kp: float,
        region: Dict
    ) -> float:
        """
        Adjust global TEC prediction for regional characteristics.

        Uses same approach as geographic climatology service.
        """
        baseline_factor = region['baseline_factor']
        variability_factor = region['variability_factor']

        # Base adjustment
        regional_tec = global_tec * baseline_factor

        # During storms (Kp > 5), apply enhanced regional variability
        if kp > 5:
            global_avg = 12.74  # Historical global average
            storm_excess = (global_tec - global_avg) * variability_factor
            regional_tec = (global_avg * baseline_factor) + storm_excess

        return max(0, regional_tec)

    def _apply_storm_enhancement(
        self,
        baseline_tec: float,
        kp: float,
        region_code: str,
        current_conditions: Dict
    ) -> float:
        """
        Apply storm-time enhancements to TEC based on current geomagnetic activity.

        During storms (Kp >= 5), TEC increases above climatological norms.
        Enhancement varies by:
        - Storm intensity (Kp index)
        - Geographic region (auroral zones most affected)
        - Solar wind parameters

        Args:
            baseline_tec: Climatological TEC value
            kp: Current Kp index
            region_code: Geographic region
            current_conditions: Current space weather parameters

        Returns:
            Enhanced TEC value accounting for storm conditions
        """
        # Storm enhancement factors by region (empirically derived)
        # These represent how much TEC increases during storms relative to quiet-time
        regional_storm_response = {
            'equatorial': 1.15,      # Modest enhancement (equatorial anomaly effects)
            'mid_latitude': 1.35,    # Moderate enhancement (main phase effects)
            'auroral': 1.65,         # Strong enhancement (particle precipitation)
            'polar': 1.45,           # Moderate-strong (cusp/cap effects)
            'global': 1.30           # Average response
        }

        response_factor = regional_storm_response.get(region_code, 1.30)

        # Calculate storm intensity factor based on Kp
        # Kp=5 (G1): minor enhancement
        # Kp=7 (G3): moderate enhancement
        # Kp=9 (G5): extreme enhancement
        if kp < 5:
            storm_intensity = 0.0  # No enhancement
        elif kp < 6:
            storm_intensity = 0.20  # G1 Minor: 20% enhancement
        elif kp < 7:
            storm_intensity = 0.35  # G2 Moderate: 35% enhancement
        elif kp < 8:
            storm_intensity = 0.55  # G3 Strong: 55% enhancement
        elif kp < 9:
            storm_intensity = 0.75  # G4 Severe: 75% enhancement
        else:
            storm_intensity = 1.00  # G5 Extreme: 100% enhancement

        # Apply regional response to storm intensity
        enhancement_factor = 1.0 + (storm_intensity * (response_factor - 1.0))

        # Additional boost for high solar wind speed (>600 km/s indicates strong driving)
        solar_wind_speed = current_conditions.get('solar_wind_speed', 400)
        if solar_wind_speed > 600:
            speed_boost = min((solar_wind_speed - 600) / 400, 0.2)  # Up to 20% extra
            enhancement_factor += speed_boost

        # Apply enhancement
        enhanced_tec = baseline_tec * enhancement_factor

        logger.info(
            f"Storm enhancement for {region_code}: Kp={kp:.1f}, "
            f"baseline={baseline_tec:.1f}, enhanced={enhanced_tec:.1f} "
            f"(+{(enhancement_factor-1)*100:.1f}%)"
        )

        return enhanced_tec

    def _calculate_global_risk(self, regional_predictions: Dict) -> Dict:
        """
        Calculate overall global risk level based on regional predictions.

        Uses population-weighted approach (mid-latitudes matter most).
        """
        # Weight regions by Earth's surface area and population
        weights = {
            'equatorial': 0.25,    # Large area, high population
            'mid_latitude': 0.40,  # Most populated regions
            'auroral': 0.20,       # Moderate area
            'polar': 0.05,         # Small area, low population
            'global': 0.10         # Reference
        }

        weighted_severity = sum(
            regional_predictions[code]['risk']['severity'] * weights.get(code, 0.2)
            for code in regional_predictions
        )

        # Convert weighted severity back to risk level
        if weighted_severity < 1.5:
            level = 'LOW'
            color = '#10b981'
        elif weighted_severity < 2.5:
            level = 'MODERATE'
            color = '#fbbf24'
        elif weighted_severity < 3.5:
            level = 'HIGH'
            color = '#f97316'
        elif weighted_severity < 4.5:
            level = 'SEVERE'
            color = '#ef4444'
        else:
            level = 'EXTREME'
            color = '#991b1b'

        return {
            'level': level,
            'severity': round(weighted_severity, 1),
            'color': color
        }

    def _generate_highlight_message(
        self,
        most_affected: Dict,
        regional_predictions: Dict
    ) -> str:
        """Generate a human-readable highlight message."""
        region_name = most_affected['region']
        severity = most_affected['severity']

        region_data = regional_predictions[most_affected['code']]
        change_pct = region_data['change_percent']

        if severity >= 4:
            return f"⚡ SEVERE STORM impacting {region_name} regions ({change_pct:+.0f}% above normal)"
        elif severity >= 3:
            return f"⚠️ Elevated conditions in {region_name} zones ({change_pct:+.0f}% above normal)"
        elif severity >= 2:
            return f"Moderate activity in {region_name} regions ({change_pct:+.0f}% from normal)"
        else:
            return f"Quiet conditions across all regions"

    async def generate_regional_time_evolution(
        self,
        session: AsyncSession,
        region_code: str,
        hours: int = 24,
        interval_hours: int = 1
    ) -> Dict:
        """
        Generate time evolution forecast for a specific region.

        Args:
            session: Database session
            region_code: Geographic region code
            hours: Hours to forecast ahead
            interval_hours: Time step interval

        Returns:
            Time series of regional predictions
        """
        region = GeographicRegion.get_region_by_code(region_code)
        if not region:
            raise ValueError(f"Invalid region code: {region_code}")

        # Get current conditions (would come from data service in production)
        # For now, use moderate defaults
        current_kp = 3.0

        time_series = []
        current_time = datetime.utcnow()

        for hour_offset in range(0, hours + 1, interval_hours):
            forecast_time = current_time + timedelta(hours=hour_offset)

            # Get climatology forecast for this time
            climatology_tec = self.geographic_climatology.get_climatology_forecast(
                region_code,
                forecast_time,
                current_kp  # In production, would forecast Kp evolution too
            )

            if climatology_tec:
                risk = RegionalRiskLevel.assess_risk(region_code, climatology_tec)

                time_series.append({
                    'timestamp': forecast_time.isoformat(),
                    'hour_offset': hour_offset,
                    'tec': round(float(climatology_tec), 2),
                    'risk_level': risk['level'],
                    'risk_severity': risk['severity']
                })

        return {
            'region': region['name'],
            'code': region_code,
            'forecast_start': current_time.isoformat(),
            'forecast_hours': hours,
            'time_series': time_series
        }
