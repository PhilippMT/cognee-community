"""
Request and Response DTOs for the Thought Graph API.

All Pydantic models used for API input validation and response serialization.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# === Request DTOs ===


class AddThoughtRequest(BaseModel):
    """Request body for adding a single thought."""

    content: str = Field(..., description="The thought content text")
    title: Optional[str] = Field(default=None, description="Optional short title")
    tags: Optional[List[str]] = Field(default=None, description="Tags for categorization")
    context: Optional[str] = Field(default=None, description="Context about when/why this thought emerged")
    energy_level: Optional[int] = Field(default=None, ge=1, le=10, description="Energy level when captured (1-10)")
    related_projects: Optional[List[str]] = Field(default=None, description="Related project names")
    importance_score: Optional[int] = Field(default=None, ge=1, le=10, description="Importance rating (1-10)")
    auto_connect: bool = Field(default=True, description="Auto-discover connections")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Min similarity for auto-connections")


class BatchAddThoughtsRequest(BaseModel):
    """Request body for adding multiple thoughts."""

    thoughts: List[AddThoughtRequest]


class DiscoverConnectionsRequest(BaseModel):
    """Request body for discovering connections."""

    thought_id: str = Field(..., description="ID of the thought")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    max_connections: int = Field(default=10, ge=1)


class EnrichGraphRequest(BaseModel):
    """Request body for graph enrichment."""

    compute_pagerank: bool = Field(default=True)
    compute_centrality: bool = Field(default=True)
    detect_communities: bool = Field(default=True)
    find_transitive: bool = Field(default=True)
    auto_add_transitive_links: bool = Field(default=False)
    transitive_strength_threshold: float = Field(default=0.3, ge=0.0, le=1.0)


class WebEnrichmentRequest(BaseModel):
    """Request body for web enrichment of a single thought."""

    thought_id: str = Field(..., description="ID of the thought to enrich")
    max_results: int = Field(default=5, ge=1, le=20)
    search_depth: str = Field(default="basic", description="'basic' or 'advanced'")


class BatchWebEnrichmentRequest(BaseModel):
    """Request body for batch web enrichment."""

    thought_ids: List[str]
    max_results_per_thought: int = Field(default=3, ge=1, le=10)
    search_depth: str = Field(default="basic")


class ProjectMatchingRequest(BaseModel):
    """Request body for project matching."""

    project_patterns: Optional[Dict[str, List[str]]] = Field(
        default=None, description="{'project_name': ['keyword1', 'keyword2']}"
    )
    auto_detect: bool = Field(default=True, description="Auto-detect repo URLs in content")


class EdgeDecayRequest(BaseModel):
    """Request body for edge weight decay."""

    decay_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    min_weight: float = Field(default=0.15, ge=0.0, le=1.0)
    time_based: bool = Field(default=True)
    days_threshold: int = Field(default=30, ge=1)


class ReinforceEdgeRequest(BaseModel):
    """Request body for reinforcing an edge."""

    source_id: str
    target_id: str
    reinforcement_amount: float = Field(default=0.1, ge=0.0, le=1.0)


class MemifyRequest(BaseModel):
    """Request body for the integrated memify operation."""

    thought_ids: Optional[List[str]] = Field(default=None, description="Specific thought IDs (None = all)")
    enable_web_enrichment: bool = Field(default=False)
    enable_project_matching: bool = Field(default=True)
    enable_edge_decay: bool = Field(default=True)
    enable_potential_connections: bool = Field(default=True)
    web_search_depth: str = Field(default="basic")
    max_web_results: int = Field(default=3)
    decay_rate: float = Field(default=0.1)
    min_edge_weight: float = Field(default=0.1)
    project_patterns: Optional[Dict[str, List[str]]] = Field(default=None)


# === Response DTOs ===


class ThoughtResponse(BaseModel):
    """Response for a thought node."""

    id: str
    content: str
    title: Optional[str] = None
    tags: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    energy_level: Optional[int] = None
    importance_score: Optional[int] = None
    related_projects: List[str] = []
    connection_count: int = 0
    centrality_score: Optional[float] = None
    pagerank_score: Optional[float] = None
    community_id: Optional[str] = None


class ConnectionResponse(BaseModel):
    """Response for a discovered connection."""

    source_id: str
    target_id: str
    relationship_type: str
    strength: float
    discovery_method: str
    explanation: Optional[str] = None


class SurpriseConnectionResponse(BaseModel):
    """Response for a surprise connection."""

    source_id: str
    target_id: str
    overall_score: float
    semantic_distance: Optional[float] = None
    temporal_distance: Optional[float] = None
    structural_distance: Optional[float] = None
    domain_distance: Optional[float] = None
    explanation: Optional[str] = None
    confidence: float = 0.5
