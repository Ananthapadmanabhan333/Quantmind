from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent / "models"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading ML models...")
    app.state.fraud_model = None
    app.state.anomaly_model = None
    app.state.segment_model = None

    fraud_model_path = MODELS_DIR / "fraud_model.pkl"
    anomaly_model_path = MODELS_DIR / "anomaly_model.pkl"

    if fraud_model_path.exists():
        try:
            app.state.fraud_model = joblib.load(fraud_model_path)
            logger.info("Fraud model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load fraud model: {e}")

    if anomaly_model_path.exists():
        try:
            app.state.anomaly_model = joblib.load(anomaly_model_path)
            logger.info("Anomaly model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load anomaly model: {e}")

    logger.info("ML Service started")
    yield

    logger.info("ML Service shutting down")


app = FastAPI(
    title="QuantMind ML Service",
    description="Machine Learning microservice for fraud detection, anomaly detection, and user segmentation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import fraud, anomaly, segmentation, risk

app.include_router(fraud.router, prefix="/ml/fraud", tags=["Fraud Detection"])
app.include_router(anomaly.router, prefix="/ml/anomaly", tags=["Anomaly Detection"])
app.include_router(
    segmentation.router, prefix="/ml/segment", tags=["User Segmentation"]
)
app.include_router(risk.router, prefix="/ml/risk", tags=["Risk Scoring"])


@app.get("/")
async def root():
    return {"service": "QuantMind ML Service", "status": "running"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "fraud_model_loaded": app.state.fraud_model is not None,
        "anomaly_model_loaded": app.state.anomaly_model is not None,
    }


@app.get("/ml/models/status")
async def model_status():
    return {
        "fraud_model": {"loaded": app.state.fraud_model is not None},
        "anomaly_model": {"loaded": app.state.anomaly_model is not None},
        "segment_model": {"loaded": app.state.segment_model is not None},
    }
