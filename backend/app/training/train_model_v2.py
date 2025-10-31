"""
Training Pipeline for Enhanced Storm Prediction Model V2

Features:
- Proper train/validation/test split
- Data augmentation for storm events
- Learning rate scheduling
- Early stopping
- Model checkpointing
- TensorBoard logging
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from datetime import datetime, timedelta
from pathlib import Path
import logging
import asyncio
from typing import List, Tuple
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.db.database import AsyncSessionLocal, init_db
from app.db.repository import HistoricalDataRepository
from app.models.storm_predictor_v2 import EnhancedStormPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StormDataGenerator:
    """
    Data generator for training with data augmentation
    """

    def __init__(
        self,
        measurements: List,
        sequence_length: int = 24,
        batch_size: int = 32,
        shuffle: bool = True,
        augment: bool = False
    ):
        self.measurements = measurements
        self.sequence_length = sequence_length
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.augment = augment
        self.predictor = EnhancedStormPredictor()

    def generate_sequences(self):
        """Generate training sequences"""
        sequences = []
        targets = {
            'storm_binary': [],
            'storm_probability': [],
            'tec_forecast': [],
            'uncertainty': []
        }

        # Create sequences
        for i in range(len(self.measurements) - self.sequence_length - 24):
            # Input: 24 hours of data
            input_sequence = self.measurements[i:i + self.sequence_length]

            # Target: data 24 hours ahead
            target_point = self.measurements[i + self.sequence_length + 24]

            # Convert to features
            features = []
            for m in input_sequence:
                data_dict = {
                    'tec_statistics': {'mean': m.tec_mean, 'std': m.tec_std},
                    'kp_index': m.kp_index,
                    'dst_index': m.dst_index,
                    'solar_wind_params': {
                        'speed': m.solar_wind_speed,
                        'density': m.solar_wind_density
                    },
                    'imf_bz': m.imf_bz,
                    'f107_flux': m.f107_flux,
                    'timestamp': m.timestamp.isoformat()
                }
                feat = self.predictor.prepare_enhanced_features(data_dict)
                feat = self.predictor.normalize_features(feat)
                features.append(feat)

            # Targets
            storm_binary = 1.0 if target_point.storm_probability >= 40.0 else 0.0
            storm_prob_24h = [
                1.0 if self.measurements[i + self.sequence_length + j].storm_probability >= 40.0 else 0.0
                for j in range(24) if i + self.sequence_length + j < len(self.measurements)
            ]
            # Pad if needed
            while len(storm_prob_24h) < 24:
                storm_prob_24h.append(0.0)

            tec_forecast_24h = [
                self.measurements[i + self.sequence_length + j].tec_mean / 100.0
                for j in range(24) if i + self.sequence_length + j < len(self.measurements)
            ]
            while len(tec_forecast_24h) < 24:
                tec_forecast_24h.append(0.2)  # Default normalized TEC

            # Uncertainty based on data quality (simplified)
            uncertainty = 0.1  # Low uncertainty for historical data

            sequences.append(np.array(features))
            targets['storm_binary'].append(storm_binary)
            targets['storm_probability'].append(storm_prob_24h)
            targets['tec_forecast'].append(tec_forecast_24h)
            targets['uncertainty'].append(uncertainty)

        X = np.array(sequences, dtype=np.float32)
        y = {
            'storm_binary': np.array(targets['storm_binary'], dtype=np.float32),
            'storm_probability': np.array(targets['storm_probability'], dtype=np.float32),
            'tec_forecast': np.array(targets['tec_forecast'], dtype=np.float32),
            'uncertainty': np.array(targets['uncertainty'], dtype=np.float32)
        }

        return X, y

    def augment_data(self, X, y):
        """
        Data augmentation for storm events
        Oversample storm periods to balance the dataset
        """
        storm_indices = np.where(y['storm_binary'] == 1.0)[0]
        non_storm_indices = np.where(y['storm_binary'] == 0.0)[0]

        logger.info(f"Original: {len(storm_indices)} storms, {len(non_storm_indices)} non-storms")

        # Oversample storm events
        if len(storm_indices) > 0:
            oversample_factor = min(3, len(non_storm_indices) // len(storm_indices))
            augmented_storm_indices = np.tile(storm_indices, oversample_factor)

            # Combine
            all_indices = np.concatenate([non_storm_indices, augmented_storm_indices])
            np.random.shuffle(all_indices)

            X_augmented = X[all_indices]
            y_augmented = {
                key: val[all_indices] for key, val in y.items()
            }

            logger.info(f"Augmented: {len(all_indices)} total samples")
            return X_augmented, y_augmented

        return X, y


async def load_training_data(start_date: datetime, end_date: datetime):
    """Load training data from database and resample to exactly 1 per hour"""
    async with AsyncSessionLocal() as session:
        measurements = await HistoricalDataRepository.get_measurements_by_time_range(
            session, start_date, end_date
        )

        # CRITICAL FIX: Resample to exactly 1 measurement per hour
        # Group by hour and take the first measurement in each hour
        hourly_measurements = {}
        for m in measurements:
            # Create hour key (year-month-day-hour)
            hour_key = m.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in hourly_measurements:
                hourly_measurements[hour_key] = m

        # Convert back to sorted list
        resampled = sorted(hourly_measurements.values(), key=lambda x: x.timestamp)

        logger.info(f"Resampled {len(measurements)} measurements to {len(resampled)} hourly samples")
        return resampled


def split_data(X, y, train_ratio=0.7, val_ratio=0.15):
    """Split data into train/val/test sets"""
    n = len(X)
    train_size = int(n * train_ratio)
    val_size = int(n * val_ratio)

    X_train = X[:train_size]
    X_val = X[train_size:train_size + val_size]
    X_test = X[train_size + val_size:]

    y_train = {key: val[:train_size] for key, val in y.items()}
    y_val = {key: val[train_size:train_size + val_size] for key, val in y.items()}
    y_test = {key: val[train_size + val_size:] for key, val in y.items()}

    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


async def train_enhanced_model():
    """Main training function"""
    logger.info("Starting Enhanced Model V2 Training Pipeline")

    # Initialize database
    await init_db()

    # Load data (use all historical data for training)
    start_date = datetime(2015, 10, 31)
    end_date = datetime(2025, 10, 28)

    logger.info(f"Loading data from {start_date} to {end_date}")
    measurements = await load_training_data(start_date, end_date)
    logger.info(f"Loaded {len(measurements)} measurements")

    if len(measurements) < 1000:
        logger.error("Insufficient data for training")
        return

    # Generate sequences
    logger.info("Generating training sequences...")
    generator = StormDataGenerator(
        measurements,
        sequence_length=24,
        batch_size=32,
        augment=True
    )
    X, y = generator.generate_sequences()
    logger.info(f"Generated {len(X)} sequences")

    # Augment data (oversample storm events)
    X, y = generator.augment_data(X, y)

    # Split data
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = split_data(X, y)
    logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

    # Build model
    logger.info("Building Enhanced Model V2...")
    predictor = EnhancedStormPredictor()
    model = predictor.model

    # Print model summary
    logger.info("\nModel Architecture:")
    model.summary()

    # Create directories
    model_dir = Path("models/v2")
    model_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = Path("logs/v2")
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Callbacks
    callbacks = [
        # Model checkpointing
        keras.callbacks.ModelCheckpoint(
            filepath=str(model_dir / "best_model.keras"),
            monitor='val_storm_binary_auc',
            mode='max',
            save_best_only=True,
            verbose=1
        ),
        # Early stopping
        keras.callbacks.EarlyStopping(
            monitor='val_storm_binary_auc',
            patience=15,
            mode='max',
            restore_best_weights=True,
            verbose=1
        ),
        # Learning rate reduction
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        ),
        # TensorBoard
        keras.callbacks.TensorBoard(
            log_dir=str(logs_dir / datetime.now().strftime("%Y%m%d-%H%M%S")),
            histogram_freq=1
        ),
        # CSV logger
        keras.callbacks.CSVLogger(
            str(logs_dir / "training_history.csv")
        )
    ]

    # Train model
    logger.info("\nStarting training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=32,
        callbacks=callbacks,
        verbose=1
    )

    # Evaluate on test set
    logger.info("\nEvaluating on test set...")
    test_results = model.evaluate(X_test, y_test, verbose=1)
    logger.info(f"Test Results: {test_results}")

    # Save final model
    final_model_path = model_dir / "final_model.keras"
    model.save(str(final_model_path))
    logger.info(f"Final model saved to {final_model_path}")

    # Generate test predictions for analysis
    logger.info("\nGenerating test predictions...")
    test_predictions = model.predict(X_test[:100])

    logger.info("\nSample predictions:")
    for i in range(5):
        logger.info(f"Sample {i}:")
        logger.info(f"  Predicted storm prob: {test_predictions['storm_binary'][i][0]:.4f}")
        logger.info(f"  Actual storm: {y_test['storm_binary'][i]:.4f}")
        logger.info(f"  Uncertainty: {test_predictions['uncertainty'][i][0]:.4f}")

    logger.info("\n✅ Training complete!")
    logger.info(f"Best model saved to: {model_dir / 'best_model.keras'}")
    logger.info(f"Training logs saved to: {logs_dir}")

    return history, model


if __name__ == "__main__":
    asyncio.run(train_enhanced_model())
