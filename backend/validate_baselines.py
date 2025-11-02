"""
Baseline Validation Script

Compares the V2 model against simple baseline forecasts:
1. Persistence: tomorrow = today
2. Climatology: average for this day-of-year and Kp level

Proper temporal split:
- Training: 2015-2022
- Testing: 2023-2024

Metrics:
- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)
- Skill Score vs baselines
- Correlation
"""
import numpy as np
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import sys
from collections import defaultdict
import json

sys.path.append(str(Path(__file__).parent))

from app.db.database import AsyncSessionLocal, init_db
from app.db.repository import HistoricalDataRepository
from app.models.storm_predictor_v2 import EnhancedStormPredictor


class BaselineValidator:
    """Validates model against baseline forecasts."""

    def __init__(self, model_path=None):
        self.predictor = EnhancedStormPredictor()

        # Load trained model if path provided
        if model_path:
            print(f"🔄 Loading trained model from {model_path}...")
            self.predictor.load_model(model_path)
            print("   ✓ Model loaded successfully")
        else:
            print("⚠️  No model path provided - using untrained model")

        self.train_years = list(range(2015, 2023))  # 2015-2022
        self.test_years = [2023, 2024]  # 2023-2024
        self.climatology_table = {}  # (day_of_year, kp_bin) -> avg_tec

    async def load_data(self):
        """Load historical data from database."""
        print("📊 Loading historical data from database...")
        await init_db()

        async with AsyncSessionLocal() as session:
            # Load all data
            start_date = datetime(2015, 1, 1)
            end_date = datetime(2024, 12, 31)

            all_measurements = await HistoricalDataRepository.get_measurements_by_time_range(
                session, start_date, end_date
            )

            print(f"   Loaded {len(all_measurements)} measurements")

            # Split by year
            self.train_data = [m for m in all_measurements if m.timestamp.year in self.train_years]
            self.test_data = [m for m in all_measurements if m.timestamp.year in self.test_years]

            print(f"   Train: {len(self.train_data)} measurements ({min(self.train_years)}-{max(self.train_years)})")
            print(f"   Test:  {len(self.test_data)} measurements ({min(self.test_years)}-{max(self.test_years)})")

            return all_measurements

    def build_climatology_table(self):
        """Build climatology lookup table from training data."""
        print("\n🗓️  Building climatology table from training data...")

        # Bin by day-of-year and Kp level
        bins = defaultdict(list)

        for m in self.train_data:
            doy = m.timestamp.timetuple().tm_yday  # Day of year (1-365)
            kp_bin = int(m.kp_index)  # Bin Kp to integer (0-9)

            bins[(doy, kp_bin)].append(m.tec_mean)

        # Calculate averages
        for key, values in bins.items():
            self.climatology_table[key] = np.mean(values)

        print(f"   Created {len(self.climatology_table)} climatology bins")

        # Fill missing bins with global average
        global_avg = np.mean([m.tec_mean for m in self.train_data])
        for doy in range(1, 366):
            for kp_bin in range(10):
                if (doy, kp_bin) not in self.climatology_table:
                    self.climatology_table[(doy, kp_bin)] = global_avg

        print(f"   Global TEC average: {global_avg:.1f} TECU")

    def persistence_forecast(self, current_tec):
        """Persistence: tomorrow = today."""
        return current_tec

    def climatology_forecast(self, timestamp, kp_index):
        """Climatology: average for this DOY and Kp."""
        doy = timestamp.timetuple().tm_yday
        kp_bin = int(kp_index)

        return self.climatology_table.get((doy, kp_bin), np.mean(list(self.climatology_table.values())))

    async def model_forecast(self, historical_sequence):
        """
        Get V2 model forecast using 24-hour historical sequence.

        Args:
            historical_sequence: List of 24 measurements (hourly data)

        Returns:
            TEC forecast value for 24h ahead
        """
        # Prepare 24-hour sequence in the format the model expects
        data_sequence = []
        for measurement in historical_sequence:
            data_dict = {
                'tec_statistics': {'mean': measurement.tec_mean, 'std': measurement.tec_std},
                'kp_index': measurement.kp_index,
                'dst_index': measurement.dst_index,
                'solar_wind_params': {
                    'speed': measurement.solar_wind_speed,
                    'density': measurement.solar_wind_density
                },
                'imf_bz': measurement.imf_bz,
                'f107_flux': measurement.f107_flux,
                'timestamp': measurement.timestamp.isoformat(),
                'latitude': 45.0,  # Default mid-latitude
                'longitude': 0.0
            }
            data_sequence.append(data_dict)

        # Get prediction from model
        prediction = await self.predictor.predict_storm(data_sequence)

        # Extract TEC forecast (first value of 24h forecast array)
        # Note: Model returns 'tec_forecast_24h' with values already denormalized (×100)
        tec_forecast_array = prediction.get('tec_forecast_24h', [20.0])  # Fallback to 20 TECU
        tec_forecast = tec_forecast_array[0]  # First hour of 24h forecast (already denormalized)

        return tec_forecast

    def calculate_metrics(self, predictions, actuals, name="Model"):
        """Calculate performance metrics."""
        predictions = np.array(predictions)
        actuals = np.array(actuals)

        # Remove NaNs
        mask = ~(np.isnan(predictions) | np.isnan(actuals))
        predictions = predictions[mask]
        actuals = actuals[mask]

        if len(predictions) == 0:
            return None

        # RMSE
        rmse = np.sqrt(np.mean((predictions - actuals) ** 2))

        # MAE
        mae = np.mean(np.abs(predictions - actuals))

        # Correlation
        correlation = np.corrcoef(predictions, actuals)[0, 1] if len(predictions) > 1 else 0

        # Bias (mean error)
        bias = np.mean(predictions - actuals)

        return {
            'name': name,
            'rmse': rmse,
            'mae': mae,
            'correlation': correlation,
            'bias': bias,
            'n_samples': len(predictions)
        }

    def calculate_skill_score(self, model_rmse, baseline_rmse):
        """
        Skill score: (baseline_rmse - model_rmse) / baseline_rmse

        > 0: Model better than baseline
        > 0.3: Model significantly better
        > 0.5: Model substantially better
        < 0: Model worse than baseline
        """
        if baseline_rmse == 0:
            return 0

        return (baseline_rmse - model_rmse) / baseline_rmse

    async def run_validation(self):
        """Run complete validation analysis."""
        print("=" * 80)
        print("BASELINE VALIDATION ANALYSIS")
        print("=" * 80)

        # Load data
        await self.load_data()

        # Build climatology
        self.build_climatology_table()

        # Run validation on test set
        print("\n🧪 Running validation on test set (2023-2024)...")
        print("   This will take a few minutes...\n")

        persistence_preds = []
        climatology_preds = []
        model_preds = []
        actuals = []
        timestamps = []
        kp_values = []

        # Only test on samples where we have 24h historical data AND 24h ahead forecast
        # Need index >= 23 (for 24h history) and index < len - 24 (for 24h forecast)
        valid_test_samples = []
        for i in range(23, len(self.test_data) - 25):
            current = self.test_data[i]
            future = self.test_data[i + 24]  # 24 hours ahead
            historical_sequence = self.test_data[i - 23:i + 1]  # 24 hours of history (including current)

            # Check timestamp is actually 24h apart (±1 hour tolerance)
            time_diff = (future.timestamp - current.timestamp).total_seconds() / 3600
            if 23 <= time_diff <= 25 and len(historical_sequence) == 24:
                valid_test_samples.append((i, current, future, historical_sequence))

        print(f"   Found {len(valid_test_samples)} valid 24h forecast pairs (with 24h history)")

        # Progress tracking
        total = len(valid_test_samples)
        chunk_size = max(1, total // 20)  # Show 20 progress updates

        for idx, (i, current, future, historical_sequence) in enumerate(valid_test_samples):
            if idx % chunk_size == 0:
                progress = (idx / total) * 100
                print(f"   Progress: {progress:.0f}% ({idx}/{total})")

            # Actual value (24h ahead)
            actual_tec = future.tec_mean

            # Persistence
            pers_pred = self.persistence_forecast(current.tec_mean)

            # Climatology
            clim_pred = self.climatology_forecast(
                future.timestamp,  # Forecast for future time
                current.kp_index   # Based on current Kp
            )

            # Model prediction (try to get from V2 model with 24h historical sequence)
            try:
                model_pred = await self.model_forecast(historical_sequence)
            except Exception as e:
                # If model fails, use NaN and continue
                # (We'll still compare baselines)
                model_pred = np.nan
                if idx == 0:  # Only log once
                    print(f"   ⚠️  Model predictions unavailable (error: {str(e)[:80]}...)")
                    print(f"   → Will compare Persistence vs Climatology baselines only\n")

            persistence_preds.append(pers_pred)
            climatology_preds.append(clim_pred)
            model_preds.append(model_pred)
            actuals.append(actual_tec)
            timestamps.append(future.timestamp)
            kp_values.append(current.kp_index)

        print(f"   ✓ Completed {len(actuals)} predictions\n")

        # Calculate metrics
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)

        persistence_metrics = self.calculate_metrics(persistence_preds, actuals, "Persistence")
        climatology_metrics = self.calculate_metrics(climatology_preds, actuals, "Climatology")
        model_metrics = self.calculate_metrics(model_preds, actuals, "V2 Model")

        # Print results
        print("\n📊 TEC Forecast Metrics (24h ahead):")
        print("-" * 80)
        print(f"{'Method':<20} {'RMSE':>10} {'MAE':>10} {'Corr':>10} {'Bias':>10} {'Samples':>10}")
        print("-" * 80)

        for metrics in [persistence_metrics, climatology_metrics, model_metrics]:
            if metrics:
                print(f"{metrics['name']:<20} "
                      f"{metrics['rmse']:>10.2f} "
                      f"{metrics['mae']:>10.2f} "
                      f"{metrics['correlation']:>10.3f} "
                      f"{metrics['bias']:>10.2f} "
                      f"{metrics['n_samples']:>10}")

        # Skill scores
        print("\n🎯 Skill Scores:")
        print("-" * 80)

        if persistence_metrics and model_metrics:
            skill_vs_pers = self.calculate_skill_score(
                model_metrics['rmse'],
                persistence_metrics['rmse']
            )
            print(f"Model vs Persistence:  {skill_vs_pers:>6.1%}")

            if skill_vs_pers > 0.5:
                print("   → EXCELLENT: Substantially better than persistence")
            elif skill_vs_pers > 0.3:
                print("   → GOOD: Significantly better than persistence")
            elif skill_vs_pers > 0:
                print("   → MARGINAL: Slightly better than persistence")
            else:
                print("   → POOR: Worse than persistence (problem!)")

        if climatology_metrics and model_metrics:
            skill_vs_clim = self.calculate_skill_score(
                model_metrics['rmse'],
                climatology_metrics['rmse']
            )
            print(f"Model vs Climatology:  {skill_vs_clim:>6.1%}")

            if skill_vs_clim > 0.5:
                print("   → EXCELLENT: Substantially better than climatology")
            elif skill_vs_clim > 0.3:
                print("   → GOOD: Significantly better than climatology")
            elif skill_vs_clim > 0:
                print("   → MARGINAL: Slightly better than climatology")
            else:
                print("   → POOR: Worse than climatology (problem!)")

        # Major storms analysis
        print("\n⚡ Performance During High Kp Events (Kp ≥ 5):")
        print("-" * 80)

        high_kp_mask = np.array(kp_values) >= 5.0
        if np.sum(high_kp_mask) > 0:
            high_kp_pers = np.array(persistence_preds)[high_kp_mask]
            high_kp_clim = np.array(climatology_preds)[high_kp_mask]
            high_kp_model = np.array(model_preds)[high_kp_mask]
            high_kp_actual = np.array(actuals)[high_kp_mask]

            high_pers_metrics = self.calculate_metrics(high_kp_pers, high_kp_actual, "Persistence")
            high_clim_metrics = self.calculate_metrics(high_kp_clim, high_kp_actual, "Climatology")
            high_model_metrics = self.calculate_metrics(high_kp_model, high_kp_actual, "V2 Model")

            print(f"Found {np.sum(high_kp_mask)} high-Kp samples")
            print(f"\n{'Method':<20} {'RMSE':>10} {'MAE':>10} {'Corr':>10}")
            print("-" * 80)

            for metrics in [high_pers_metrics, high_clim_metrics, high_model_metrics]:
                if metrics:
                    print(f"{metrics['name']:<20} "
                          f"{metrics['rmse']:>10.2f} "
                          f"{metrics['mae']:>10.2f} "
                          f"{metrics['correlation']:>10.3f}")
        else:
            print("No high-Kp events found in test set")

        # Save detailed results
        results = {
            'validation_date': datetime.now().isoformat(),
            'train_years': self.train_years,
            'test_years': self.test_years,
            'test_samples': len(actuals),
            'metrics': {
                'persistence': persistence_metrics,
                'climatology': climatology_metrics,
                'v2_model': model_metrics
            },
            'skill_scores': {
                'vs_persistence': float(skill_vs_pers) if persistence_metrics and model_metrics else None,
                'vs_climatology': float(skill_vs_clim) if climatology_metrics and model_metrics else None
            }
        }

        # Save to file
        output_file = Path(__file__).parent / 'BASELINE_VALIDATION_RESULTS.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Detailed results saved to: {output_file}")

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)

        if model_metrics and persistence_metrics:
            if skill_vs_pers > 0.3:
                print("✅ Model shows significant skill vs baseline forecasts")
                print("   → Production-ready for operational use")
            elif skill_vs_pers > 0:
                print("⚠️  Model shows marginal skill vs baselines")
                print("   → Consider additional features or tuning")
            else:
                print("❌ Model does not beat simple baselines")
                print("   → Fundamental issues need to be addressed")

        print("=" * 80)

        return results


async def main():
    """Main entry point."""
    # Load the best trained model from V2.1 training
    model_path = "models/v2/best_model.keras"
    validator = BaselineValidator(model_path=model_path)
    await validator.run_validation()


if __name__ == "__main__":
    asyncio.run(main())
