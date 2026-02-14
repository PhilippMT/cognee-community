"""Centrality measures for identifying important nodes in the thought graph."""

from typing import Dict, List, Tuple, Any, Optional
from uuid import UUID
import networkx as nx
from cognee.shared.logging_utils import get_logger

logger = get_logger(__name__)


async def calculate_centrality(
    nodes: List[Tuple[str, Dict[str, Any]]],
    edges: List[Tuple[str, str, str, Dict[str, Any]]],
    centrality_type: str = "betweenness"
) -> Dict[UUID, float]:
    """
    Calculate centrality scores for all nodes in the thought graph.
    
    Centrality measures identify important nodes based on their position in the network:
    - Betweenness: Nodes that lie on many shortest paths between other nodes (bridge ideas)
    - Closeness: Nodes that are close to all other nodes (central concepts)
    - Degree: Nodes with many direct connections (highly connected thoughts)
    - Eigenvector: Nodes connected to other important nodes (influential ideas)
    
    Args:
        nodes: List of (node_id, properties) tuples
        edges: List of (source_id, target_id, relationship_type, properties) tuples
        centrality_type: Type of centrality to calculate:
            - "betweenness": Betweenness centrality (bridge ideas)
            - "closeness": Closeness centrality (central concepts)
            - "degree": Degree centrality (highly connected)
            - "eigenvector": Eigenvector centrality (influential)
            - "all": Calculate all centrality measures and return average
            
    Returns:
        Dictionary mapping node IDs to centrality scores (0.0 to 1.0)
        
    Example:
        >>> centrality = await calculate_centrality(nodes, edges, "betweenness")
        >>> # Find bridge ideas that connect different thought clusters
        >>> bridges = [(nid, score) for nid, score in centrality.items() if score > 0.5]
    """
    if not nodes:
        logger.warning("Cannot calculate centrality: no nodes provided")
        return {}
    
    if not edges:
        logger.info("No edges provided, returning zero centrality scores")
        return {UUID(node_id): 0.0 for node_id, _ in nodes}
    
    try:
        # Build NetworkX graph (undirected for most centrality measures)
        G = nx.Graph()
        
        # Add nodes
        for node_id, properties in nodes:
            G.add_node(node_id, **properties)
        
        # Add edges
        for source_id, target_id, rel_type, properties in edges:
            weight = properties.get("strength", 1.0) if properties else 1.0
            G.add_edge(source_id, target_id, weight=weight)
        
        logger.info(f"Calculating {centrality_type} centrality for {G.number_of_nodes()} nodes")
        
        # Calculate centrality based on type
        if centrality_type == "betweenness":
            centrality_scores = nx.betweenness_centrality(G, weight="weight")
        elif centrality_type == "closeness":
            centrality_scores = nx.closeness_centrality(G, distance="weight")
        elif centrality_type == "degree":
            centrality_scores = nx.degree_centrality(G)
        elif centrality_type == "eigenvector":
            try:
                centrality_scores = nx.eigenvector_centrality(G, weight="weight", max_iter=100)
            except nx.PowerIterationFailedConvergence:
                logger.warning("Eigenvector centrality failed to converge, using degree centrality")
                centrality_scores = nx.degree_centrality(G)
        elif centrality_type == "all":
            # Calculate all and average them
            scores = {}
            try:
                betweenness = nx.betweenness_centrality(G, weight="weight")
                closeness = nx.closeness_centrality(G, distance="weight")
                degree = nx.degree_centrality(G)
                eigenvector = nx.eigenvector_centrality(G, weight="weight", max_iter=100)
                
                for node_id in G.nodes():
                    scores[node_id] = (
                        betweenness[node_id] +
                        closeness[node_id] +
                        degree[node_id] +
                        eigenvector[node_id]
                    ) / 4.0
                    
                centrality_scores = scores
            except Exception as e:
                logger.warning(f"Error calculating combined centrality, falling back to degree: {e}")
                centrality_scores = nx.degree_centrality(G)
        else:
            logger.warning(f"Unknown centrality type '{centrality_type}', using degree centrality")
            centrality_scores = nx.degree_centrality(G)
        
        # Convert string IDs back to UUIDs
        result = {UUID(node_id): score for node_id, score in centrality_scores.items()}
        
        logger.info(f"Centrality calculation complete. Max score: {max(result.values()):.4f}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating centrality: {e}")
        return {UUID(node_id): 0.0 for node_id, _ in nodes}


async def find_bridge_thoughts(
    nodes: List[Tuple[str, Dict[str, Any]]],
    edges: List[Tuple[str, str, str, Dict[str, Any]]],
    threshold: float = 0.3
) -> List[UUID]:
    """
    Find "bridge" thoughts that connect different parts of the graph.
    
    Bridge thoughts have high betweenness centrality and are crucial for
    connecting different topic clusters or idea domains.
    
    Args:
        nodes: List of (node_id, properties) tuples
        edges: List of (source_id, target_id, relationship_type, properties) tuples
        threshold: Minimum betweenness centrality to be considered a bridge
        
    Returns:
        List of node IDs that are bridges
    """
    betweenness = await calculate_centrality(nodes, edges, "betweenness")
    bridges = [node_id for node_id, score in betweenness.items() if score >= threshold]
    
    logger.info(f"Found {len(bridges)} bridge thoughts (threshold={threshold})")
    
    return bridges
