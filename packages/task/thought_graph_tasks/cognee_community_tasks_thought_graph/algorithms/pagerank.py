"""PageRank algorithm for identifying influential thoughts in the graph."""

from typing import Any, Dict, List, Tuple
from uuid import UUID

import networkx as nx
from cognee.shared.logging_utils import get_logger

logger = get_logger(__name__)


async def calculate_pagerank(
    nodes: List[Tuple[str, Dict[str, Any]]],
    edges: List[Tuple[str, str, str, Dict[str, Any]]],
    alpha: float = 0.85,
    max_iterations: int = 100,
    tolerance: float = 1e-6,
) -> Dict[UUID, float]:
    """
    Calculate PageRank scores for all nodes in the thought graph.

    PageRank identifies the most "important" or "central" thoughts based on
    the structure of connections. Thoughts that are referenced by many other
    important thoughts will have higher PageRank scores.

    This is particularly useful for:
    - Identifying core/foundational ideas in your thought network
    - Finding thoughts that serve as hubs connecting different topics
    - Prioritizing which thoughts to review or develop further

    Args:
        nodes: List of (node_id, properties) tuples
        edges: List of (source_id, target_id, relationship_type, properties) tuples
        alpha: Damping parameter (typically 0.85), controls random walk probability
        max_iterations: Maximum number of iterations for convergence
        tolerance: Convergence threshold

    Returns:
        Dictionary mapping node IDs to PageRank scores (0.0 to 1.0)

    Example:
        >>> nodes = [(str(id1), {"content": "Idea 1"}), ...]
        >>> edges = [(str(id1), str(id2), "relates_to", {}), ...]
        >>> pagerank_scores = await calculate_pagerank(nodes, edges)
        >>> print(f"Most important thought: {max(pagerank_scores, key=pagerank_scores.get)}")
    """
    if not nodes:
        logger.warning("Cannot calculate PageRank: no nodes provided")
        return {}

    if not edges:
        logger.info("No edges provided, returning uniform PageRank scores")
        uniform_score = 1.0 / len(nodes)
        return {UUID(node_id): uniform_score for node_id, _ in nodes}

    try:
        # Build NetworkX directed graph
        G = nx.DiGraph()

        # Add nodes
        for node_id, properties in nodes:
            G.add_node(node_id, **properties)

        # Add edges with weights based on connection strength
        for source_id, target_id, rel_type, properties in edges:
            weight = properties.get("strength", 1.0) if properties else 1.0
            G.add_edge(source_id, target_id, weight=weight, relationship=rel_type)

        logger.info(f"Calculating PageRank for graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

        # Calculate PageRank
        pagerank_scores = nx.pagerank(
            G,
            alpha=alpha,
            max_iter=max_iterations,
            tol=tolerance,
            weight="weight"
        )

        # Convert string IDs back to UUIDs
        result = {UUID(node_id): score for node_id, score in pagerank_scores.items()}

        logger.info(f"PageRank calculation complete. Top score: {max(result.values()):.4f}")

        return result

    except Exception as e:
        logger.error(f"Error calculating PageRank: {e}")
        # Return uniform scores as fallback
        uniform_score = 1.0 / len(nodes)
        return {UUID(node_id): uniform_score for node_id, _ in nodes}


async def get_top_pagerank_thoughts(
    pagerank_scores: Dict[UUID, float],
    top_k: int = 10
) -> List[Tuple[UUID, float]]:
    """
    Get the top K thoughts by PageRank score.

    Args:
        pagerank_scores: Dictionary of node ID to PageRank score
        top_k: Number of top thoughts to return

    Returns:
        List of (node_id, score) tuples, sorted by score descending
    """
    sorted_thoughts = sorted(
        pagerank_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_thoughts[:top_k]
