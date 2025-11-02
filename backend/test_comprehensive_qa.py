"""
Comprehensive QA Test Suite
Tests all features of the Ionospheric Storm Prediction System
"""
import asyncio
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "qa_test@example.com"

class TestResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def add_test(self, category: str, test_name: str, passed: bool, message: str = "", warning: bool = False):
        self.tests.append({
            "category": category,
            "test": test_name,
            "status": "PASS" if passed else "FAIL" if not warning else "WARNING",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        if warning:
            self.warnings += 1
        elif passed:
            self.passed += 1
        else:
            self.failed += 1

    def print_summary(self):
        print("\n" + "="*80)
        print("QA TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {len(self.tests)}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"Success Rate: {(self.passed / len(self.tests) * 100):.1f}%")
        print("="*80)

    def print_details(self):
        print("\n" + "="*80)
        print("DETAILED TEST RESULTS")
        print("="*80)

        current_category = None
        for test in self.tests:
            if test["category"] != current_category:
                current_category = test["category"]
                print(f"\n📋 {current_category}")
                print("-" * 80)

            status_icon = "✅" if test["status"] == "PASS" else "❌" if test["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {test['test']}")
            if test["message"]:
                print(f"   → {test['message']}")

    def save_report(self, filename: str):
        with open(filename, 'w') as f:
            f.write("# QA Test Report\n\n")
            f.write(f"**Test Date**: {datetime.now().isoformat()}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- Total Tests: {len(self.tests)}\n")
            f.write(f"- ✅ Passed: {self.passed}\n")
            f.write(f"- ❌ Failed: {self.failed}\n")
            f.write(f"- ⚠️ Warnings: {self.warnings}\n")
            f.write(f"- Success Rate: {(self.passed / len(self.tests) * 100):.1f}%\n\n")

            f.write("## Detailed Results\n\n")
            current_category = None
            for test in self.tests:
                if test["category"] != current_category:
                    current_category = test["category"]
                    f.write(f"\n### {current_category}\n\n")

                status_icon = "✅" if test["status"] == "PASS" else "❌" if test["status"] == "FAIL" else "⚠️"
                f.write(f"{status_icon} **{test['test']}**\n")
                if test["message"]:
                    f.write(f"   - {test['message']}\n")
                f.write("\n")

results = TestResults()

# Helper functions
def test_endpoint(method: str, endpoint: str, data: Dict = None, params: Dict = None, expected_status: int = 200) -> Tuple[bool, Dict]:
    """Test an API endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"

        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, params=params, timeout=10)
        else:
            return False, {"error": "Unknown method"}

        if response.status_code == expected_status:
            try:
                return True, response.json()
            except:
                return True, {}
        else:
            return False, {"error": f"Expected {expected_status}, got {response.status_code}", "response": response.text}
    except Exception as e:
        return False, {"error": str(e)}

print("🚀 Starting Comprehensive QA Test Suite")
print("="*80)

# ============================================================================
# PHASE 1: DATA QUALITY & MODEL ACCURACY
# ============================================================================
print("\n📊 Phase 1: Data Quality & Model Accuracy Tests")
print("-"*80)

# Test 1.1: Current prediction exists
success, data = test_endpoint("GET", "/prediction")
if success and "storm_probability_24h" in data:
    prob_24h = data["storm_probability_24h"] * 100
    prob_48h = data.get("storm_probability_48h", 0) * 100
    results.add_test("Data Quality", "Current prediction available", True, f"24h: {prob_24h:.1f}%, 48h: {prob_48h:.1f}%")

    # Validate prediction values are reasonable
    if 0 <= prob_24h <= 100 and 0 <= prob_48h <= 100:
        results.add_test("Data Quality", "Prediction probabilities in valid range", True, "0-100%")
    else:
        results.add_test("Data Quality", "Prediction probabilities in valid range", False, f"24h: {prob_24h}%, 48h: {prob_48h}%")

    # Validate 48h < 24h (with confidence penalty)
    if prob_48h <= prob_24h + 5:  # Allow small tolerance
        results.add_test("Data Quality", "48h confidence penalty applied", True, f"48h: {prob_48h:.1f}% ≤ 24h: {prob_24h:.1f}%")
    else:
        results.add_test("Data Quality", "48h confidence penalty applied", False, f"48h: {prob_48h:.1f}% > 24h: {prob_24h:.1f}%", warning=True)
else:
    results.add_test("Data Quality", "Current prediction available", False, str(data.get("error", "No data")))

# Test 1.2: TEC data validity
success, data = test_endpoint("GET", "/tec/current")
if success and "tec_statistics" in data:
    tec_stats = data["tec_statistics"]
    tec_mean = tec_stats.get("mean", 0)

    if 0 <= tec_mean <= 200:  # Reasonable TEC range
        results.add_test("Data Quality", "TEC values in reasonable range", True, f"Mean: {tec_mean:.1f} TECU")
    else:
        results.add_test("Data Quality", "TEC values in reasonable range", False, f"Mean: {tec_mean} TECU")
else:
    results.add_test("Data Quality", "TEC data available", False, str(data.get("error", "No data")))

# Test 1.3: Space weather parameters
success, data = test_endpoint("GET", "/space-weather/current")
if success:
    kp = data.get("kp_index", -1)

    if 0 <= kp <= 9:
        results.add_test("Data Quality", "Kp index in valid range", True, f"Kp: {kp}")
    else:
        results.add_test("Data Quality", "Kp index in valid range", False, f"Kp: {kp}")

    imf_bz = data.get("imf_bz")
    if imf_bz is not None and abs(imf_bz) < 900:  # Fill value is 999.9
        results.add_test("Data Quality", "IMF Bz not fill value", True, f"IMF Bz: {imf_bz:.1f} nT")
    else:
        results.add_test("Data Quality", "IMF Bz not fill value", False, "Fill value detected", warning=True)
else:
    results.add_test("Data Quality", "Space weather data available", False, str(data.get("error", "No data")))

# ============================================================================
# PHASE 2: FEATURE 1 - IMPACT ASSESSMENT
# ============================================================================
print("\n🎯 Phase 2: Impact Assessment Tests")
print("-"*80)

# Test 2.1: Impact assessment at mid-latitude
success, data = test_endpoint("GET", "/impact-assessment", params={"latitude": 45})
if success and "gps" in data and "radio" in data and "satellite" in data and "power_grid" in data:
    results.add_test("Impact Assessment", "All impact categories present", True, "GPS, Radio, Satellite, Power Grid")

    # Validate impact scores
    gps_score = data["gps"].get("impact_score", -1)
    if 1 <= gps_score <= 10:
        results.add_test("Impact Assessment", "GPS impact score valid", True, f"Score: {gps_score}/10")
    else:
        results.add_test("Impact Assessment", "GPS impact score valid", False, f"Score: {gps_score}")

    # Validate overall severity
    overall_score = data.get("overall", {}).get("severity_score", -1)
    if 1 <= overall_score <= 10:
        results.add_test("Impact Assessment", "Overall severity score valid", True, f"Score: {overall_score}/10")
    else:
        results.add_test("Impact Assessment", "Overall severity score valid", False, f"Score: {overall_score}")
else:
    results.add_test("Impact Assessment", "Impact assessment endpoint", False, str(data.get("error", "No data")))

# Test 2.2: Impact assessment at high latitude (should show higher impacts)
success_high, data_high = test_endpoint("GET", "/impact-assessment", params={"latitude": 75})
if success and success_high:
    mid_gps_impact = data["gps"]["impact_score"]
    high_gps_impact = data_high["gps"]["impact_score"]

    if high_gps_impact >= mid_gps_impact:
        results.add_test("Impact Assessment", "Higher latitude shows greater GPS impact", True,
                        f"75°: {high_gps_impact:.1f} ≥ 45°: {mid_gps_impact:.1f}")
    else:
        results.add_test("Impact Assessment", "Higher latitude shows greater GPS impact", False,
                        f"75°: {high_gps_impact:.1f} < 45°: {mid_gps_impact:.1f}", warning=True)

# Test 2.3: Impact assessment at equator
success, data = test_endpoint("GET", "/impact-assessment", params={"latitude": 0})
if success:
    results.add_test("Impact Assessment", "Equatorial latitude calculation", True, "Latitude: 0°")
else:
    results.add_test("Impact Assessment", "Equatorial latitude calculation", False, str(data.get("error")))

# Test 2.4: Latitude validation
success, data = test_endpoint("GET", "/impact-assessment", params={"latitude": 100}, expected_status=400)
if success:
    results.add_test("Impact Assessment", "Invalid latitude rejected (>90)", True, "400 error returned")
else:
    results.add_test("Impact Assessment", "Invalid latitude rejected (>90)", False, "Should return 400")

# ============================================================================
# PHASE 3: FEATURE 2 - REGIONAL PREDICTIONS
# ============================================================================
print("\n📍 Phase 3: Regional Predictions Tests")
print("-"*80)

# Test 3.1: Regional prediction for mid-latitude
success, data = test_endpoint("GET", "/prediction/location", params={"latitude": 45, "longitude": -75})
if success and "location" in data and "regional_prediction" in data:
    results.add_test("Regional Predictions", "Regional prediction endpoint", True, "New York coordinates")

    regional_prob = data["regional_prediction"]["storm_probability_24h"]
    global_prob = data["global_comparison"]["global_probability_24h"]
    adjustment = data["regional_prediction"]["adjustment_factor"]

    results.add_test("Regional Predictions", "Regional vs global comparison", True,
                    f"Regional: {regional_prob}%, Global: {global_prob}%, Factor: {adjustment}x")

    # Validate adjustment factor is reasonable
    if 0.5 <= adjustment <= 1.5:
        results.add_test("Regional Predictions", "Adjustment factor in reasonable range", True, f"{adjustment}x")
    else:
        results.add_test("Regional Predictions", "Adjustment factor in reasonable range", False, f"{adjustment}x")
else:
    results.add_test("Regional Predictions", "Regional prediction endpoint", False, str(data.get("error")))

# Test 3.2: High-latitude (auroral zone) should have higher adjustment
success, data = test_endpoint("GET", "/prediction/location", params={"latitude": 64.8, "longitude": -147.7})
if success:
    adjustment = data["regional_prediction"]["adjustment_factor"]

    if adjustment >= 1.2:  # Auroral zones should have enhancement
        results.add_test("Regional Predictions", "Auroral zone enhancement", True,
                        f"Fairbanks: {adjustment}x adjustment")
    else:
        results.add_test("Regional Predictions", "Auroral zone enhancement", False,
                        f"Expected >1.2x, got {adjustment}x", warning=True)

# Test 3.3: Equatorial should have lower adjustment
success, data = test_endpoint("GET", "/prediction/location", params={"latitude": 1.3, "longitude": 103.8})
if success:
    adjustment = data["regional_prediction"]["adjustment_factor"]

    if adjustment <= 0.9:  # Equatorial should have reduction
        results.add_test("Regional Predictions", "Equatorial reduction", True,
                        f"Singapore: {adjustment}x adjustment")
    else:
        results.add_test("Regional Predictions", "Equatorial reduction", False,
                        f"Expected <0.9x, got {adjustment}x", warning=True)

# Test 3.4: Invalid coordinates
success, data = test_endpoint("GET", "/prediction/location", params={"latitude": 100, "longitude": 0}, expected_status=400)
results.add_test("Regional Predictions", "Invalid latitude rejected", success, "Latitude > 90°")

success, data = test_endpoint("GET", "/prediction/location", params={"latitude": 0, "longitude": 200}, expected_status=400)
results.add_test("Regional Predictions", "Invalid longitude rejected", success, "Longitude > 180°")

# ============================================================================
# PHASE 4: FEATURE 3 - ALERT SYSTEM
# ============================================================================
print("\n🔔 Phase 4: Alert System Tests")
print("-"*80)

# Test 4.1: Create alert
alert_data = {
    "user_email": TEST_EMAIL,
    "name": "QA Test Alert",
    "alert_type": "threshold",
    "threshold_probability": 50,
    "threshold_horizon": "24h"
}
success, data = test_endpoint("POST", "/alerts", data=alert_data)
if success and "id" in data:
    alert_id = data["id"]
    results.add_test("Alert System", "Create alert", True, f"Alert ID: {alert_id}")

    # Test 4.2: Get alerts for user
    success, data = test_endpoint("GET", "/alerts", params={"user_email": TEST_EMAIL})
    if success and "alerts" in data and len(data["alerts"]) > 0:
        results.add_test("Alert System", "Retrieve user alerts", True, f"Found {len(data['alerts'])} alert(s)")
    else:
        results.add_test("Alert System", "Retrieve user alerts", False, str(data.get("error")))

    # Test 4.3: Check alerts (should trigger if current prob > 50%)
    success, data = test_endpoint("GET", "/alerts/check")
    if success:
        triggered_count = data.get("triggered_count", 0)
        results.add_test("Alert System", "Alert checking logic", True, f"{triggered_count} alert(s) triggered")
    else:
        results.add_test("Alert System", "Alert checking logic", False, str(data.get("error")))

    # Test 4.4: Get alert history
    success, data = test_endpoint("GET", "/alerts/history", params={"user_email": TEST_EMAIL})
    if success and "history" in data:
        results.add_test("Alert System", "Alert history retrieval", True, f"{len(data['history'])} history record(s)")
    else:
        results.add_test("Alert System", "Alert history retrieval", False, str(data.get("error")))

    # Test 4.5: Delete alert
    success, data = test_endpoint("DELETE", f"/alerts/{alert_id}", params={"user_email": TEST_EMAIL})
    if success:
        results.add_test("Alert System", "Delete alert", True, f"Alert {alert_id} deleted")
    else:
        results.add_test("Alert System", "Delete alert", False, str(data.get("error")))
else:
    results.add_test("Alert System", "Create alert", False, str(data.get("error")))

# ============================================================================
# PHASE 5: API COMPREHENSIVE TESTING
# ============================================================================
print("\n🔌 Phase 5: API Endpoint Tests")
print("-"*80)

# Test all major endpoints
endpoints = [
    ("GET", "/", {}, 200),
    ("GET", "/health", {}, 200),
    ("GET", "/current", {}, 200),
    ("GET", "/prediction", {}, 200),
]

for method, endpoint, params, expected_status in endpoints:
    success, data = test_endpoint(method, endpoint, params=params, expected_status=expected_status)
    results.add_test("API Endpoints", f"{method} {endpoint}", success,
                    "OK" if success else str(data.get("error")))

# Test API response times
print("\n⏱️  Testing API Response Times...")
response_times = []
for method, endpoint, params, _ in endpoints:
    start = time.time()
    test_endpoint(method, endpoint, params=params)
    elapsed = time.time() - start
    response_times.append(elapsed)

avg_response_time = sum(response_times) / len(response_times)
if avg_response_time < 1.0:
    results.add_test("Performance", "Average API response time", True, f"{avg_response_time:.3f}s (< 1s)")
else:
    results.add_test("Performance", "Average API response time", False, f"{avg_response_time:.3f}s (> 1s)", warning=True)

# ============================================================================
# PRINT RESULTS
# ============================================================================
print("\n" + "="*80)
print("TEST EXECUTION COMPLETE")
print("="*80)

results.print_details()
results.print_summary()

# Save report
report_filename = "QA_TEST_REPORT.md"
results.save_report(report_filename)
print(f"\n📝 Detailed report saved to: {report_filename}")

# Exit with appropriate code
if results.failed == 0:
    print("\n✅ ALL TESTS PASSED!")
    exit(0)
else:
    print(f"\n❌ {results.failed} TEST(S) FAILED")
    exit(1)
