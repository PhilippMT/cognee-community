"""Community detection for identifying thought clusters in the graph."""

from typing import Any, Dict, List, Tuple
from uuid import UUID

import networkx as nx
from cognee.shared.logging_utils import get_logger

logger = get_logger(__name__)


async def detect_communities(
    nodes: List[Tuple[str, Dict[str, Any]]],
    edges: List[Tuple[str, str, str, Dict[str, Any]]],
    algorithm: str = "louvain",
    resolution: float = 1.0
) -> Dict[UUID, str]:
    """
    Detect communities/clusters of related thoughts in the graph.

    Community detection groups thoughts into clusters based on their connectivity patterns.
    This is especially useful for:
    - Organizing scattered ADHD thoughts into coherent topics
    - Discovering thematic clusters in your idea collection
    - Identifying isolated thoughts that might need more connections

    Args:
        nodes: List of (node_id, properties) tuples
        edges: List of (source_id, target_id, relationship_type, properties) tuples
        algorithm: Community detection algorithm:
            - "louvain": Louvain method (fast, good quality)
            - "greedy": Greedy modularity maximization
            - "label_propagation": Label propagation (very fast)
        resolution: Resolution parameter (higher = more communities)

    Returns:
        Dictionary mapping node IDs to community IDs (as strings)

    Example:
        >>> communities = await detect_communities(nodes, edges)
        >>> # Group thoughts by community
        >>> for community_id in set(communities.values()):
        >>>     thoughts = [nid for nid, cid in communities.items() if cid == community_id]
        >>>     print(f"Community {community_id}: {len(thoughts)} thoughts")
    """
    if not nodes:
        logger.warning("Cannot detect communities: no nodes provided")
        return {}

    if not edges:
        logger.info("No edges provided, each node is its own community")
        return {UUID(node_id): f"community_{i}" for i, (node_id, _) in enumerate(nodes)}

    try:
        # Build NetworkX undirected graph
        G = nx.Graph()

        # Add nodes
        for node_id, properties in nodes:
            G.add_node(node_id, **properties)

        # Add edges with weights
        for source_id, target_id, _rel_type, properties in edges:
            weight = properties.get("strength", 1.0) if properties else 1.0
            G.add_edge(source_id, target_id, weight=weight)

        logger.info(f"Detecting communities using {algorithm} algorithm")

        # Detect communities based on algorithm
        if algorithm == "louvain":
            communities_gen = nx.community.louvain_communities(
                G,
                weight="weight",
                resolution=resolution
            )
            communities_list = list(communities_gen)

        elif algorithm == "greedy":
            communities_gen = nx.community.greedy_modularity_communities(
                G,
                weight="weight",
                resolution=resolution
            )
            communities_list = list(communities_gen)

        elif algorithm == "label_propagation":
            communities_gen = nx.community.label_propagation_communities(G)
            communities_list = list(communities_gen)

        else:
            logger.warning(f"Unknown algorithm '{algorithm}', using greedy")
            communities_gen = nx.community.greedy_modularity_communities(G, weight="weight")
            communities_list = list(communities_gen)

        # Convert to node_id -> community_id mapping
        node_to_community = {}
        for community_idx, community_nodes in enumerate(communities_list):
            community_id = f"community_{community_idx}"
            for node_id in community_nodes:
                node_to_community[UUID(node_id)] = community_id

        logger.info(f"Detected {len(communities_list)} communities")

        return node_to_community

    except Exception as e:
        logger.error(f"Error detecting communities: {e}")
        # Fallback: each node is its own community
        return {UUID(node_id): f"community_{i}" for i, (node_id, _) in enumerate(nodes)}


async def get_community_summary(
    nodes: List[Tuple[str, Dict[str, Any]]],
    communities: Dict[UUID, str]
) -> Dict[str, Dict[str, Any]]:
    """
    Get summary statistics for each community.

    Args:
        nodes: List of (node_id, properties) tuples
        communities: Dictionary mapping node IDs to community IDs

    Returns:
        Dictionary mapping community IDs to summary information:
        - size: Number of nodes in community
        - tags: Most common tags across nodes
        - avg_importance: Average importance score
    """
    community_summaries = {}

    # Group nodes by community
    community_nodes: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
    for node_id, properties in nodes:
        node_uuid = UUID(node_id)
        if node_uuid in communities:
            community_id = communities[node_uuid]
            if community_id not in community_nodes:
                community_nodes[community_id] = []
            community_nodes[community_id].append((node_id, properties))

    # Calculate summaries
    for community_id, comm_nodes in community_nodes.items():
        # Collect tags
        all_tags = []
        importance_scores = []

        for _, properties in comm_nodes:
            if "tags" in properties and properties["tags"]:
                all_tags.extend(properties["tags"])
            if "importance_score" in properties and properties["importance_score"]:
                importance_scores.append(properties["importance_score"])

        # Find most common tags
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        community_summaries[community_id] = {
            "size": len(comm_nodes),
            "top_tags": [tag for tag, _ in top_tags],
            "avg_importance": sum(importance_scores) / len(importance_scores) if importance_scores else None,
        }

    return community_summaries
