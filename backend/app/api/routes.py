"""
API Routes for the Ionospheric Storm Prediction System
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import List
import asyncio
import json
import logging
from datetime import datetime, timedelta

from app.services.data_service import DataService
from app.services.backtesting_service import BacktestingService
from app.db.database import get_db
from app.db.repository import HistoricalDataRepository
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Global data service instance
data_service: DataService = None

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
async def get_prediction():
    """Get the latest storm prediction"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service not initialized")

    if data_service.latest_prediction is None:
        raise HTTPException(status_code=404, detail="No prediction available yet")

    return data_service.latest_prediction


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
