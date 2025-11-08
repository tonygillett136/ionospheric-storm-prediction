# Diagram Specifications for Science Guide

## Overview

These diagrams are designed to complement the Science Guide with clear, professional visualizations. Each spec includes layout, colors, labels, and design notes for implementation.

---

## Diagram 1: Ionospheric Layers

**Purpose:** Show the vertical structure of Earth's atmosphere with ionospheric layers

**Type:** Vertical cutaway diagram

**Dimensions:** 800px × 1000px

**Layout:**
- Earth surface at bottom
- Vertical scale on left (0-1000 km altitude)
- Atmospheric layers stacked vertically
- Ionospheric layers overlaid with transparency

**Elements:**

1. **Earth Surface (0 km)**
   - Color: #2d5016 (green/brown landmass)
   - Ocean: #1e40af (blue)
   - Thin line representing surface

2. **Troposphere (0-15 km)**
   - Color: #bae6fd (light blue), 80% opacity
   - Label: "Troposphere" + "Weather occurs here"
   - Clouds illustrated at 5-10 km

3. **Stratosphere (15-50 km)**
   - Color: #7dd3fc (blue), 60% opacity
   - Label: "Stratosphere" + "Ozone layer"
   - Thin ozone band at 20-30 km (darker blue)

4. **D Region (50-90 km)**
   - Color: #fef3c7 (pale yellow), 40% opacity
   - Label: "D Region" + "Daytime only"
   - Icon: ☀️ with arrow pointing to layer
   - Dashed outline (exists only in daylight)

5. **E Region (90-150 km)**
   - Color: #fde68a (yellow), 50% opacity
   - Label: "E Region" + "Meteor ionization"
   - Icon: ☄️ meteor trail illustrated
   - Solid outline

6. **F1 Region (150-220 km)**
   - Color: #fed7aa (orange), 60% opacity
   - Label: "F1 Region" + "Merges with F2 at night"
   - Dashed vertical divider showing day/night difference

7. **F2 Region (220-500 km)**
   - Color: #fdba74 (deep orange), 70% opacity
   - Label: "F2 Region" + "Peak electron density"
   - Thicker border (most important layer)
   - Peak density line at ~300 km

8. **Thermosphere (500-1000 km)**
   - Color: gradient from #f97316 to #7c2d12
   - Label: "Thermosphere" + "Satellites orbit here"
   - ISS icon at 400 km
   - Satellite icons at various altitudes

**Additional Annotations:**
- GPS signal path illustrated (diagonal line through all layers)
- Signal delay indication: "GPS delay occurs here" arrow
- Temperature scale on right: "Temperature increases with altitude (paradox!)"
- Day/night division (vertical split showing difference)

**Color Scheme:**
- Cooler colors (blues) for lower atmosphere
- Warmer colors (yellows/oranges) for ionosphere
- Gradient to red for upper thermosphere

---

## Diagram 2: TEC and GPS Error Relationship

**Purpose:** Visual explanation of how TEC causes GPS positioning errors

**Type:** Infographic with satellite-to-ground signal path

**Dimensions:** 1000px × 600px

**Layout:**

**Left Panel (40%):**
- GPS satellite at top
- Signal path (wavy line) through ionosphere to ground receiver
- Color-coded path based on TEC level

**Right Panel (60%):**
- Bar chart showing TEC values vs. GPS errors
- Real-world impact annotations

**Elements:**

1. **GPS Satellite**
   - Icon: 🛰️ detailed satellite illustration
   - Label: "GPS Satellite (20,200 km altitude)"
   - Signal beam emanating downward

2. **Ionosphere Layer**
   - Semi-transparent orange cloud (100-1000 km altitude)
   - Free electrons illustrated as small dots
   - Density increases with TEC
   - Label: "Ionosphere - Free electrons slow signal"

3. **Signal Path**
   - Wavy line showing signal propagation
   - Delays illustrated with clock symbols
   - Formula shown: "Delay ∝ TEC (Total Electron Content)"

4. **Ground Receiver**
   - Icon: GPS receiver / smartphone
   - Crosshair target showing position
   - Error circle illustrated (larger for higher TEC)

**Bar Chart (Right Panel):**

X-axis: TEC (TECU) - values: 5, 10, 20, 40, 80, 100
Y-axis: GPS Error (meters) - values: 0, 5, 10, 15, 20

**Bars:**
- 5 TECU → 0.8m (green, "Excellent")
- 10 TECU → 1.6m (green, "Good")
- 20 TECU → 3.2m (yellow, "Degraded")
- 40 TECU → 6.4m (orange, "Impaired")
- 80 TECU → 12.8m (red, "Major Errors")
- 100 TECU → 16m (dark red, "Critical")

**Annotations:**
- Green zone: "Normal GPS accuracy"
- Yellow zone: "Precision approaches affected"
- Orange zone: "Surveying impacted"
- Red zone: "Navigation unreliable"

**Formula Box:**
- "GPS Error ≈ 0.16 × TEC (in meters)"
- "For L1 frequency (1575.42 MHz)"

**Color Palette:**
- Signal: #3b82f6 (blue)
- Ionosphere: #fb923c (orange glow)
- Errors: gradient from #10b981 → #fbbf24 → #ef4444

---

## Diagram 3: Sun-Earth Connection

**Purpose:** Show how solar phenomena affect Earth's ionosphere

**Type:** Space weather flow diagram

**Dimensions:** 1200px × 800px

**Layout:**
- Sun on left
- Earth on right
- Multiple interaction pathways between them

**Elements:**

1. **The Sun (Left)**
   - Large yellow circle with corona
   - Sunspot groups visible
   - Solar flare illustrated (bright flash)
   - CME eruption (cloud of particles)

2. **Solar Radiation**
   - Wavy lines: EUV and X-rays
   - Color: #fbbf24 (yellow/orange)
   - Label: "EUV & X-rays (8 min to Earth)"
   - Arrow pointing to Earth's dayside

3. **Solar Wind**
   - Blue streamlines flowing from Sun
   - Particles illustrated
   - Speed annotation: "400-800 km/s typical, 1000+ during storms"
   - Label: "Solar Wind (1-3 days to Earth)"

4. **Coronal Mass Ejection (CME)**
   - Large bubble of plasma
   - Magnetic field lines illustrated
   - Color: #f87171 (reddish)
   - Label: "CME - Billions of tons of plasma"
   - Timeline: "Impact in 1-3 days"

5. **Earth and Magnetosphere**
   - Earth (blue/green) with magnetic field lines
   - Magnetosphere compressed on dayside
   - Magnetotail stretched on nightside
   - Bow shock illustrated

6. **Interaction Points**
   - **Point A: Dayside Ionosphere**
     - EUV arrow hitting upper atmosphere
     - Ionization illustrated (atoms → ions + electrons)
     - Label: "Photoionization creates TEC"

   - **Point B: Magnetopause**
     - Solar wind impact point
     - Magnetic reconnection illustrated
     - Label: "When IMF Bz negative, energy enters"

   - **Point C: Polar Regions**
     - Particles funneling down field lines
     - Aurora illustrated (green/red)
     - Label: "Particle precipitation enhances TEC"

   - **Point D: Ring Current**
     - Doughnut-shaped current around Earth
     - Label: "Ring current creates Dst index"

**Callout Boxes:**

1. **Solar Activity:**
   - F10.7 flux meter
   - "Measures solar EUV output"
   - Current value shown

2. **IMF Bz:**
   - Arrow showing north/south direction
   - "North (+) = shield locked 🔒"
   - "South (-) = shield unlocked 🔓"

3. **Storm Development:**
   - Timeline: "0h: CME impact → 6h: Main phase → 24h: Peak → 72h: Recovery"

**Color Coding:**
- Sun: #fbbf24 (yellow)
- Solar wind: #60a5fa (blue)
- CME: #f87171 (red)
- Earth: #10b981 (green)
- Magnetosphere: #a78bfa (purple field lines)

---

## Diagram 4: Regional TEC Differences

**Purpose:** Show why same TEC means different things at different latitudes

**Type:** Cross-section of Earth with TEC profiles

**Dimensions:** 1000px × 700px

**Layout:**
- Earth cross-section (pole to pole)
- TEC profiles above each latitude
- Color-coded risk levels

**Elements:**

1. **Earth Cross-Section**
   - Semicircle showing poles and equator
   - Latitude lines: 90°N, 70°N, 50°N, 20°N, 0°, 20°S, 50°S, 70°S, 90°S
   - Magnetic field lines overlaid

2. **Regional Zones (Marked)**
   - **Polar (>70°):** Light blue shading
   - **Auroral (50-70°):** Green shading
   - **Mid-Latitude (20-50°):** Yellow shading
   - **Equatorial (±20°):** Orange shading

3. **TEC Profiles (Vertical bars above each zone)**
   - Height represents typical TEC value
   - Color represents risk level
   - All profiles shown for same storm condition (e.g., Kp=6)

   **Profiles shown:**
   - **Equatorial:** 45 TECU (green bar, "LOW risk - below normal")
   - **Mid-Latitude:** 25 TECU (orange bar, "HIGH risk")
   - **Auroral:** 25 TECU (red bar, "SEVERE risk")
   - **Polar:** 25 TECU (dark red bar, "EXTREME risk")

4. **Baseline Comparison**
   - Dashed line showing "normal" TEC for each zone
   - Equatorial: 35 TECU normal
   - Mid-Latitude: 18 TECU normal
   - Auroral: 12 TECU normal
   - Polar: 9 TECU normal

5. **Impact Icons**
   - At each zone, show what 25 TECU means:
     - Equatorial: ✅ "Normal operations"
     - Mid-Latitude: ⚠️ "GPS degraded 3-5m"
     - Auroral: ❌ "Major disruptions"
     - Polar: ⚠️⚠️ "Critical - GPS >10m error"

**Callout Boxes:**

**"Why Differences?"**
- Equatorial: "Plasma fountain, natural enhancement"
- Mid-Latitude: "Reference zone, typical ionosphere"
- Auroral: "Particle precipitation during storms"
- Polar: "Lowest baseline, extreme sensitivity"

**Color Scheme:**
- Risk levels: Green → Yellow → Orange → Red → Dark Red
- Earth: Blue/green
- Magnetic field lines: Purple
- TEC bars: Gradient based on risk

---

## Diagram 5: Storm Anatomy Timeline

**Purpose:** Show the phases of an ionospheric storm from start to finish

**Type:** Horizontal timeline with phases

**Dimensions:** 1200px × 600px

**Layout:**
- Horizontal timeline from T-48h to T+72h
- Multiple parameter tracks (Kp, Dst, TEC, IMF Bz)
- Phase annotations

**Elements:**

1. **Timeline (X-axis)**
   - T-48h to T+72h (120 hours total)
   - Marked in 12-hour increments
   - Phases color-coded

2. **Trigger Phase (T-48 to T0)**
   - Background: Light blue
   - Events shown:
     - T-48h: Solar flare (X-class)
     - T-47h: CME eruption
     - T-2h: Solar wind shock arrival
     - T0: IMF Bz turns south

3. **Main Phase (T0 to T+6h)**
   - Background: Orange gradient
   - Events:
     - T0: Storm onset
     - T+2h: Kp reaches 7
     - T+4h: Dst minimum (-150 nT)
     - T+6h: TEC peaks

4. **Peak Phase (T+6 to T+24h)**
   - Background: Red
   - Events:
     - T+12h: Maximum TEC (80 TECU)
     - T+18h: Auroral activity peak
     - T+24h: Begin recovery

5. **Recovery Phase (T+24 to T+72h)**
   - Background: Yellow gradient to green
   - Events:
     - T+36h: Kp drops below 5
     - T+48h: TEC returns to normal
     - T+72h: Quiet conditions restored

**Parameter Tracks:**

**Track 1: Kp Index**
- Y-axis: 0-9
- Line color: #fbbf24 (yellow)
- Shows: Quiet (0-2) → Spike to 8 → Gradual return

**Track 2: Dst Index**
- Y-axis: +20 to -200 nT
- Line color: #ef4444 (red)
- Shows: Slight rise → Plunge to -150 nT → Slow recovery

**Track 3: TEC**
- Y-axis: 0-100 TECU
- Line color: #3b82f6 (blue)
- Shows: Baseline 20 → Peak 80 → Return to 25

**Track 4: IMF Bz**
- Y-axis: -15 to +15 nT
- Line color: #10b981 (green positive, red negative)
- Shows: Neutral → Strongly negative → Recovery

**Annotations:**

- "Solar flare" icon and label at T-48h
- "CME impact" with cloud icon at T-2h
- "Storm onset" marker at T0
- "Maximum TEC" flag at T+12h
- "Recovery begins" at T+24h

**Impact Bar (Bottom):**
- Color-coded by severity
- Green: Normal GPS
- Yellow: Degraded GPS
- Orange: Major impacts
- Red: Severe disruptions
- Back to green: Normal operations

---

## Diagram 6: Machine Learning Architecture

**Purpose:** Show the V2.1 neural network structure

**Type:** Architecture diagram with data flow

**Dimensions:** 1000px × 800px

**Layout:**
- Left to right data flow
- Vertical layers stacked
- Component boxes with connections

**Elements:**

1. **Input Layer (Left)**
   - Box: "24 Hours Historical Data"
   - 24 physics-informed features listed:
     - TEC (mean, std)
     - Kp, Dst
     - Solar wind (speed, density)
     - IMF Bz
     - F10.7
     - Time (hour, day-of-year)
     - Magnetic coords
     - Rate-of-change features
   - Dimensions: (24 timesteps × 24 features)

2. **CNN Feature Extraction**
   - Two Conv1D blocks
   - Filters: 128 → 256
   - Residual connections illustrated (skip arrows)
   - Layer normalization
   - MaxPooling illustrated
   - Color: #3b82f6 (blue)

3. **BiLSTM Layer**
   - Forward LSTM (top arrow →)
   - Backward LSTM (bottom arrow ←)
   - Merge in middle
   - Units: 256
   - Color: #10b981 (green)

4. **Multi-Head Attention**
   - 8 attention heads illustrated
   - Q, K, V matrices shown
   - Scaled dot-product attention
   - Residual connection
   - Color: #a78bfa (purple)

5. **Second BiLSTM**
   - Similar to first
   - Units: 128
   - Global pooling (avg + max)
   - Color: #10b981 (green)

6. **Dense Layers**
   - 512 units → 256 units
   - Residual connections
   - Dropout illustrated
   - Color: #fbbf24 (yellow)

7. **Output Heads (Right)**
   - **Head 1:** Storm Binary (sigmoid, 1 unit)
     - Icon: ⚡ Storm Yes/No
   - **Head 2:** Hourly Probabilities (sigmoid, 24 units)
     - Icon: 📊 24-hour forecast
   - **Head 3:** TEC Forecast (linear, 24 units)
     - Icon: 📈 TEC evolution
   - **Head 4:** Uncertainty (sigmoid, 1 unit)
     - Icon: ❓ Confidence

**Annotations:**

- Total parameters: 3.88M
- Loss weights: Storm (3.0), Probability (2.0), TEC (1.0), Uncertainty (0.5)
- Training data: 2015-2022 (8 years)
- Validation: 90-day backtest (MAE: 10-13 TECU)

**Color Scheme:**
- Inputs: #64748b (gray)
- CNN: #3b82f6 (blue)
- LSTM: #10b981 (green)
- Attention: #a78bfa (purple)
- Dense: #fbbf24 (yellow)
- Outputs: #ef4444 (red)

---

## Diagram 7: Climatology Binning

**Purpose:** Show how climatology table works

**Type:** 3D cube visualization

**Dimensions:** 800px × 800px

**Layout:**
- 3D cube with 3 axes
- Example bins highlighted
- Lookup flow illustrated

**Elements:**

1. **Cube Axes**
   - X-axis: Day of Year (1-365)
   - Y-axis: Kp Bin (0-9)
   - Z-axis: Region (5 zones)

2. **Cube Interior**
   - Grid of bins (3,650 per region)
   - Color-coded by TEC value
   - Green (low TEC) → Red (high TEC)

3. **Example Lookup**
   - Today: March 15 (day 74)
   - Kp: 5 (moderate storm)
   - Region: Mid-Latitude
   - Path illustrated with arrows
   - Bin highlighted: shows "23.5 TECU"

4. **Fallback Strategy**
   - If bin empty, search ±1 day, ±1 Kp
   - Illustrated with expanding search pattern
   - Ultimate fallback: regional baseline

5. **Data Points**
   - Individual measurements shown as dots
   - Average computed for each bin
   - "8 years of data (2015-2022)" label

**Callout:**
- "16,185 bins total (3,650 per region)"
- "Each bin = average of all measurements matching conditions"
- "Captures seasonal, diurnal, and storm patterns"

---

## Implementation Notes

### Design Guidelines

**Color Palette (Consistent Across All Diagrams):**
- Background: #0f172a (dark blue)
- Text: #e2e8f0 (light gray)
- Accents: #3b82f6 (blue), #10b981 (green), #fbbf24 (yellow), #ef4444 (red)
- Gradients: Use for transitions and depth

**Typography:**
- Headings: 18-24px, bold, #ffffff
- Labels: 14-16px, regular, #cbd5e1
- Annotations: 12-14px, italic, #94a3b8

**Icons:**
- Use consistent icon style (outlined or filled, not mixed)
- Size: 24-32px for primary icons
- Color: Match context (e.g., storm = red, GPS = blue)

**Spacing:**
- Generous whitespace (minimum 20px margins)
- Consistent grid alignment
- Group related elements

**Interactivity (If SVG):**
- Hover states: Highlight + tooltip
- Click: Zoom or expand detail
- Animate: Transitions between states

### File Formats

**Recommended:**
- **SVG:** For diagrams 1-5 (scalable, crisp)
- **PNG:** Backup at 2x resolution for retina displays
- **Interactive:** Consider D3.js or Three.js for diagram 6

### Accessibility

- **Alt text:** Provide detailed descriptions
- **Color blindness:** Ensure sufficient contrast, don't rely solely on color
- **Labels:** Large enough to read (minimum 12px)
- **Patterns:** Use in addition to color for distinction

---

These diagrams will transform the Science Guide from text-heavy to visually engaging, making complex concepts immediately graspable!
