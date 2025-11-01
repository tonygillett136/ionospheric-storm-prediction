"""
Create a simple visualization of prediction horizon analysis results.
"""

# Results from the analysis
results = {
    "1 day": {"accuracy": 60.6, "f1": 58.8, "detection": 58.2, "false_alarm": 37.2},
    "2 days": {"accuracy": 54.4, "f1": 52.0, "detection": 51.8, "false_alarm": 43.2},
    "3 days": {"accuracy": 47.0, "f1": 44.4, "detection": 44.5, "false_alarm": 50.8},
    "5 days": {"accuracy": 48.7, "f1": 46.4, "detection": 46.6, "false_alarm": 49.4},
    "7 days": {"accuracy": 47.1, "f1": 45.3, "detection": 44.7, "false_alarm": 50.6},
}

print("="*90)
print("IONOSPHERIC STORM PREDICTION HORIZON ANALYSIS")
print("="*90)
print()

# Accuracy chart
print("ACCURACY BY PREDICTION HORIZON")
print("-"*90)
for horizon, metrics in results.items():
    acc = metrics["accuracy"]
    bar_length = int(acc / 2)  # Scale to fit terminal
    bar = "█" * bar_length

    # Color coding
    if acc >= 55:
        status = "✅ GOOD"
    elif acc >= 50:
        status = "⚠️  MARGINAL"
    else:
        status = "❌ POOR"

    print(f"{horizon:8} {bar:<30} {acc:5.1f}%  {status}")

print()
print("="*90)
print()

# Comparison table
print("DETAILED METRICS COMPARISON")
print("-"*90)
print(f"{'Horizon':<10} {'Accuracy':<12} {'F1 Score':<12} {'Detection':<12} {'False Alarms':<12}")
print("-"*90)

for horizon, metrics in results.items():
    acc_emoji = "✅" if metrics["accuracy"] >= 55 else "⚠️" if metrics["accuracy"] >= 50 else "❌"
    print(
        f"{horizon:<10} "
        f"{metrics['accuracy']:>5.1f}% {acc_emoji:<4} "
        f"{metrics['f1']:>5.1f}%      "
        f"{metrics['detection']:>5.1f}%      "
        f"{metrics['false_alarm']:>5.1f}%"
    )

print("-"*90)
print()

# Key insights
print("="*90)
print("KEY INSIGHTS")
print("="*90)
print()

print("📊 ACCURACY DEGRADATION:")
acc_1d = results["1 day"]["accuracy"]
acc_2d = results["2 days"]["accuracy"]
acc_7d = results["7 days"]["accuracy"]

drop_2d = acc_1d - acc_2d
drop_7d = acc_1d - acc_7d

print(f"   1 day → 2 days: -{drop_2d:.1f}% ({drop_2d/acc_1d*100:.1f}% relative)")
print(f"   1 day → 7 days: -{drop_7d:.1f}% ({drop_7d/acc_1d*100:.1f}% relative)")
print()

print("🎯 DETECTION CAPABILITY:")
det_1d = results["1 day"]["detection"]
det_7d = results["7 days"]["detection"]
print(f"   1 day:  Can detect {det_1d:.0f}% of storms (~6 out of 10)")
print(f"   7 days: Can detect {det_7d:.0f}% of storms (~4 out of 10) ❌")
print()

print("🚨 FALSE ALARM PROBLEM:")
fa_1d = results["1 day"]["false_alarm"]
fa_7d = results["7 days"]["false_alarm"]
print(f"   1 day:  {fa_1d:.0f}% false alarms (acceptable)")
print(f"   7 days: {fa_7d:.0f}% false alarms (basically random!) ❌")
print()

print("="*90)
print("RECOMMENDATIONS")
print("="*90)
print()

print("✅ RECOMMENDED: Add 48-hour (2-day) predictions")
print("   • 54.4% accuracy is meaningful (4 points above random)")
print("   • Doubles warning time while maintaining useful skill")
print("   • Implement with 'Medium Confidence' label")
print()

print("⚠️  CONDITIONAL: Add 72-hour (3-day) predictions with strong caveats")
print("   • 47% accuracy is marginal but may have strategic value")
print("   • Must include large uncertainty bands")
print("   • Label as 'Low Confidence - Planning Guidance Only'")
print()

print("❌ NOT RECOMMENDED: 5-7 day predictions")
print("   • Accuracy at random chance level (~47%)")
print("   • 50%+ false alarm rate undermines trust")
print("   • No meaningful predictive skill")
print()

print("="*90)
print()

print("💡 IMPLEMENTATION SUGGESTION:")
print()
print("   Current Risk:     [======= 65% =======]  HIGH CONFIDENCE")
print("   24h Forecast:     [====== 58% ======]   HIGH CONFIDENCE")
print("   48h Forecast:     [==== 42% ====]      MEDIUM CONFIDENCE ⚠️")
print("                     (Less reliable - early warning only)")
print()
print("="*90)
