# Cognee Community Pipeline: Thought Graph

ADHD-optimized thought graph pipeline for [cognee](https://github.com/topoteretes/cognee). Orchestrates the full workflow from thought capture through enrichment to surprise discovery using cognee's `Task`/`run_tasks` infrastructure.

## Installation

```bash
pip install cognee-community-pipeline-thought-graph
```

This automatically installs `cognee-community-tasks-thought-graph` as a dependency.

## Pipeline Phases

The pipeline processes thought data through three sequential phases:

```
Input: List[Dict]  →  Phase 1: Batch Add  →  Phase 2: Enrich  →  Phase 3: Surprises
                       ├─ Create nodes       ├─ PageRank          ├─ Find transitive
                       └─ Auto-connect       ├─ Centrality        └─ Score surprise
                                             ├─ Communities
                                             └─ Transitive links
```

1. **Batch Add Thoughts** — Creates thought nodes in the graph with automatic connection discovery via semantic similarity and tag overlap.
2. **Enrich Graph** — Runs PageRank, centrality, community detection, and transitive connection algorithms to surface structural insights.
3. **Find Surprises** — Discovers unexpected connections based on semantic, temporal, structural, and domain distance.

## Usage

```python
import asyncio
from cognee_community_pipeline_thought_graph import run_thought_graph_pipeline

async def main():
    thoughts = [
        {
            "content": "Build a knowledge graph for ADHD thought management",
            "title": "Knowledge Graph System",
            "tags": ["adhd", "productivity", "ai"],
            "importance_score": 9,
            "energy_level": 8,
        },
        {
            "content": "ADHD brains think in non-linear, associative patterns",
            "tags": ["adhd", "neuroscience"],
            "importance_score": 8,
        },
        {
            "content": "PageRank could identify the most important thoughts",
            "tags": ["algorithms", "graphs"],
        },
    ]

    async for status in run_thought_graph_pipeline(thoughts):
        print(status)

asyncio.run(main())
```

## API Reference

### `run_thought_graph_pipeline()`

```python
async def run_thought_graph_pipeline(
    thoughts_data: List[Dict[str, Any]],
    auto_connect: bool = True,
    run_memify: bool = False,
    user: User = None,
    dataset_name: str = "thought_graph",
) -> AsyncGenerator:
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `thoughts_data` | `list[dict]` | required | List of thought dicts with `content`, `title`, `tags`, etc. |
| `auto_connect` | `bool` | `True` | Auto-discover connections when adding |
| `run_memify` | `bool` | `False` | Run full memify enrichment after pipeline |
| `user` | `User?` | `None` | Cognee user (uses default if None) |
| `dataset_name` | `str` | `"thought_graph"` | Name for the cognee dataset |

**Thought dict fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | `str` | Yes | The thought text |
| `title` | `str` | No | Short title |
| `tags` | `list[str]` | No | Categorization tags |
| `importance_score` | `int` | No | 1-10 importance |
| `energy_level` | `int` | No | 1-10 energy when captured |
| `context` | `str` | No | When/why the thought emerged |
| `related_projects` | `list[str]` | No | Associated projects |

## Running the Example

```bash
cd examples
python thought_graph_example.py
```

The example captures 10 sample thoughts, runs the full pipeline, and displays detected communities.

## Open TODOs and Known Limitations

### Pipeline-Level Limitations

1. **`run_memify` parameter is accepted but not wired** — The `run_memify=True` flag is defined in the function signature but the pipeline does not currently add a memify phase. To run memify, call `memify_thoughts()` separately after the pipeline completes.

2. **No incremental/delta processing** — The pipeline always processes the full `thoughts_data` list. There is no support for incremental loading (adding only new thoughts since the last run). The `run_tasks` call does not pass `incremental_loading=True`.

3. **No error recovery between phases** — If Phase 2 (enrich) fails, Phase 3 (surprises) is skipped entirely. There is no retry or partial-result handling between pipeline phases.

### Inherited from Task Package

The pipeline calls operations from `cognee-community-tasks-thought-graph` and inherits their limitations:

| Phase | Operation | Limitation |
|-------|-----------|------------|
| Phase 1: Batch Add | `add_thoughts_batch` → `discover_connections` | LLM-based connection inference is stubbed (only semantic + tag matching works) |
| Phase 2: Enrich | `enrich_thought_graph` | Computed metrics (PageRank, centrality, community_id) are calculated but node property updates may not persist depending on graph backend |
| Phase 3: Surprises | `find_surprise_connections` | Semantic distance uses word-overlap heuristic instead of vector embeddings |

### Planned Pipeline Enhancements

- **Memify phase integration** — Wire `run_memify=True` to add web enrichment, project matching, and edge decay as Phase 4
- **Incremental loading** — Support delta processing for adding only new thoughts
- **Progress callbacks** — Emit structured progress events during each phase
- **Configurable algorithm selection** — Allow callers to choose which enrichment algorithms to run
- **Parallel phase execution** — Run independent enrichment algorithms concurrently

See the [task package README](../../packages/task/thought_graph_tasks/README.md) for the full list of open TODOs and backend dependencies.

## Dependencies

- `cognee >= 0.5.2`
- `cognee-community-tasks-thought-graph >= 0.1.0`
