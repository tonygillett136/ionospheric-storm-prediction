"""
API Routes for the Ionospheric Storm Prediction System
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import List
import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timedelta

from app.services.data_service import DataService
from app.services.backtesting_service import BacktestingService
from app.services.impact_assessment_service import ImpactAssessmentService
from app.services.regional_prediction_service import RegionalPredictionService
from app.services.alert_service import AlertService
from app.services.recent_storm_performance_service import RecentStormPerformanceService
from app.services.geographic_climatology_service import GeographicClimatologyService, GeographicRegion
from app.db.database import get_db
from app.db.repository import HistoricalDataRepository
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Global data service instance
data_service: DataService = None

# Geographic climatology service instance
geographic_climatology_service: GeographicClimatologyService = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


manager = ConnectionManager()


def init_data_service():
    """Initialize the global data service"""
    global data_service
    data_service = DataService()
    return data_service


async def init_geographic_climatology(db: AsyncSession):
    """Initialize and build geographic climatology service"""
    global geographic_climatology_service

    logger.info("Initializing geographic climatology service")
    geographic_climatology_service = GeographicClimatologyService()

    # Build climatology tables for all regions
    bin_counts = await geographic_climatology_service.build_climatology(db)

    logger.info(f"Geographic climatology initialized: {bin_counts}")

    return geographic_climatology_service


@router.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "Ionospheric Storm Prediction System",
        "version": "1.0.0",
        "status": "operational"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service not initialized")

    return {
        "status": "healthy",
        "last_data_update": data_service.last_data_update.isoformat() if data_service.last_data_update else None,
        "last_prediction_update": data_service.last_prediction_update.isoformat() if data_service.last_prediction_update else None,
        "historical_points": len(data_service.historical_data)
    }


@router.get("/current")
async def get_current_data():
    """Get current ionospheric conditions and predictions"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service not initialized")

    status = await data_service.get_current_status()
    return status


@router.get("/prediction")
async def get_prediction(db: AsyncSession = Depends(get_db), use_ensemble: bool = True):
    """
    Get the latest storm prediction.

    By default returns ensemble prediction (70% climatology + 30% V2.1).
    Set use_ensemble=false to get V2.1 model predictions only.
    """
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service not initialized")

    # Return ensemble prediction by default
    if use_ensemble:
        from app.models.ensemble_predictor import EnsembleStormPredictor

        if data_service.latest_data is None:
            raise HTTPException(status_code=404, detail="No data available for prediction")

        try:
            # Initialize ensemble predictor with default 70/30 weighting
            ensemble = EnsembleStormPredictor(
                model_path="models/v2/best_model.keras",
                climatology_weight=0.7,
                model_weight=0.3
            )

            # Load climatology if not already loaded
            if not ensemble.climatology_loaded:
                await ensemble.load_climatology()

            # Use in-memory historical data
            in_memory_data = list(data_service.historical_data)

            if len(in_memory_data) < 24:
                # Fall back to V2.1-only if insufficient data for ensemble
                if data_service.latest_prediction is None:
                    raise HTTPException(status_code=404, detail="No prediction available yet")
                return data_service.latest_prediction

            # Format data for ensemble predictor
            historical_data = []
            for d in in_memory_data[-24:]:
                tec_stats = d.get('tec_statistics', {})
                sw_params = d.get('solar_wind_params', {})

                historical_data.append({
                    'tec_statistics': {
                        'mean': tec_stats.get('mean', 0),
                        'std': tec_stats.get('std', 0)
                    },
                    'kp_index': d.get('kp_index', 0),
                    'dst_index': d.get('dst_index', 0),
                    'solar_wind_params': {
                        'speed': sw_params.get('speed', 0),
                        'density': sw_params.get('density', 0)
                    },
                    'imf_bz': d.get('imf_bz', 0),
                    'f107_flux': d.get('f107_flux', 100),
                    'timestamp': d.get('timestamp', datetime.utcnow().isoformat()),
                    'latitude': 45.0,
                    'longitude': 0.0
                })

            # Get ensemble prediction
            prediction = await ensemble.predict_with_components(historical_data)
            return prediction

        except Exception as e:
            logger.error(f"Ensemble prediction failed: {e}")
            # Fall back to V2.1-only prediction on error
            if data_service.latest_prediction is None:
                raise HTTPException(status_code=404, detail="No prediction available yet")
            return data_service.latest_prediction

    # V2.1-only prediction (when use_ensemble=false)
    if data_service.latest_prediction is None:
        raise HTTPException(status_code=404, detail="No prediction available yet")

    return data_service.latest_prediction


@router.get("/prediction/ensemble")
async def get_ensemble_prediction(
    climatology_weight: float = 0.7,
    model_weight: float = 0.3,
    db: AsyncSession = Depends(get_db)
):
    """
    Get ensemble storm prediction combining climatology and V2.1 model.

    Args:
        climatology_weight: Weight for climatology forecast (default 0.7 = 70%)
        model_weight: Weight for V2.1 model forecast (default 0.3 = 30%)

    Returns:
        Enhanced prediction with separate climatology, V2.1, and ensemble forecasts
    """
    from app.models.ensemble_predictor import EnsembleStormPredictor

    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service not initialized")

    if data_service.latest_data is None:
        raise HTTPException(status_code=404, detail="No data available for prediction")

    # Validate weights
    if not (0.0 <= climatology_weight <= 1.0 and 0.0 <= model_weight <= 1.0):
        raise HTTPException(status_code=400, detail="Weights must be between 0.0 and 1.0")

    if abs(climatology_weight + model_weight - 1.0) > 0.01:
        raise HTTPException(status_code=400, detail="Weights must sum to 1.0")

    try:
        # Initialize ensemble predictor
        ensemble = EnsembleStormPredictor(
            model_path="models/v2/best_model.keras",
            climatology_weight=climatology_weight,
            model_weight=model_weight
        )

        # Load climatology if not already loaded
        if not ensemble.climatology_loaded:
            await ensemble.load_climatology()

        # Use in-memory historical data from data_service
        # (Live data is collected but not persisted to database)
        in_memory_data = list(data_service.historical_data)

        if len(in_memory_data) < 24:
            raise HTTPException(
                status_code=503,
                detail=f"Insufficient historical data (need 24 hours, have {len(in_memory_data)})"
            )

        # Format data for ensemble predictor - use last 24 data points
        historical_data = []
        for d in in_memory_data[-24:]:
            tec_stats = d.get('tec_statistics', {})
            sw_params = d.get('solar_wind_params', {})

            historical_data.append({
                'tec_statistics': {
                    'mean': tec_stats.get('mean', 0),
                    'std': tec_stats.get('std', 0)
                },
                'kp_index': d.get('kp_index', 0),
                'dst_index': d.get('dst_index', 0),
                'solar_wind_params': {
                    'speed': sw_params.get('speed', 0),
                    'density': sw_params.get('density', 0)
                },
                'imf_bz': d.get('imf_bz', 0),
                'f107_flux': d.get('f107_flux', 100),
                'timestamp': d.get('timestamp', datetime.utcnow().isoformat()),
                'latitude': 45.0,  # Default mid-latitude
                'longitude': 0.0
            })

        # Get ensemble prediction with all components
        prediction = await ensemble.predict_with_components(historical_data)

        return prediction

    except Exception as e:
        logger.error(f"Ensemble prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ensemble prediction failed: {str(e)}")


@router.get("/tec/current")
async def get_current_tec():
    """Get current TEC data"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service not initialized")

    if data_service.latest_data is None:
        raise HTTPException(status_code=404, detail="No TEC data available yet")

    return {
        "tec_data": data_service.latest_data.get("tec_data", {}),
        "tec_statistics": data_service.latest_data.get("tec_statistics", {})
    }


@router.get("/space-weather/current")
async def get_current_space_weather():
    """Get current space weather parameters"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service not initialized")

    if data_service.latest_data is None:
        raise HTTPException(status_code=404, detail="No space weather data available yet")

    return {
        "timestamp": data_service.latest_data.get("timestamp"),
        "kp_index": data_service.latest_data.get("kp_index"),
        "solar_wind": data_service.latest_data.get("solar_wind_params"),
        "imf_bz": data_service.latest_data.get("imf_bz"),
        "f107_flux": data_service.latest_data.get("f107_flux")
    }


@router.get("/trends/{hours}")
async def get_trends(hours: int = 24, db: AsyncSession = Depends(get_db)):
    """
    Get historical trends for specified hours from database.
    Supports up to 87,600 hours (10 years) of data.
    """
    if hours < 1 or hours > 87600:
        raise HTTPException(
            status_code=400,
            detail="Hours must be between 1 and 87,600 (10 years)"
        )

    try:
        # Query database for measurements
        measurements = await HistoricalDataRepository.get_measurements_last_n_hours(db, hours)

        if not measurements:
            raise HTTPException(status_code=404, detail="No historical data found")

        # Format data for frontend (filter out fill values from NASA OMNI)
        data = []
        for m in measurements:
            # Skip records with fill/invalid values
            # Real Kp ranges from 0-9, any value > 9 indicates bad data
            # IMF Bz fill value is 999.9
            if m.kp_index is None or m.kp_index > 9:
                continue
            if m.imf_bz and abs(m.imf_bz) > 900:
                continue

            data.append({
                "timestamp": m.timestamp.isoformat(),
                "stormProbability": m.storm_probability or 0,
                "kp_index": m.kp_index,
                "tec_mean": m.tec_mean,
                "solar_wind_speed": m.solar_wind_speed,
                "dst_index": m.dst_index,
                "imf_bz": m.imf_bz,
                "f107_flux": m.f107_flux
            })

        return {"data": data, "count": len(data)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching trends: {str(e)}")


@router.post("/update/data")
async def trigger_data_update():
    """Manually trigger a data collection update"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service not initialized")

    data = await data_service.collect_all_data()

    # Broadcast update to WebSocket clients
    await manager.broadcast({
        "type": "data_update",
        "data": data
    })

    return {"status": "success", "timestamp": data.get("timestamp")}


@router.post("/update/prediction")
async def trigger_prediction_update():
    """Manually trigger a prediction update"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service not initialized")

    prediction = await data_service.update_prediction()

    # Broadcast update to WebSocket clients
    await manager.broadcast({
        "type": "prediction_update",
        "prediction": prediction
    })

    return {"status": "success", "prediction": prediction}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    Clients receive updates when new data or predictions are available
    """
    await manager.connect(websocket)

    try:
        # Send initial data
        if data_service and data_service.latest_data:
            await websocket.send_json({
                "type": "initial_data",
                "data": data_service.latest_data,
                "prediction": data_service.latest_prediction
            })

        # Keep connection alive and listen for client messages
        while True:
            try:
                # Wait for client message with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)

                # Handle client requests
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

                elif message.get("type") == "request_update":
                    if data_service:
                        status = await data_service.get_current_status()
                        await websocket.send_json({
                            "type": "status_update",
                            "status": status
                        })

            except asyncio.TimeoutError:
                # Send periodic heartbeat
                await websocket.send_json({"type": "heartbeat"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_updates():
    """
    Background task to broadcast updates to all connected WebSocket clients
    """
    while True:
        try:
            await asyncio.sleep(60)  # Check every minute

            if data_service and data_service.latest_data:
                await manager.broadcast({
                    "type": "periodic_update",
                    "data": {
                        "timestamp": data_service.latest_data.get("timestamp"),
                        "kp_index": data_service.latest_data.get("kp_index"),
                        "tec_mean": data_service.latest_data.get("tec_statistics", {}).get("mean"),
                        "risk_level": data_service.latest_prediction.get("risk_level") if data_service.latest_prediction else None
                    }
                })

        except Exception as e:
            logger.error(f"Error in broadcast loop: {e}")
            await asyncio.sleep(5)


# Backtesting endpoints
class BacktestRequest(BaseModel):
    start_date: str  # ISO format
    end_date: str  # ISO format
    storm_threshold: float = 40.0
    sample_interval_hours: int = 1
    model_version: str = 'v1'  # 'v1' or 'v2'


class OptimizeThresholdRequest(BaseModel):
    start_date: str  # ISO format
    end_date: str  # ISO format
    optimization_method: str = 'f1'  # 'f1', 'youden', or 'cost'
    cost_false_alarm: float = 1.0
    cost_missed_storm: float = 5.0
    sample_interval_hours: int = 1
    model_version: str = 'v1'  # 'v1' or 'v2'


@router.post("/backtest/run")
async def run_backtest(request: BacktestRequest, db: AsyncSession = Depends(get_db)):
    """
    Run backtest on historical data to evaluate model performance.

    This compares model predictions against actual outcomes to validate accuracy.

    Parameters:
    - model_version: 'v1' (original) or 'v2' (enhanced with attention) - default 'v1'
    """
    try:
        # Parse dates
        start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))

        # Validate date range
        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")

        duration_days = (end_date - start_date).days
        if duration_days < 2:
            raise HTTPException(status_code=400, detail="Minimum backtest period is 2 days")

        if duration_days > 365:
            raise HTTPException(status_code=400, detail="Maximum backtest period is 365 days")

        logger.info(f"Running backtest from {start_date} to {end_date} using model {request.model_version}")

        # Run backtest with specified model version
        backtesting_service = BacktestingService(model_version=request.model_version)
        results = await backtesting_service.run_backtest(
            db,
            start_date,
            end_date,
            request.storm_threshold,
            request.sample_interval_hours
        )

        return results

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.post("/backtest/optimize-threshold")
async def optimize_threshold(request: OptimizeThresholdRequest, db: AsyncSession = Depends(get_db)):
    """
    Find optimal probability threshold by testing multiple values.

    Optimization methods:
    - 'f1': Maximize F1 score (balance of precision and recall)
    - 'youden': Maximize Youden's J statistic (sensitivity + specificity - 1)
    - 'cost': Minimize cost (weighted combination of false alarms and missed storms)

    Parameters:
    - model_version: 'v1' (original) or 'v2' (enhanced with attention) - default 'v1'
    """
    try:
        # Parse dates
        start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))

        # Validate date range
        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")

        duration_days = (end_date - start_date).days
        if duration_days < 2:
            raise HTTPException(status_code=400, detail="Minimum optimization period is 2 days")

        if duration_days > 365:
            raise HTTPException(status_code=400, detail="Maximum optimization period is 365 days")

        logger.info(f"Optimizing threshold from {start_date} to {end_date} using {request.optimization_method} method")

        # Run backtest first to get predictions and actuals
        backtesting_service = BacktestingService(model_version=request.model_version)

        # Use threshold=40 for initial run (will be optimized)
        backtest_results = await backtesting_service.run_backtest(
            db,
            start_date,
            end_date,
            storm_threshold=40.0,  # Initial threshold
            sample_interval_hours=request.sample_interval_hours
        )

        # Extract predictions and actuals
        predictions = [p['predicted_probability'] for p in backtest_results['predictions']]
        actuals = [p['actual_probability'] for p in backtest_results['predictions']]

        # Optimize threshold
        optimization_results = backtesting_service.optimize_threshold(
            predictions=predictions,
            actuals=actuals,
            optimization_method=request.optimization_method,
            cost_false_alarm=request.cost_false_alarm,
            cost_missed_storm=request.cost_missed_storm,
            threshold_step=5
        )

        return {
            'metadata': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'duration_days': duration_days,
                'optimization_method': request.optimization_method,
                'model_version': request.model_version,
                'sample_interval_hours': request.sample_interval_hours,
                'total_predictions': len(predictions)
            },
            'optimization': optimization_results
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error optimizing threshold: {e}")
        raise HTTPException(status_code=500, detail=f"Threshold optimization failed: {str(e)}")


@router.get("/backtest/storm-events")
async def get_storm_events(
    start_date: str,
    end_date: str,
    threshold: float = 40.0,
    db: AsyncSession = Depends(get_db)
):
    """Get historical storm events in a date range."""
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        backtesting_service = BacktestingService()
        storms = await backtesting_service.get_storm_events(db, start, end, threshold)

        return {
            "storms": storms,
            "count": len(storms),
            "threshold": threshold
        }

    except Exception as e:
        logger.error(f"Error getting storm events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Impact Assessment endpoint
@router.get("/impact-assessment")
async def get_impact_assessment(
    latitude: float = 45.0
):
    """
    Get real-world impact assessment for current storm conditions.

    Translates ionospheric storm predictions into actionable impacts for:
    - GPS accuracy degradation
    - HF radio propagation
    - Satellite operations
    - Power grid (GIC risk)

    Parameters:
    - latitude: Geographic latitude for regional effects (default: 45.0, range: -90 to 90)
    """
    try:
        # Validate latitude
        if not (-90 <= latitude <= 90):
            raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")

        if data_service is None or data_service.latest_prediction is None:
            raise HTTPException(status_code=503, detail="Prediction data not available")

        prediction = data_service.latest_prediction
        latest_data = data_service.latest_data or {}

        # Extract current conditions
        probability_24h = prediction.get('storm_probability_24h', 0)
        probability_48h = prediction.get('storm_probability_48h', 0)
        kp_index = latest_data.get('kp_index', 3.0)
        tec_mean = latest_data.get('tec_statistics', {}).get('mean', 20.0)
        dst_index = latest_data.get('dst_index', 0)

        # Calculate impacts
        impact_service = ImpactAssessmentService()
        impacts = impact_service.assess_impacts(
            probability_24h=probability_24h,
            probability_48h=probability_48h,
            kp_index=kp_index,
            tec_mean=tec_mean,
            dst_index=dst_index,
            latitude=latitude
        )

        return impacts

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing impacts: {e}")
        raise HTTPException(status_code=500, detail=f"Impact assessment failed: {str(e)}")


# Regional Prediction endpoint
@router.get("/prediction/location")
async def get_regional_prediction(
    latitude: float,
    longitude: float
):
    """
    Get location-specific ionospheric storm prediction.

    Adjusts global predictions based on regional factors:
    - Latitude effects (high-latitude auroral zones more affected)
    - Regional TEC distribution
    - Magnetic latitude considerations

    Parameters:
    - latitude: Geographic latitude (-90 to 90)
    - longitude: Geographic longitude (-180 to 180)
    """
    try:
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")

        if data_service is None or data_service.latest_prediction is None:
            raise HTTPException(status_code=503, detail="Prediction data not available")

        # Get global prediction and TEC data
        global_prediction = data_service.latest_prediction
        tec_data = {
            'tec_statistics': data_service.latest_data.get('tec_statistics', {})
        } if data_service.latest_data else None

        # Calculate regional prediction
        regional_service = RegionalPredictionService()
        regional_prediction = regional_service.get_regional_prediction(
            latitude=latitude,
            longitude=longitude,
            global_prediction=global_prediction,
            tec_data=tec_data
        )

        return regional_prediction

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating regional prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Regional prediction failed: {str(e)}")


# Alert System Pydantic models
class CreateAlertRequest(BaseModel):
    user_email: str
    name: str
    alert_type: str  # 'threshold', 'regional', 'impact'
    threshold_probability: float = None
    threshold_horizon: str = None  # '24h', '48h'
    location_lat: float = None
    location_lon: float = None
    location_name: str = None


# Alert endpoints
@router.post("/alerts")
async def create_alert(request: CreateAlertRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new storm alert.

    Alert types:
    - threshold: Alert when probability exceeds threshold
    - regional: Alert for specific location (future enhancement)
    - impact: Alert based on impact severity (future enhancement)
    """
    try:
        alert_service = AlertService()
        alert = await alert_service.create_alert(
            db=db,
            user_email=request.user_email,
            name=request.name,
            alert_type=request.alert_type,
            threshold_probability=request.threshold_probability,
            threshold_horizon=request.threshold_horizon or '24h',
            location_lat=request.location_lat,
            location_lon=request.location_lon,
            location_name=request.location_name
        )

        return {
            "id": alert.id,
            "name": alert.name,
            "alert_type": alert.alert_type,
            "threshold_probability": alert.threshold_probability,
            "threshold_horizon": alert.threshold_horizon,
            "enabled": alert.enabled,
            "created_at": alert.created_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")


@router.get("/alerts")
async def get_alerts(user_email: str, db: AsyncSession = Depends(get_db)):
    """Get all alerts for a user."""
    try:
        alert_service = AlertService()
        alerts = await alert_service.get_user_alerts(db, user_email)

        return {
            "alerts": [
                {
                    "id": alert.id,
                    "name": alert.name,
                    "alert_type": alert.alert_type,
                    "threshold_probability": alert.threshold_probability,
                    "threshold_horizon": alert.threshold_horizon,
                    "location_name": alert.location_name,
                    "enabled": alert.enabled,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in alerts
            ],
            "count": len(alerts)
        }

    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")


@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int, user_email: str, db: AsyncSession = Depends(get_db)):
    """Delete an alert."""
    try:
        alert_service = AlertService()
        success = await alert_service.delete_alert(db, alert_id, user_email)

        if not success:
            raise HTTPException(status_code=404, detail="Alert not found or unauthorized")

        return {"status": "success", "message": "Alert deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")


@router.get("/alerts/check")
async def check_alerts_now(db: AsyncSession = Depends(get_db)):
    """
    Check all alerts against current prediction (for testing/demo).

    In production, this would be called by a background task.
    """
    try:
        if data_service is None or data_service.latest_prediction is None:
            raise HTTPException(status_code=503, detail="Prediction data not available")

        alert_service = AlertService()
        triggered = await alert_service.check_alerts(db, data_service.latest_prediction)

        return {
            "triggered_count": len(triggered),
            "triggered_alerts": triggered
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check alerts: {str(e)}")


@router.get("/alerts/history")
async def get_alert_history(user_email: str, limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Get alert trigger history for a user."""
    try:
        alert_service = AlertService()
        history = await alert_service.get_alert_history(db, user_email, limit)

        return {
            "history": [
                {
                    "alert_id": h.alert_id,
                    "triggered_at": h.triggered_at.isoformat(),
                    "probability_24h": h.probability_24h,
                    "probability_48h": h.probability_48h,
                    "risk_level_24h": h.risk_level_24h,
                    "notification_sent": h.notification_sent
                }
                for h in history
            ],
            "count": len(history)
        }

    except Exception as e:
        logger.error(f"Error fetching alert history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch alert history: {str(e)}")


# Climatology Exploration endpoints
@router.get("/climatology/explore")
async def explore_climatology(
    start_date: str = None,
    end_date: str = None,
    days: int = 365,
    kp_scenario: str = "current",  # 'current', 'quiet', 'moderate', 'storm', 'specific'
    kp_value: float = 3.0,
    hourly_resolution: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Explore climatology data for any date range, including future dates.

    Since climatology is based on day-of-year patterns, it can be projected
    indefinitely into the future. This endpoint is designed to help users
    understand climatological patterns in ionospheric TEC.

    Parameters:
    - start_date: ISO format start date (default: today)
    - end_date: ISO format end date (default: start_date + days)
    - days: Number of days to project (default: 365, max: 730 for 2 years)
    - kp_scenario: Geomagnetic activity scenario:
        * 'current' - Use current Kp index
        * 'quiet' - Use Kp=2 (quiet conditions)
        * 'moderate' - Use Kp=5 (moderate storm)
        * 'storm' - Use Kp=7 (strong storm)
        * 'specific' - Use kp_value parameter
    - kp_value: Specific Kp value when kp_scenario='specific' (0-9)
    - hourly_resolution: If true, return hourly data points (24x more data)

    Returns:
    - Climatology forecast data with timestamps and TEC values
    - Statistics and metadata about the climatological period
    """
    from app.models.ensemble_predictor import EnsembleStormPredictor

    try:
        # Parse or default dates
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            start_dt = datetime.utcnow()

        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            end_dt = start_dt + timedelta(days=days)

        # Validate date range
        if start_dt >= end_dt:
            raise HTTPException(status_code=400, detail="Start date must be before end date")

        duration_days = (end_dt - start_dt).days
        if duration_days > 730:
            raise HTTPException(
                status_code=400,
                detail="Maximum range is 730 days (2 years). Climatology repeats annually."
            )

        # Determine Kp index to use
        if kp_scenario == "current":
            # Use current Kp from data service
            if data_service and data_service.latest_data:
                kp = data_service.latest_data.get('kp_index', 3.0)
            else:
                kp = 3.0  # Default moderate value
        elif kp_scenario == "quiet":
            kp = 2.0
        elif kp_scenario == "moderate":
            kp = 5.0
        elif kp_scenario == "storm":
            kp = 7.0
        elif kp_scenario == "specific":
            kp = max(0.0, min(9.0, kp_value))  # Clamp to valid range
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid kp_scenario: {kp_scenario}"
            )

        # Initialize ensemble predictor and load climatology
        ensemble = EnsembleStormPredictor(
            model_path="models/v2/best_model.keras",
            climatology_weight=1.0,
            model_weight=0.0
        )

        if not ensemble.climatology_loaded:
            await ensemble.load_climatology()

        # Generate climatology data
        climatology_data = []

        if hourly_resolution:
            # Hourly resolution
            current_dt = start_dt
            while current_dt < end_dt:
                tec_value = ensemble.get_climatology_forecast(current_dt, kp)
                climatology_data.append({
                    "timestamp": current_dt.isoformat(),
                    "tec_mean": round(tec_value, 2),
                    "day_of_year": current_dt.timetuple().tm_yday,
                    "kp_index": kp
                })
                current_dt += timedelta(hours=1)
        else:
            # Daily resolution (noon each day)
            current_dt = start_dt.replace(hour=12, minute=0, second=0, microsecond=0)
            while current_dt < end_dt:
                tec_value = ensemble.get_climatology_forecast(current_dt, kp)
                climatology_data.append({
                    "timestamp": current_dt.isoformat(),
                    "tec_mean": round(tec_value, 2),
                    "day_of_year": current_dt.timetuple().tm_yday,
                    "kp_index": kp
                })
                current_dt += timedelta(days=1)

        # Calculate statistics
        tec_values = [d["tec_mean"] for d in climatology_data]
        stats = {
            "mean": round(np.mean(tec_values), 2),
            "std": round(np.std(tec_values), 2),
            "min": round(np.min(tec_values), 2),
            "max": round(np.max(tec_values), 2),
            "median": round(np.median(tec_values), 2)
        }

        return {
            "metadata": {
                "start_date": start_dt.isoformat(),
                "end_date": end_dt.isoformat(),
                "duration_days": duration_days,
                "kp_scenario": kp_scenario,
                "kp_value": kp,
                "hourly_resolution": hourly_resolution,
                "data_points": len(climatology_data),
                "description": "Climatological TEC forecast based on 2015-2022 historical patterns"
            },
            "statistics": stats,
            "data": climatology_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating climatology data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Climatology exploration failed: {str(e)}"
        )


@router.get("/climatology/heatmap")
async def get_climatology_heatmap(db: AsyncSession = Depends(get_db)):
    """
    Get climatology data formatted as a heatmap (day-of-year × Kp index).

    Returns the complete climatology table showing how TEC varies by:
    - Day of year (1-365, rows)
    - Kp index (0-9, columns)

    This provides a comprehensive view of seasonal and geomagnetic patterns.
    """
    from app.models.ensemble_predictor import EnsembleStormPredictor

    try:
        # Initialize and load climatology
        ensemble = EnsembleStormPredictor(
            model_path="models/v2/best_model.keras",
            climatology_weight=1.0,
            model_weight=0.0
        )

        if not ensemble.climatology_loaded:
            await ensemble.load_climatology()

        # Build heatmap data structure
        heatmap_data = []

        for doy in range(1, 366):  # Day of year 1-365
            row = {
                "day_of_year": doy,
                "date_example": datetime(2025, 1, 1) + timedelta(days=doy-1),
                "kp_values": {}
            }

            for kp_bin in range(10):  # Kp 0-9
                tec_value = ensemble.climatology_table.get((doy, kp_bin), 0)
                row["kp_values"][f"kp_{kp_bin}"] = round(tec_value, 2)

            heatmap_data.append(row)

        # Calculate statistics by Kp level
        kp_stats = {}
        for kp_bin in range(10):
            values = [ensemble.climatology_table.get((doy, kp_bin), 0) for doy in range(1, 366)]
            kp_stats[f"kp_{kp_bin}"] = {
                "mean": round(np.mean(values), 2),
                "std": round(np.std(values), 2),
                "min": round(np.min(values), 2),
                "max": round(np.max(values), 2)
            }

        # Calculate statistics by season
        seasons = {
            "winter": list(range(1, 80)) + list(range(356, 366)),  # Dec-Feb
            "spring": list(range(80, 172)),  # Mar-May
            "summer": list(range(172, 264)),  # Jun-Aug
            "autumn": list(range(264, 356))   # Sep-Nov
        }

        seasonal_stats = {}
        for season_name, days in seasons.items():
            values = []
            for doy in days:
                for kp_bin in range(10):
                    values.append(ensemble.climatology_table.get((doy, kp_bin), 0))

            seasonal_stats[season_name] = {
                "mean": round(np.mean(values), 2),
                "std": round(np.std(values), 2),
                "min": round(np.min(values), 2),
                "max": round(np.max(values), 2)
            }

        return {
            "metadata": {
                "total_bins": len(ensemble.climatology_table),
                "days": 365,
                "kp_levels": 10,
                "data_source": "Historical measurements 2015-2022",
                "description": "Complete climatology table showing TEC patterns by day-of-year and Kp index"
            },
            "heatmap": heatmap_data,
            "statistics": {
                "by_kp_level": kp_stats,
                "by_season": seasonal_stats
            }
        }

    except Exception as e:
        logger.error(f"Error generating climatology heatmap: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Climatology heatmap generation failed: {str(e)}"
        )


# Geographic Climatology endpoints
@router.get("/climatology/regions")
async def get_available_regions():
    """
    Get list of available geographic regions for climatology analysis.

    Returns region definitions including latitude ranges and descriptions.
    """
    regions = GeographicRegion.get_all_regions()

    return {
        "regions": [
            {
                "code": r['code'],
                "name": r['name'],
                "lat_range": r['lat_range'],
                "description": r['description']
            }
            for r in regions
        ],
        "total_regions": len(regions)
    }


@router.get("/climatology/geographic/explore")
async def explore_geographic_climatology(
    region: str = "global",  # equatorial, mid_latitude, auroral, polar, global
    days: int = 365,
    kp_scenario: str = "moderate",
    kp_value: float = 3.0,
    db: AsyncSession = Depends(get_db)
):
    """
    Explore climatology data for a specific geographic region.

    This endpoint provides region-specific TEC forecasts accounting for
    latitude-dependent ionospheric behavior.

    Parameters:
    - region: Geographic region code (equatorial, mid_latitude, auroral, polar, global)
    - days: Number of days to forecast (1-730)
    - kp_scenario: Kp scenario (quiet, moderate, storm, current, specific)
    - kp_value: Specific Kp value if scenario is 'specific'
    """
    global geographic_climatology_service

    if geographic_climatology_service is None:
        # Initialize if not already done
        geographic_climatology_service = GeographicClimatologyService()
        await geographic_climatology_service.build_climatology(db)

    # Validate region
    region_def = GeographicRegion.get_region_by_code(region)
    if not region_def:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid region code: {region}. Use /climatology/regions to see available regions."
        )

    # Validate days
    if not (1 <= days <= 730):
        raise HTTPException(status_code=400, detail="Days must be between 1 and 730")

    # Determine Kp value
    kp_scenarios = {
        "quiet": 2.0,
        "moderate": 3.0,
        "storm": 6.0,
        "current": data_service.latest_data.get('kp_index', 3.0) if data_service and data_service.latest_data else 3.0
    }

    if kp_scenario == "specific":
        kp = max(0, min(9, kp_value))
    else:
        kp = kp_scenarios.get(kp_scenario, 3.0)

    # Get forecast
    start_date = datetime.utcnow()
    forecast = geographic_climatology_service.get_multi_region_forecast(
        start_date,
        kp,
        days
    )

    # Extract data for requested region
    region_forecast = forecast.get(region, [])

    return {
        "region": {
            "code": region,
            "name": region_def['name'],
            "lat_range": region_def['lat_range'],
            "description": region_def['description']
        },
        "parameters": {
            "start_date": start_date.date().isoformat(),
            "days": len(region_forecast),
            "kp_scenario": kp_scenario,
            "kp_value": round(kp, 1)
        },
        "forecast": region_forecast,
        "statistics": {
            "mean_tec": round(np.mean([p['tec'] for p in region_forecast]), 2) if region_forecast else 0,
            "max_tec": round(max([p['tec'] for p in region_forecast]), 2) if region_forecast else 0,
            "min_tec": round(min([p['tec'] for p in region_forecast]), 2) if region_forecast else 0
        }
    }


@router.get("/climatology/geographic/compare")
async def compare_regions(
    target_date: str = None,
    kp_scenario: str = "moderate",
    kp_value: float = 3.0,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare TEC values across all geographic regions for a specific date.

    This endpoint allows users to see how TEC varies across different
    latitude bands under the same geomagnetic conditions.

    Parameters:
    - target_date: Date to compare (YYYY-MM-DD, default: today)
    - kp_scenario: Kp scenario (quiet, moderate, storm, specific)
    - kp_value: Specific Kp value if scenario is 'specific'
    """
    global geographic_climatology_service

    if geographic_climatology_service is None:
        geographic_climatology_service = GeographicClimatologyService()
        await geographic_climatology_service.build_climatology(db)

    # Parse target date
    if target_date:
        try:
            date_obj = datetime.fromisoformat(target_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        date_obj = datetime.utcnow()

    # Determine Kp value
    kp_scenarios = {
        "quiet": 2.0,
        "moderate": 3.0,
        "storm": 6.0,
        "current": data_service.latest_data.get('kp_index', 3.0) if data_service and data_service.latest_data else 3.0
    }

    if kp_scenario == "specific":
        kp = max(0, min(9, kp_value))
    else:
        kp = kp_scenarios.get(kp_scenario, 3.0)

    # Get comparison
    comparisons = geographic_climatology_service.compare_regions(date_obj, kp)

    return {
        "date": date_obj.date().isoformat(),
        "day_of_year": date_obj.timetuple().tm_yday,
        "kp_scenario": kp_scenario,
        "kp_value": round(kp, 1),
        "regions": comparisons,
        "insights": {
            "highest_tec_region": comparisons[0]['region'] if comparisons else None,
            "lowest_tec_region": comparisons[-1]['region'] if comparisons else None,
            "tec_range": round(comparisons[0]['tec'] - comparisons[-1]['tec'], 2) if len(comparisons) >= 2 else 0
        }
    }


# Historical Storm Gallery endpoints
@router.get("/storms/gallery")
async def get_storm_gallery():
    """
    Get curated gallery of major historical geomagnetic storms.

    Returns notable storm events from 2015-2025 with:
    - Storm metadata and severity
    - Real-world impacts
    - Scientific context
    - Links to external resources
    """
    import sys
    sys.path.append('/Users/tonygillett/code/ionospheric_prediction/backend')
    from storm_events import MAJOR_STORM_EVENTS

    try:
        return {
            "storms": MAJOR_STORM_EVENTS,
            "count": len(MAJOR_STORM_EVENTS),
            "date_range": {
                "start": "2015-01-01",
                "end": "2025-12-31"
            },
            "severity_levels": {
                "G1": "Minor",
                "G2": "Moderate",
                "G3": "Strong",
                "G4": "Severe",
                "G5": "Extreme"
            }
        }

    except Exception as e:
        logger.error(f"Error loading storm gallery: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Storm gallery failed: {str(e)}"
        )


# Recent Storm Performance endpoints (must be before /storms/{storm_id})
@router.get("/storms/recent")
async def get_recent_storms(
    days_back: int = 365,
    kp_threshold: float = 5.0,
    analyze_performance: bool = False,
    model_version: str = 'v2',
    db: AsyncSession = Depends(get_db)
):
    """
    Get catalog of recent storms (up to 1 year back) with optional model performance analysis.

    This endpoint detects storms based on Kp index and optionally evaluates how well
    the prediction model performed on each storm.

    Query Parameters:
    - days_back: How many days to look back (default 365, max 365)
    - kp_threshold: Kp index threshold for storm detection (default 5.0 = G1 minor)
    - analyze_performance: Run model performance analysis on each storm (slower, default false)
    - model_version: Model version to use for analysis ('v1' or 'v2', default 'v2')

    Returns:
    - List of detected storms with metadata (severity, duration, peak Kp, etc.)
    - If analyze_performance=true: includes model prediction accuracy for each storm
    - Aggregate statistics (severity distribution, strongest storm, etc.)

    Performance analysis includes:
    - Whether model detected the storm
    - How many hours in advance it was detected
    - Prediction accuracy (RMSE, MAE)
    - Detection rate during storm
    """
    try:
        # Limit to 365 days
        if days_back > 365:
            days_back = 365

        # Validate Kp threshold
        if kp_threshold < 0 or kp_threshold > 9:
            raise HTTPException(status_code=400, detail="kp_threshold must be between 0 and 9")

        logger.info(f"Getting recent storms: days_back={days_back}, kp_threshold={kp_threshold}, analyze={analyze_performance}")

        # Create service instance
        service = RecentStormPerformanceService(model_version=model_version)

        # Get storm catalog
        catalog = await service.get_recent_storm_catalog(
            db,
            days_back=days_back,
            kp_threshold=kp_threshold,
            analyze_performance=analyze_performance
        )

        return catalog

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recent storms: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent storms: {str(e)}"
        )


@router.get("/storms/recent/{storm_id}/performance")
async def get_storm_performance(
    storm_id: str,
    model_version: str = 'v2',
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed model performance analysis for a specific recent storm.

    This endpoint analyzes how well the model predicted a specific storm by:
    1. Running the model retrospectively with data available before the storm
    2. Comparing predictions to actual storm evolution
    3. Calculating performance metrics

    Path Parameters:
    - storm_id: Storm identifier (format: storm_YYYYMMDD_HHMM)

    Query Parameters:
    - model_version: Model version to use ('v1' or 'v2', default 'v2')

    Returns:
    - Storm metadata (start time, peak Kp, duration, severity)
    - Model performance metrics:
      - Detection: whether storm was detected and how early
      - Accuracy: RMSE and MAE during storm period
      - Detection rate: percentage of storm duration model predicted correctly
    - Detailed prediction time series (predicted vs actual)
    """
    try:
        logger.info(f"Analyzing performance for storm: {storm_id}")

        # Parse storm ID to extract timestamp
        # Format: storm_YYYYMMDD_HHMM
        if not storm_id.startswith('storm_'):
            raise HTTPException(status_code=400, detail="Invalid storm_id format")

        timestamp_str = storm_id.replace('storm_', '')
        try:
            storm_start = datetime.strptime(timestamp_str, '%Y%m%d_%H%M')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid storm_id timestamp format")

        # Look for this storm in recent data (search +/- 24 hours)
        search_start = storm_start - timedelta(hours=24)
        search_end = storm_start + timedelta(hours=72)  # storms can last up to 3 days

        # Create service and detect storms in this window
        service = RecentStormPerformanceService(model_version=model_version)
        storms = await service.detect_storms(
            db,
            start_date=search_start,
            end_date=search_end,
            kp_threshold=5.0,
            min_duration_hours=1
        )

        # Find the storm matching this ID
        matching_storm = None
        for storm in storms:
            if storm['storm_id'] == storm_id:
                matching_storm = storm
                break

        if not matching_storm:
            raise HTTPException(
                status_code=404,
                detail=f"Storm {storm_id} not found in database"
            )

        # Analyze performance for this storm
        analysis = await service.analyze_storm_performance(db, matching_storm)

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing storm performance: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze storm performance: {str(e)}"
        )


@router.get("/storms/{storm_id}")
async def get_storm_details(storm_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get detailed data for a specific historical storm event.

    Returns:
    - Storm metadata
    - Actual measurements during the storm period
    - Time series data (Kp, TEC, solar wind, etc.)
    - Peak values and statistics
    """
    import sys
    sys.path.append('/Users/tonygillett/code/ionospheric_prediction/backend')
    from storm_events import get_storm_by_id

    try:
        # Get storm metadata
        storm_info = get_storm_by_id(storm_id)
        if not storm_info:
            raise HTTPException(status_code=404, detail=f"Storm {storm_id} not found")

        # Parse dates
        start_date = datetime.fromisoformat(storm_info['date_start'])
        end_date = datetime.fromisoformat(storm_info['date_end']) + timedelta(days=1)

        # Query database for actual measurements during storm
        measurements = await HistoricalDataRepository.get_measurements_by_time_range(
            db, start_date, end_date
        )

        # Format time series data
        time_series = []
        for m in measurements:
            # Skip fill values
            if m.kp_index > 9 or (m.imf_bz and abs(m.imf_bz) > 900):
                continue

            time_series.append({
                "timestamp": m.timestamp.isoformat(),
                "kp_index": m.kp_index,
                "dst_index": m.dst_index,
                "tec_mean": m.tec_mean,
                "solar_wind_speed": m.solar_wind_speed,
                "solar_wind_density": m.solar_wind_density,
                "imf_bz": m.imf_bz,
                "f107_flux": m.f107_flux
            })

        # Calculate storm statistics
        if time_series:
            kp_values = [d['kp_index'] for d in time_series if d['kp_index'] is not None]
            tec_values = [d['tec_mean'] for d in time_series if d['tec_mean'] is not None]

            storm_stats = {
                "max_kp": max(kp_values) if kp_values else None,
                "avg_kp": round(np.mean(kp_values), 2) if kp_values else None,
                "max_tec": max(tec_values) if tec_values else None,
                "avg_tec": round(np.mean(tec_values), 2) if tec_values else None,
                "duration_hours": len(time_series)
            }
        else:
            storm_stats = {}

        return {
            "storm_info": storm_info,
            "measurements": time_series,
            "statistics": storm_stats,
            "data_availability": len(time_series) > 0
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching storm details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch storm details: {str(e)}"
        )
