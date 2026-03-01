"""SurpriseScore model for quantifying unexpected connections."""

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SurpriseScore(BaseModel):
    """
    Represents a surprise/serendipity score for a connection or thought cluster.

    This quantifies how unexpected or novel a connection is based on various factors:
    - Semantic distance (how different the concepts are)
    - Temporal distance (how far apart the thoughts were created)
    - Structural distance (graph distance before connection was made)
    - Domain distance (how different the topics/tags are)

    Attributes:
        source_id: ID of the source thought
        target_id: ID of the target thought
        overall_score: Overall surprise score (0.0 to 1.0), higher = more surprising
        semantic_distance: Distance based on content similarity (0.0 to 1.0)
        temporal_distance: Distance based on time separation (0.0 to 1.0)
        structural_distance: Distance in graph before connection (normalized)
        domain_distance: Distance based on topic/tag differences (0.0 to 1.0)
        explanation: Human-readable explanation of why this is surprising
        confidence: Confidence in this surprise score (0.0 to 1.0)
    """

    source_id: UUID = Field(description="ID of the source thought")
    target_id: UUID = Field(description="ID of the target thought")

    overall_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall surprise score (0.0 to 1.0)"
    )

    semantic_distance: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Semantic content distance"
    )

    temporal_distance: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Temporal distance (time separation)"
    )

    structural_distance: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Normalized graph structural distance"
    )

    domain_distance: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Topic/domain distance"
    )

    explanation: Optional[str] = Field(
        default=None,
        description="Human-readable explanation of surprise"
    )

    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence in surprise score"
    )

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str
        }

    def __repr__(self) -> str:
        """String representation of the surprise score."""
        return f"SurpriseScore({self.source_id} <-> {self.target_id}, score={self.overall_score:.2f})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert surprise score to dictionary."""
        return {
            "source_id": str(self.source_id),
            "target_id": str(self.target_id),
            "overall_score": self.overall_score,
            "semantic_distance": self.semantic_distance,
            "temporal_distance": self.temporal_distance,
            "structural_distance": self.structural_distance,
            "domain_distance": self.domain_distance,
            "explanation": self.explanation,
            "confidence": self.confidence,
        }
