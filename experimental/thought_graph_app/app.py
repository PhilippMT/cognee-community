"""
ADHD Thought Graph API — Standalone FastAPI Application.

A REST API for managing ADHD-optimized thought graphs with automatic
connection discovery, graph enrichment, and surprise insights.

Run:
    uvicorn app:app --reload --host 0.0.0.0 --port 8000

Swagger UI:
    http://localhost:8000/docs
"""

import os
from contextlib import asynccontextmanager
from uuid import UUID

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from dtos import (
    AddThoughtRequest,
    BatchAddThoughtsRequest,
    BatchWebEnrichmentRequest,
    ConnectionResponse,
    DiscoverConnectionsRequest,
    EdgeDecayRequest,
    EnrichGraphRequest,
    MemifyRequest,
    ProjectMatchingRequest,
    ReinforceEdgeRequest,
    SurpriseConnectionResponse,
    ThoughtResponse,
    WebEnrichmentRequest,
)

load_dotenv()

os.environ.setdefault("ENABLE_BACKEND_ACCESS_CONTROL", "false")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize cognee database and default user on startup."""
    from cognee.infrastructure.databases.relational import get_relational_engine

    db_engine = get_relational_engine()
    await db_engine.create_database()

    from cognee.modules.users.methods import get_default_user

    await get_default_user()
    yield


app = FastAPI(
    title="ADHD Thought Graph API",
    version="0.1.0",
    description=(
        "REST API for managing ADHD-optimized thought graphs. "
        "Capture scattered thoughts, discover hidden connections, "
        "enrich with graph algorithms, and surface surprise insights."
    ),
    lifespan=lifespan,
    docs_url=None,
)


@app.get("/docs", include_in_schema=False)
async def scalar_docs():
    from scalar_fastapi import get_scalar_api_reference

    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ───────────────────────────────────────────────────────────────


@app.get("/", tags=["health"])
async def root():
    """Root endpoint."""
    return {"message": "ADHD Thought Graph API is running", "docs": "/docs"}


@app.get("/health", tags=["health"])
async def health():
    """Health check."""
    return {"status": "ok"}


# ── Thought Management ──────────────────────────────────────────────────


@app.post("/thoughts", response_model=ThoughtResponse, tags=["thoughts"])
async def add_thought(payload: AddThoughtRequest):
    """
    Add a new thought to the graph.

    Creates a thought node with optional auto-connection discovery.
    Optimized for ADHD quick-capture workflows.
    """
    from cognee_community_tasks_thought_graph.operations.add_thought import (
        add_thought as add_thought_op,
    )

    try:
        node = await add_thought_op(
            content=payload.content,
            title=payload.title,
            tags=payload.tags,
            context=payload.context,
            energy_level=payload.energy_level,
            related_projects=payload.related_projects,
            importance_score=payload.importance_score,
            auto_connect=payload.auto_connect,
            similarity_threshold=payload.similarity_threshold,
        )
        return ThoughtResponse(
            id=str(node.id),
            content=node.content,
            title=node.title,
            tags=node.tags,
            created_at=node.created_at,
            updated_at=node.updated_at,
            energy_level=node.energy_level,
            importance_score=node.importance_score,
            related_projects=node.related_projects,
            connection_count=node.connection_count,
            centrality_score=node.centrality_score,
            pagerank_score=node.pagerank_score,
            community_id=node.community_id,
        )
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/thoughts/batch", response_model=list[ThoughtResponse], tags=["thoughts"])
async def add_thoughts_batch(payload: BatchAddThoughtsRequest):
    """
    Add multiple thoughts in batch.

    Efficient for brainstorming sessions where many ideas need capturing at once.
    """
    from cognee_community_tasks_thought_graph.operations.add_thought import (
        add_thoughts_batch as batch_op,
    )

    try:
        nodes = await batch_op(
            [
                {
                    "content": t.content,
                    "title": t.title,
                    "tags": t.tags,
                    "context": t.context,
                    "energy_level": t.energy_level,
                    "related_projects": t.related_projects,
                    "importance_score": t.importance_score,
                }
                for t in payload.thoughts
            ],
            auto_connect=payload.thoughts[0].auto_connect if payload.thoughts else True,
        )
        return [
            ThoughtResponse(
                id=str(n.id),
                content=n.content,
                title=n.title,
                tags=n.tags,
                created_at=n.created_at,
                updated_at=n.updated_at,
                energy_level=n.energy_level,
                importance_score=n.importance_score,
                related_projects=n.related_projects,
            )
            for n in nodes
        ]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Connection Discovery ────────────────────────────────────────────────


@app.post("/connections/discover", response_model=list[ConnectionResponse], tags=["connections"])
async def discover_connections(payload: DiscoverConnectionsRequest):
    """
    Discover connections for a thought.

    Uses semantic similarity, tag overlap, and LLM inference to find
    related thoughts and create connections.
    """
    from cognee_community_tasks_thought_graph.operations.discover_connections import (
        discover_connections as discover_op,
    )

    try:
        connections = await discover_op(
            thought_id=UUID(payload.thought_id),
            similarity_threshold=payload.similarity_threshold,
            max_connections=payload.max_connections,
        )
        return [
            ConnectionResponse(
                source_id=str(c.source_id),
                target_id=str(c.target_id),
                relationship_type=c.relationship_type,
                strength=c.strength,
                discovery_method=c.discovery_method,
                explanation=c.explanation,
            )
            for c in connections
        ]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/connections/surprise", response_model=list[SurpriseConnectionResponse], tags=["connections"])
async def find_surprise_connections(
    min_surprise_score: float = 0.5,
    max_results: int = 20,
):
    """
    Find surprise connections in the thought graph.

    Surfaces unexpected relationships based on semantic distance,
    temporal distance, structural distance, and domain distance.
    Especially valuable for ADHD pattern recognition strengths.
    """
    from cognee_community_tasks_thought_graph.operations.find_surprise_connections import (
        find_surprise_connections as surprise_op,
    )

    try:
        surprises = await surprise_op(
            min_surprise_score=min_surprise_score,
            max_results=max_results,
            include_explanation=True,
        )
        return [
            SurpriseConnectionResponse(
                source_id=str(s.source_id),
                target_id=str(s.target_id),
                overall_score=s.overall_score,
                semantic_distance=s.semantic_distance,
                temporal_distance=s.temporal_distance,
                structural_distance=s.structural_distance,
                domain_distance=s.domain_distance,
                explanation=s.explanation,
                confidence=s.confidence,
            )
            for s in surprises
        ]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Graph Enrichment ────────────────────────────────────────────────────


@app.post("/enrich", tags=["enrichment"])
async def enrich_graph(payload: EnrichGraphRequest):
    """
    Enrich the thought graph with algorithms.

    Runs PageRank, centrality, community detection, and transitive
    connection discovery to surface insights about your thought network.
    """
    from cognee_community_tasks_thought_graph.operations.enrich_thought_graph import (
        enrich_thought_graph,
    )

    try:
        results = await enrich_thought_graph(
            compute_pagerank=payload.compute_pagerank,
            compute_centrality=payload.compute_centrality,
            detect_communities_flag=payload.detect_communities,
            find_transitive=payload.find_transitive,
            auto_add_transitive_links=payload.auto_add_transitive_links,
            transitive_strength_threshold=payload.transitive_strength_threshold,
        )
        return results
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/communities", tags=["enrichment"])
async def get_communities(algorithm: str = "greedy", include_summary: bool = True):
    """
    Get thought communities detected in the graph.

    Returns thematic clusters of related thoughts identified by
    community detection algorithms.
    """
    from cognee_community_tasks_thought_graph.operations.get_thought_communities import (
        get_thought_communities,
    )

    try:
        return await get_thought_communities(
            algorithm=algorithm,
            include_summary=include_summary,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Web Enrichment ──────────────────────────────────────────────────────


@app.post("/enrich/web", tags=["web-enrichment"])
async def enrich_with_web(payload: WebEnrichmentRequest):
    """
    Enrich a thought with web search results.

    Uses Tavily API to find relevant web content and link it to the thought.
    Requires TAVILY_API_KEY environment variable.
    """
    from cognee_community_tasks_thought_graph.operations.enrich_with_web import (
        enrich_with_web_search,
    )

    try:
        return await enrich_with_web_search(
            thought_id=UUID(payload.thought_id),
            max_results=payload.max_results,
            search_depth=payload.search_depth,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/enrich/web/batch", tags=["web-enrichment"])
async def batch_enrich_with_web(payload: BatchWebEnrichmentRequest):
    """
    Batch enrich multiple thoughts with web search.

    Efficiently performs web research for multiple thoughts at once.
    """
    from cognee_community_tasks_thought_graph.operations.enrich_with_web import (
        batch_enrich_with_web as batch_web_op,
    )

    try:
        return await batch_web_op(
            thought_ids=[UUID(tid) for tid in payload.thought_ids],
            max_results_per_thought=payload.max_results_per_thought,
            search_depth=payload.search_depth,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Project Matching ────────────────────────────────────────────────────


@app.post("/projects/match", tags=["projects"])
async def match_projects(payload: ProjectMatchingRequest):
    """
    Match thoughts to projects and repositories.

    Auto-detects GitHub/GitLab repository mentions and matches thoughts
    to custom project keyword patterns.
    """
    from cognee_community_tasks_thought_graph.operations.match_projects import (
        match_to_projects,
    )

    try:
        result = await match_to_projects(
            auto_detect=payload.auto_detect,
            project_patterns=payload.project_patterns,
        )
        # Convert sets to lists for JSON serialization
        result["projects_found"] = list(result.get("projects_found", set()))
        result["matches"] = [
            {"thought_id": str(m[0]), "project": m[1], "confidence": m[2]}
            for m in result.get("matches", [])
        ]
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Edge Weight Management ──────────────────────────────────────────────


@app.post("/edges/decay", tags=["edges"])
async def decay_edges(payload: EdgeDecayRequest):
    """
    Apply time-based decay to edge weights.

    Older connections gradually weaken and are removed when weight
    drops below the minimum threshold. Helps the graph evolve.
    """
    from cognee_community_tasks_thought_graph.operations.edge_weight_management import (
        decay_edge_weights,
    )

    try:
        return await decay_edge_weights(
            decay_rate=payload.decay_rate,
            min_weight=payload.min_weight,
            time_based=payload.time_based,
            days_threshold=payload.days_threshold,
        )
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/edges/reinforce", tags=["edges"])
async def reinforce_edge(payload: ReinforceEdgeRequest):
    """
    Reinforce a specific edge by increasing its weight.

    Strengthens important connections to prevent them from being pruned.
    """
    from cognee_community_tasks_thought_graph.operations.edge_weight_management import (
        reinforce_edge as reinforce_op,
    )

    try:
        success = await reinforce_op(
            source_id=UUID(payload.source_id),
            target_id=UUID(payload.target_id),
            reinforcement_amount=payload.reinforcement_amount,
        )
        return {"success": success}
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/edges/potential", tags=["edges"])
async def get_potential_connections(
    thought_id: str,
    min_potential_weight: float = 0.3,
    max_results: int = 10,
):
    """
    Calculate potential connections for a thought.

    Discovers missing links based on shared communities, common neighbors,
    tag similarity, and project overlap.
    """
    from cognee_community_tasks_thought_graph.operations.edge_weight_management import (
        calculate_potential_connections,
    )

    try:
        potentials = await calculate_potential_connections(
            thought_id=UUID(thought_id),
            min_potential_weight=min_potential_weight,
            max_results=max_results,
        )
        return [
            {"target_id": str(p[0]), "potential_weight": p[1], "reason": p[2]}
            for p in potentials
        ]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Integrated Memify ───────────────────────────────────────────────────


@app.post("/memify", tags=["memify"])
async def memify(payload: MemifyRequest):
    """
    Integrated memify operation for comprehensive enrichment.

    Runs all enrichment phases: graph algorithms, web search,
    project matching, edge decay, and potential connection discovery.
    """
    from cognee_community_tasks_thought_graph.operations.memify_thoughts import (
        memify_thoughts,
    )

    try:
        thought_uuids = [UUID(tid) for tid in payload.thought_ids] if payload.thought_ids else None
        return await memify_thoughts(
            thought_ids=thought_uuids,
            enable_web_enrichment=payload.enable_web_enrichment,
            enable_project_matching=payload.enable_project_matching,
            enable_edge_decay=payload.enable_edge_decay,
            enable_potential_connections=payload.enable_potential_connections,
            web_search_depth=payload.web_search_depth,
            max_web_results=payload.max_web_results,
            decay_rate=payload.decay_rate,
            min_edge_weight=payload.min_edge_weight,
            project_patterns=payload.project_patterns,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Graph Exploration ───────────────────────────────────────────────────


@app.get("/thoughts/{thought_id}/neighbors", tags=["exploration"])
async def get_neighbors(thought_id: str, max_depth: int = 1):
    """
    Get neighboring thoughts for a specific thought.

    Returns thoughts connected up to max_depth hops away.
    """
    from cognee_community_tasks_thought_graph.operations.get_thought_neighbors import (
        get_thought_neighbors,
    )

    try:
        return await get_thought_neighbors(
            thought_id=UUID(thought_id),
            max_depth=max_depth,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Graph Visualization ─────────────────────────────────────────────────


@app.get("/visualize", response_class=HTMLResponse, tags=["visualization"])
async def visualize():
    """
    Generate an interactive HTML visualization of the thought graph.

    Returns a self-contained HTML page with the full knowledge graph
    rendered as an interactive network diagram.
    """
    from cognee.api.v1.visualize import visualize_graph

    try:
        html = await visualize_graph()
        return HTMLResponse(html)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ── Entry Point ─────────────────────────────────────────────────────────


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
