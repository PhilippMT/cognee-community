"""
Graph Algorithms for Thought Graph Analysis.

Provides NetworkX-based algorithms for analyzing thought graphs to surface
insights especially valuable for ADHD thought patterns:

Modules:
    pagerank: Identify influential thoughts based on connection prestige.
    centrality: Find bridge ideas (betweenness, closeness, degree, eigenvector).
    community_detection: Organize scattered thoughts into thematic clusters.
    shortest_path: Discover how thoughts connect through intermediary ideas.
    transitive_connections: Find hidden indirect relationships (A→B→C).
"""

from .centrality import calculate_centrality, find_bridge_thoughts
from .community_detection import detect_communities, get_community_summary
from .pagerank import calculate_pagerank, get_top_pagerank_thoughts
from .shortest_path import find_connection_chains, find_shortest_paths
from .transitive_connections import find_transitive_connections, suggest_missing_links

__all__ = [
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
]
