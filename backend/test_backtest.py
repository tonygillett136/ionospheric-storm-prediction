"""Quick test script for backtesting API"""
import requests
import json

# Test backtesting endpoint (using dates within our seeded range)
# Use ISO format with time to match database timestamps better
payload = {
    "start_date": "2020-06-02T00:00:00",
    "end_date": "2020-06-08T00:00:00",
    "storm_threshold": 40.0,
    "sample_interval_hours": 24  # Daily predictions for simpler test
}

print("Testing backtest API endpoint...")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        "http://localhost:8000/api/v1/backtest/run",
        json=payload,
        timeout=120  # 2 minute timeout for processing
    )

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS! Backtest completed.")
        print(f"\nMetadata:")
        print(f"  Duration: {result['metadata']['duration_days']} days")
        print(f"  Total Predictions: {result['metadata']['total_predictions']}")

        print(f"\nMetrics:")
        print(f"  Accuracy: {result['metrics']['accuracy']:.2%}")
        print(f"  Precision: {result['metrics']['precision']:.2%}")
        print(f"  Recall: {result['metrics']['recall']:.2%}")
        print(f"  F1 Score: {result['metrics']['f1_score']:.3f}")
        print(f"  RMSE: {result['metrics']['rmse']:.2f}%")
        print(f"  MAE: {result['metrics']['mae']:.2f}%")

        print(f"\nConfusion Matrix:")
        print(f"  True Positives: {result['metrics']['true_positives']}")
        print(f"  True Negatives: {result['metrics']['true_negatives']}")
        print(f"  False Positives: {result['metrics']['false_positives']}")
        print(f"  False Negatives: {result['metrics']['false_negatives']}")

        print(f"\nSummary:")
        print(f"  Average Error: {result['summary']['average_error']:.2f}%")
        print(f"  Max Error: {result['summary']['max_error']:.2f}%")
        print(f"  Storm Detection Rate: {result['summary']['storm_detection_rate']:.2f}%")
        print(f"  False Alarm Rate: {result['summary']['false_alarm_rate']:.2f}%")

        print(f"\nAnalysis:")
        print(f"  Missed Storms: {len(result['analysis']['missed_storms'])}")
        print(f"  False Alarms: {len(result['analysis']['false_alarms'])}")

    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"\n❌ Exception: {e}")
