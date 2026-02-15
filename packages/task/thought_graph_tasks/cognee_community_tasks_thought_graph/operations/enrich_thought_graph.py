"""Enrich the thought graph with computed metrics and discovered connections."""

from typing import Any, Dict

from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.shared.logging_utils import get_logger

from cognee_community_tasks_thought_graph.algorithms.centrality import calculate_centrality
from cognee_community_tasks_thought_graph.algorithms.community_detection import detect_communities
from cognee_community_tasks_thought_graph.algorithms.pagerank import calculate_pagerank
from cognee_community_tasks_thought_graph.algorithms.transitive_connections import (
    find_transitive_connections,
)

logger = get_logger(__name__)


async def enrich_thought_graph(
    compute_pagerank: bool = True,
    compute_centrality: bool = True,
    detect_communities_flag: bool = True,
    find_transitive: bool = True,
    auto_add_transitive_links: bool = False,
    transitive_strength_threshold: float = 0.3
) -> Dict[str, Any]:
    """
    Enrich the thought graph with computed metrics and discovered connections.

    This is the main enrichment pipeline that:
    1. Calculates PageRank scores to identify influential thoughts
    2. Calculates centrality measures to find bridge thoughts
    3. Detects communities to organize thoughts into clusters
    4. Finds transitive connections that could be made explicit
    5. Optionally adds high-confidence transitive connections

    Run this periodically (e.g., after adding multiple thoughts) to keep the
    graph enriched with insights.

    Args:
        compute_pagerank: Calculate PageRank scores
        compute_centrality: Calculate centrality measures
        detect_communities_flag: Detect community structure
        find_transitive: Find transitive connections
        auto_add_transitive_links: Automatically add strong transitive connections as edges
        transitive_strength_threshold: Minimum strength for auto-adding transitive links

    Returns:
        Dictionary with enrichment results:
        - nodes_enriched: Number of nodes that were enriched
        - pagerank_computed: Whether PageRank was calculated
        - centrality_computed: Whether centrality was calculated
        - communities_detected: Number of communities found
        - transitive_found: Number of transitive connections found
        - transitive_added: Number of transitive connections added as edges

    Example:
        >>> results = await enrich_thought_graph(
        ...     compute_pagerank=True,
        ...     detect_communities_flag=True,
        ...     auto_add_transitive_links=True
        ... )
        >>> print(f"Enriched {results['nodes_enriched']} thoughts")
        >>> print(f"Found {results['communities_detected']} communities")
    """
    logger.info("Starting thought graph enrichment")

    try:
        graph_engine = await get_graph_engine()

        # Get graph data
        nodes, edges = await graph_engine.get_graph_data()

        if not nodes:
            logger.info("No nodes to enrich")
            return {
                "nodes_enriched": 0,
                "pagerank_computed": False,
                "centrality_computed": False,
                "communities_detected": 0,
                "transitive_found": 0,
                "transitive_added": 0
            }

        results = {
            "nodes_enriched": len(nodes),
            "pagerank_computed": False,
            "centrality_computed": False,
            "communities_detected": 0,
            "transitive_found": 0,
            "transitive_added": 0
        }

        node_updates = {}  # Store updates to be applied

        # 1. Calculate PageRank
        if compute_pagerank:
            logger.info("Computing PageRank scores")
            pagerank_scores = await calculate_pagerank(nodes, edges)

            for node_id, score in pagerank_scores.items():
                if str(node_id) not in node_updates:
                    node_updates[str(node_id)] = {}
                node_updates[str(node_id)]["pagerank_score"] = float(score)

            results["pagerank_computed"] = True
            logger.info(f"PageRank computed for {len(pagerank_scores)} nodes")

        # 2. Calculate Centrality
        if compute_centrality:
            logger.info("Computing centrality measures")

            # Calculate betweenness centrality (bridge thoughts)
            centrality_scores = await calculate_centrality(nodes, edges, "betweenness")

            for node_id, score in centrality_scores.items():
                if str(node_id) not in node_updates:
                    node_updates[str(node_id)] = {}
                node_updates[str(node_id)]["centrality_score"] = float(score)

            results["centrality_computed"] = True
            logger.info(f"Centrality computed for {len(centrality_scores)} nodes")

        # 3. Detect Communities
        if detect_communities_flag:
            logger.info("Detecting communities")
            communities = await detect_communities(nodes, edges)

            for node_id, community_id in communities.items():
                if str(node_id) not in node_updates:
                    node_updates[str(node_id)] = {}
                node_updates[str(node_id)]["community_id"] = community_id

            results["communities_detected"] = len(set(communities.values()))
            logger.info(f"Detected {results['communities_detected']} communities")

        # Update connection counts for all nodes
        for node_id, _ in nodes:
            # Count edges for this node
            connection_count = sum(
                1 for src, tgt, _, _ in edges
                if src == node_id or tgt == node_id
            )

            if node_id not in node_updates:
                node_updates[node_id] = {}
            node_updates[node_id]["connection_count"] = connection_count

        # Apply all node updates
        logger.info(f"Applying updates to {len(node_updates)} nodes")
        for node_id, updates in node_updates.items():
            try:
                # Get current node data
                current_data = await graph_engine.get_node(node_id)
                if current_data:
                    updated_data = {**current_data, **updates}

                    # Remove the node and re-add with updated properties
                    await graph_engine.delete_node(node_id)
                    await graph_engine.add_nodes([(node_id, updated_data)])
                    logger.debug(f"Updated node {node_id} with: {updates}")

            except Exception as e:
                logger.warning(f"Error updating node {node_id}: {e}")

        # 4. Find Transitive Connections
        if find_transitive:
            logger.info("Finding transitive connections")
            transitive_connections = await find_transitive_connections(
                nodes,
                edges,
                max_hops=3,
                min_strength=transitive_strength_threshold
            )

            results["transitive_found"] = len(transitive_connections)
            logger.info(f"Found {len(transitive_connections)} transitive connections")

            # Optionally add strong transitive connections
            if auto_add_transitive_links and transitive_connections:
                new_edges = []

                for src_id, tgt_id, hop_count, path in transitive_connections[:50]:  # Limit to top 50
                    # Add as a new edge with lower strength
                    new_edges.append((
                        str(src_id),
                        str(tgt_id),
                        "transitive_connection",
                        {
                            "strength": transitive_strength_threshold,
                            "discovery_method": "transitive",
                            "hop_count": hop_count,
                            "path": [str(nid) for nid in path]
                        }
                    ))

                if new_edges:
                    await graph_engine.add_edges(new_edges)
                    results["transitive_added"] = len(new_edges)
                    logger.info(f"Added {len(new_edges)} transitive connections as edges")

        logger.info("Thought graph enrichment complete")

        return results

    except Exception as e:
        logger.error(f"Error enriching thought graph: {e}")
        return {
            "nodes_enriched": 0,
            "pagerank_computed": False,
            "centrality_computed": False,
            "communities_detected": 0,
            "transitive_found": 0,
            "transitive_added": 0,
            "error": str(e)
        }
