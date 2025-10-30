"""
Main application entry point for Ionospheric Storm Prediction System
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router, init_data_service, broadcast_updates
from app.db.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Ionospheric Storm Prediction System...")

    # Initialize database
    logger.info("Initializing database...")
    await init_db()

    # Initialize data service
    data_service = init_data_service()
    await data_service.initialize()

    # Collect initial data
    logger.info("Collecting initial data...")
    await data_service.collect_all_data()
    await data_service.update_prediction()

    # Start background tasks
    logger.info("Starting background update tasks...")
    update_task = asyncio.create_task(
        data_service.start_periodic_updates(
            data_interval=settings.DATA_UPDATE_INTERVAL,
            prediction_interval=settings.PREDICTION_UPDATE_INTERVAL
        )
    )
    broadcast_task = asyncio.create_task(broadcast_updates())

    logger.info("System fully operational!")

    yield

    # Shutdown
    logger.info("Shutting down...")
    update_task.cancel()
    broadcast_task.cancel()
    await data_service.shutdown()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "api_docs": f"{settings.API_PREFIX}/docs"
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
