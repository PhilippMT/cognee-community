"""
ADHD Thought Graph Pipeline.

Orchestrates the full thought graph workflow using cognee's Task/run_tasks
infrastructure. The pipeline processes raw thought data through these phases:

1. Batch-add thoughts to the graph with auto-connection discovery
2. Enrich the graph with algorithms (PageRank, centrality, communities)
3. Find surprise connections for serendipitous discovery
4. Optionally run the full memify enrichment (web, projects, edge decay)

Usage:
    async for status in run_thought_graph_pipeline(thoughts_data):
        print(status)
"""

from typing import Any, Dict, List

from cognee.modules.data.methods import create_authorized_dataset
from cognee.modules.pipelines import run_tasks
from cognee.modules.pipelines.tasks.task import Task
from cognee.modules.users.methods import get_default_user
from cognee.modules.users.models import User
from cognee.shared.logging_utils import get_logger
from cognee_community_tasks_thought_graph.operations.add_thought import add_thoughts_batch
from cognee_community_tasks_thought_graph.operations.enrich_thought_graph import (
    enrich_thought_graph,
)
from cognee_community_tasks_thought_graph.operations.find_surprise_connections import (
    find_surprise_connections,
)
from cognee_community_tasks_thought_graph.operations.memify_thoughts import memify_thoughts

logger = get_logger("thought_graph_pipeline")


async def _add_thoughts_task(thoughts_data: List[Dict[str, Any]], auto_connect: bool = True):
    """Task wrapper: add thoughts in batch and yield the created nodes."""
    thoughts = await add_thoughts_batch(thoughts_data, auto_connect=auto_connect)
    logger.info(f"Added {len(thoughts)} thoughts to graph")
    yield thoughts


async def _enrich_graph_task(thoughts, **kwargs):
    """Task wrapper: enrich the thought graph with algorithms."""
    results = await enrich_thought_graph(
        compute_pagerank=True,
        compute_centrality=True,
        detect_communities_flag=True,
        find_transitive=True,
        auto_add_transitive_links=True,
    )
    logger.info(f"Enrichment complete: {results.get('nodes_enriched', 0)} nodes")
    yield results


async def _find_surprises_task(enrichment_results, **kwargs):
    """Task wrapper: find surprise connections."""
    surprises = await find_surprise_connections(
        min_surprise_score=0.4,
        max_results=20,
        include_explanation=True,
    )
    logger.info(f"Found {len(surprises)} surprise connections")
    yield {"enrichment": enrichment_results, "surprises": surprises}


async def _memify_task(previous_results, **kwargs):
    """Task wrapper: run the full memify enrichment pipeline."""
    results = await memify_thoughts(
        enable_web_enrichment=kwargs.get("enable_web_enrichment", False),
        enable_project_matching=kwargs.get("enable_project_matching", True),
        enable_edge_decay=kwargs.get("enable_edge_decay", True),
        enable_potential_connections=kwargs.get("enable_potential_connections", True),
        project_patterns=kwargs.get("project_patterns"),
    )
    logger.info("Memify enrichment complete")
    yield {"previous": previous_results, "memify": results}


async def run_thought_graph_pipeline(
    thoughts_data: List[Dict[str, Any]],
    auto_connect: bool = True,
    run_memify: bool = False,
    user: User = None,
    dataset_name: str = "thought_graph",
):
    """
    Run the full ADHD thought graph pipeline.

    Processes a list of thought dictionaries through capture, enrichment,
    and surprise discovery phases using cognee's pipeline infrastructure.

    Args:
        thoughts_data: List of dicts with keys: content, title, tags,
                       importance_score, energy_level, context, related_projects.
        auto_connect: Auto-discover connections when adding thoughts.
        run_memify: Run the full memify enrichment (web, projects, decay).
        user: Cognee User object. Uses default user if None.
        dataset_name: Name for the cognee dataset.

    Yields:
        Pipeline run status updates.

    Example:
        >>> thoughts = [
        ...     {"content": "Graph databases for ADHD", "tags": ["adhd", "graphs"]},
        ...     {"content": "Working memory limitations", "tags": ["adhd", "neuroscience"]},
        ... ]
        >>> async for status in run_thought_graph_pipeline(thoughts):
        ...     print(status)
    """
    if not user:
        from cognee.low_level import setup
        await setup()
        user = await get_default_user()

    tasks = [
        Task(_add_thoughts_task, auto_connect=auto_connect),
        Task(_enrich_graph_task),
        Task(_find_surprises_task),
    ]

    if run_memify:
        tasks.append(Task(_memify_task))

    dataset = await create_authorized_dataset(dataset_name, user)

    async for run_status in run_tasks(
        tasks,
        dataset.id,
        thoughts_data,
        user,
        "thought_graph_pipeline",
    ):
        yield run_status
