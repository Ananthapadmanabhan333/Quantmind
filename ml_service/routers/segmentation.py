from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

router = APIRouter()


class UserSegmentRequest(BaseModel):
    user_id: str
    transaction_count: int
    avg_amount: float
    total_volume: float
    avg_frequency: float
    flagged_count: int = 0
    last_7d_volume: float = 0
    last_24h_volume: float = 0


class UserSegmentResponse(BaseModel):
    user_id: str
    cluster_id: int
    segment_name: str
    risk_level: str
    characteristics: Dict[str, any]


SEGMENT_NAMES = {
    0: "Premium",
    1: "Regular",
    2: "High Risk",
    3: "New User",
    4: "Dormant",
}


@router.post("/users", response_model=UserSegmentResponse)
async def segment_user(request: UserSegmentRequest):
    try:
        features = np.array(
            [
                np.log1p(request.transaction_count),
                np.log1p(request.avg_amount),
                np.log1p(request.total_volume),
                request.avg_frequency,
                request.flagged_count / max(request.transaction_count, 1),
                np.log1p(request.last_7d_volume),
            ]
        ).reshape(1, -1)

        if request.transaction_count < 5:
            cluster_id = 3
        elif request.flagged_count / max(request.transaction_count, 1) > 0.3:
            cluster_id = 2
        elif request.avg_amount > 500:
            cluster_id = 0
        else:
            cluster_id = 1

        segment_name = SEGMENT_NAMES.get(cluster_id, "Regular")

        risk_level = "LOW"
        if cluster_id == 2:
            risk_level = "HIGH"
        elif cluster_id == 0:
            risk_level = "MEDIUM"

        characteristics = {
            "avg_amount": round(request.avg_amount, 2),
            "transaction_count": request.transaction_count,
            "risk_indicator": request.flagged_count / max(request.transaction_count, 1),
        }

        return UserSegmentResponse(
            user_id=request.user_id,
            cluster_id=cluster_id,
            segment_name=segment_name,
            risk_level=risk_level,
            characteristics=characteristics,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segmentation error: {str(e)}")


@router.post("/batch")
async def batch_segment_users(users: List[UserSegmentRequest]):
    results = []
    for user in users:
        result = await segment_user(user)
        results.append(result)
    return results


@router.post("/refresh")
async def refresh_segments():
    try:
        return {
            "status": "refreshed",
            "segments": list(SEGMENT_NAMES.values()),
            "cluster_count": len(SEGMENT_NAMES),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh error: {str(e)}")


@router.get("/segments")
async def get_segments():
    return [
        {"id": id, "name": name, "description": f"User segment {name}"}
        for id, name in SEGMENT_NAMES.items()
    ]
