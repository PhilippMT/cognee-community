"""Get community information for thoughts."""

from typing import Any, Dict

from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.shared.logging_utils import get_logger

from cognee_community_tasks_thought_graph.algorithms.community_detection import (
    detect_communities,
    get_community_summary,
)

logger = get_logger(__name__)


async def get_thought_communities(
    algorithm: str = "greedy",
    include_summary: bool = True
) -> Dict[str, Any]:
    """
    Get community/cluster information for all thoughts.

    Organizes thoughts into thematic clusters based on their connectivity patterns.

    Args:
        algorithm: Community detection algorithm ("greedy", "label_propagation")
        include_summary: Whether to include summary stats for each community

    Returns:
        Dictionary containing:
        - communities: Map of thought IDs to community IDs
        - summaries: Community summary information (if included)
        - total_communities: Total number of communities detected
    """
    logger.info(f"Getting thought communities using {algorithm} algorithm")

    try:
        graph_engine = await get_graph_engine()

        # Get graph data
        nodes, edges = await graph_engine.get_graph_data()

        if not nodes:
            logger.info("No thoughts in graph")
            return {
                "communities": {},
                "summaries": {},
                "total_communities": 0
            }

        # Detect communities
        communities = await detect_communities(nodes, edges, algorithm=algorithm)

        result = {
            "communities": {str(k): v for k, v in communities.items()},
            "total_communities": len(set(communities.values()))
        }

        # Get summaries if requested
        if include_summary:
            summaries = await get_community_summary(nodes, communities)
            result["summaries"] = summaries
        else:
            result["summaries"] = {}

        logger.info(f"Found {result['total_communities']} communities")

        return result

    except Exception as e:
        logger.error(f"Error getting thought communities: {e}")
        return {
            "communities": {},
            "summaries": {},
            "total_communities": 0
        }
