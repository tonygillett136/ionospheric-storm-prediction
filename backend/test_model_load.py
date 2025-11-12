"""Quick test to see the full error when loading and using the model"""
from app.models.storm_predictor_v2 import EnhancedStormPredictor

# Create predictor and load trained model
predictor = EnhancedStormPredictor()
print("Loading model...")
predictor.load_model("models/v2/best_model.keras")
print("Model loaded successfully")

# Try to make a prediction
test_data = {
    'tec_statistics': {'mean': 25.0, 'std': 5.0},
    'kp_index': 3.0,
    'dst_index': -20.0,
    'solar_wind_params': {
        'speed': 400.0,
        'density': 5.0
    },
    'imf_bz': -2.0,
    'f107_flux': 120.0,
    'timestamp': '2023-01-01T12:00:00'
}

print("Testing prediction...")
try:
    prediction = predictor.predict(test_data)
    print(f"Success! Prediction: {prediction}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
