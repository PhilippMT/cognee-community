"""Transitive connection discovery for finding indirect relationships."""

from typing import Dict, List, Tuple, Any, Set
from uuid import UUID
import networkx as nx
from cognee.shared.logging_utils import get_logger

logger = get_logger(__name__)


async def find_transitive_connections(
    nodes: List[Tuple[str, Dict[str, Any]]],
    edges: List[Tuple[str, str, str, Dict[str, Any]]],
    max_hops: int = 3,
    min_strength: float = 0.1
) -> List[Tuple[UUID, UUID, int, List[UUID]]]:
    """
    Discover transitive connections between thoughts that aren't directly linked.
    
    A transitive connection exists when thoughts A and C are connected through
    intermediate thought B (A -> B -> C). These indirect connections often reveal
    non-obvious relationships and are particularly valuable for ADHD brain fog,
    where connections might not be immediately apparent.
    
    This function finds "missing links" that could be explicitly added to the graph.
    
    Args:
        nodes: List of (node_id, properties) tuples
        edges: List of (source_id, target_id, relationship_type, properties) tuples
        max_hops: Maximum number of hops in transitive connection (2 = A->B->C)
        min_strength: Minimum combined connection strength to consider
        
    Returns:
        List of (source_id, target_id, hop_count, path) tuples representing
        potential transitive connections that don't currently exist as direct links
        
    Example:
        >>> transitive = await find_transitive_connections(nodes, edges, max_hops=2)
        >>> for src, tgt, hops, path in transitive:
        >>>     print(f"Potential connection: {src} -> {tgt} via {hops} hops")
        >>>     print(f"  Path: {' -> '.join(str(nid) for nid in path)}")
    """
    if not nodes or not edges:
        logger.warning("Cannot find transitive connections: insufficient graph data")
        return []
    
    try:
        # Build NetworkX undirected graph
        G = nx.Graph()
        
        # Add nodes
        for node_id, properties in nodes:
            G.add_node(node_id, **properties)
        
        # Track existing direct connections
        direct_connections: Set[Tuple[str, str]] = set()
        
        # Add edges
        for src_id, tgt_id, rel_type, properties in edges:
            strength = properties.get("strength", 1.0) if properties else 1.0
            G.add_edge(src_id, tgt_id, weight=strength)
            # Add both directions to the set (since graph is undirected)
            direct_connections.add((src_id, tgt_id))
            direct_connections.add((tgt_id, src_id))
        
        logger.info(f"Finding transitive connections (max_hops={max_hops})")
        
        transitive_connections = []
        
        # For each pair of nodes, check if they have a path but no direct edge
        node_list = list(G.nodes())
        
        for i, source_node in enumerate(node_list):
            if i % 100 == 0 and i > 0:
                logger.debug(f"Processed {i}/{len(node_list)} nodes")
            
            # Use single-source shortest path for efficiency
            try:
                paths = nx.single_source_shortest_path(G, source_node, cutoff=max_hops)
                
                for target_node, path in paths.items():
                    # Skip if same node or if direct connection already exists
                    if source_node == target_node:
                        continue
                    if (source_node, target_node) in direct_connections:
                        continue
                    
                    # We found a path without a direct edge
                    hop_count = len(path) - 1
                    
                    if 2 <= hop_count <= max_hops:
                        # Calculate combined strength along path
                        path_strength = 1.0
                        for j in range(len(path) - 1):
                            edge_data = G.get_edge_data(path[j], path[j + 1])
                            edge_strength = edge_data.get("weight", 1.0) if edge_data else 1.0
                            path_strength *= edge_strength
                        
                        # Only include if combined strength meets threshold
                        if path_strength >= min_strength:
                            transitive_connections.append((
                                UUID(source_node),
                                UUID(target_node),
                                hop_count,
                                [UUID(nid) for nid in path]
                            ))
                            
            except Exception as e:
                logger.debug(f"Error processing node {source_node}: {e}")
                continue
        
        # Sort by hop count (shorter paths first) and limit results
        transitive_connections.sort(key=lambda x: x[2])
        result = transitive_connections[:500]  # Limit to top 500
        
        logger.info(f"Found {len(result)} transitive connections")
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding transitive connections: {e}")
        return []


async def suggest_missing_links(
    nodes: List[Tuple[str, Dict[str, Any]]],
    edges: List[Tuple[str, str, str, Dict[str, Any]]],
    top_k: int = 20
) -> List[Dict[str, Any]]:
    """
    Suggest missing links that could strengthen the thought graph.
    
    This analyzes transitive connections and recommends which ones
    should be made explicit as direct connections.
    
    Args:
        nodes: List of (node_id, properties) tuples
        edges: List of (source_id, target_id, relationship_type, properties) tuples
        top_k: Number of suggestions to return
        
    Returns:
        List of dictionaries with suggestion details:
        - source_id: Source thought ID
        - target_id: Target thought ID
        - hop_count: Number of hops in current path
        - path: List of intermediate node IDs
        - reason: Human-readable explanation
    """
    transitive = await find_transitive_connections(nodes, edges, max_hops=3)
    
    if not transitive:
        return []
    
    # Convert to suggestions with explanations
    suggestions = []
    
    for src_id, tgt_id, hops, path in transitive[:top_k]:
        # Build explanation
        if hops == 2:
            reason = f"These thoughts are connected through 1 intermediate idea"
        else:
            reason = f"These thoughts are connected through {hops - 1} intermediate ideas"
        
        suggestions.append({
            "source_id": str(src_id),
            "target_id": str(tgt_id),
            "hop_count": hops,
            "path": [str(nid) for nid in path],
            "reason": reason,
            "suggested_relationship": "relates_to"
        })
    
    return suggestions
