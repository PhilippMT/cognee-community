"""Enhanced memify operation for thought graphs with web enrichment and project matching."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from cognee.shared.logging_utils import get_logger

from .edge_weight_management import calculate_potential_connections, decay_edge_weights
from .enrich_thought_graph import enrich_thought_graph
from .enrich_with_web import batch_enrich_with_web
from .match_projects import create_project_connections, match_to_projects

logger = get_logger(__name__)


async def memify_thoughts(
    thought_ids: Optional[List[UUID]] = None,
    enable_web_enrichment: bool = True,
    enable_project_matching: bool = True,
    enable_edge_decay: bool = True,
    enable_potential_connections: bool = True,
    web_search_depth: str = "basic",
    max_web_results: int = 3,
    decay_rate: float = 0.1,
    min_edge_weight: float = 0.1,
    project_patterns: Optional[Dict[str, List[str]]] = None
) -> Dict[str, Any]:
    """
    Enhanced memify operation for thought graphs.

    Performs comprehensive enrichment including:
    1. Graph algorithm enrichment (PageRank, communities, etc.)
    2. Web search enrichment for each thought
    3. Project and repository matching
    4. Edge weight decay and pruning
    5. Potential connection discovery

    This is the main enrichment pipeline that should be run periodically
    (e.g., after adding new thoughts or daily/weekly).

    Args:
        thought_ids: Specific thoughts to enrich (None = all thoughts)
        enable_web_enrichment: Enrich with web search results
        enable_project_matching: Match thoughts to projects
        enable_edge_decay: Apply time-based edge weight decay
        enable_potential_connections: Calculate potential new connections
        web_search_depth: "basic" or "advanced" web search
        max_web_results: Max web results per thought
        decay_rate: Edge weight decay rate
        min_edge_weight: Minimum edge weight before removal
        project_patterns: Dictionary of project -> keywords for matching

    Returns:
        Dictionary with comprehensive enrichment results:
        - graph_enrichment: Results from graph algorithms
        - web_enrichment: Results from web search
        - project_matching: Results from project matching
        - edge_management: Results from edge decay
        - potential_connections: Number of potential connections found

    Example:
        >>> results = await memify_thoughts(
        ...     enable_web_enrichment=True,
        ...     enable_project_matching=True,
        ...     project_patterns={
        ...         "cognee": ["cognee", "knowledge graph", "ai"],
        ...         "backend": ["api", "server", "backend"]
        ...     }
        ... )
        >>> print(f"Graph enrichment: {results['graph_enrichment']}")
        >>> print(f"Web resources added: {results['web_enrichment']}")
        >>> print(f"Project matches: {results['project_matching']}")
    """
    logger.info("Starting enhanced memify operation for thought graph")

    results = {
        "graph_enrichment": {},
        "web_enrichment": {},
        "project_matching": {},
        "edge_management": {},
        "potential_connections": 0
    }

    try:
        # 1. Graph Algorithm Enrichment
        logger.info("Phase 1: Graph algorithm enrichment")
        graph_results = await enrich_thought_graph(
            compute_pagerank=True,
            compute_centrality=True,
            detect_communities_flag=True,
            find_transitive=True,
            auto_add_transitive_links=True
        )
        results["graph_enrichment"] = graph_results
        logger.info(f"Graph enrichment complete: {graph_results.get('nodes_enriched', 0)} nodes")

        # 2. Web Enrichment
        if enable_web_enrichment:
            logger.info("Phase 2: Web enrichment")

            if thought_ids:
                web_results = await batch_enrich_with_web(
                    thought_ids=thought_ids,
                    max_results_per_thought=max_web_results,
                    search_depth=web_search_depth
                )
            else:
                # Enrich all thoughts (or top N by PageRank)
                # For now, skip to avoid excessive API calls
                logger.info("Skipping web enrichment for all thoughts (would be expensive)")
                web_results = {
                    "thoughts_enriched": 0,
                    "total_search_results": 0,
                    "total_connections": 0,
                    "total_content_added": 0
                }

            results["web_enrichment"] = web_results
            enriched = web_results.get("thoughts_enriched", 0)
            logger.info(f"Web enrichment complete: {enriched} thoughts enriched")

        # 3. Project Matching
        if enable_project_matching:
            logger.info("Phase 3: Project matching")

            match_results = await match_to_projects(
                thought_id=thought_ids[0] if thought_ids else None,
                auto_detect=True,
                project_patterns=project_patterns
            )

            # Create connections for matches
            if match_results["matches"]:
                connections_created = await create_project_connections(
                    matches=match_results["matches"],
                    min_confidence=0.5
                )
                match_results["connections_created"] = connections_created

            results["project_matching"] = match_results
            matched = match_results.get("thoughts_matched", 0)
            logger.info(f"Project matching complete: {matched} matches")

        # 4. Edge Weight Management
        if enable_edge_decay:
            logger.info("Phase 4: Edge weight decay")

            decay_results = await decay_edge_weights(
                decay_rate=decay_rate,
                min_weight=min_edge_weight,
                time_based=True,
                days_threshold=30
            )

            results["edge_management"] = decay_results
            removed = decay_results.get("edges_removed", 0)
            logger.info(f"Edge decay complete: {removed} edges removed")

        # 5. Potential Connections
        if enable_potential_connections and thought_ids:
            logger.info("Phase 5: Calculating potential connections")

            total_potentials = 0
            for thought_id in thought_ids[:5]:  # Limit to first 5 to avoid excessive computation
                potentials = await calculate_potential_connections(
                    thought_id=thought_id,
                    min_potential_weight=0.4,
                    max_results=10
                )
                total_potentials += len(potentials)

            results["potential_connections"] = total_potentials
            logger.info(f"Found {total_potentials} potential connections")

        logger.info("Enhanced memify operation complete")

        return results

    except Exception as e:
        logger.error(f"Error in memify_thoughts: {e}")
        return results


async def cognify_and_memify_thoughts(
    data: Any,
    enable_all_enrichments: bool = True,
    project_patterns: Optional[Dict[str, List[str]]] = None
) -> Dict[str, Any]:
    """
    Combined cognify and memify operation for thought graphs.

    Processes raw data through cognify to add thoughts, then runs the full
    memify enrichment pipeline.

    Args:
        data: Raw data to process — a list of thought dictionaries with keys
              like ``content``, ``title``, ``tags``, etc., or plain text strings.
        enable_all_enrichments: Enable all enrichment features
        project_patterns: Project matching patterns

    Returns:
        Combined results from cognify and memify operations
    """
    logger.info("Starting combined cognify and memify operation")

    from .add_thought import add_thoughts_batch

    # Normalise incoming data into a list of thought dicts
    thoughts_data: list = []
    if isinstance(data, str):
        thoughts_data = [{"content": data}]
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                thoughts_data.append({"content": item})
            elif isinstance(item, dict):
                thoughts_data.append(item)
    elif isinstance(data, dict):
        thoughts_data = [data]

    # Phase 1: Cognify — add thoughts to the graph
    cognify_results: Dict[str, Any] = {}
    thought_ids: list = []

    if thoughts_data:
        nodes = await add_thoughts_batch(thoughts_data, auto_connect=True)
        thought_ids = [n.id for n in nodes]
        cognify_results = {
            "thoughts_added": len(nodes),
            "thought_ids": [str(tid) for tid in thought_ids],
        }
        logger.info(f"Cognify phase added {len(nodes)} thoughts")
    else:
        cognify_results = {"thoughts_added": 0, "thought_ids": []}

    # Phase 2: Memify — run the full enrichment pipeline
    memify_results = await memify_thoughts(
        thought_ids=thought_ids if thought_ids else None,
        enable_web_enrichment=enable_all_enrichments,
        enable_project_matching=enable_all_enrichments,
        enable_edge_decay=enable_all_enrichments,
        enable_potential_connections=enable_all_enrichments,
        project_patterns=project_patterns
    )

    return {
        "cognify_results": cognify_results,
        "memify_results": memify_results
    }
