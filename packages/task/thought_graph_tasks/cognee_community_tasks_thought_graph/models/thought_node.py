"""ThoughtNode model for representing individual thoughts/ideas in the graph."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from cognee.infrastructure.engine import DataPoint
from pydantic import Field


class ThoughtNode(DataPoint):
    """
    Represents a thought or idea node in the thought graph.

    Optimized for ADHD brainfog management with quick capture and rich metadata.

    Attributes:
        content: The actual thought/idea content (text)
        title: Optional short title for the thought
        tags: List of tags for categorization
        created_at: When this thought was captured
        updated_at: When this thought was last modified
        context: Optional context about when/why this thought emerged
        energy_level: Energy level when thought was captured (for ADHD patterns)
        related_projects: Projects this thought might relate to
        importance_score: User-defined importance (1-10)
        connection_count: Number of connections this thought has (computed)
        centrality_score: Graph centrality score (computed)
        community_id: Community/cluster this thought belongs to (computed)
    """

    content: str = Field(description="The main thought or idea content")
    title: Optional[str] = Field(default=None, description="Optional short title")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when thought was captured"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of last update"
    )

    metadata: Optional[Dict[str, Any]] = {"index_fields": ["content"]}
    context: Optional[str] = Field(
        default=None,
        description="Context about when/why this thought emerged"
    )
    energy_level: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Energy level when thought was captured (1-10)"
    )
    related_projects: List[str] = Field(
        default_factory=list,
        description="Project names this thought might relate to"
    )
    importance_score: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="User-defined importance score (1-10)"
    )

    # Computed graph metrics (set by enrichment algorithms)
    connection_count: int = Field(default=0, description="Number of connections")
    centrality_score: Optional[float] = Field(
        default=None,
        description="Graph centrality score (computed)"
    )
    pagerank_score: Optional[float] = Field(
        default=None,
        description="PageRank score (computed)"
    )
    community_id: Optional[str] = Field(
        default=None,
        description="Community/cluster ID (computed)"
    )

    def __repr__(self) -> str:
        """String representation of the thought node."""
        title_part = f"'{self.title}'" if self.title else f"{self.content[:50]}..."
        return f"ThoughtNode({title_part}, tags={self.tags})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert thought node to dictionary."""
        return {
            "id": str(self.id),
            "content": self.content,
            "title": self.title,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "context": self.context,
            "energy_level": self.energy_level,
            "related_projects": self.related_projects,
            "importance_score": self.importance_score,
            "connection_count": self.connection_count,
            "centrality_score": self.centrality_score,
            "pagerank_score": self.pagerank_score,
            "community_id": self.community_id,
        }
