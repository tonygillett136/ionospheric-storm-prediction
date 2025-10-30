# API Documentation

## Base URL
- REST API: `http://localhost:8000/api/v1`
- WebSocket: `ws://localhost:8000/api/v1`

## REST Endpoints

### Health Check
**GET** `/health`

Returns system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-24T12:00:00Z",
  "version": "1.0.0"
}
```

### Current Space Weather
**GET** `/space-weather/current`

Returns current space weather parameters.

**Response:**
```json
{
  "kp_index": 3.0,
  "dst_index": -15.0,
  "solar_wind": {
    "speed": 450.0,
    "density": 5.2,
    "temperature": 100000.0
  },
  "imf_bz": -2.5,
  "f107_flux": 120.0,
  "timestamp": "2025-01-24T12:00:00Z"
}
```

### Current TEC Data
**GET** `/tec/current`

Returns current Total Electron Content measurements.

**Response:**
```json
{
  "tec_data": {
    "latitudes": [-90, -87.5, ..., 90],
    "longitudes": [-180, -175, ..., 180],
    "tec_values": [[...], [...], ...],
    "roti_values": [[...], [...], ...],
    "timestamp": "2025-01-24T12:00:00Z"
  }
}
```

### Storm Prediction
**GET** `/prediction`

Returns 24-hour storm prediction.

**Response:**
```json
{
  "storm_probability_24h": 0.35,
  "risk_level": "moderate",
  "hourly_probabilities": [0.25, 0.28, ..., 0.42],
  "tec_forecast_24h": [25.5, 26.2, ..., 28.1],
  "max_probability": 0.42,
  "average_probability": 0.33,
  "model_version": "CNN-LSTM v1.0",
  "confidence": 0.87,
  "timestamp": "2025-01-24T12:00:00Z"
}
```

### Historical Trends
**GET** `/trends/{hours}`

Returns historical data for specified time period.

**Parameters:**
- `hours` (path): Number of hours to retrieve (24, 168, 720, 8760)

**Response:**
```json
{
  "data": [
    {
      "timestamp": "2025-01-24T12:00:00Z",
      "storm_probability": 0.35,
      "kp_index": 3.0,
      "tec_mean": 25.5,
      "solar_wind_speed": 450.0
    },
    ...
  ]
}
```

### Trigger Data Update
**POST** `/update/data`

Manually triggers data collection from external sources.

**Response:**
```json
{
  "status": "success",
  "message": "Data update triggered",
  "timestamp": "2025-01-24T12:00:00Z"
}
```

### Trigger Prediction Update
**POST** `/update/prediction`

Manually triggers prediction model execution.

**Response:**
```json
{
  "status": "success",
  "message": "Prediction update triggered",
  "timestamp": "2025-01-24T12:00:00Z"
}
```

## WebSocket

### Connection
**WS** `/ws`

Establish WebSocket connection for real-time updates.

**Client → Server:**
```json
{
  "action": "subscribe",
  "channels": ["predictions", "tec", "space_weather"]
}
```

**Server → Client:**
```json
{
  "type": "initial_data",
  "data": {...},
  "prediction": {...},
  "timestamp": "2025-01-24T12:00:00Z"
}
```

**Server → Client (Updates):**
```json
{
  "type": "prediction_update",
  "prediction": {...},
  "timestamp": "2025-01-24T12:05:00Z"
}
```

```json
{
  "type": "tec_update",
  "data": {...},
  "timestamp": "2025-01-24T12:05:00Z"
}
```

## Error Responses

All endpoints return standard error format:

```json
{
  "detail": "Error description",
  "status_code": 400,
  "timestamp": "2025-01-24T12:00:00Z"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable

## Rate Limiting

- REST API: 100 requests/minute per IP
- WebSocket: 10 connections per IP

## CORS

By default, CORS is enabled for `http://localhost:5173`

To configure for production, update `backend/app/core/config.py`:
```python
CORS_ORIGINS = [
    "https://your-domain.com"
]
```
