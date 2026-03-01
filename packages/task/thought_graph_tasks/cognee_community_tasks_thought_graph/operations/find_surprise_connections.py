"""Find surprise connections - unexpected or serendipitous relationships between thoughts."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.infrastructure.databases.vector import get_vector_engine
from cognee.shared.logging_utils import get_logger

from cognee_community_tasks_thought_graph.algorithms.transitive_connections import (
    find_transitive_connections,
)
from cognee_community_tasks_thought_graph.models.surprise_score import SurpriseScore

logger = get_logger(__name__)


async def find_surprise_connections(
    min_surprise_score: float = 0.5,
    max_results: int = 20,
    include_explanation: bool = True
) -> List[SurpriseScore]:
    """
    Find surprising or unexpected connections in the thought graph.

    Surprise connections are relationships that aren't obvious but reveal
    interesting insights when discovered. These are particularly valuable
    for ADHD brains as they highlight the non-linear, associative thinking patterns.

    Factors that make a connection surprising:
    - Semantic distance: Thoughts with very different content/topics
    - Temporal distance: Thoughts captured far apart in time
    - Structural distance: Thoughts that are far apart in the graph
    - Domain distance: Thoughts with different tags/categories

    Args:
        min_surprise_score: Minimum surprise score to return (0.0-1.0)
        max_results: Maximum number of surprise connections to return
        include_explanation: Whether to generate human-readable explanations

    Returns:
        List of SurpriseScore objects, sorted by overall_score descending

    Example:
        >>> surprises = await find_surprise_connections(min_surprise_score=0.7)
        >>> for surprise in surprises:
        >>>     print(f"Surprising connection: {surprise.explanation}")
        >>>     print(f"  Score: {surprise.overall_score:.2f}")
    """
    logger.info(f"Finding surprise connections (min_score={min_surprise_score})")

    try:
        graph_engine = await get_graph_engine()
        vector_engine = get_vector_engine()

        # Get all nodes and edges
        nodes, edges = await graph_engine.get_graph_data()

        if len(nodes) < 2:
            logger.info("Not enough nodes to find surprise connections")
            return []

        # Find transitive connections (indirect relationships)
        transitive = await find_transitive_connections(nodes, edges, max_hops=3)

        surprise_scores = []

        for source_id, target_id, hop_count, _path in transitive:
            # Get node data
            source_data = await graph_engine.get_node(str(source_id))
            target_data = await graph_engine.get_node(str(target_id))

            if not source_data or not target_data:
                continue

            # Calculate surprise components

            # 1. Semantic distance
            semantic_distance = await _calculate_semantic_distance(
                source_data.get("content", ""),
                target_data.get("content", ""),
                vector_engine
            )

            # 2. Temporal distance (normalized)
            temporal_distance = _calculate_temporal_distance(
                source_data.get("created_at"),
                target_data.get("created_at")
            )

            # 3. Structural distance (based on hop count)
            structural_distance = min(hop_count / 5.0, 1.0)  # Normalize to 0-1

            # 4. Domain distance (tag dissimilarity)
            domain_distance = _calculate_domain_distance(
                source_data.get("tags", []),
                target_data.get("tags", [])
            )

            # Calculate overall surprise score
            # Higher weight on semantic and domain distance (content-based surprise)
            overall_score = (
                0.4 * semantic_distance +
                0.2 * temporal_distance +
                0.2 * structural_distance +
                0.2 * domain_distance
            )

            if overall_score >= min_surprise_score:
                explanation = None
                if include_explanation:
                    explanation = _generate_surprise_explanation(
                        source_data,
                        target_data,
                        semantic_distance,
                        temporal_distance,
                        structural_distance,
                        domain_distance,
                        hop_count
                    )

                surprise = SurpriseScore(
                    source_id=source_id,
                    target_id=target_id,
                    overall_score=overall_score,
                    semantic_distance=semantic_distance,
                    temporal_distance=temporal_distance,
                    structural_distance=structural_distance,
                    domain_distance=domain_distance,
                    explanation=explanation,
                    confidence=0.7  # Base confidence
                )

                surprise_scores.append(surprise)

        # Sort by overall score descending
        surprise_scores.sort(key=lambda s: s.overall_score, reverse=True)

        result = surprise_scores[:max_results]

        logger.info(f"Found {len(result)} surprise connections")

        return result

    except Exception as e:
        logger.error(f"Error finding surprise connections: {e}")
        return []


async def _calculate_semantic_distance(
    content1: str,
    content2: str,
    vector_engine
) -> float:
    """Calculate semantic distance between two pieces of content."""
    try:
        # Use vector similarity (0 = identical, 1 = completely different)
        # This is a simplified implementation - in practice, you'd get embeddings and calculate distance

        # For now, use simple heuristic based on word overlap
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 or not words2:
            return 1.0

        overlap = len(words1 & words2)
        union = len(words1 | words2)

        similarity = overlap / union if union > 0 else 0.0
        distance = 1.0 - similarity

        return distance

    except Exception as e:
        logger.warning(f"Error calculating semantic distance: {e}")
        return 0.5  # Default mid-range


def _calculate_temporal_distance(created1: Optional[datetime], created2: Optional[datetime]) -> float:
    """Calculate normalized temporal distance between two timestamps."""
    if not created1 or not created2:
        return 0.0

    try:
        # Convert to datetime if string
        if isinstance(created1, str):
            created1 = datetime.fromisoformat(created1.replace('Z', '+00:00'))
        if isinstance(created2, str):
            created2 = datetime.fromisoformat(created2.replace('Z', '+00:00'))

        # Calculate days apart
        delta = abs((created1 - created2).total_seconds() / 86400)  # Days

        # Normalize: 0 days = 0, 30+ days = 1.0
        normalized = min(delta / 30.0, 1.0)

        return normalized

    except Exception as e:
        logger.warning(f"Error calculating temporal distance: {e}")
        return 0.0


def _calculate_domain_distance(tags1: List[str], tags2: List[str]) -> float:
    """Calculate domain distance based on tag dissimilarity."""
    if not tags1 or not tags2:
        return 1.0 if (tags1 or tags2) else 0.0

    set1 = set(tags1)
    set2 = set(tags2)

    overlap = len(set1 & set2)
    union = len(set1 | set2)

    similarity = overlap / union if union > 0 else 0.0
    distance = 1.0 - similarity

    return distance


def _generate_surprise_explanation(
    source_data: Dict[str, Any],
    target_data: Dict[str, Any],
    semantic_distance: float,
    temporal_distance: float,
    structural_distance: float,
    domain_distance: float,
    hop_count: int
) -> str:
    """Generate human-readable explanation of why this connection is surprising."""
    reasons = []

    if semantic_distance > 0.6:
        reasons.append("very different topics")

    if temporal_distance > 0.7:
        reasons.append("captured far apart in time")

    if structural_distance > 0.6:
        reasons.append(f"separated by {hop_count} degrees in the graph")

    if domain_distance > 0.8:
        reasons.append("completely different categories")

    if not reasons:
        reasons.append("indirectly connected")

    source_title = source_data.get("title") or source_data.get("content", "")[:50]
    target_title = target_data.get("title") or target_data.get("content", "")[:50]

    explanation = (
        f"Unexpected connection between '{source_title}' and '{target_title}' - "
        f"surprising because they have {' and '.join(reasons)}."
    )

    return explanation
