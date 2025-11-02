# QA Test Report

**Test Date**: 2025-11-02T09:55:09.642527

## Summary

- Total Tests: 29
- ✅ Passed: 29
- ❌ Failed: 0
- ⚠️ Warnings: 0
- Success Rate: 100.0%

## Detailed Results


### Data Quality

✅ **Current prediction available**
   - 24h: 77.0%, 48h: 69.3%

✅ **Prediction probabilities in valid range**
   - 0-100%

✅ **48h confidence penalty applied**
   - 48h: 69.3% ≤ 24h: 77.0%

✅ **TEC values in reasonable range**
   - Mean: 23.1 TECU

✅ **Kp index in valid range**
   - Kp: 3.0

✅ **IMF Bz not fill value**
   - IMF Bz: -3.8 nT


### Impact Assessment

✅ **All impact categories present**
   - GPS, Radio, Satellite, Power Grid

✅ **GPS impact score valid**
   - Score: 8.6/10

✅ **Overall severity score valid**
   - Score: 5.8/10

✅ **Higher latitude shows greater GPS impact**
   - 75°: 9.7 ≥ 45°: 8.6

✅ **Equatorial latitude calculation**
   - Latitude: 0°

✅ **Invalid latitude rejected (>90)**
   - 400 error returned


### Regional Predictions

✅ **Regional prediction endpoint**
   - New York coordinates

✅ **Regional vs global comparison**
   - Regional: 77.05%, Global: 77.05%, Factor: 1.0x

✅ **Adjustment factor in reasonable range**
   - 1.0x

✅ **Auroral zone enhancement**
   - Fairbanks: 1.438x adjustment

✅ **Equatorial reduction**
   - Singapore: 0.85x adjustment

✅ **Invalid latitude rejected**
   - Latitude > 90°

✅ **Invalid longitude rejected**
   - Longitude > 180°


### Alert System

✅ **Create alert**
   - Alert ID: 2

✅ **Retrieve user alerts**
   - Found 1 alert(s)

✅ **Alert checking logic**
   - 2 alert(s) triggered

✅ **Alert history retrieval**
   - 1 history record(s)

✅ **Delete alert**
   - Alert 2 deleted


### API Endpoints

✅ **GET /**
   - OK

✅ **GET /health**
   - OK

✅ **GET /current**
   - OK

✅ **GET /prediction**
   - OK


### Performance

✅ **Average API response time**
   - 0.014s (< 1s)

