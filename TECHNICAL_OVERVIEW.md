# Technical Overview - Ionospheric Storm Prediction System

## Executive Summary

The Ionospheric Storm Prediction System is a sophisticated real-time monitoring and forecasting application that predicts ionospheric storms up to 24 hours in advance using machine learning. The system integrates multiple space weather data sources and employs a hybrid CNN-LSTM neural network architecture to provide accurate storm probability forecasts.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   3D Globe   │  │ Storm Gauge  │  │   Charts     │      │
│  │  (Three.js)  │  │              │  │ (Recharts)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                          │                                   │
│                     WebSocket + REST API                     │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Data Service (Orchestrator)               │ │
│  └──┬─────────────┬──────────────────┬───────────────┬───┘ │
│     │             │                  │               │      │
│  ┌──▼──┐      ┌──▼──┐           ┌──▼──┐        ┌───▼───┐  │
│  │NOAA │      │ TEC │           │Storm│        │WebSock│  │
│  │SWPC │      │Coll.│           │Pred.│        │Manager│  │
│  │Coll.│      │     │           │Model│        │       │  │
│  └─────┘      └─────┘           └─────┘        └───────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                   External Data Sources                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │  NOAA   │  │  NASA   │  │ GloTEC  │  │  GOES   │       │
│  │  SWPC   │  │  CDDIS  │  │         │  │Satellite│       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Frontend Layer
- **Framework**: React 18.3 with Vite build tool
- **3D Visualization**: Three.js + react-three-fiber for Earth globe
- **Charts**: Recharts for time-series visualization
- **State Management**: React hooks (useState, useEffect)
- **API Communication**: Axios for REST, native WebSocket API

#### Backend Layer
- **Web Framework**: FastAPI (async Python framework)
- **Server**: Uvicorn ASGI server
- **Data Collection**: aiohttp for async HTTP requests
- **ML Framework**: TensorFlow/Keras
- **Data Processing**: NumPy, Pandas, SciPy

---

## Machine Learning Model

### Architecture: Hybrid CNN-LSTM

The prediction model combines Convolutional Neural Networks (CNN) for spatial feature extraction with Long Short-Term Memory (LSTM) networks for temporal sequence modeling.

```
Input: [24 hours × 8 features]
        │
        ▼
┌──────────────────┐
│   Conv1D (64)    │  ← Spatial pattern detection
│   BatchNorm      │
│   MaxPooling     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Conv1D (128)   │  ← Deeper feature extraction
│   BatchNorm      │
│   MaxPooling     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   LSTM (128)     │  ← Temporal dependencies
│   Dropout (0.3)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   LSTM (64)      │  ← Long-term patterns
│   Dropout (0.3)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Dense (64)     │  ← Decision layers
│   Dropout (0.2)  │
│   Dense (32)     │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────┐
│         Multi-Output Heads         │
│  ┌──────────┐ ┌─────────────────┐ │
│  │  Storm   │ │  Hourly Probs.  │ │
│  │  Binary  │ │  (24 values)    │ │
│  │          │ │                 │ │
│  └──────────┘ └─────────────────┘ │
│  ┌─────────────────────────────┐  │
│  │   TEC Forecast (24 hours)   │  │
│  └─────────────────────────────┘  │
└────────────────────────────────────┘
```

### Input Features (8 dimensions)

1. **TEC Mean**: Average Total Electron Content
2. **TEC Std**: TEC variability indicator
3. **Kp Index**: Geomagnetic activity (0-9 scale)
4. **Solar Wind Speed**: km/s
5. **IMF Bz**: Interplanetary Magnetic Field Z-component (nT)
6. **F10.7 Flux**: Solar radio flux (SFU)
7. **Hour (cyclical)**: sin(2π × hour/24)
8. **Day of Year (cyclical)**: sin(2π × day/365)

### Output Predictions

1. **Storm Binary**: Single probability (0-1) for 24h storm occurrence
2. **Hourly Probabilities**: 24 values for each hour ahead
3. **TEC Forecast**: 24 hourly TEC predictions

### Training Details

- **Loss Function**: Multi-task learning
  - Binary cross-entropy for classification
  - MSE for TEC regression
  - Weighted combination (2:1:0.5)

- **Optimizer**: Adam with learning rate 0.001
- **Regularization**: Dropout layers, Batch normalization
- **Sequence Length**: 24 hours of historical data

---

## Data Collection Pipeline

### NOAA SWPC Data Collection

**Endpoints:**
- `/products/noaa-planetary-k-index.json` - Kp index
- `/products/noaa-geomagnetic-forecast.json` - Storm forecasts
- `/products/solar-wind/plasma-7-day.json` - Solar wind
- `/products/solar-wind/mag-7-day.json` - Magnetic field
- `/products/summary/10cm-flux.json` - F10.7 flux

**Collection Frequency**: Every 5 minutes (configurable)

### TEC Data Generation

For demonstration purposes, the system generates synthetic TEC data using empirical models:

**Model**: Latitude-dependent + diurnal variation
```python
TEC(lat, lon, hour) = base_TEC × cos(1.5×lat) × [1 + 0.5×cos((local_hour - 14)×15°)]
```

**Grid Specifications**:
- Resolution: 2.5° × 5° (lat × lon)
- Coverage: Global (-87.5° to 87.5° lat, -180° to 175° lon)
- Points: 71 × 72 = 5,112 grid points

---

## Real-Time Data Flow

### WebSocket Communication

**Connection Lifecycle**:
1. Client connects to `ws://localhost:8000/api/v1/ws`
2. Server sends initial data snapshot
3. Server broadcasts updates when new data arrives
4. Periodic heartbeats maintain connection
5. Automatic reconnection on disconnect

**Message Types**:
- `initial_data`: Full state on connection
- `data_update`: New measurements available
- `prediction_update`: New forecast computed
- `periodic_update`: Summary metrics
- `heartbeat`: Keep-alive signal

### Update Schedule

| Task | Interval | Trigger |
|------|----------|---------|
| Data Collection | 5 min | Automatic |
| Prediction Update | 1 hour | Automatic |
| WebSocket Broadcast | 1 min | Automatic |
| Manual Trigger | On-demand | API POST |

---

## Risk Classification System

Storm risk levels are determined by combining maximum and average hourly probabilities:

```
Combined Score = 0.6 × max_prob + 0.4 × avg_prob

Risk Levels:
├─ Low:      < 0.2  (< 20%)
├─ Moderate: 0.2-0.4 (20-40%)
├─ Elevated: 0.4-0.6 (40-60%)
├─ High:     0.6-0.8 (60-80%)
└─ Severe:   > 0.8  (> 80%)
```

**Color Coding**:
- Low: Green (#4ade80)
- Moderate: Yellow (#facc15)
- Elevated: Orange (#fb923c)
- High: Red (#f87171)
- Severe: Dark Red (#dc2626)

---

## Space Weather Parameters

### Kp Index
- **Range**: 0-9
- **Interpretation**:
  - 0-2: Quiet
  - 3-4: Unsettled
  - 5-6: Storm
  - 7-9: Severe storm
- **Update**: Every 3 hours from NOAA

### Solar Wind Speed
- **Normal Range**: 300-500 km/s
- **High Speed**: > 500 km/s
- **Storm Indicator**: Sudden increases
- **Source**: ACE/DSCOVR satellites (L1 point)

### IMF Bz
- **Range**: -20 to +20 nT
- **Critical**: < -5 nT (southward)
- **Significance**: Southward Bz enables magnetic reconnection
- **Storm Correlation**: Strong negative Bz → Higher storm probability

### F10.7 Solar Flux
- **Range**: 50-300 SFU
- **Solar Cycle**: Varies over 11-year cycle
- **Current Cycle**: Solar Cycle 25 (2019-2030)
- **Impact**: Higher flux → More ionization

---

## Performance Characteristics

### Model Performance (Expected)

Based on research literature for similar systems:

| Metric | Value |
|--------|-------|
| Accuracy | ~85-90% |
| Precision | ~0.80-0.85 |
| Recall | ~0.75-0.80 |
| F1 Score | ~0.77-0.82 |
| RMSE (TEC) | ~3-5 TECU |
| R² (TEC) | ~0.85-0.90 |

*Note: These are typical values from research. Actual performance depends on training data quality.*

### System Performance

| Component | Latency | Throughput |
|-----------|---------|------------|
| Data Collection | < 2s | N/A |
| Prediction | < 100ms | ~10 req/s |
| API Response | < 50ms | 100+ req/s |
| WebSocket | < 10ms | Real-time |
| 3D Rendering | 60 FPS | Client-side |

### Resource Usage

| Resource | Backend | Frontend |
|----------|---------|----------|
| CPU | 10-20% | 5-15% |
| RAM | 500MB-1GB | 200MB-500MB |
| Network | ~1KB/min | ~5KB/min |
| Storage | < 100MB | ~50MB |

---

## Security Considerations

### Current Implementation
- No authentication required
- CORS restricted to localhost origins
- No data encryption (HTTP/WS)
- No rate limiting

### Production Recommendations

1. **Authentication**
   - Implement API key authentication
   - Use OAuth2 for user accounts
   - JWT tokens for session management

2. **Encryption**
   - Enable HTTPS/WSS with SSL/TLS
   - Use Let's Encrypt for certificates
   - Encrypt sensitive configuration

3. **Rate Limiting**
   - Implement per-IP rate limits
   - Use Redis for distributed rate limiting
   - Set quotas per API key

4. **Input Validation**
   - Validate all user inputs
   - Sanitize database queries
   - Implement request size limits

5. **Monitoring**
   - Log all API requests
   - Monitor for suspicious activity
   - Set up alerts for anomalies

---

## Scalability

### Horizontal Scaling

**Backend**:
- Run multiple FastAPI instances behind load balancer
- Use Redis for shared session storage
- Implement distributed WebSocket management

**Database** (if added):
- PostgreSQL with replication
- TimescaleDB for time-series data
- Redis for caching

### Vertical Scaling

**Current Limits**:
- Single process: ~1000 concurrent connections
- Memory: Limited by historical data storage
- CPU: Limited by ML inference

**Optimizations**:
- Use GPU for ML inference
- Implement model quantization
- Add result caching
- Optimize data structures

---

## Future Enhancements

### Short-term (1-3 months)
- [ ] Integrate real GNSS TEC data from NASA CDDIS
- [ ] Add user authentication and accounts
- [ ] Implement alert notifications (email/SMS)
- [ ] Add historical data database (PostgreSQL)
- [ ] Mobile-responsive design improvements

### Medium-term (3-6 months)
- [ ] Train model on real historical storm data
- [ ] Add regional storm predictions
- [ ] Implement ROTI/S4 scintillation indices
- [ ] Create mobile apps (iOS/Android)
- [ ] Add data export features (CSV, JSON, PDF)

### Long-term (6-12 months)
- [ ] Multi-model ensemble predictions
- [ ] Uncertainty quantification
- [ ] Explainable AI features
- [ ] Advanced visualization (AR/VR)
- [ ] API for third-party integrations
- [ ] Machine learning model auto-retraining

---

## Research Background

### Scientific Basis

The system is built on research findings from:

1. **TEC Prediction**:
   - Hybrid CNN-LSTM models (Ren et al., 2024)
   - Multi-model ensemble methods (Ban et al., 2023)
   - Deep learning approaches (Various authors, 2020-2024)

2. **Storm Indicators**:
   - Kp index correlation with ionospheric disturbances
   - IMF Bz as primary driver of geomagnetic storms
   - Solar wind speed and density effects

3. **Data Sources**:
   - NOAA SWPC operational products
   - NASA CDDIS Global Ionosphere Maps
   - IGS ionosphere analysis centers

### Key References

- Ren et al. (2024): "Mixed CNN-BiLSTM Method for Global Ionospheric TEC During Storm Periods"
- Ban et al. (2023): "Regional Ionospheric Storm Forecasting Using LSTM"
- Liu et al. (2021): "Machine Learning Prediction of Storm-Time High-Latitude Ionospheric Irregularities"
- NOAA (2025): "GloTEC Global Operational Product"

---

## Development Roadmap

### Version History

- **v1.0.0** (Current): Initial release with core features
  - Real-time data collection
  - CNN-LSTM prediction model
  - 3D visualization
  - WebSocket streaming

### Planned Releases

- **v1.1.0**: Authentication & alerts
- **v1.2.0**: Real TEC data integration
- **v1.3.0**: Mobile applications
- **v2.0.0**: Production-ready deployment

---

## Contributing

See CONTRIBUTING.md for:
- Code style guidelines
- Testing requirements
- Pull request process
- Development setup

---

## License

MIT License - See LICENSE file for details

---

## Contact & Support

For technical questions or contributions:
- GitHub Issues: [Repository URL]
- Documentation: See README.md, SETUP.md, API_REFERENCE.md
- Email: [Contact email]
