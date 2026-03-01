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

from .add_thought import add_thought, add_thoughts_batch
from .discover_connections import discover_connections
from .edge_weight_management import (
    calculate_potential_connections,
    decay_edge_weights,
    prune_weak_connections,
    reinforce_edge,
)
from .enrich_thought_graph import enrich_thought_graph
from .enrich_with_web import (
    batch_enrich_with_web,
    enrich_with_scraped_content,
    enrich_with_web_search,
)
from .find_surprise_connections import find_surprise_connections
from .get_thought_communities import get_thought_communities
from .get_thought_neighbors import get_thought_neighbors
from .match_projects import create_project_connections, find_project_clusters, match_to_projects
from .memify_thoughts import cognify_and_memify_thoughts, memify_thoughts

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
