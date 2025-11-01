# Data Limitations and Real Data Requirements

## Current Status: DEMO MODE

⚠️ **CRITICAL**: This system is currently operating with **100% synthetically generated training data**. All predictions are for demonstration purposes only and should NOT be used for operational decision-making.

## What's Synthetic

### Training Data (backend/data/ionospheric.db)
- **All 175,200 historical measurements** (10 years, 2015-2025) are synthetically generated
- Created by `backend/seed_historical_data.py` using mathematical models
- Data includes:
  - Geomagnetic indices (Kp, Dst)
  - Solar wind parameters (speed, density, temperature)
  - IMF Bz (Interplanetary Magnetic Field)
  - F10.7 solar flux
  - TEC (Total Electron Content) statistics
  - Storm probabilities

### Model Implications
- The V2 BiLSTM-Attention model (3.9M parameters) was trained exclusively on synthetic data
- Model learned patterns from mathematical approximations, not real ionospheric physics
- **Prediction accuracy on real-world storms is unknown**
- Model has never seen actual storm events or real space weather patterns

## Required Real Data Sources

To convert this to a production system, the following real observational data is required:

### 1. TEC Data (Total Electron Content)
**Primary Sources:**
- **NASA CDDIS**: ftp://cddis.nasa.gov/gnss/products/ionex/
  - IONEX format files (IONosphere Map EXchange)
  - Global TEC maps at 2-hour resolution
  - Historical data available from 1998

- **CODE (Center for Orbit Determination in Europe)**
  - ftp://ftp.aiub.unibe.ch/CODE/
  - High-quality global ionosphere maps

- **MIT Haystack MADRIGAL**
  - http://cedar.openmadrigal.org/
  - Various TEC measurement techniques
  - HDF5 and netCDF formats

**Data Volume**: ~100GB for 10 years of IONEX files

### 2. Geomagnetic Indices (Kp, Dst)
**Primary Sources:**
- **GFZ Potsdam (Kp Index)**
  - https://www-app3.gfz-potsdam.de/kp_index/
  - Definitive Kp values (3-hour resolution)
  - ASCII text format

- **WDC Kyoto (Dst Index)**
  - http://wdc.kugi.kyoto-u.ac.jp/dstdir/
  - Hourly Dst index
  - Text files with provisional and final values

- **NOAA SWPC (Real-time)**
  - https://services.swpc.noaa.gov/
  - `/text/daily-geomagnetic-indices/`
  - Recent data (last 30 days)

**Data Volume**: ~500MB for 10 years

### 3. Solar Wind Data
**Primary Sources:**
- **NASA OMNI**
  - https://omniweb.gsfc.nasa.gov/form/omni_min.html
  - 1-minute resolution solar wind data
  - Merged from multiple spacecraft (ACE, DSCOVR, Wind)
  - Parameters: speed, density, temperature, IMF components

- **NOAA DSCOVR**
  - https://services.swpc.noaa.gov/products/solar-wind/
  - Real-time L1 solar wind monitoring
  - JSON format for recent data

**Data Volume**: ~50GB for 10 years at 1-minute resolution

### 4. Solar Activity (F10.7 Flux)
**Primary Sources:**
- **NOAA SWPC**
  - https://services.swpc.noaa.gov/text/daily-solar-indices/
  - Daily F10.7 observations

- **NRCan (Natural Resources Canada)**
  - https://www.spaceweather.gc.ca/solarflux/sx-5-en.php
  - Official source for F10.7 measurements
  - CSV format

**Data Volume**: ~10MB for 10 years

## Implementation Complexity

### Data Acquisition Pipeline
**Estimated Effort**: 40-60 hours

1. **IONEX Parser** (15-20 hours)
   - Parse compressed IONEX files (.Z format)
   - Extract TEC maps at all lat/lon points
   - Calculate global statistics (mean, std, max, min)
   - Handle missing data and quality flags

2. **Geomagnetic Index Fetcher** (10-15 hours)
   - Parse GFZ Kp format (fixed-width text)
   - Parse Kyoto Dst format
   - Handle provisional vs final values
   - Align timestamps across sources

3. **Solar Wind Data Processor** (8-12 hours)
   - Access NASA OMNI database
   - Downsample 1-min data to hourly
   - Handle data gaps and bad values
   - Process multiple parameters simultaneously

4. **Data Integration** (7-13 hours)
   - Align all data sources to common hourly timestamps
   - Handle time zones (all sources use different conventions)
   - Quality control and validation
   - Database schema updates

### Retraining Requirements
**Estimated Effort**: 5-8 hours

1. **Data Validation** (1-2 hours)
   - Verify all parameters are within physical ranges
   - Check for systematic biases
   - Identify and handle data gaps

2. **Model Retraining** (2-3 hours)
   - Same architecture as current V2 model
   - 100 epochs training on real data
   - Validation on held-out test set

3. **Performance Evaluation** (2-3 hours)
   - Compare against known storm events
   - Calculate true positive/false positive rates
   - Validate against NOAA storm warnings

## Risks and Challenges

### Data Quality Issues
1. **Missing Data**: All real-world datasets have gaps
   - GNSS TEC: Gaps during solar storms (ionospheric scintillation)
   - Solar wind: L1 spacecraft downtime
   - Geomagnetic indices: Delayed availability (provisional vs final)

2. **Timestamp Alignment**: Different update schedules
   - TEC: 2-hour resolution
   - Kp: 3-hour resolution
   - Solar wind: 1-minute resolution
   - Dst: Hourly resolution

3. **Format Heterogeneity**: Each source uses different formats
   - IONEX: Custom binary/ASCII hybrid
   - OMNI: Space-delimited ASCII with fill values
   - Kp/Dst: Fixed-width text files

### Computational Challenges
1. **Storage**: ~150GB total for 10 years
2. **Processing**: IONEX files require significant CPU to parse
3. **Download Time**: FTP transfers can be slow and unreliable

## Current Frontend Fixes

The following changes have been implemented to ensure data integrity:

1. **24h Forecast Chart**: Fixed Y-axis domain to [0, 100%]
   - Previously auto-scaled, causing clipping at 12% when data reached 39%

2. **Historical Trends**: Removed synthetic data fallback
   - Now displays error message when real data unavailable
   - Clear warning about data source requirements

3. **Warning Banner**: Added prominent "DEMO MODE" notice
   - Visible on all pages
   - Lists required real data sources
   - Warns against operational use

## Recommendations

### Short Term (Demo/Research)
- ✅ Current state is acceptable for demonstration purposes
- ✅ UI clearly warns about data limitations
- ✅ Synthetic data display has been disabled

### Medium Term (Validation)
- ⬜ Acquire 1-2 months of real data for validation
- ⬜ Retrain model on real data
- ⬜ Compare predictions against known storm events
- ⬜ Publish validation results

### Long Term (Production)
- ⬜ Implement full data acquisition pipeline
- ⬜ Set up automated daily data updates
- ⬜ Continuous retraining with new data
- ⬜ Real-time monitoring and alerting
- ⬜ Validation against operational space weather centers

## File Locations

- **Synthetic Data Generator**: `backend/seed_historical_data.py`
- **Training Pipeline**: `backend/app/training/train_model_v2.py`
- **Database**: `backend/data/ionospheric.db` (51MB, excluded from git)
- **UI Warning**: `frontend/src/App.jsx` (lines 240-261)

## References

1. **IONEX Format**: ftp://igs.org/pub/data/format/ionex1.pdf
2. **OMNI Data**: https://omniweb.gsfc.nasa.gov/html/ow_data.html
3. **Kp Index**: https://www.gfz-potsdam.de/en/section/geomagnetism/data-products-services/geomagnetic-kp-index/
4. **Space Weather Data Guide**: https://www.swpc.noaa.gov/products-and-data

---

**Last Updated**: 2025-10-31
**Status**: DEMO MODE - Synthetic Data Only
