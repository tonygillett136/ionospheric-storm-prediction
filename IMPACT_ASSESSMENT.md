# Impact Assessment Feature

## Overview

The Impact Assessment feature translates ionospheric storm predictions into concrete, actionable impacts for four critical infrastructure systems:

1. **GPS Navigation** - Accuracy degradation estimates
2. **HF Radio Communications** - Blackout probabilities by frequency band
3. **Satellite Operations** - Drag, charging, and SEU risks
4. **Power Grid** - GIC (Geomagnetically Induced Current) risks

## Access

Navigate to the **🎯 Impact Assessment** tab in the main application.

## Features

### Overall Severity Score
- **Scale**: 1-10
- **Levels**: Minimal, Low, Moderate, High, Severe
- **Calculation**: Weighted combination of storm probability (50%), Kp index (30%), and TEC (20%)

### GPS Impact
**Metrics**:
- Normal accuracy: ~3.5m
- Degraded accuracy: Calculated based on current conditions
- Accuracy loss percentage

**Scientific Basis**: Klobuchar ionospheric model

**Impact Factors**:
- TEC (Total Electron Content)
- Kp index (geomagnetic activity)
- Storm probability
- Latitude (higher impact at polar regions)

**Example**: During moderate storm (Kp=3, TEC=23 TECU, 76% probability):
- GPS accuracy degrades from 3.5m to 25.6m
- 630% accuracy loss
- Impact score: 8.5/10 (Severe)

**Recommendations** (varies by severity):
- Low: No special precautions
- Moderate: Use DGPS/WAAS, increase margins
- High/Severe: Avoid GPS-critical operations, use alternative navigation

### HF Radio Impact
**Metrics**:
- Blackout probability (0-95%)
- Frequency-dependent impacts:
  - Low band (3-10 MHz): Most affected
  - Mid band (10-20 MHz): Moderately affected
  - High band (20-30 MHz): Least affected

**Scientific Basis**: ITU radio propagation standards

**Impact Factors**:
- Storm probability
- Kp index
- TEC (absorption effects)

**Recommendations**:
- Low: Monitor conditions
- Moderate: Use lower frequencies, increase power
- High/Severe: Switch to VHF/UHF or satellite comms

### Satellite Operations Impact
**Metrics**:
- Atmospheric drag multiplier (1.0x → 2-10x normal)
- Surface charging risk (0-95%)
- Single Event Upset (SEU) risk (0-90%)

**Impact Factors**:
- Storm probability
- Kp index
- Dst index (magnetic storm intensity)

**Recommendations**:
- Low: Normal operations
- Moderate: Increase orbit determination frequency, monitor charging
- High/Severe: Delay maneuvers, activate fault protection

### Power Grid Impact
**Metrics**:
- GIC risk (0-95%)
- Regional effects (latitude-dependent)

**Geographic Sensitivity**:
- Below 45°: Minimal risk (10% factor)
- 45-60°: Moderate risk (50% factor)
- Above 60°: High risk (100% factor)

**Impact Factors**:
- Storm probability
- Kp index
- Geographic latitude

**Recommendations**:
- Low: Normal operations
- Moderate: Monitor transformer temperatures
- High/Severe: Reduce grid load, prepare for outages

## Regional Customization

Use the **latitude selector** to adjust impacts for your location:
- Equator (0°)
- Low Latitude (30°)
- Mid Latitude (45°)
- High Latitude (60°)
- Polar (75°)

Higher latitudes experience greater GPS and power grid impacts.

## API Endpoint

```bash
GET /api/v1/impact-assessment?latitude=45.0
```

**Response**:
```json
{
  "gps": {
    "normal_accuracy_m": 3.5,
    "degraded_accuracy_m": 25.6,
    "accuracy_loss_pct": 630.0,
    "impact_score": 8.5,
    "impact_level": "severe",
    "description": "Significant GPS degradation (15-30m)",
    "recommendations": [...]
  },
  "radio": {
    "blackout_probability_pct": 95,
    "frequency_impacts": {...},
    "impact_score": 7.9,
    "recommendations": [...]
  },
  "satellite": {
    "atmospheric_drag_multiplier": 2.15,
    "surface_charging_risk_pct": 95,
    "single_event_upset_risk_pct": 82.1,
    "impact_score": 6.6,
    "recommendations": [...]
  },
  "power_grid": {
    "gic_risk_pct": 53.2,
    "impact_score": 5.3,
    "recommendations": [...]
  },
  "overall": {
    "severity_score": 5.7,
    "severity_level": "moderate"
  },
  "metadata": {
    "probability_24h": 76.41,
    "probability_48h": 68.77,
    "kp_index": 3.0,
    "tec_mean": 23.1
  }
}
```

## Use Cases

### Aviation
- **Use**: Pre-flight planning, polar route decisions
- **Metrics**: GPS accuracy, HF radio blackout
- **Threshold**: Avoid GPS-critical ops when impact score > 7

### Satellite Operations
- **Use**: Maneuver planning, anomaly preparedness
- **Metrics**: Drag multiplier, charging risk, SEU risk
- **Threshold**: Delay non-essential maneuvers when impact score > 6

### Power Grid Operators
- **Use**: Transformer protection, load balancing
- **Metrics**: GIC risk (high-latitude only)
- **Threshold**: Alert when GIC risk > 50% and latitude > 60°

### Maritime/Emergency Communications
- **Use**: Backup communication planning
- **Metrics**: HF radio blackout probability
- **Threshold**: Activate backup comms when blackout probability > 60%

### Survey & Precision Agriculture
- **Use**: Delay high-precision GNSS work
- **Metrics**: GPS accuracy degradation
- **Threshold**: Postpone when accuracy > 10m

## Scientific References

1. **Klobuchar, J.A.** (1987). "Ionospheric Time-Delay Algorithm for Single-Frequency GPS Users"
2. **NOAA Space Weather Prediction Center** - Storm scale guidelines
3. **ITU-R P.533** - HF propagation prediction method
4. **Boteler, D.H.** (2019). "A 21st Century View of the March 1989 Magnetic Storm"

## Implementation Details

**Backend Service**: `backend/app/services/impact_assessment_service.py`
**API Route**: `backend/app/api/routes.py:471-518`
**Frontend Component**: `frontend/src/components/ImpactDashboard.jsx`

**Total Code**: ~800 lines
**Testing**: Validated against current real-world conditions

## Future Enhancements

Potential additions (not currently implemented):
- Historical impact database
- Industry-specific impact models (aviation, maritime, etc.)
- Impact forecasts for 48h and 72h horizons
- SMS/email alerts for high-impact events
- Detailed satellite orbit perturbation calculations
- Power grid vulnerability maps
