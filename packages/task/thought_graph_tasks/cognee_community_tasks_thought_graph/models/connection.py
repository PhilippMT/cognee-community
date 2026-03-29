"""Connection model for representing relationships between thoughts."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Connection(BaseModel):
    """
    Represents a connection/relationship between two thoughts.

    Attributes:
        source_id: ID of the source thought node
        target_id: ID of the target thought node
        relationship_type: Type of relationship (e.g., 'relates_to', 'inspired_by', 'contradicts')
        strength: Connection strength (0.0 to 1.0), can be learned or user-defined
        created_at: When this connection was discovered/created
        discovery_method: How this connection was discovered (e.g., 'user_linked', 'llm_inferred', 'semantic_similarity')
        explanation: Optional explanation of why these thoughts are connected
        bidirectional: Whether this connection works both ways
        surprise_score: How unexpected/novel this connection is (computed)
    """

    source_id: UUID = Field(description="ID of the source thought node")
    target_id: UUID = Field(description="ID of the target thought node")
    relationship_type: str = Field(
        default="relates_to",
        description="Type of relationship between thoughts"
    )
    strength: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Connection strength (0.0 to 1.0)"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When connection was discovered/created"
    )
    discovery_method: str = Field(
        default="unknown",
        description="How this connection was discovered"
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Explanation of why these thoughts are connected"
    )
    bidirectional: bool = Field(
        default=True,
        description="Whether connection works both ways"
    )
    surprise_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="How unexpected/novel this connection is"
    )

    # Metadata for path-based connections
    path_length: Optional[int] = Field(
        default=None,
        description="Length of shortest path (for transitive connections)"
    )
    intermediate_nodes: Optional[list[UUID]] = Field(
        default=None,
        description="IDs of intermediate nodes in the connection path"
    )

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }

    def __repr__(self) -> str:
        """String representation of the connection."""
        return f"Connection({self.source_id} --[{self.relationship_type}]--> {self.target_id}, strength={self.strength:.2f})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert connection to dictionary."""
        return {
            "source_id": str(self.source_id),
            "target_id": str(self.target_id),
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "created_at": self.created_at.isoformat(),
            "discovery_method": self.discovery_method,
            "explanation": self.explanation,
            "bidirectional": self.bidirectional,
            "surprise_score": self.surprise_score,
            "path_length": self.path_length,
            "intermediate_nodes": [str(nid) for nid in self.intermediate_nodes] if self.intermediate_nodes else None,
        }
