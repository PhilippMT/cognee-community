# Braindump Ingestion Workflow

## Overview

This document provides a detailed workflow for ingesting a "braindump" (collection of scattered thoughts) into the Thought Graph system, including visual descriptions of dataflow and the ontologies used.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Dataflow Architecture](#dataflow-architecture)
3. [Ontology Model](#ontology-model)
4. [Workflow Phases](#workflow-phases)
5. [Connection Discovery Pipeline](#connection-discovery-pipeline)
6. [Enrichment Pipeline](#enrichment-pipeline)
7. [Complete Example](#complete-example)

---

## Quick Start

```python
from cognee_community_tasks_thought_graph.operations import add_thoughts_batch, enrich_thought_graph

# 1. Capture braindump
braindump = [
    {"content": "Thought 1...", "tags": ["tag1"]},
    {"content": "Thought 2...", "tags": ["tag2"]},
    # ... more thoughts
]

thoughts = await add_thoughts_batch(braindump, auto_connect=True)

# 2. Enrich the graph
results = await enrich_thought_graph(
    compute_pagerank=True,
    detect_communities_flag=True,
    find_transitive=True
)
```

---

## Dataflow Architecture

### High-Level Dataflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BRAINDUMP INGESTION                          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: CAPTURE                                                   │
│  ┌───────────────┐                                                  │
│  │  Raw Thoughts │ ──────────────────────────────────────┐         │
│  │  (text, tags, │                                        │         │
│  │   metadata)   │                                        │         │
│  └───────────────┘                                        │         │
│         │                                                  │         │
│         ▼                                                  ▼         │
│  ┌─────────────────────────────────────┐   ┌──────────────────────┐│
│  │   ThoughtNode Creation              │   │  Vector Embedding    ││
│  │   - Assign UUID                     │   │  Generation          ││
│  │   - Add timestamps                  │   │  (for semantic       ││
│  │   - Validate fields                 │   │   search)            ││
│  └─────────────────────────────────────┘   └──────────────────────┘│
│         │                                            │               │
│         └────────────────┬───────────────────────────┘               │
│                          ▼                                           │
│         ┌─────────────────────────────────────────┐                 │
│         │  Graph Database Storage                 │                 │
│         │  (Kuzu/Neo4j/Neptune/Memgraph)          │                 │
│         └─────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: CONNECTION DISCOVERY                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  For Each ThoughtNode:                                        │  │
│  │                                                                │  │
│  │  Method 1: Semantic Similarity                                │  │
│  │  ┌────────────────┐        ┌────────────────┐                │  │
│  │  │ Vector Search  │───────▶│ Find Similar   │                │  │
│  │  │ (embeddings)   │        │ Thoughts       │                │  │
│  │  └────────────────┘        └────────────────┘                │  │
│  │                                     │                          │  │
│  │  Method 2: Tag Overlap                                        │  │
│  │  ┌────────────────┐        ┌────────────────┐                │  │
│  │  │ Compare Tags   │───────▶│ Find Shared    │                │  │
│  │  │                │        │ Categories     │                │  │
│  │  └────────────────┘        └────────────────┘                │  │
│  │                                     │                          │  │
│  │  Method 3: LLM Inference (Optional)                           │  │
│  │  ┌────────────────┐        ┌────────────────┐                │  │
│  │  │ LLM Analysis   │───────▶│ Non-obvious    │                │  │
│  │  │ (future)       │        │ Connections    │                │  │
│  │  └────────────────┘        └────────────────┘                │  │
│  │                                     │                          │  │
│  │                          ┌──────────▼──────────┐              │  │
│  │                          │  Create Connection  │              │  │
│  │                          │  Edges in Graph     │              │  │
│  │                          └─────────────────────┘              │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 3: GRAPH ENRICHMENT                                          │
│                                                                      │
│  Algorithm 1: PageRank                                              │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Input: Graph with nodes & edges                           │    │
│  │  Process: Iterative importance propagation                 │    │
│  │  Output: pagerank_score for each ThoughtNode              │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Algorithm 2: Centrality Measures                                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  - Betweenness: Bridge thoughts                            │    │
│  │  - Closeness: Central concepts                             │    │
│  │  - Degree: Highly connected                                │    │
│  │  - Eigenvector: Influential connections                    │    │
│  │  Output: centrality_score for each ThoughtNode            │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Algorithm 3: Community Detection                                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Process: Greedy modularity or label propagation          │    │
│  │  Output: community_id for each ThoughtNode                │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Algorithm 4: Transitive Connections                                │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Process: Find A→B→C paths                                 │    │
│  │  Output: New potential Connection edges                    │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Algorithm 5: Surprise Scoring                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Process: Calculate semantic, temporal, structural,        │    │
│  │           and domain distances                             │    │
│  │  Output: SurpriseScore for unexpected connections         │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 4: OUTPUT & VISUALIZATION                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Enriched Knowledge Graph                                    │  │
│  │  - Nodes with computed metrics                              │  │
│  │  - Edges with relationship types                            │  │
│  │  - Community structure                                       │  │
│  │  - Surprise connections identified                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Ontology Model

### Core Entities

```
┌─────────────────────────────────────────────────────────────────────┐
│                          THOUGHT GRAPH ONTOLOGY                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  ThoughtNode (extends DataPoint)                                     │
├──────────────────────────────────────────────────────────────────────┤
│  Core Properties:                                                    │
│    • id: UUID                         [Primary Key]                  │
│    • content: str                     [Required, main thought text]  │
│    • title: Optional[str]             [Short descriptor]             │
│                                                                       │
│  Categorization:                                                     │
│    • tags: List[str]                  [Topic/category labels]        │
│    • related_projects: List[str]      [Project associations]         │
│                                                                       │
│  Temporal Metadata:                                                  │
│    • created_at: datetime             [Capture timestamp]            │
│    • updated_at: datetime             [Last modification]            │
│    • context: Optional[str]           [Capture circumstances]        │
│                                                                       │
│  ADHD-Specific:                                                      │
│    • energy_level: Optional[int]      [1-10, energy at capture]      │
│    • importance_score: Optional[int]  [1-10, user priority]          │
│                                                                       │
│  Computed Metrics (from enrichment):                                 │
│    • connection_count: int            [Number of edges]              │
│    • pagerank_score: Optional[float]  [0.0-1.0, influence]           │
│    • centrality_score: Optional[float][0.0-1.0, bridging]            │
│    • community_id: Optional[str]      [Cluster assignment]           │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  Connection (Pydantic BaseModel)                                     │
├──────────────────────────────────────────────────────────────────────┤
│  Endpoint Identification:                                            │
│    • source_id: UUID                  [Origin thought]               │
│    • target_id: UUID                  [Destination thought]          │
│                                                                       │
│  Relationship Semantics:                                             │
│    • relationship_type: str           [e.g., "relates_to",           │
│                                        "inspired_by", "contradicts"] │
│    • strength: float                  [0.0-1.0, connection weight]   │
│    • bidirectional: bool              [Works both ways?]             │
│                                                                       │
│  Discovery Metadata:                                                 │
│    • discovery_method: str            [How found: "semantic",        │
│                                        "tag_overlap", "llm"]         │
│    • explanation: Optional[str]       [Why connected]                │
│    • created_at: datetime             [When discovered]              │
│                                                                       │
│  Path Information (for transitive):                                  │
│    • path_length: Optional[int]       [Hops in path]                 │
│    • intermediate_nodes: List[UUID]   [A→B→C: B is intermediate]     │
│                                                                       │
│  Quality Metrics:                                                    │
│    • surprise_score: Optional[float]  [0.0-1.0, unexpectedness]      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  SurpriseScore (Pydantic BaseModel)                                  │
├──────────────────────────────────────────────────────────────────────┤
│  Connection Identification:                                          │
│    • source_id: UUID                                                 │
│    • target_id: UUID                                                 │
│                                                                       │
│  Distance Metrics:                                                   │
│    • semantic_distance: float         [0.0-1.0, content diff]        │
│    • temporal_distance: float         [0.0-1.0, time separation]     │
│    • structural_distance: float       [0.0-1.0, graph distance]      │
│    • domain_distance: float           [0.0-1.0, tag dissimilarity]   │
│                                                                       │
│  Aggregate Measures:                                                 │
│    • overall_score: float             [Weighted combination]         │
│    • confidence: float                [0.0-1.0, score reliability]   │
│    • explanation: Optional[str]       [Human-readable why]           │
└──────────────────────────────────────────────────────────────────────┘
```

### Relationship Types

```
ThoughtNode ──[relates_to]──────────▶ ThoughtNode
            │                          
            ├─[inspired_by]──────────▶ ThoughtNode
            │
            ├─[contradicts]───────────▶ ThoughtNode
            │
            ├─[builds_on]─────────────▶ ThoughtNode
            │
            ├─[semantically_related]──▶ ThoughtNode
            │
            ├─[shares_tags]───────────▶ ThoughtNode
            │
            └─[transitive_connection]─▶ ThoughtNode
```

---

## Workflow Phases

### Phase 1: Rapid Capture

**Goal**: Capture thoughts with minimal friction

```python
from cognee_community_tasks_thought_graph.operations import add_thought

# Single thought capture
thought = await add_thought(
    content="Graph databases are perfect for non-hierarchical relationships",
    title="Graph DB Benefits",           # Optional
    tags=["database", "technology"],     # Optional
    context="While researching PKM",     # Optional
    energy_level=7,                      # Optional, 1-10
    importance_score=8,                  # Optional, 1-10
    related_projects=["cognee"],         # Optional
    auto_connect=True                    # Enable automatic connection discovery
)
```

**Data Flow**:
```
User Input (text + metadata)
    │
    ▼
ThoughtNode Object Creation
    ├─▶ Generate UUID
    ├─▶ Add timestamps (created_at, updated_at)
    ├─▶ Validate fields (energy_level 1-10, etc.)
    └─▶ Set defaults (connection_count=0, etc.)
    │
    ▼
Store in Graph Database
    ├─▶ Add node to graph (Kuzu/Neo4j/etc.)
    └─▶ Generate vector embedding (for semantic search)
    │
    ▼
[If auto_connect=True]
Trigger Connection Discovery
```

**Batch Capture**:
```python
from cognee_community_tasks_thought_graph.operations import add_thoughts_batch

braindump = [
    {"content": "Thought 1...", "tags": ["adhd", "productivity"]},
    {"content": "Thought 2...", "tags": ["technology", "graphs"]},
    {"content": "Thought 3...", "tags": ["creativity", "innovation"]},
    # ... more thoughts
]

thoughts = await add_thoughts_batch(braindump, auto_connect=True)
# Returns: List[ThoughtNode]
```

### Phase 2: Connection Discovery

**Goal**: Automatically find relationships between thoughts

```
For each new ThoughtNode:
┌─────────────────────────────────────────────────────────────────┐
│ 1. SEMANTIC SIMILARITY (Vector Search)                         │
├─────────────────────────────────────────────────────────────────┤
│   Query: thought.content (embedded as vector)                   │
│   Search: Vector database (LanceDB/Qdrant/etc.)                │
│   Filter: similarity_score >= threshold (default 0.7)          │
│   Result: List of semantically similar ThoughtNodes            │
│                                                                  │
│   For each similar thought:                                     │
│     Create Connection(                                          │
│       source_id=new_thought.id,                                │
│       target_id=similar_thought.id,                            │
│       relationship_type="semantically_related",                │
│       strength=similarity_score,                               │
│       discovery_method="semantic_similarity"                   │
│     )                                                           │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. TAG OVERLAP (Category Matching)                             │
├─────────────────────────────────────────────────────────────────┤
│   Compare: new_thought.tags with existing_thought.tags         │
│   Calculate: overlap_ratio = |intersection| / |union|          │
│   Filter: overlap_ratio >= 0.3 (30% shared tags)              │
│   Result: List of ThoughtNodes with shared categories          │
│                                                                  │
│   For each matching thought:                                    │
│     Create Connection(                                          │
│       relationship_type="shares_tags",                         │
│       strength=overlap_ratio,                                  │
│       discovery_method="tag_overlap",                          │
│       explanation=f"Shared tags: {common_tags}"                │
│     )                                                           │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. LLM INFERENCE (Future Enhancement)                          │
├─────────────────────────────────────────────────────────────────┤
│   Analyze: new_thought + candidate_thoughts                    │
│   Prompt: "Find non-obvious connections..."                    │
│   Process: LLM reasoning about relationships                   │
│   Result: Non-obvious connections with explanations            │
│                                                                  │
│   For each LLM-identified connection:                           │
│     Create Connection(                                          │
│       relationship_type=llm_suggested_type,                    │
│       discovery_method="llm_inference",                        │
│       explanation=llm_explanation                              │
│     )                                                           │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. STORE CONNECTIONS                                            │
├─────────────────────────────────────────────────────────────────┤
│   Deduplicate: Remove duplicate source-target pairs            │
│   Sort: By strength (descending)                               │
│   Limit: Keep top N connections (default max_connections=10)   │
│   Store: Add edges to graph database                           │
│   Update: Increment connection_count on both nodes             │
└─────────────────────────────────────────────────────────────────┘
```

**Code Example**:
```python
from cognee_community_tasks_thought_graph.operations import discover_connections

connections = await discover_connections(
    thought_id=new_thought.id,
    similarity_threshold=0.7,    # Min semantic similarity
    max_connections=10,          # Limit connections
    use_llm=False                # LLM inference (future)
)
# Returns: List[Connection]
```

### Phase 3: Graph Enrichment

**Goal**: Compute metrics and find hidden patterns

```python
from cognee_community_tasks_thought_graph.operations import enrich_thought_graph

results = await enrich_thought_graph(
    compute_pagerank=True,           # Influential thoughts
    compute_centrality=True,         # Bridge thoughts
    detect_communities_flag=True,    # Thematic clusters
    find_transitive=True,            # Hidden connections
    auto_add_transitive_links=True,  # Add strong indirect links
    transitive_strength_threshold=0.3
)
```

**Enrichment Algorithms**:

#### 1. PageRank
```
Purpose: Identify influential/foundational thoughts
Algorithm: Iterative importance propagation
Input: Graph G(V, E) with nodes and edges
Process:
  1. Initialize: PR(node) = 1/N for all nodes
  2. Iterate until convergence:
     PR(node) = (1-d)/N + d × Σ(PR(neighbor) / outdegree(neighbor))
     where d = damping factor (0.85)
  3. Normalize scores to 0.0-1.0 range
Output: pagerank_score for each ThoughtNode
Usage: "Which thoughts are most central to my thinking?"
```

#### 2. Centrality Measures
```
Betweenness Centrality:
  Purpose: Find bridge thoughts connecting different topics
  Process: Count shortest paths passing through each node
  Output: centrality_score (0.0-1.0)
  Usage: "Which thoughts connect different idea clusters?"

Closeness Centrality:
  Purpose: Find centrally located concepts
  Process: Calculate average distance to all other nodes
  Output: Normalized closeness score
  Usage: "Which thoughts are conceptually central?"

Degree Centrality:
  Purpose: Find highly connected hub thoughts
  Process: Count direct connections (edges)
  Output: Normalized degree
  Usage: "Which thoughts have the most connections?"

Eigenvector Centrality:
  Purpose: Find thoughts connected to other important thoughts
  Process: Recursive importance based on neighbor importance
  Output: Eigenvector score
  Usage: "Which thoughts are connected to influential ideas?"
```

#### 3. Community Detection
```
Purpose: Organize thoughts into thematic clusters
Algorithms:
  • Greedy Modularity: Fast, good quality clustering
  • Label Propagation: Very fast for large graphs

Process:
  1. Start with each node in its own community
  2. Iteratively merge communities to maximize modularity
  3. Modularity = fraction of edges within communities
     minus expected fraction in random graph
  4. Stop when no improvement possible

Output: community_id assigned to each ThoughtNode
Example: "community_0", "community_1", etc.

Usage: "How do my scattered thoughts naturally group together?"
```

#### 4. Transitive Connection Discovery
```
Purpose: Find indirect relationships (A→B→C implies A→C)

Process:
  For each pair of nodes (source, target):
    1. Check if direct edge exists → skip if yes
    2. Find shortest path with length 2-3 hops
    3. Calculate combined strength along path:
       path_strength = Π(edge.strength for edge in path)
    4. If path_strength >= threshold:
       → Suggest as missing connection
  
Output: List of (source, target, hop_count, path)

Auto-add: If auto_add_transitive_links=True:
  • Create new Connection edges for strong transitive links
  • Mark with relationship_type="transitive_connection"
  • Store path information in edge properties

Usage: "What hidden connections exist between my ideas?"
```

#### 5. Surprise Connection Discovery
```
Purpose: Find unexpected/serendipitous connections

Distance Metrics:
  1. Semantic Distance:
     • Calculate: 1 - cosine_similarity(embedding_A, embedding_B)
     • Range: 0.0 (identical) to 1.0 (completely different)
  
  2. Temporal Distance:
     • Calculate: min(days_apart / 30, 1.0)
     • Range: 0.0 (same day) to 1.0 (30+ days apart)
  
  3. Structural Distance:
     • Calculate: shortest_path_length / max_hops
     • Range: 0.0 (adjacent) to 1.0 (far apart in graph)
  
  4. Domain Distance:
     • Calculate: 1 - (|shared_tags| / |all_tags|)
     • Range: 0.0 (identical tags) to 1.0 (no shared tags)

Overall Surprise Score:
  surprise = 0.4×semantic + 0.2×temporal + 0.2×structural + 0.2×domain

Output: SurpriseScore objects for unexpected connections
Usage: "What surprising connections exist between distant ideas?"
```

**Enrichment Data Flow**:
```
Graph State (nodes + edges)
    │
    ├─▶ PageRank Algorithm ──▶ Update: pagerank_score
    │
    ├─▶ Centrality Algorithm ─▶ Update: centrality_score
    │
    ├─▶ Community Detection ──▶ Update: community_id
    │
    ├─▶ Transitive Discovery ─▶ Create: new Connection edges
    │
    └─▶ Surprise Calculation ─▶ Generate: SurpriseScore objects
    │
    ▼
Enriched Graph (nodes with computed metrics)
```

### Phase 4: Exploration & Analysis

**Community Analysis**:
```python
from cognee_community_tasks_thought_graph.operations import get_thought_communities

communities = await get_thought_communities(
    algorithm="greedy",      # or "label_propagation"
    include_summary=True
)

# Output structure:
{
    "communities": {
        "thought_id_1": "community_0",
        "thought_id_2": "community_0",
        "thought_id_3": "community_1",
        ...
    },
    "summaries": {
        "community_0": {
            "size": 5,
            "top_tags": ["adhd", "productivity", "tools"],
            "avg_importance": 7.8
        },
        "community_1": {
            "size": 3,
            "top_tags": ["technology", "graphs", "ai"],
            "avg_importance": 6.5
        }
    },
    "total_communities": 2
}
```

**Surprise Connections**:
```python
from cognee_community_tasks_thought_graph.operations import find_surprise_connections

surprises = await find_surprise_connections(
    min_surprise_score=0.5,
    max_results=20,
    include_explanation=True
)

# Each SurpriseScore contains:
# - overall_score: Combined surprise measure
# - semantic_distance: Content dissimilarity
# - temporal_distance: Time separation
# - structural_distance: Graph distance
# - domain_distance: Tag dissimilarity
# - explanation: Human-readable description
```

**Neighborhood Exploration**:
```python
from cognee_community_tasks_thought_graph.operations import get_thought_neighbors

neighbors = await get_thought_neighbors(
    thought_id=selected_thought.id,
    max_depth=2,                  # Get neighbors of neighbors
    include_relationship_info=True
)

# Output structure:
{
    "neighbors": [
        {"id": "...", "content": "...", "tags": [...]},
        ...
    ],
    "relationships": [
        {
            "source_id": "...",
            "target_id": "...",
            "relationship_type": "relates_to",
            "strength": 0.85
        },
        ...
    ],
    "depth_map": {
        "thought_id_1": 1,  # Direct neighbor
        "thought_id_2": 2,  # Neighbor of neighbor
        ...
    }
}
```

---

## Connection Discovery Pipeline

### Detailed Process Flow

```
INPUT: ThoughtNode (newly added)
│
├─▶ STEP 1: Extract Features
│   ├─ content: "Graph databases represent non-hierarchical relationships"
│   ├─ tags: ["database", "technology", "graphs"]
│   └─ Generate vector embedding: [0.12, -0.45, 0.89, ...]
│
├─▶ STEP 2: Semantic Search
│   Query Vector Database:
│   ┌────────────────────────────────────────────────────────┐
│   │ SELECT node_id, content, similarity_score              │
│   │ FROM vector_index                                       │
│   │ WHERE similarity(embedding, query_vector) >= 0.7       │
│   │ ORDER BY similarity DESC                               │
│   │ LIMIT 20                                               │
│   └────────────────────────────────────────────────────────┘
│   Results:
│   • Node A: similarity = 0.88 → CREATE CONNECTION
│   • Node B: similarity = 0.75 → CREATE CONNECTION
│   • Node C: similarity = 0.65 → SKIP (below threshold)
│
├─▶ STEP 3: Tag Overlap Analysis
│   Query Graph Database:
│   ┌────────────────────────────────────────────────────────┐
│   │ MATCH (n:ThoughtNode)                                  │
│   │ WHERE n.id != $new_thought_id                          │
│   │ RETURN n.id, n.tags                                    │
│   └────────────────────────────────────────────────────────┘
│   
│   For each existing thought:
│     overlap = |new_tags ∩ existing_tags| / |new_tags ∪ existing_tags|
│     
│   Example:
│     New: ["database", "technology", "graphs"]
│     Existing: ["graphs", "algorithms", "ai"]
│     Overlap: {"graphs"} → 1/5 = 0.20 → SKIP (< 0.3)
│     
│     New: ["database", "technology", "graphs"]
│     Existing: ["database", "graphs", "storage"]
│     Overlap: {"database", "graphs"} → 2/4 = 0.50 → CREATE CONNECTION
│
├─▶ STEP 4: LLM Inference (Optional, Future)
│   Prepare Context:
│   ┌────────────────────────────────────────────────────────┐
│   │ New Thought: "Graph databases represent non-hierarchi- │
│   │              cal relationships"                         │
│   │                                                         │
│   │ Candidates:                                             │
│   │ 1. "ADHD brains work differently - non-linear thinking"│
│   │ 2. "PageRank algorithm could identify important..."    │
│   │ 3. "Knowledge graph system for scattered thoughts"     │
│   └────────────────────────────────────────────────────────┘
│   
│   LLM Prompt:
│   "Analyze connections between the new thought and candidates.
│    Identify non-obvious relationships and explain why they connect."
│   
│   LLM Response:
│   • New ↔ Candidate 1: Both involve non-hierarchical organization
│   • New ↔ Candidate 3: Graph databases enable knowledge graph systems
│
└─▶ STEP 5: Deduplicate & Store
    Deduplicate by (source_id, target_id) pair
    Sort by strength (descending)
    Limit to max_connections (e.g., 10)
    
    Store in Graph Database:
    ┌────────────────────────────────────────────────────────┐
    │ CREATE (source:ThoughtNode {id: $source_id})           │
    │ CREATE (target:ThoughtNode {id: $target_id})           │
    │ CREATE (source)-[r:RELATES_TO {                        │
    │   relationship_type: $type,                            │
    │   strength: $strength,                                 │
    │   discovery_method: $method,                           │
    │   created_at: $timestamp                               │
    │ }]->(target)                                           │
    └────────────────────────────────────────────────────────┘
    
    Update Node Metrics:
    • source.connection_count += 1
    • target.connection_count += 1

OUTPUT: List[Connection]
```

---

## Enrichment Pipeline

### Complete Enrichment Workflow

```
┌───────────────────────────────────────────────────────────────────┐
│                    ENRICHMENT PIPELINE START                      │
└───────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 1: Fetch Graph Data                                         │
├───────────────────────────────────────────────────────────────────┤
│ Query: get_graph_data()                                           │
│ Returns:                                                          │
│   • nodes: List[(node_id, properties)]                           │
│   • edges: List[(source_id, target_id, rel_type, properties)]   │
└───────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 2: Build NetworkX Graph                                     │
├───────────────────────────────────────────────────────────────────┤
│ G = nx.Graph() or nx.DiGraph()                                   │
│ For each node: G.add_node(id, **properties)                      │
│ For each edge: G.add_edge(src, tgt, weight=strength)            │
└───────────────────────────────────────────────────────────────────┘
                            │
                            ├─────────────────┬─────────────────┬─────────────────┐
                            ▼                 ▼                 ▼                 ▼
    ┌────────────────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
    │ PAGERANK                   │ │ CENTRALITY       │ │ COMMUNITY        │ │ TRANSITIVE       │
    │ COMPUTATION                │ │ COMPUTATION      │ │ DETECTION        │ │ DISCOVERY        │
    ├────────────────────────────┤ ├──────────────────┤ ├──────────────────┤ ├──────────────────┤
    │ Algorithm:                 │ │ Algorithms:      │ │ Algorithms:      │ │ Algorithm:       │
    │ • nx.pagerank()            │ │ • Betweenness    │ │ • Greedy modular.│ │ • Shortest paths │
    │                            │ │ • Closeness      │ │ • Label propag.  │ │ • Path analysis  │
    │ Parameters:                │ │ • Degree         │ │                  │ │                  │
    │ • alpha=0.85               │ │ • Eigenvector    │ │ Parameters:      │ │ Parameters:      │
    │ • max_iter=100             │ │                  │ │ • resolution=1.0 │ │ • max_hops=3     │
    │ • weight='weight'          │ │ Weight: edge     │ │                  │ │ • min_strength   │
    │                            │ │ strength         │ │                  │ │   =0.1           │
    │ Output:                    │ │                  │ │ Output:          │ │                  │
    │ {node_id: score}           │ │ Output:          │ │ {node_id:        │ │ Output:          │
    │                            │ │ {node_id: score} │ │  community_id}   │ │ List[(src, tgt,  │
    │ Update node:               │ │                  │ │                  │ │  hops, path)]    │
    │ pagerank_score             │ │ Update node:     │ │ Update node:     │ │                  │
    │                            │ │ centrality_score │ │ community_id     │ │ Create new edges │
    └────────────────────────────┘ └──────────────────┘ └──────────────────┘ └──────────────────┘
                            │                 │                 │                 │
                            └─────────────────┴─────────────────┴─────────────────┘
                                              │
                                              ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 3: Aggregate Results                                        │
├───────────────────────────────────────────────────────────────────┤
│ For each ThoughtNode:                                             │
│   • Collect computed metrics                                      │
│   • Count connections (connection_count)                          │
│   • Package updates                                               │
└───────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 4: Update Graph Database                                    │
├───────────────────────────────────────────────────────────────────┤
│ For each node with updates:                                       │
│   MATCH (n:ThoughtNode {id: $node_id})                           │
│   SET n.pagerank_score = $pagerank                               │
│   SET n.centrality_score = $centrality                           │
│   SET n.community_id = $community                                │
│   SET n.connection_count = $count                                │
│                                                                   │
│ For new transitive connections:                                  │
│   CREATE (src)-[r:TRANSITIVE_CONNECTION {                        │
│     strength: $strength,                                         │
│     path_length: $hops,                                          │
│     intermediate_nodes: $path                                    │
│   }]->(tgt)                                                      │
└───────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 5: Surprise Connection Analysis                             │
├───────────────────────────────────────────────────────────────────┤
│ For each transitive connection (A→B→C):                          │
│                                                                   │
│   Calculate Distances:                                           │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ semantic_distance = 1 - cosine_similarity(embed_A, C)   │   │
│   │ temporal_distance = |created_A - created_C| / 30 days   │   │
│   │ structural_distance = path_length / max_hops            │   │
│   │ domain_distance = 1 - |tags_A ∩ tags_C| / |tags_A ∪ C| │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│   Compute Overall Surprise:                                      │
│   surprise = 0.4×semantic + 0.2×temporal +                      │
│              0.2×structural + 0.2×domain                         │
│                                                                   │
│   If surprise >= min_surprise_score:                             │
│     Create SurpriseScore object                                  │
│     Generate explanation                                         │
└───────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                    ENRICHMENT PIPELINE END                        │
├───────────────────────────────────────────────────────────────────┤
│ Returns:                                                          │
│   {                                                               │
│     "nodes_enriched": count,                                      │
│     "pagerank_computed": bool,                                    │
│     "centrality_computed": bool,                                  │
│     "communities_detected": count,                                │
│     "transitive_found": count,                                    │
│     "transitive_added": count                                     │
│   }                                                               │
└───────────────────────────────────────────────────────────────────┘
```

---

## Complete Example

### Full Braindump Workflow

```python
"""
Complete workflow for ingesting and enriching a braindump.
Demonstrates all phases with detailed output.
"""

import asyncio
from cognee_community_tasks_thought_graph.operations import (
    add_thoughts_batch,
    enrich_thought_graph,
    find_surprise_connections,
    get_thought_communities
)

async def process_braindump():
    # ═══════════════════════════════════════════════════════════════
    # PHASE 1: CAPTURE - Rapid braindump ingestion
    # ═══════════════════════════════════════════════════════════════
    
    print("Phase 1: Capturing braindump...")
    
    braindump = [
        {
            "content": "ADHD brains excel at making creative connections between disparate ideas",
            "title": "ADHD Creative Strength",
            "tags": ["adhd", "creativity", "neuroscience"],
            "importance_score": 9,
            "energy_level": 8
        },
        {
            "content": "Graph databases like Neo4j and Kuzu are perfect for non-hierarchical data",
            "title": "Graph DB Benefits",
            "tags": ["database", "technology", "graphs"],
            "importance_score": 7
        },
        {
            "content": "Need a system that captures thoughts instantly without breaking flow",
            "title": "Quick Capture Need",
            "tags": ["productivity", "adhd", "tools"],
            "importance_score": 8,
            "context": "Driving to work, idea popped up"
        },
        {
            "content": "PageRank algorithm identifies important nodes in a network",
            "title": "PageRank Algorithm",
            "tags": ["algorithms", "graphs", "ai"],
            "importance_score": 6
        },
        {
            "content": "Community detection reveals natural groupings in data",
            "title": "Community Detection",
            "tags": ["algorithms", "clustering", "patterns"],
            "importance_score": 6
        },
        {
            "content": "Obsidian and Roam use bidirectional links but lack automatic discovery",
            "title": "PKM Tool Limitations",
            "tags": ["tools", "productivity", "notes"],
            "importance_score": 7
        },
        {
            "content": "Working memory challenges make external systems crucial for ADHD",
            "title": "External Memory Need",
            "tags": ["adhd", "neuroscience", "productivity"],
            "importance_score": 9
        },
        {
            "content": "Serendipitous connections often lead to the best insights",
            "title": "Value of Serendipity",
            "tags": ["creativity", "innovation", "discovery"],
            "importance_score": 8
        }
    ]
    
    # Batch capture with auto-connection
    thoughts = await add_thoughts_batch(braindump, auto_connect=True)
    
    print(f"✓ Captured {len(thoughts)} thoughts")
    print(f"✓ Auto-discovered initial connections via semantic similarity")
    print()
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 2: ENRICHMENT - Run graph algorithms
    # ═══════════════════════════════════════════════════════════════
    
    print("Phase 2: Enriching graph with algorithms...")
    
    results = await enrich_thought_graph(
        compute_pagerank=True,           # Find influential thoughts
        compute_centrality=True,         # Find bridge thoughts
        detect_communities_flag=True,    # Find thematic clusters
        find_transitive=True,            # Find hidden connections
        auto_add_transitive_links=True,  # Add strong indirect links
        transitive_strength_threshold=0.3
    )
    
    print(f"✓ Enriched {results['nodes_enriched']} nodes")
    print(f"✓ PageRank computed: {results['pagerank_computed']}")
    print(f"✓ Centrality computed: {results['centrality_computed']}")
    print(f"✓ Communities detected: {results['communities_detected']}")
    print(f"✓ Transitive connections found: {results['transitive_found']}")
    print(f"✓ Transitive connections added: {results['transitive_added']}")
    print()
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 3: ANALYSIS - Explore the enriched graph
    # ═══════════════════════════════════════════════════════════════
    
    print("Phase 3: Analyzing enriched graph...")
    
    # Get community structure
    communities = await get_thought_communities(include_summary=True)
    
    print(f"\nCommunities ({communities['total_communities']} found):")
    for community_id, summary in communities['summaries'].items():
        print(f"  {community_id}:")
        print(f"    Size: {summary['size']} thoughts")
        print(f"    Topics: {', '.join(summary['top_tags'])}")
        if summary['avg_importance']:
            print(f"    Avg importance: {summary['avg_importance']:.1f}/10")
    print()
    
    # Find surprise connections
    surprises = await find_surprise_connections(
        min_surprise_score=0.5,
        max_results=10,
        include_explanation=True
    )
    
    print(f"\nSurprise Connections ({len(surprises)} found):")
    for i, surprise in enumerate(surprises[:5], 1):
        print(f"\n  {i}. {surprise.explanation}")
        print(f"     Overall surprise: {surprise.overall_score:.2f}")
        print(f"     Semantic distance: {surprise.semantic_distance:.2f}")
        print(f"     Temporal distance: {surprise.temporal_distance:.2f}")
        print(f"     Domain distance: {surprise.domain_distance:.2f}")
    print()
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 4: INSIGHTS - Summarize findings
    # ═══════════════════════════════════════════════════════════════
    
    print("Phase 4: Key Insights")
    print("=" * 70)
    print()
    print("Your braindump has been transformed into a knowledge graph with:")
    print(f"  • {len(thoughts)} thought nodes with computed metrics")
    print(f"  • Automatic semantic connections discovered")
    print(f"  • {results['communities_detected']} thematic communities identified")
    print(f"  • {results['transitive_found']} hidden connections revealed")
    print(f"  • {len(surprises)} surprising connections for creative insights")
    print()
    print("Next steps:")
    print("  1. Review high PageRank thoughts (most influential)")
    print("  2. Explore bridge thoughts (high centrality)")
    print("  3. Develop isolated thoughts (low connection count)")
    print("  4. Follow surprise connections for new ideas")
    print()

if __name__ == "__main__":
    asyncio.run(process_braindump())
```

### Expected Output

```
Phase 1: Capturing braindump...
✓ Captured 8 thoughts
✓ Auto-discovered initial connections via semantic similarity

Phase 2: Enriching graph with algorithms...
✓ Enriched 8 nodes
✓ PageRank computed: True
✓ Centrality computed: True
✓ Communities detected: 3
✓ Transitive connections found: 12
✓ Transitive connections added: 5

Phase 3: Analyzing enriched graph...

Communities (3 found):
  community_0:
    Size: 3 thoughts
    Topics: adhd, neuroscience, productivity
    Avg importance: 8.7/10
  community_1:
    Size: 3 thoughts
    Topics: database, technology, graphs, algorithms
    Avg importance: 6.3/10
  community_2:
    Size: 2 thoughts
    Topics: creativity, innovation, tools
    Avg importance: 7.5/10

Surprise Connections (5 found):

  1. Unexpected connection between 'ADHD Creative Strength' and 'Graph 
     DB Benefits' - surprising because they have very different topics 
     and completely different categories.
     Overall surprise: 0.72
     Semantic distance: 0.85
     Temporal distance: 0.00
     Domain distance: 1.00

  2. Unexpected connection between 'PageRank Algorithm' and 'External 
     Memory Need' - surprising because they have very different topics 
     and separated by 3 degrees in the graph.
     Overall surprise: 0.68
     Semantic distance: 0.78
     Temporal distance: 0.00
     Domain distance: 0.83

  ... (3 more)

Phase 4: Key Insights
======================================================================

Your braindump has been transformed into a knowledge graph with:
  • 8 thought nodes with computed metrics
  • Automatic semantic connections discovered
  • 3 thematic communities identified
  • 12 hidden connections revealed
  • 5 surprising connections for creative insights

Next steps:
  1. Review high PageRank thoughts (most influential)
  2. Explore bridge thoughts (high centrality)
  3. Develop isolated thoughts (low connection count)
  4. Follow surprise connections for new ideas
```

---

## Summary

This workflow documentation provides:

1. **Visual Dataflow**: Clear diagrams showing how data moves through the system
2. **Ontology Details**: Complete specification of ThoughtNode, Connection, and SurpriseScore
3. **Phase-by-Phase Guide**: Capture → Discovery → Enrichment → Analysis
4. **Algorithm Explanations**: How PageRank, centrality, communities, etc. work
5. **Complete Examples**: Working code demonstrating the full workflow

The system is optimized for ADHD braindump management by:
- **Low friction capture**: Minimal required fields
- **Automatic organization**: Algorithms find structure
- **Non-linear connections**: Embraces associative thinking
- **Serendipitous discovery**: Surfaces unexpected insights
- **External memory**: Offloads cognitive load to the system
