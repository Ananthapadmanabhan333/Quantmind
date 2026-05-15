from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import numpy as np

router = APIRouter()


class AnomalyDetectionRequest(BaseModel):
    amount: float
    transaction_type: str
    merchant_category: str
    hour: int
    day_of_week: int
    user_avg_amount: Optional[float] = 0
    user_avg_frequency: Optional[float] = 0
    location: Optional[str] = "UNKNOWN"


class AnomalyDetectionResponse(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    anomaly_type: Optional[str] = None
    details: Dict[str, float]


@router.post("/detect", response_model=AnomalyDetectionResponse)
async def detect_anomaly(request: AnomalyDetectionRequest):
    try:
        score = 0.0
        anomaly_type = None

        if request.user_avg_amount > 0:
            amount_ratio = request.amount / request.user_avg_amount
            if amount_ratio > 5:
                score += 0.4
                anomaly_type = "AMOUNT_SPIKE"
            elif amount_ratio > 3:
                score += 0.2

        if request.hour < 6 or request.hour > 23:
            score += 0.2
            if not anomaly_type:
                anomaly_type = "UNUSUAL_HOUR"

        if request.transaction_type in ["WITHDRAWAL", "TRANSFER"]:
            score += 0.15
            if not anomaly_type:
                anomaly_type = "HIGH_RISK_TYPE"

        day_of_week = request.day_of_week
        if day_of_week in [5, 6]:
            score += 0.1

        score = min(score, 1.0)

        return AnomalyDetectionResponse(
            is_anomaly=score > 0.5,
            anomaly_score=round(score, 4),
            anomaly_type=anomaly_type,
            details={
                "amount_ratio": request.amount / max(request.user_avg_amount, 1),
                "hour_score": 1.0 if request.hour < 6 or request.hour > 23 else 0.0,
                "type_risk": 1.0
                if request.transaction_type in ["WITHDRAWAL", "TRANSFER"]
                else 0.0,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Anomaly detection error: {str(e)}"
        )


@router.post("/batch")
async def batch_anomaly_detection(transactions: List[AnomalyDetectionRequest]):
    results = []
    for tx in transactions:
        result = await detect_anomaly(tx)
        results.append(result)
    return results
