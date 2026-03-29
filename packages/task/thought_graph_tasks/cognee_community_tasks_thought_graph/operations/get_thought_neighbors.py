"""Get neighboring thoughts in the graph."""

from typing import Any, Dict
from uuid import UUID

from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.shared.logging_utils import get_logger

logger = get_logger(__name__)


async def get_thought_neighbors(
    thought_id: UUID,
    max_depth: int = 1,
    include_relationship_info: bool = True
) -> Dict[str, Any]:
    """
    Get neighboring thoughts connected to a given thought.

    Args:
        thought_id: ID of the thought to get neighbors for
        max_depth: Maximum depth of neighbors to retrieve (1 = direct, 2 = neighbors of neighbors)
        include_relationship_info: Whether to include relationship metadata

    Returns:
        Dictionary containing:
        - neighbors: List of neighbor thought data
        - relationships: List of relationship info (if included)
        - depth_map: Map of node IDs to their depth from source
    """
    logger.info(f"Getting neighbors for thought {thought_id} (max_depth={max_depth})")

    try:
        graph_engine = await get_graph_engine()

        # Get direct neighbors
        neighbors_data = await graph_engine.get_neighbors(str(thought_id))

        if not neighbors_data:
            logger.info(f"No neighbors found for thought {thought_id}")
            return {
                "neighbors": [],
                "relationships": [],
                "depth_map": {}
            }

        # Build result
        neighbors = []
        relationships = []
        depth_map = {thought_id: 0}

        # Process direct neighbors (depth 1)
        for neighbor_data in neighbors_data:
            neighbor_id = UUID(neighbor_data.get("id"))
            neighbors.append(neighbor_data)
            depth_map[neighbor_id] = 1

            if include_relationship_info:
                # Get edge data
                connections = await graph_engine.get_connections(str(thought_id))
                for conn in connections:
                    source_data, edge_data, target_data = conn
                    target_id = UUID(target_data.get("id"))

                    if target_id == neighbor_id:
                        relationships.append({
                            "source_id": str(thought_id),
                            "target_id": str(neighbor_id),
                            "relationship_type": edge_data.get("relationship_type", "unknown"),
                            "strength": edge_data.get("strength", 1.0),
                        })

        # If max_depth > 1, recursively get neighbors of neighbors
        if max_depth > 1:
            current_depth = 1
            current_level = [UUID(n.get("id")) for n in neighbors_data]

            while current_depth < max_depth and current_level:
                next_level = []

                for node_id in current_level:
                    next_neighbors = await graph_engine.get_neighbors(str(node_id))

                    for neighbor_data in next_neighbors:
                        neighbor_id = UUID(neighbor_data.get("id"))

                        # Skip if already visited
                        if neighbor_id not in depth_map:
                            neighbors.append(neighbor_data)
                            depth_map[neighbor_id] = current_depth + 1
                            next_level.append(neighbor_id)

                current_level = next_level
                current_depth += 1

        logger.info(f"Found {len(neighbors)} neighbors at depth <= {max_depth}")

        return {
            "neighbors": neighbors,
            "relationships": relationships,
            "depth_map": {str(k): v for k, v in depth_map.items()}
        }

    except Exception as e:
        logger.error(f"Error getting thought neighbors: {e}")
        return {
            "neighbors": [],
            "relationships": [],
            "depth_map": {}
        }
