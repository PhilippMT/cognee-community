"""
Thought Graph Operations.

High-level operations for managing the ADHD thought graph, including
thought capture, connection discovery, graph enrichment, web research,
project matching, edge weight management, and integrated memify pipelines.

Modules:
    add_thought: Quick thought capture with auto-connection discovery.
    discover_connections: Semantic, tag-based, and LLM connection discovery.
    enrich_thought_graph: Graph algorithm enrichment (PageRank, centrality, communities).
    find_surprise_connections: Surface unexpected serendipitous relationships.
    get_thought_neighbors: Explore the graph neighborhood of a thought.
    get_thought_communities: Detect and summarize thematic clusters.
    enrich_with_web: Web search enrichment via Tavily API.
    match_projects: Match thoughts to projects and repositories.
    edge_weight_management: Time-based decay, reinforcement, and pruning.
    memify_thoughts: Integrated enrichment pipeline combining all features.
"""

from .discover_connections import discover_connections
from .find_surprise_connections import find_surprise_connections
from .get_thought_neighbors import get_thought_neighbors
from .enrich_thought_graph import enrich_thought_graph
from .add_thought import add_thought, add_thoughts_batch
from .get_thought_communities import get_thought_communities
from .enrich_with_web import enrich_with_web_search, enrich_with_scraped_content, batch_enrich_with_web
from .match_projects import match_to_projects, create_project_connections, find_project_clusters
from .edge_weight_management import (
    decay_edge_weights,
    reinforce_edge,
    calculate_potential_connections,
    prune_weak_connections,
)
from .memify_thoughts import memify_thoughts, cognify_and_memify_thoughts

__all__ = [
    "discover_connections",
    "find_surprise_connections",
    "get_thought_neighbors",
    "enrich_thought_graph",
    "add_thought",
    "add_thoughts_batch",
    "get_thought_communities",
    "enrich_with_web_search",
    "enrich_with_scraped_content",
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
