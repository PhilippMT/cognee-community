"""
ADHD Thought Graph Tasks for Cognee.

This package provides models, algorithms, and operations for managing
interconnected ideas and thoughts with a focus on discovering hidden
connections, transitive relationships, and surprising associations
that are especially valuable for ADHD thought patterns.

Subpackages:
    models: Data models (ThoughtNode, Connection, SurpriseScore)
    algorithms: Graph algorithms (PageRank, centrality, community detection, etc.)
    operations: High-level operations (add thoughts, discover connections, enrich, etc.)
"""

import cognee_community_tasks_thought_graph.kuzu_compat  # noqa: F401 — patch KuzuAdapter

from .algorithms import (
    calculate_centrality,
    calculate_pagerank,
    detect_communities,
    find_bridge_thoughts,
    find_connection_chains,
    find_shortest_paths,
    find_transitive_connections,
    get_community_summary,
    get_top_pagerank_thoughts,
    suggest_missing_links,
)
from .models import Connection, SurpriseScore, ThoughtNode
from .operations import (
    add_thought,
    add_thoughts_batch,
    batch_enrich_with_web,
    calculate_potential_connections,
    cognify_and_memify_thoughts,
    create_project_connections,
    decay_edge_weights,
    discover_connections,
    enrich_thought_graph,
    enrich_with_web_search,
    find_project_clusters,
    find_surprise_connections,
    get_thought_communities,
    get_thought_neighbors,
    match_to_projects,
    memify_thoughts,
    prune_weak_connections,
    reinforce_edge,
)

__all__ = [
    # Models
    "ThoughtNode",
    "Connection",
    "SurpriseScore",
    # Algorithms
    "calculate_pagerank",
    "get_top_pagerank_thoughts",
    "calculate_centrality",
    "find_bridge_thoughts",
    "detect_communities",
    "get_community_summary",
    "find_shortest_paths",
    "find_connection_chains",
    "find_transitive_connections",
    "suggest_missing_links",
    # Operations
    "add_thought",
    "add_thoughts_batch",
    "discover_connections",
    "enrich_thought_graph",
    "find_surprise_connections",
    "get_thought_neighbors",
    "get_thought_communities",
    "enrich_with_web_search",
    "batch_enrich_with_web",
    "match_to_projects",
    "create_project_connections",
    "find_project_clusters",
    "decay_edge_weights",
    "reinforce_edge",
    "calculate_potential_connections",
    "prune_weak_connections",
    "memify_thoughts",
    "cognify_and_memify_thoughts",
]
