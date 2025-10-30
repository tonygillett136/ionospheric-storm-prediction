# API Reference - Ionospheric Storm Prediction System

This document describes all available API endpoints for the backend service.

## Base URL

```
http://localhost:8000/api/v1
```

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

Currently, the API does not require authentication. For production deployment, consider implementing API keys or OAuth2.

---

## Endpoints

### Health Check

#### `GET /health`

Check the health status of the system.

**Response:**
```json
{
  "status": "healthy",
  "last_data_update": "2025-10-23T21:30:00.000Z",
  "last_prediction_update": "2025-10-23T21:00:00.000Z",
  "historical_points": 24
}
```

---

### Current Data

#### `GET /current`

Get all current ionospheric conditions and predictions.

**Response:**
```json
{
  "timestamp": "2025-10-23T21:30:00.000Z",
  "latest_data": {
    "timestamp": "2025-10-23T21:30:00.000Z",
    "tec_data": { ... },
    "tec_statistics": {
      "mean": 22.5,
      "median": 21.3,
      "std": 8.2,
      "min": 5.1,
      "max": 45.6,
      "percentile_95": 38.2
    },
    "kp_index": 3.0,
    "solar_wind_params": {
      "speed": 420,
      "density": 5.2,
      "temperature": 100000
    },
    "imf_bz": -2.1,
    "f107_flux": 95.0
  },
  "latest_prediction": { ... }
}
```

---

### Storm Prediction

#### `GET /prediction`

Get the latest ionospheric storm prediction.

**Response:**
```json
{
  "timestamp": "2025-10-23T21:00:00.000Z",
  "storm_probability_24h": 0.35,
  "hourly_probabilities": [0.15, 0.18, 0.22, ..., 0.45],
  "tec_forecast_24h": [22.1, 23.5, 24.8, ..., 26.2],
  "risk_level": "moderate",
  "max_probability": 0.45,
  "average_probability": 0.32,
  "model_version": "CNN-LSTM-v1.0"
}
```

**Response Fields:**

- `storm_probability_24h`: Overall probability of storm in next 24h (0-1)
- `hourly_probabilities`: Array of 24 hourly probabilities
- `tec_forecast_24h`: Array of 24 hourly TEC forecasts (TECU)
- `risk_level`: Categorical risk level (low, moderate, elevated, high, severe)
- `max_probability`: Maximum hourly probability
- `average_probability`: Average of all hourly probabilities
- `model_version`: Version identifier of the prediction model

---

### TEC Data

#### `GET /tec/current`

Get current Total Electron Content data.

**Response:**
```json
{
  "tec_data": {
    "timestamp": "2025-10-23T21:30:00.000Z",
    "latitudes": [-87.5, -85.0, ..., 87.5],
    "longitudes": [-180, -175, ..., 175],
    "tec_values": [[...], [...], ...],
    "units": "TECU",
    "source": "empirical_model"
  },
  "tec_statistics": {
    "mean": 22.5,
    "median": 21.3,
    "std": 8.2,
    "min": 5.1,
    "max": 45.6,
    "percentile_95": 38.2
  }
}
```

**TEC Data Structure:**

- Grid resolution: 2.5° latitude × 5° longitude
- Latitude range: -87.5° to 87.5° (71 points)
- Longitude range: -180° to 175° (72 points)
- Values in Total Electron Content Units (TECU)

---

### Space Weather

#### `GET /space-weather/current`

Get current space weather parameters.

**Response:**
```json
{
  "timestamp": "2025-10-23T21:30:00.000Z",
  "kp_index": 3.0,
  "solar_wind": {
    "timestamp": "2025-10-23T21:28:00.000Z",
    "speed": 420,
    "density": 5.2,
    "temperature": 100000
  },
  "imf_bz": -2.1,
  "f107_flux": 95.0
}
```

**Parameter Descriptions:**

- `kp_index`: Planetary K-index (0-9), measures geomagnetic activity
- `solar_wind.speed`: Solar wind speed in km/s
- `solar_wind.density`: Solar wind density in particles/cm³
- `solar_wind.temperature`: Solar wind temperature in Kelvin
- `imf_bz`: Z-component of Interplanetary Magnetic Field in nT
- `f107_flux`: 10.7 cm solar radio flux in Solar Flux Units

---

### Historical Trends

#### `GET /trends/{hours}`

Get historical trends for specified time period.

**Parameters:**
- `hours` (path parameter): Number of hours (1-168)

**Example:**
```
GET /trends/24
```

**Response:**
```json
{
  "timestamps": ["2025-10-22T21:00:00Z", "2025-10-22T22:00:00Z", ...],
  "kp_index": [2.3, 2.7, 3.0, ...],
  "tec_mean": [18.5, 19.2, 20.1, ...],
  "solar_wind_speed": [380, 395, 410, ...],
  "data_points": 24
}
```

---

### Manual Updates

#### `POST /update/data`

Manually trigger a data collection update.

**Response:**
```json
{
  "status": "success",
  "timestamp": "2025-10-23T21:35:00.000Z"
}
```

#### `POST /update/prediction`

Manually trigger a prediction update.

**Response:**
```json
{
  "status": "success",
  "prediction": { ... }
}
```

---

## WebSocket Connection

### `WS /ws`

Real-time data stream via WebSocket.

**Connection URL:**
```
ws://localhost:8000/api/v1/ws
```

**Message Types:**

#### Server → Client

1. **Initial Data**
```json
{
  "type": "initial_data",
  "data": { ... },
  "prediction": { ... }
}
```

2. **Data Update**
```json
{
  "type": "data_update",
  "data": { ... }
}
```

3. **Prediction Update**
```json
{
  "type": "prediction_update",
  "prediction": { ... }
}
```

4. **Periodic Update**
```json
{
  "type": "periodic_update",
  "data": {
    "timestamp": "2025-10-23T21:35:00.000Z",
    "kp_index": 3.0,
    "tec_mean": 22.5,
    "risk_level": "moderate"
  }
}
```

5. **Heartbeat**
```json
{
  "type": "heartbeat"
}
```

#### Client → Server

1. **Ping**
```json
{
  "type": "ping"
}
```

**Response:** `{"type": "pong"}`

2. **Request Update**
```json
{
  "type": "request_update"
}
```

**Response:** `{"type": "status_update", "status": {...}}`

---

## Data Sources

The system collects data from:

1. **NOAA SWPC** - Space Weather Prediction Center
   - Kp index
   - Geomagnetic storm forecasts
   - Solar wind parameters
   - Magnetic field data
   - F10.7 solar flux

2. **Empirical Models** - For demonstration purposes
   - TEC distribution based on latitude, longitude, and time
   - Realistic diurnal and latitudinal variations

In a production system, you would integrate:
- NASA CDDIS for real GNSS TEC data
- NOAA GloTEC for global TEC products
- GOES satellite magnetometer data

---

## Error Responses

All endpoints may return error responses:

### 404 Not Found
```json
{
  "detail": "No prediction available yet"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Data service not initialized"
}
```

### 400 Bad Request
```json
{
  "detail": "Hours must be between 1 and 168"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production:
- Consider implementing rate limiting (e.g., 100 requests/minute)
- Use caching for frequently accessed endpoints
- Implement API keys for tracking usage

---

## Data Update Intervals

Default intervals (configurable via `.env`):

- **Data Collection**: Every 5 minutes (300 seconds)
- **Prediction Update**: Every 1 hour (3600 seconds)
- **WebSocket Heartbeat**: Every 60 seconds

---

## Example Client Code

### JavaScript (Browser)

```javascript
// REST API
const response = await fetch('http://localhost:8000/api/v1/prediction');
const prediction = await response.json();
console.log('Storm probability:', prediction.storm_probability_24h);

// WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

ws.send(JSON.stringify({ type: 'ping' }));
```

### Python

```python
import requests

# REST API
response = requests.get('http://localhost:8000/api/v1/prediction')
prediction = response.json()
print(f"Storm probability: {prediction['storm_probability_24h']}")

# WebSocket
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data}")

ws = websocket.WebSocketApp(
    'ws://localhost:8000/api/v1/ws',
    on_message=on_message
)
ws.run_forever()
```

### cURL

```bash
# Get current prediction
curl http://localhost:8000/api/v1/prediction

# Trigger manual update
curl -X POST http://localhost:8000/api/v1/update/data

# Get 24-hour trends
curl http://localhost:8000/api/v1/trends/24
```

---

## CORS Configuration

Default allowed origins (configurable in `.env`):
- http://localhost:5173 (Vite dev server)
- http://localhost:3000 (Alternative dev port)

To add more origins, update `CORS_ORIGINS` in `.env`:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://yourdomain.com
```
