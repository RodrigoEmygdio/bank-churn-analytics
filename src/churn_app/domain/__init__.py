"""Infrastructure-independent domain contracts for churn prediction."""

from churn_app.domain.customer import CustomerInput
from churn_app.domain.interpretation import InterpretationResult
from churn_app.domain.prediction import (
    ModelIdentity,
    ModelPrediction,
    ModelRole,
    ModelType,
    PredictionResult,
)
from churn_app.domain.presentation import ModelPresentationResult, PresentationResult
from churn_app.domain.recommendation import (
    RecommendationPriority,
    RecommendationResult,
)
from churn_app.domain.risk_level import RiskLevel

__all__ = [
    "CustomerInput",
    "InterpretationResult",
    "ModelIdentity",
    "ModelPrediction",
    "ModelPresentationResult",
    "ModelRole",
    "ModelType",
    "PredictionResult",
    "PresentationResult",
    "RecommendationPriority",
    "RecommendationResult",
    "RiskLevel",
]
