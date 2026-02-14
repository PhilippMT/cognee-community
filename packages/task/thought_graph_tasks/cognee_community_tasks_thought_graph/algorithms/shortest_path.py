"""Shortest path algorithms for finding connections between thoughts."""

from typing import Dict, List, Tuple, Any, Optional
from uuid import UUID
import networkx as nx
from cognee.shared.logging_utils import get_logger

logger = get_logger(__name__)


async def find_shortest_paths(
    nodes: List[Tuple[str, Dict[str, Any]]],
    edges: List[Tuple[str, str, str, Dict[str, Any]]],
    source_id: UUID,
    target_id: Optional[UUID] = None,
    max_length: int = 5
) -> Dict[UUID, List[UUID]]:
    """
    Find shortest paths from a source thought to other thoughts.
    
    This helps discover how thoughts are connected through intermediary ideas.
    Useful for understanding chains of reasoning or idea evolution.
    
    Args:
        nodes: List of (node_id, properties) tuples
        edges: List of (source_id, target_id, relationship_type, properties) tuples
        source_id: Starting thought node ID
        target_id: Optional target thought node ID. If None, finds paths to all reachable nodes
        max_length: Maximum path length to consider
        
    Returns:
        Dictionary mapping target node IDs to paths (lists of node IDs from source to target)
        
    Example:
        >>> paths = await find_shortest_paths(nodes, edges, idea1_id, idea2_id)
        >>> if idea2_id in paths:
        >>>     path = paths[idea2_id]
        >>>     print(f"Connection: {' -> '.join(str(nid) for nid in path)}")
    """
    if not nodes or not edges:
        logger.warning("Cannot find paths: insufficient graph data")
        return {}
    
    try:
        # Build NetworkX undirected graph
        G = nx.Graph()
        
        # Add nodes
        for node_id, properties in nodes:
            G.add_node(node_id, **properties)
        
        # Add edges (unweighted for shortest path, or use inverse of strength)
        for src_id, tgt_id, rel_type, properties in edges:
            # Use inverse of strength as distance (stronger connections = shorter distance)
            strength = properties.get("strength", 1.0) if properties else 1.0
            distance = 1.0 / max(strength, 0.1)  # Avoid division by zero
            G.add_edge(src_id, tgt_id, weight=distance)
        
        source_str = str(source_id)
        
        if source_str not in G:
            logger.warning(f"Source node {source_id} not found in graph")
            return {}
        
        paths = {}
        
        if target_id is not None:
            # Find single shortest path
            target_str = str(target_id)
            if target_str not in G:
                logger.warning(f"Target node {target_id} not found in graph")
                return {}
            
            try:
                path = nx.shortest_path(G, source_str, target_str, weight="weight")
                if len(path) <= max_length + 1:  # +1 because path includes both endpoints
                    paths[target_id] = [UUID(nid) for nid in path]
            except nx.NetworkXNoPath:
                logger.info(f"No path found from {source_id} to {target_id}")
                
        else:
            # Find shortest paths to all reachable nodes
            try:
                all_paths = nx.single_source_shortest_path(G, source_str, cutoff=max_length)
                for target_str, path in all_paths.items():
                    target_uuid = UUID(target_str)
                    if target_uuid != source_id:  # Don't include path to self
                        paths[target_uuid] = [UUID(nid) for nid in path]
            except Exception as e:
                logger.error(f"Error finding shortest paths: {e}")
        
        logger.info(f"Found {len(paths)} shortest paths from {source_id}")
        
        return paths
        
    except Exception as e:
        logger.error(f"Error in shortest path calculation: {e}")
        return {}


async def find_connection_chains(
    nodes: List[Tuple[str, Dict[str, Any]]],
    edges: List[Tuple[str, str, str, Dict[str, Any]]],
    min_length: int = 2,
    max_length: int = 4
) -> List[List[UUID]]:
    """
    Find interesting chains of connected thoughts.
    
    A chain is a path through the graph that shows progression or evolution of ideas.
    This is especially useful for ADHD thought patterns where ideas often build on each other
    in non-obvious ways.
    
    Args:
        nodes: List of (node_id, properties) tuples
        edges: List of (source_id, target_id, relationship_type, properties) tuples
        min_length: Minimum chain length (number of nodes)
        max_length: Maximum chain length
        
    Returns:
        List of chains, where each chain is a list of node IDs
    """
    if not nodes or not edges:
        return []
    
    try:
        # Build NetworkX directed graph to preserve direction
        G = nx.DiGraph()
        
        for node_id, properties in nodes:
            G.add_node(node_id, **properties)
        
        for src_id, tgt_id, rel_type, properties in edges:
            G.add_edge(src_id, tgt_id)
        
        chains = []
        
        # Find all simple paths of the specified length
        for source_node in list(G.nodes())[:100]:  # Limit to first 100 nodes for performance
            for target_node in G.nodes():
                if source_node != target_node:
                    try:
                        paths = nx.all_simple_paths(
                            G,
                            source_node,
                            target_node,
                            cutoff=max_length - 1
                        )
                        for path in paths:
                            if min_length <= len(path) <= max_length:
                                chain = [UUID(nid) for nid in path]
                                chains.append(chain)
                                
                    except (nx.NetworkXNoPath, nx.NodeNotFound):
                        continue
        
        logger.info(f"Found {len(chains)} connection chains")
        
        return chains[:100]  # Return top 100 chains
        
    except Exception as e:
        logger.error(f"Error finding connection chains: {e}")
        return []
