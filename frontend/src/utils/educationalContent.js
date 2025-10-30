/**
 * Educational Content Library
 * Comprehensive information about ionospheric phenomena and metrics
 */

export const EDUCATIONAL_CONTENT = {
  // Main Concepts
  ionosphere: {
    title: "What is the Ionosphere?",
    content: `The ionosphere is a layer of Earth's atmosphere, extending from about 50 to 1,000 km altitude, where solar radiation ionizes atoms and molecules. This creates a region rich in free electrons and ions that affects radio wave propagation, GPS signals, and satellite communications.

Key characteristics:
• Divided into D, E, and F layers (F splits into F1 and F2)
• F2 layer (200-400 km) has highest electron density
• Highly variable due to solar activity, time of day, and season
• Critical for modern technology infrastructure`
  },

  tec: {
    title: "Total Electron Content (TEC)",
    content: `TEC measures the total number of electrons along a path through the ionosphere, typically from a GNSS satellite to a ground receiver.

Units: TECU (TEC Units)
• 1 TECU = 10¹⁶ electrons/m²

Typical values:
• Nighttime: 2-10 TECU
• Daytime: 10-40 TECU
• Equatorial region: Up to 100+ TECU
• Storm conditions: Can exceed 150 TECU

Impact: Higher TEC causes greater GPS signal delays, requiring corrections for accurate positioning. TEC variations indicate ionospheric disturbances that can affect communications and navigation.`
  },

  kpIndex: {
    title: "Kp Index - Geomagnetic Activity",
    content: `The planetary K-index (Kp) quantifies disturbances in Earth's magnetic field caused by solar wind interactions.

Scale: 0 to 9 (in thirds: 0, 0+, 1-, 1, 1+, etc.)

Classification:
• Kp 0-2: Quiet conditions
• Kp 3-4: Unsettled conditions
• Kp 5: Minor geomagnetic storm (G1)
• Kp 6: Moderate storm (G2)
• Kp 7: Strong storm (G3)
• Kp 8: Severe storm (G4)
• Kp 9: Extreme storm (G5)

Updated every 3 hours based on magnetometer data from 13 stations worldwide.

Why it matters: Higher Kp indicates stronger geomagnetic disturbances that can:
• Disrupt power grids
• Affect satellite operations
• Degrade GPS accuracy
• Enable aurora at lower latitudes
• Disturb HF radio communications`
  },

  solarWind: {
    title: "Solar Wind",
    content: `The solar wind is a stream of charged particles (mostly protons and electrons) continuously flowing from the Sun's corona.

Normal conditions:
• Speed: 300-500 km/s
• Density: 3-10 particles/cm³
• Temperature: ~100,000 K

High-speed streams: 600-800 km/s
• From coronal holes
• Can last several days
• Cause recurrent geomagnetic activity

Storm conditions: >1000 km/s
• Associated with Coronal Mass Ejections (CMEs)
• Can reach Earth in 15-18 hours
• Cause major geomagnetic storms

The solar wind carries the Sun's magnetic field (Interplanetary Magnetic Field, IMF) and transfers energy to Earth's magnetosphere, especially when IMF Bz turns southward.`
  },

  imfBz: {
    title: "IMF Bz Component",
    content: `The Bz component of the Interplanetary Magnetic Field (IMF) is the north-south component crucial for geomagnetic activity.

Direction matters:
• Northward (Bz > 0): Stable, reduced activity
  - Magnetic field lines don't easily reconnect
  - Protects Earth's magnetosphere

• Southward (Bz < 0): Unstable, enhanced activity
  - Enables magnetic reconnection
  - Transfers solar wind energy to magnetosphere
  - Primary trigger for geomagnetic storms

Critical thresholds:
• Bz < -5 nT: Moderate reconnection
• Bz < -10 nT: Strong reconnection
• Bz < -20 nT: Extreme conditions

A strong southward Bz combined with high solar wind speed creates the most severe space weather events. Even a moderate southward Bz sustained for several hours can trigger significant storms.`
  },

  f107: {
    title: "F10.7 Solar Flux",
    content: `The F10.7 index measures solar radio emissions at 10.7 cm wavelength (2800 MHz), serving as a proxy for overall solar activity.

Units: Solar Flux Units (sfu)
• 1 sfu = 10⁻²² W/(m²·Hz)

Typical values:
• Solar minimum: 60-90 sfu
• Solar moderate: 90-150 sfu
• Solar maximum: 150-250 sfu
• Extreme flares: >300 sfu

Why 10.7 cm?
• Correlates well with UV/EUV radiation
• Easily measured from ground
• Long historical record (since 1947)
• Not affected by ionospheric absorption

Relationship to ionosphere:
Higher F10.7 → More UV radiation → Increased ionization → Higher TEC

The F10.7 index helps predict ionospheric conditions, radio propagation, and satellite drag. It follows the ~11-year solar cycle.`
  },

  ionosphericStorms: {
    title: "Ionospheric Storms",
    content: `Ionospheric storms are large-scale disturbances in ionospheric electron density, primarily caused by geomagnetic storms.

Phases:
1. Initial phase (0-2 hours):
   - TEC may briefly increase
   - Enhanced equatorward winds

2. Main phase (2-12 hours):
   - Large TEC depletions at mid-latitudes
   - TEC enhancements at low latitudes
   - Irregular structures form

3. Recovery phase (12-72 hours):
   - Gradual return to normal
   - Can take several days

Causes:
• Enhanced electric fields
• Disturbed thermospheric winds
• Changes in neutral composition
• Particle precipitation

Impacts:
• GPS positioning errors (meters to 10s of meters)
• Loss of GPS signal lock
• HF radio blackouts or enhancements
• Increased satellite drag
• Scintillation (signal fading)

Not all geomagnetic storms cause ionospheric storms, and the response varies by latitude, local time, and season.`
  },

  predictionModel: {
    title: "Storm Prediction Model",
    content: `This system uses a hybrid CNN-LSTM deep learning model to predict ionospheric storms up to 24 hours in advance.

Architecture:
• Convolutional Neural Network (CNN) layers extract spatial patterns
• Long Short-Term Memory (LSTM) layers capture temporal dependencies
• Multi-task learning predicts both storm probability and TEC values

Input features (8 dimensions):
1. TEC mean and standard deviation
2. Kp index (geomagnetic activity)
3. Solar wind speed
4. IMF Bz component
5. F10.7 solar flux
6. Hour of day (cyclical encoding)
7. Day of year (seasonal effects)

The model analyzes 24 hours of historical data to forecast:
• Overall storm probability (0-100%)
• Hourly probabilities for next 24 hours
• TEC forecast for next 24 hours
• Risk classification (low/moderate/elevated/high/severe)

Based on research from:
• Ren et al. (2024) - Mixed CNN-BiLSTM methods
• Ban et al. (2023) - Regional LSTM forecasting
• Multiple studies on deep learning for space weather

Accuracy: Typical ML models achieve 85-90% accuracy for storm detection, with lower accuracy during extreme events.`
  },

  scintillation: {
    title: "Ionospheric Scintillation",
    content: `Scintillation refers to rapid fluctuations in GNSS signal amplitude and phase caused by ionospheric irregularities.

Types:
• Amplitude scintillation (S4 index): Signal fading
• Phase scintillation (σφ): Carrier phase variations

S4 Index scale:
• S4 < 0.3: Weak scintillation
• S4 0.3-0.6: Moderate
• S4 0.6-1.0: Strong
• S4 > 1.0: Severe (signal loss possible)

Common causes:
• Equatorial plasma bubbles
• Polar cap patches
• Auroral irregularities
• Storm-enhanced density structures

Geographic distribution:
• Most severe: Equatorial regions (±20° lat)
• Moderate: High latitudes (>60° lat)
• Least: Mid-latitudes

ROTI (Rate of TEC Index) serves as a proxy for scintillation, calculated from standard GNSS receivers.

Effects:
• GPS position errors
• Loss of signal lock
• Reduced availability of satellites
• Impact on aviation, maritime navigation`
  },

  dataSource: {
    title: "Data Sources",
    content: `This system integrates real-time data from multiple authoritative sources:

NOAA Space Weather Prediction Center (SWPC):
• Kp and Dst indices
• Solar wind plasma data
• Magnetic field measurements
• Geomagnetic storm forecasts
• Updated every 1-3 hours

NASA CDDIS (Crustal Dynamics Data Information System):
• Global Ionosphere Maps (GIM)
• GNSS TEC products
• Ionospheric delay data
• Real-time and archived data

NOAA GloTEC:
• Global operational TEC product (2025)
• Vertical and slant TEC
• Near real-time updates
• COSMIC-2 satellite data integration

GOES Satellites:
• Real-time magnetometer data
• Solar X-ray flux
• Energetic particle measurements

All data is collected automatically every 5 minutes, with predictions updated hourly using the latest measurements.`
  },

  applications: {
    title: "Real-World Applications",
    content: `Ionospheric storm predictions are critical for numerous sectors:

Aviation:
• GPS-based navigation (Required Navigation Performance)
• Automatic Dependent Surveillance-Broadcast (ADS-B)
• Wide Area Augmentation System (WAAS) integrity
• Polar route HF communications

Maritime:
• Vessel positioning and navigation
• Dynamic positioning systems for offshore platforms
• Maritime safety communications

Satellite Operations:
• Satellite tracking and orbit determination
• Collision avoidance maneuvers
• Satellite drag estimation
• Communication link budgets

Power Grid Management:
• Geomagnetically Induced Current (GIC) warnings
• Transformer protection
• Grid stability monitoring

Military & Defense:
• Over-the-horizon radar
• Secure communications
• Missile defense systems
• Navigation warfare assessment

Survey & Mapping:
• High-precision GNSS surveying
• Real-Time Kinematic (RTK) positioning
• Geodetic control networks

Telecommunications:
• HF radio propagation forecasting
• Satellite communication link planning
• Emergency communication readiness

Early warning of ionospheric disturbances allows operators to:
• Switch to backup systems
• Adjust observation schedules
• Implement mitigation strategies
• Inform stakeholders of potential impacts`
  }
};

// Helper function to get content
export const getEducationalContent = (key) => {
  return EDUCATIONAL_CONTENT[key] || { title: "Information", content: "Content not available" };
};
