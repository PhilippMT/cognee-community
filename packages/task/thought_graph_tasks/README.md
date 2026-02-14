# Cognee Community Tasks: Thought Graph

ADHD-optimized thought graph tasks for [cognee](https://github.com/topoteretes/cognee). Provides models, algorithms, and operations for managing scattered thoughts, discovering hidden connections, and organizing brainfog into actionable insights.

## Installation

```bash
pip install cognee-community-tasks-thought-graph
```

## Package Structure

```
cognee_community_tasks_thought_graph/
├── models/          # Data models
│   ├── thought_node.py      # ThoughtNode (extends cognee DataPoint)
│   ├── connection.py        # Connection between thoughts
│   └── surprise_score.py    # Surprise/serendipity score
├── algorithms/      # Graph algorithms (NetworkX-based)
│   ├── pagerank.py           # Identify influential thoughts
│   ├── centrality.py         # Find bridge ideas
│   ├── community_detection.py # Organize into thematic clusters
│   ├── shortest_path.py      # Find connection chains
│   └── transitive_connections.py # Discover hidden indirect links
└── operations/      # High-level operations
    ├── add_thought.py         # Quick thought capture
    ├── discover_connections.py # Semantic + tag + LLM connection discovery
    ├── enrich_thought_graph.py # Run all enrichment algorithms
    ├── find_surprise_connections.py # Surface unexpected relationships
    ├── get_thought_neighbors.py    # Explore graph neighborhood
    ├── get_thought_communities.py  # Detect thematic clusters
    ├── enrich_with_web.py     # Web search enrichment (Tavily)
    ├── match_projects.py      # Match thoughts to projects/repos
    ├── edge_weight_management.py # Decay, reinforce, prune edges
    └── memify_thoughts.py     # Integrated enrichment pipeline
```

## Models

### ThoughtNode

Represents a single thought/idea in the graph. Extends cognee's `DataPoint`.

| Field | Type | Description |
|-------|------|-------------|
| `content` | `str` | The thought content (required) |
| `title` | `str?` | Optional short title |
| `tags` | `list[str]` | Tags for categorization |
| `energy_level` | `int?` | Energy when captured (1-10) |
| `importance_score` | `int?` | User-defined importance (1-10) |
| `related_projects` | `list[str]` | Associated project names |
| `pagerank_score` | `float?` | Computed influence score |
| `centrality_score` | `float?` | Computed bridge score |
| `community_id` | `str?` | Thematic cluster ID |

### Connection

Represents a relationship between two thoughts.

| Field | Type | Description |
|-------|------|-------------|
| `source_id` | `UUID` | Source thought ID |
| `target_id` | `UUID` | Target thought ID |
| `relationship_type` | `str` | e.g., `relates_to`, `semantically_related` |
| `strength` | `float` | Connection strength (0.0–1.0) |
| `discovery_method` | `str` | How it was found |
| `surprise_score` | `float?` | How unexpected it is |

### SurpriseScore

Quantifies how unexpected a connection is.

| Field | Type | Description |
|-------|------|-------------|
| `overall_score` | `float` | Combined surprise (0.0–1.0) |
| `semantic_distance` | `float?` | Content dissimilarity |
| `temporal_distance` | `float?` | Time separation |
| `structural_distance` | `float?` | Graph distance |
| `domain_distance` | `float?` | Tag/category dissimilarity |

## Algorithms

### PageRank — Find Influential Thoughts

```python
from cognee_community_tasks_thought_graph.algorithms import calculate_pagerank

scores = await calculate_pagerank(nodes, edges, alpha=0.85)
# Returns {UUID: float} mapping thought IDs to importance scores
```

### Centrality — Find Bridge Ideas

```python
from cognee_community_tasks_thought_graph.algorithms import calculate_centrality

# Types: "betweenness", "closeness", "degree", "eigenvector", "all"
scores = await calculate_centrality(nodes, edges, "betweenness")
```

### Community Detection — Organize Into Clusters

```python
from cognee_community_tasks_thought_graph.algorithms import detect_communities

# Algorithms: "greedy", "label_propagation", "louvain"
communities = await detect_communities(nodes, edges, algorithm="greedy")
# Returns {UUID: "community_0"} mapping
```

### Transitive Connections — Find Hidden Links

```python
from cognee_community_tasks_thought_graph.algorithms import find_transitive_connections

transitive = await find_transitive_connections(nodes, edges, max_hops=3)
# Returns [(source_id, target_id, hop_count, path)]
```

## Operations

### Quick Thought Capture

```python
from cognee_community_tasks_thought_graph.operations import add_thought, add_thoughts_batch

thought = await add_thought(
    content="Build a knowledge graph for ADHD thought management",
    tags=["adhd", "productivity"],
    importance_score=8,
    auto_connect=True,
)

thoughts = await add_thoughts_batch([
    {"content": "Idea 1", "tags": ["tag1"]},
    {"content": "Idea 2", "tags": ["tag2"]},
])
```

### Graph Enrichment

```python
from cognee_community_tasks_thought_graph.operations import enrich_thought_graph

results = await enrich_thought_graph(
    compute_pagerank=True,
    detect_communities_flag=True,
    find_transitive=True,
    auto_add_transitive_links=True,
)
```

### Surprise Connections

```python
from cognee_community_tasks_thought_graph.operations import find_surprise_connections

surprises = await find_surprise_connections(min_surprise_score=0.5, max_results=20)
for s in surprises:
    print(f"{s.explanation} (score: {s.overall_score:.2f})")
```

### Web Enrichment

```python
from cognee_community_tasks_thought_graph.operations import enrich_with_web_search

# Requires TAVILY_API_KEY environment variable
results = await enrich_with_web_search(thought_id=thought.id, max_results=5)
```

### Integrated Memify

```python
from cognee_community_tasks_thought_graph.operations import memify_thoughts

results = await memify_thoughts(
    enable_web_enrichment=True,
    enable_project_matching=True,
    enable_edge_decay=True,
    project_patterns={"my_project": ["keyword1", "keyword2"]},
)
```

## Why This Helps ADHD Brains

- **Non-linear thinking**: The graph embraces associative, non-hierarchical connections
- **Working memory support**: Externalize ideas — the graph maintains relationships automatically
- **Serendipitous discovery**: Surprise connections highlight non-obvious relationships
- **Reduced organization overhead**: Capture first, let algorithms organize later
- **Energy-aware**: Track energy levels when thoughts are captured

## Implementation Status

| Component | Status | Completion | Notes |
|-----------|--------|------------|-------|
| Models (ThoughtNode, Connection, SurpriseScore) | ✅ Complete | 100% | All data models fully implemented with Pydantic validation |
| Graph algorithms (PageRank, centrality, communities, shortest path, transitive) | ✅ Complete | 100% | All 5 algorithms working via NetworkX |
| Thought capture (`add_thought`, `add_thoughts_batch`) | ✅ Complete | 100% | Input validation, graph persistence, auto-connect |
| Connection discovery (`discover_connections`) | ⚠️ Partial | 80% | Semantic + tag-based working; LLM inference stubbed |
| Graph enrichment (`enrich_thought_graph`) | ✅ Complete | 100% | Runs all algorithms, updates node metrics |
| Surprise connections (`find_surprise_connections`) | ✅ Complete | 100% | Multi-factor scoring with explanations |
| Graph exploration (`get_thought_neighbors`, `get_thought_communities`) | ✅ Complete | 100% | Depth-based traversal, community summaries |
| Web enrichment (`enrich_with_web_search`, `enrich_with_scraped_content`) | ⚠️ Partial | 75% | Tavily API works; graph persistence pending |
| Project matching (`match_to_projects`, `create_project_connections`) | ⚠️ Partial | 80% | Analysis works; node property updates pending |
| Edge weight management (`decay_edge_weights`, `reinforce_edge`, `prune_weak_connections`) | ⚠️ Partial | 60% | Calculation works; graph persistence pending |
| Potential connections (`calculate_potential_connections`) | ✅ Complete | 100% | Read-only analysis, fully functional |
| Integrated memify (`memify_thoughts`) | ✅ Complete | 90% | Orchestration works; limited by individual operation status |
| Combined cognify+memify (`cognify_and_memify_thoughts`) | ⚠️ Placeholder | 20% | Calls memify only; cognify integration not yet wired |

## Open TODOs and Unfinished Features

### ⚠️ LLM-Based Connection Inference

**File**: `operations/discover_connections.py`
**Status**: Stubbed — the code path exists but logs "LLM-based connection discovery not yet implemented" and skips.
**What's needed**: Integrate with cognee's `LLMGateway` to send candidate thought pairs for non-obvious connection analysis using structured output. The prompt template and response model need to be defined.
**Impact**: Only semantic similarity and tag overlap are used for auto-connection; non-obvious connections are missed.

### ⚠️ Web Enrichment — Graph Persistence

**File**: `operations/enrich_with_web.py`
**Status**: Tavily API integration works and returns search results, but results are only logged — not persisted to the graph.
**What's needed**:
1. A `WebResource` data model extending `DataPoint` with fields: `url`, `title`, `content`, `relevance_score`, `scraped_at`, `source`
2. Node creation in the graph for each web resource
3. Edge creation connecting web resources to the source thought
4. Vector indexing of web resource content for future similarity search

**Current behavior**: Returns `search_results`, `connections_created` (count only), `content_added` (byte count) — but nothing is saved to the graph database.

### ⚠️ Web Scraping — Content Analysis

**File**: `operations/enrich_with_web.py` (`enrich_with_scraped_content`)
**Status**: Calls `web_scraper_task` but returns estimated counts without analyzing content relevance or creating graph edges.
**What's needed**: Content relevance analysis and proper graph edge creation between scraped content and the source thought.

### ⚠️ Project Matching — Node Property Updates

**File**: `operations/match_projects.py`
**Status**: `match_to_projects()` correctly analyzes content and returns matches with confidence scores. `create_project_connections()` calculates what would be updated but doesn't persist.
**What's needed**: Graph backend support for node property updates to write `related_projects` field back to thought nodes.
**Current behavior**: Logs `"Would update thought {id} with projects: {list}"` but doesn't actually update.

### ⚠️ Edge Weight Decay — Graph Persistence

**File**: `operations/edge_weight_management.py`
**Status**: `decay_edge_weights()` correctly calculates time-based graduated decay and identifies edges for removal, but doesn't persist changes.
**What's needed**:
1. Graph backend edge property update support
2. Graph backend edge deletion support
3. Transaction support for atomic batch operations

**Current behavior**: Returns `edges_decayed` and `edges_removed` counts of what *would* change. Logs `"Changes calculated but not persisted (requires edge property update support)"`.

### ⚠️ Edge Reinforcement — Placeholder

**File**: `operations/edge_weight_management.py` (`reinforce_edge`)
**Status**: Validates parameters and returns `True`, but doesn't query or update any edge data.
**What's needed**: Graph backend edge property query and update support.
**Current behavior**: Logs `"Edge would be reinforced by {amount} (not persisted)"` and returns `True`.

### ⚠️ Edge Pruning — No Actual Removal

**File**: `operations/edge_weight_management.py` (`prune_weak_connections`)
**Status**: Identifies weak connections and respects the `preserve_recent` flag, but doesn't remove edges.
**What's needed**: Graph backend edge deletion support.

### ⚠️ Graph Enrichment — Node Updates

**File**: `operations/enrich_thought_graph.py`
**Status**: Computes PageRank, centrality, and community IDs correctly, but the node update loop logs `"Would update node {id} with: {updates}"` instead of persisting.
**What's needed**: Graph engine support for node property updates (to write `pagerank_score`, `centrality_score`, `community_id`, `connection_count` back to nodes).

### ⚠️ cognify_and_memify_thoughts — Placeholder

**File**: `operations/memify_thoughts.py`
**Status**: Only calls `memify_thoughts()`. The cognify integration (processing raw data through the main cognify pipeline before memifying) is not wired up.
**What's needed**: Integration with cognee's main `cognify()` pipeline to process raw data into the graph before running memify enrichment.

## Backend Dependencies for Full Functionality

The following graph backend capabilities are required to complete the pending features:

| Capability | Status | Blocking |
|------------|--------|----------|
| Node creation | ✅ Working | — |
| Edge creation | ✅ Working | — |
| Node queries | ✅ Working | — |
| Edge queries | ✅ Working | — |
| Node property updates | ❌ Not available | Enrichment persistence, project matching |
| Edge property updates | ❌ Not available | Edge weight decay, reinforcement |
| Edge deletion | ❌ Not available | Edge pruning, weak connection removal |
| Batch operations | ❌ Not available | Performance for large graphs |
| Transaction support | ❌ Not available | Atomic multi-step operations |

## Planned Future Enhancements

These features are not yet started:

1. **LLM connection inference** — Use structured LLM output to discover non-obvious connections between thoughts
2. **Temporal pattern analysis** — Track how thinking evolves over time, identify recurring themes
3. **Energy-aware suggestions** — Recommend thoughts to work on based on current energy level
4. **Interactive visualization** — Web-based graph explorer for the thought network
5. **Voice capture** — Add thoughts via speech-to-text
6. **Cross-project links** — Connect thoughts to tasks and project management tools
7. **Collaborative graphs** — Share and merge thought networks between users
8. **Caching layer** — Performance optimization for large graphs (1,000+ thoughts)
9. **Pagination** — Cursor-based pagination for large result sets
10. **Event system** — Reactive graph updates when thoughts are added or modified
11. **Multi-modal enrichment** — Support for images, audio, and video content
12. **Collaborative filtering** — Learn from user interactions to improve connection suggestions

## Testing Status

| Component | Unit Tests | Integration Tests | Notes |
|-----------|------------|-------------------|-------|
| Models | ✅ 7 tests | — | Full coverage |
| Algorithms | ✅ 12 tests | — | Full coverage |
| Operations | ❌ None | ❌ None | Needs mock graph backend tests |

**Testing gaps**: No operation tests, no integration tests, no end-to-end workflow tests, no error handling tests. Recommended: input validation tests, mock graph backend tests, web enrichment API tests, edge decay calculation tests.

## Performance Characteristics

| Operation | Complexity | Recommended Limit |
|-----------|------------|-------------------|
| `add_thought()` | O(1) + O(n) for auto-connect | — |
| `discover_connections()` | O(n) for tag matching | — |
| `enrich_thought_graph()` | O(n²) for some algorithms | < 10,000 thoughts |
| `find_surprise_connections()` | O(e) where e = edges | — |
| `enrich_with_web_search()` | O(1) per thought | Rate-limited by Tavily API |
| `decay_edge_weights()` | O(e) | — |

- **Small graphs** (1–100 thoughts): All features fast
- **Medium graphs** (100–1,000): Enrichment takes seconds
- **Large graphs** (1,000–10,000): Consider caching
- **Very large** (10,000+): Pagination recommended (not yet implemented)

## Dependencies

- `cognee >= 0.5.2` — Core cognee infrastructure
- `networkx >= 3.0` — Graph algorithms
