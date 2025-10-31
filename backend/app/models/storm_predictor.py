"""
Ionospheric Storm Prediction Model
Hybrid CNN-LSTM model for predicting ionospheric storms
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StormPredictor:
    """
    Hybrid CNN-LSTM model for ionospheric storm prediction
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model: Optional[keras.Model] = None
        self.model_path = model_path
        self.sequence_length = 24  # 24 hours of historical data
        self.feature_count = 8  # Number of input features

        # Feature scaling parameters (to be set during training)
        self.feature_means = None
        self.feature_stds = None

        if model_path:
            self.load_model(model_path)
        else:
            self.model = self.build_model()

    def build_model(self) -> keras.Model:
        """
        Build the hybrid CNN-LSTM architecture for storm prediction
        """
        inputs = layers.Input(shape=(self.sequence_length, self.feature_count))

        # CNN layers for spatial feature extraction
        x = layers.Conv1D(filters=64, kernel_size=3, activation='relu', padding='same')(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling1D(pool_size=2)(x)

        x = layers.Conv1D(filters=128, kernel_size=3, activation='relu', padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling1D(pool_size=2)(x)

        # LSTM layers for temporal dependencies
        x = layers.LSTM(128, return_sequences=True)(x)
        x = layers.Dropout(0.3)(x)

        x = layers.LSTM(64, return_sequences=False)(x)
        x = layers.Dropout(0.3)(x)

        # Dense layers for prediction
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(0.2)(x)

        x = layers.Dense(32, activation='relu')(x)

        # Output layers
        # Multi-output: storm probability for next 24 hours
        storm_prob = layers.Dense(24, activation='sigmoid', name='storm_probability')(x)

        # Binary classification: will a storm occur?
        storm_binary = layers.Dense(1, activation='sigmoid', name='storm_binary')(x)

        # TEC prediction
        tec_prediction = layers.Dense(24, activation='linear', name='tec_forecast')(x)

        model = keras.Model(
            inputs=inputs,
            outputs={
                'storm_probability': storm_prob,
                'storm_binary': storm_binary,
                'tec_forecast': tec_prediction
            }
        )

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss={
                'storm_probability': 'binary_crossentropy',
                'storm_binary': 'binary_crossentropy',
                'tec_forecast': 'mse'
            },
            loss_weights={
                'storm_probability': 1.0,
                'storm_binary': 2.0,  # Higher weight for binary prediction
                'tec_forecast': 0.5
            },
            metrics={
                'storm_probability': ['accuracy'],
                'storm_binary': ['accuracy', tf.keras.metrics.AUC()],
                'tec_forecast': ['mae']
            }
        )

        logger.info("Built CNN-LSTM storm prediction model")
        return model

    def prepare_features(self, data: Dict) -> np.ndarray:
        """
        Prepare input features from collected data

        Features:
        1. TEC mean
        2. TEC std
        3. Kp index
        4. Solar wind speed
        5. IMF Bz
        6. F10.7 flux
        7. Hour of day (cyclical)
        8. Day of year (cyclical)
        """
        try:
            features = []

            # TEC features
            tec_stats = data.get('tec_statistics', {})
            features.append(tec_stats.get('mean', 0))
            features.append(tec_stats.get('std', 0))

            # Geomagnetic index
            features.append(data.get('kp_index', 0))

            # Solar wind parameters
            solar_wind = data.get('solar_wind_params', {})
            features.append(solar_wind.get('speed', 400))
            features.append(data.get('imf_bz', 0))

            # Solar activity
            features.append(data.get('f107_flux', 70))

            # Time features (cyclical encoding)
            timestamp = datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat()))
            hour_angle = 2 * np.pi * timestamp.hour / 24
            features.append(np.sin(hour_angle))

            day_of_year = timestamp.timetuple().tm_yday
            day_angle = 2 * np.pi * day_of_year / 365
            features.append(np.sin(day_angle))

            return np.array(features)

        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return np.zeros(self.feature_count)

    def normalize_features(self, features: np.ndarray) -> np.ndarray:
        """
        Normalize features using pre-computed statistics
        """
        if self.feature_means is None or self.feature_stds is None:
            # Initialize with reasonable defaults if not set
            self.feature_means = np.array([20, 5, 3, 400, 0, 100, 0, 0])
            self.feature_stds = np.array([15, 3, 2, 100, 5, 50, 1, 1])

        return (features - self.feature_means) / (self.feature_stds + 1e-8)

    async def predict_storm(self, historical_data: List[Dict]) -> Dict:
        """
        Predict ionospheric storm probability for the next 24 hours

        Args:
            historical_data: List of data dictionaries for the past 24 hours

        Returns: Prediction results including probabilities and TEC forecast
        """
        try:
            # Prepare feature sequence
            feature_sequence = []
            for data_point in historical_data[-self.sequence_length:]:
                features = self.prepare_features(data_point)
                normalized = self.normalize_features(features)
                feature_sequence.append(normalized)

            # Pad if necessary
            while len(feature_sequence) < self.sequence_length:
                feature_sequence.insert(0, np.zeros(self.feature_count))

            # Convert to numpy array and reshape for model input
            X = np.array(feature_sequence).reshape(1, self.sequence_length, self.feature_count)

            # Make prediction
            if self.model is None:
                logger.warning("Model not initialized, building new model")
                self.model = self.build_model()

            predictions = self.model.predict(X, verbose=0)

            # Extract predictions
            hourly_probs = predictions['storm_probability'][0].tolist()
            storm_binary = float(predictions['storm_binary'][0][0])
            tec_forecast = predictions['tec_forecast'][0].tolist()

            # Calculate overall risk level
            max_prob = max(hourly_probs)
            avg_prob = sum(hourly_probs) / len(hourly_probs)

            risk_level = self._calculate_risk_level(max_prob, avg_prob)

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "storm_probability_24h": round(storm_binary, 4),
                "hourly_probabilities": [round(p, 4) for p in hourly_probs],
                "tec_forecast_24h": [round(t, 2) for t in tec_forecast],
                "risk_level": risk_level,
                "max_probability": round(max_prob, 4),
                "average_probability": round(avg_prob, 4),
                "model_version": "CNN-LSTM-v1.0"
            }

        except Exception as e:
            logger.error(f"Error predicting storm: {e}")
            return self._get_default_prediction()

    def _calculate_risk_level(self, max_prob: float, avg_prob: float) -> str:
        """
        Calculate overall risk level based on probabilities
        """
        # Weight both max and average probabilities
        combined_score = 0.6 * max_prob + 0.4 * avg_prob

        if combined_score < 0.2:
            return "low"
        elif combined_score < 0.4:
            return "moderate"
        elif combined_score < 0.6:
            return "elevated"
        elif combined_score < 0.8:
            return "high"
        else:
            return "severe"

    def _get_default_prediction(self) -> Dict:
        """
        Return default prediction when model fails
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "storm_probability_24h": 0.0,
            "hourly_probabilities": [0.0] * 24,
            "tec_forecast_24h": [20.0] * 24,
            "risk_level": "unknown",
            "max_probability": 0.0,
            "average_probability": 0.0,
            "model_version": "CNN-LSTM-v1.0",
            "error": "Prediction failed"
        }

    def save_model(self, path: str):
        """Save the trained model"""
        if self.model:
            self.model.save(path)
            logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load a trained model"""
        try:
            self.model = keras.models.load_model(path)
            logger.info(f"Model loaded from {path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.info("Building new model instead")
            self.model = self.build_model()

    def get_model_summary(self) -> str:
        """Get model architecture summary"""
        if self.model:
            summary_list = []
            self.model.summary(print_fn=lambda x: summary_list.append(x))
            return '\n'.join(summary_list)
        return "Model not initialized"
