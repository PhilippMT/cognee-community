# ADHD Thought Graph API

A standalone FastAPI application for managing ADHD-optimized thought graphs. Provides REST API endpoints with interactive Swagger UI for capturing thoughts, discovering connections, enriching with graph algorithms, and surfacing surprise insights.

## Overview

This experimental application wraps the `cognee-community-tasks-thought-graph` package in a standalone HTTP API, making the thought graph system accessible via REST endpoints. It's designed for:

- **Quick prototyping** — Test thought graph features via Swagger UI
- **Integration** — Connect to frontends, mobile apps, or other services
- **Exploration** — Interactively explore your thought network

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Application                  │
│                                                       │
│  ┌─────────┐  ┌──────────┐  ┌───────────────────┐   │
│  │ Swagger  │  │  DTOs    │  │    Endpoints      │   │
│  │   UI     │  │ (dtos.py)│  │    (app.py)       │   │
│  │  /docs   │  │          │  │                   │   │
│  └─────────┘  └──────────┘  └────────┬──────────┘   │
│                                       │               │
└───────────────────────────────────────┼───────────────┘
                                        │
                    ┌───────────────────┼───────────────┐
                    │  cognee-community-tasks-thought-graph │
                    │                                       │
                    │  ┌──────────┐  ┌──────────────┐      │
                    │  │  Models  │  │  Algorithms   │      │
                    │  │          │  │  (NetworkX)   │      │
                    │  └──────────┘  └──────────────┘      │
                    │  ┌──────────────────────────────┐    │
                    │  │        Operations             │    │
                    │  │  add_thought, discover,        │    │
                    │  │  enrich, surprise, memify...   │    │
                    │  └──────────────┬───────────────┘    │
                    └─────────────────┼────────────────────┘
                                      │
                    ┌─────────────────┼────────────────────┐
                    │           cognee core                  │
                    │  Graph DB │ Vector DB │ LLM Gateway    │
                    └───────────────────────────────────────┘
```

## Quick Start

### 1. Install dependencies

```bash
cd experimental/thought_graph_app
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.template .env
# Edit .env with your API keys
```

### 3. Start the server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open Swagger UI

Navigate to **http://localhost:8000/docs** to explore all endpoints interactively.

## API Endpoints

### Thoughts

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/thoughts` | Add a single thought |
| `POST` | `/thoughts/batch` | Add multiple thoughts |

### Connections

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/connections/discover` | Discover connections for a thought |
| `GET` | `/connections/surprise` | Find surprise connections |

### Enrichment

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/enrich` | Run graph algorithms (PageRank, centrality, communities) |
| `GET` | `/communities` | Get detected thought communities |

### Web Enrichment

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/enrich/web` | Enrich a thought with web search (Tavily) |
| `POST` | `/enrich/web/batch` | Batch web enrichment |

### Projects

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/projects/match` | Match thoughts to projects/repos |

### Edge Management

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/edges/decay` | Apply time-based weight decay |
| `POST` | `/edges/reinforce` | Strengthen a connection |
| `GET` | `/edges/potential` | Find potential new connections |

### Memify

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/memify` | Run integrated enrichment pipeline |

### Exploration

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/thoughts/{id}/neighbors` | Get neighboring thoughts |

## Example Workflow with curl

### Step 1: Add thoughts

```bash
# Add a single thought
curl -X POST http://localhost:8000/thoughts \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Build a knowledge graph for ADHD thought management",
    "tags": ["adhd", "productivity", "graphs"],
    "importance_score": 9,
    "energy_level": 8
  }'

# Add multiple thoughts
curl -X POST http://localhost:8000/thoughts/batch \
  -H "Content-Type: application/json" \
  -d '{
    "thoughts": [
      {"content": "ADHD brains think non-linearly", "tags": ["adhd", "neuroscience"]},
      {"content": "PageRank identifies important nodes", "tags": ["algorithms", "graphs"]},
      {"content": "Community detection reveals clusters", "tags": ["algorithms", "organization"]}
    ]
  }'
```

### Step 2: Enrich the graph

```bash
curl -X POST http://localhost:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "compute_pagerank": true,
    "compute_centrality": true,
    "detect_communities": true,
    "find_transitive": true
  }'
```

### Step 3: Explore communities

```bash
curl http://localhost:8000/communities
```

### Step 4: Find surprise connections

```bash
curl "http://localhost:8000/connections/surprise?min_surprise_score=0.4&max_results=10"
```

### Step 5: Run full memify

```bash
curl -X POST http://localhost:8000/memify \
  -H "Content-Type: application/json" \
  -d '{
    "enable_project_matching": true,
    "enable_edge_decay": true,
    "enable_potential_connections": true,
    "project_patterns": {
      "cognee": ["cognee", "knowledge graph", "memory"]
    }
  }'
```

### Step 6: Explore neighbors

```bash
# Replace <thought_id> with an actual UUID from step 1
curl "http://localhost:8000/thoughts/<thought_id>/neighbors?max_depth=2"
```

## ADHD Design Philosophy

This system is designed around how ADHD brains actually work:

1. **Capture first, organize later** — Add thoughts instantly without worrying about structure. The algorithms find patterns for you.

2. **Non-linear connections** — Unlike hierarchical note systems, the graph embraces associative thinking. Ideas connect in any direction.

3. **Working memory externalization** — Instead of holding multiple ideas in your head, externalize them. The graph maintains relationships automatically.

4. **Serendipitous discovery** — The surprise connection finder leverages ADHD strengths in pattern recognition by surfacing non-obvious relationships.

5. **Energy-aware capture** — Track your energy level when capturing thoughts to understand your productivity patterns over time.

6. **Reduced cognitive load** — Graph algorithms (PageRank, communities) do the heavy lifting of organization, so you don't have to.

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LLM_API_KEY` | Yes | OpenAI or other LLM provider API key |
| `LLM_MODEL` | No | LLM model (default: `openai/gpt-4o-mini`) |
| `TAVILY_API_KEY` | No | Required for `/enrich/web` endpoints |
| `HOST` | No | Server host (default: `0.0.0.0`) |
| `PORT` | No | Server port (default: `8000`) |
| `ENABLE_BACKEND_ACCESS_CONTROL` | No | Set to `false` for local dev |

## File Structure

```
thought_graph_app/
├── app.py              # FastAPI application with all endpoints
├── dtos.py             # Pydantic request/response models
├── .env.template       # Environment variable template
├── pyproject.toml      # Project metadata and dependencies
├── requirements.txt    # pip-installable dependencies
└── README.md           # This file
```

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Thought CRUD | ✅ | Add single and batch |
| Connection discovery | ⚠️ | Semantic + tag-based working; LLM inference stubbed |
| Graph enrichment | ⚠️ | Algorithms run; node property updates may not persist |
| Surprise connections | ✅ | Multi-dimensional scoring with explanations |
| Web enrichment | ⚠️ | Tavily search returns results; graph persistence pending |
| Project matching | ⚠️ | Analysis + confidence scores work; node updates pending |
| Edge decay | ⚠️ | Calculation works; graph persistence pending |
| Edge reinforce | ⚠️ | Placeholder — validates params, returns success, doesn't persist |
| Edge pruning | ⚠️ | Identifies weak edges; doesn't remove them |
| Potential connections | ✅ | Read-only analysis, fully functional |
| Memify pipeline | ✅ | Orchestration works; limited by individual operation status |
| Swagger UI | ✅ | Full interactive documentation at `/docs` |

## Open TODOs and Endpoint-Specific Limitations

### `POST /thoughts` and `POST /thoughts/batch`

✅ Fully working. Input validation raises 400 for empty content, out-of-range energy/importance, invalid similarity threshold.

**Known limitation**: Auto-connection discovery (`auto_connect=true`) uses semantic similarity and tag overlap only. LLM-based inference for non-obvious connections is stubbed and logs `"LLM-based connection discovery not yet implemented"`.

### `POST /connections/discover`

⚠️ Two of three discovery methods work:
- ✅ **Semantic similarity** — Vector embedding search
- ✅ **Tag overlap** — Shared tag analysis (≥30% overlap)
- ❌ **LLM inference** — Stubbed. The code path exists but skips with a log message. Needs: LLM structured output integration with a prompt template and response model.

### `GET /connections/surprise`

✅ Fully working. Scores connections on 4 dimensions (semantic, temporal, structural, domain distance).

**Known limitation**: Semantic distance uses a word-overlap heuristic (Jaccard similarity on split words) instead of actual vector embeddings. This is a simplified implementation noted in the code.

### `POST /enrich`

⚠️ All algorithms run correctly (PageRank, centrality, community detection, transitive connections), but **computed metrics are not persisted back to graph nodes**. The enrichment loop logs `"Would update node {id} with: {updates}"` instead of writing `pagerank_score`, `centrality_score`, `community_id`, and `connection_count` to the graph.

**What's needed**: Graph backend support for node property updates.

### `GET /communities`

✅ Fully working. Detects communities and returns summaries with top tags and average importance.

### `POST /enrich/web`

⚠️ Tavily API integration works — search results are retrieved and returned. However:
- ❌ No `WebResource` nodes are created in the graph
- ❌ No edges are created connecting web resources to thoughts
- ❌ No vector indexing of web content

The `connections_created` count in the response reflects how many results were found, not actual graph connections. The code logs `"Web resources logged but not persisted (requires WebResource data model)"`.

**What's needed**: A `WebResource` data model, graph node creation, edge creation, and vector indexing.

### `POST /enrich/web/batch`

⚠️ Same limitations as single web enrichment, applied to multiple thoughts sequentially.

### `POST /projects/match`

⚠️ Pattern matching and auto-detection (GitHub/GitLab URLs) work correctly. Confidence scores are calculated. However, `create_project_connections()` does not actually update the `related_projects` field on thought nodes — it logs `"Would update thought {id} with projects: {list}"`.

**What's needed**: Graph backend node property update support.

### `POST /edges/decay`

⚠️ Time-based graduated decay is calculated correctly (older edges decay faster, edges below threshold are identified for removal). However:
- ❌ Edge weights are not actually updated in the graph
- ❌ Weak edges are not actually removed

Returns accurate statistics of what *would* change. Logs `"Changes calculated but not persisted (requires edge property update support)"`.

**What's needed**: Graph backend edge property update and edge deletion support.

### `POST /edges/reinforce`

⚠️ **Placeholder only**. Validates parameters (returns 400 for invalid ranges) and returns `{"success": true}`, but does not query or modify any edge data. Logs `"Edge would be reinforced by {amount} (not persisted)"`.

**What's needed**: Graph backend edge property query and update support.

### `GET /edges/potential`

✅ Fully working. Analyzes community membership, tag similarity, project overlap, and common neighbors to suggest missing connections.

### `POST /memify`

✅ Orchestration works — runs all enabled phases (graph enrichment, web enrichment, project matching, edge decay, potential connections). Results are aggregated from all phases.

**Inherited limitations**: Each phase has the same limitations as its individual endpoint (web results not persisted, edge weights not updated, etc.).

**Additional note**: When `thought_ids` is `None` and `enable_web_enrichment` is `True`, web enrichment is skipped for all thoughts to avoid excessive API calls. Only specific thought IDs trigger web enrichment.

### `GET /thoughts/{id}/neighbors`

✅ Fully working. Supports depth-based traversal with relationship metadata.

## Backend Dependencies for Full Functionality

These graph backend capabilities are needed to resolve the pending features:

| Capability | Status | Endpoints Affected |
|------------|--------|--------------------|
| Node property updates | ❌ Not available | `/enrich`, `/projects/match` |
| Edge property updates | ❌ Not available | `/edges/decay`, `/edges/reinforce` |
| Edge deletion | ❌ Not available | `/edges/decay` (removal of weak edges) |
| WebResource data model | ❌ Not created | `/enrich/web`, `/enrich/web/batch` |
| Vector indexing for web content | ❌ Not available | `/enrich/web` |

## Planned Future Enhancements

1. **LLM connection inference** — Use structured LLM output in `/connections/discover` for non-obvious connections
2. **Vector-based semantic distance** — Replace word-overlap heuristic in surprise scoring with actual embedding distance
3. **WebResource persistence** — Create graph nodes and edges for web enrichment results
4. **Full edge weight persistence** — Persist decay, reinforcement, and pruning to the graph
5. **Temporal pattern analysis** — New endpoint to analyze how thinking evolves over time
6. **Energy-aware suggestions** — Recommend thoughts to work on based on current energy level
7. **Interactive visualization** — Serve an HTML graph explorer alongside the API
8. **Voice capture** — Speech-to-text endpoint for adding thoughts
9. **Pagination** — Cursor-based pagination for large result sets
10. **Caching** — Performance optimization for graphs with 1,000+ thoughts
11. **Authentication** — Optional API key or JWT authentication for multi-user deployments

## Related Packages

- [`cognee-community-tasks-thought-graph`](../../packages/task/thought_graph_tasks/) — Core models, algorithms, and operations (see its README for the full technical TODO list)
- [`cognee-community-pipeline-thought-graph`](../../packages/pipeline/thought_graph_pipeline/) — Pipeline orchestration for batch processing
