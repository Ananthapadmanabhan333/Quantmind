from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import numpy as np
import joblib
from pathlib import Path

router = APIRouter()
MODELS_DIR = Path(__file__).parent.parent / "ml_service" / "models"


class FraudPredictionRequest(BaseModel):
    amount: float
    transaction_type: str
    merchant_category: str
    hour: int
    day_of_week: int
    location: Optional[str] = "UNKNOWN"
    user_id: Optional[str] = None


class FraudPredictionResponse(BaseModel):
    fraud_probability: float
    is_fraud: bool
    confidence: float
    risk_factors: List[str]


def get_transaction_features(data: FraudPredictionRequest) -> np.ndarray:
    type_encoding = {
        "DEBIT": 0,
        "CREDIT": 1,
        "TRANSFER": 2,
        "WITHDRAWAL": 3,
        "DEPOSIT": 4,
    }

    hour_normalized = data.hour / 24.0
    day_normalized = data.day_of_week / 7.0

    amount_log = np.log1p(data.amount)
    amount_normalized = min(data.amount / 10000, 1.0)

    category_hash = hash(data.merchant_category) % 20 / 20.0

    features = [
        amount_log,
        amount_normalized,
        hour_normalized,
        day_normalized,
        type_encoding.get(data.transaction_type, 0) / 5.0,
        category_hash,
        1.0 if data.hour < 6 or data.hour > 22 else 0.0,
    ]

    return np.array(features).reshape(1, -1)


@router.post("/predict", response_model=FraudPredictionResponse)
async def predict_fraud(request: FraudPredictionRequest):
    try:
        features = get_transaction_features(request)

        probability = float(np.random.random() * 0.3)

        if request.amount > 5000:
            probability += 0.2
        if request.hour < 6 or request.hour > 23:
            probability += 0.1
        if request.transaction_type in ["WITHDRAWAL", "TRANSFER"]:
            probability += 0.15

        probability = min(probability, 0.99)

        risk_factors = []
        if request.amount > 5000:
            risk_factors.append("High transaction amount")
        if request.hour < 6 or request.hour > 23:
            risk_factors.append("Unusual transaction time")
        if request.transaction_type in ["WITHDRAWAL", "TRANSFER"]:
            risk_factors.append("High-risk transaction type")

        return FraudPredictionResponse(
            fraud_probability=round(probability, 4),
            is_fraud=probability > 0.7,
            confidence=round(1 - abs(probability - 0.5) * 2, 2),
            risk_factors=risk_factors,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.post("/train")
async def train_fraud_model():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    import pandas as pd

    try:
        np.random.seed(42)
        n_samples = 10000

        data = pd.DataFrame(
            {
                "amount": np.random.exponential(200, n_samples),
                "hour": np.random.randint(0, 24, n_samples),
                "day_of_week": np.random.randint(0, 7, n_samples),
                "transaction_type": np.random.choice(
                    ["DEBIT", "CREDIT", "TRANSFER", "WITHDRAWAL", "DEPOSIT"], n_samples
                ),
                "is_fraud": (np.random.random(n_samples) < 0.05).astype(int),
            }
        )

        data.loc[data["amount"] > 1000, "is_fraud"] = 1
        data.loc[(data["hour"] < 6) | (data["hour"] > 23), "is_fraud"] = 1

        features = data[["amount", "hour", "day_of_week"]].values
        labels = data["is_fraud"].values

        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42
        )

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        accuracy = model.score(X_test, y_test)

        model_path = MODELS_DIR / "fraud_model.pkl"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)

        return {
            "status": "trained",
            "accuracy": round(accuracy, 4),
            "samples": n_samples,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")
