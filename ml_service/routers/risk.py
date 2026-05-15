from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import numpy as np

router = APIRouter()


class RiskScoreRequest(BaseModel):
    user_id: str
    transaction_count: int
    avg_amount: float
    total_volume: float
    flagged_count: int = 0
    last_24h_volume: float = 0
    last_7d_volume: float = 0
    avg_frequency: float = 0
    fraud_probability: float = 0


class RiskScoreResponse(BaseModel):
    risk_score: float
    risk_level: str
    factors: Dict[str, float]
    recommendations: list


@router.post("/score", response_model=RiskScoreResponse)
async def calculate_risk_score(request: RiskScoreRequest):
    try:
        base_score = 30.0

        fraud_weight = request.fraud_probability * 40

        if request.transaction_count > 0:
            fraud_rate = request.flagged_count / request.transaction_count
            fraud_rate_weight = min(fraud_rate * 30, 30)
        else:
            fraud_rate_weight = 0

        volume_weight = 0
        if request.last_24h_volume > 5000:
            volume_weight += 15
        elif request.last_24h_volume > 2000:
            volume_weight += 10
        elif request.last_24h_volume > 0:
            volume_weight += 5

        frequency_weight = 0
        if request.avg_frequency > 5:
            frequency_weight += 10
        elif request.avg_frequency > 2:
            frequency_weight += 5

        total_score = (
            base_score
            + fraud_weight
            + fraud_rate_weight
            + volume_weight
            + frequency_weight
        )
        total_score = max(0, min(100, total_score))

        if total_score >= 80:
            risk_level = "CRITICAL"
        elif total_score >= 60:
            risk_level = "HIGH"
        elif total_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        factors = {
            "fraud_probability": round(request.fraud_probability, 3),
            "fraud_rate": round(
                request.flagged_count / max(request.transaction_count, 1), 3
            ),
            "volume_risk": round(volume_weight / 30, 2),
            "frequency_risk": round(frequency_weight / 10, 2),
        }

        recommendations = []
        if risk_level in ["HIGH", "CRITICAL"]:
            recommendations.append("Enable enhanced monitoring")
        if request.last_24h_volume > 5000:
            recommendations.append("Review high-volume activity")
        if request.avg_frequency > 5:
            recommendations.append("Flag rapid transaction patterns")
        if request.fraud_probability > 0.3:
            recommendations.append("Consider transaction limits")

        return RiskScoreResponse(
            risk_score=round(total_score, 1),
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk scoring error: {str(e)}")


@router.post("/batch")
async def batch_calculate_risk(requests: list[RiskScoreRequest]):
    results = []
    for req in requests:
        result = await calculate_risk_score(req)
        results.append(result)
    return results
