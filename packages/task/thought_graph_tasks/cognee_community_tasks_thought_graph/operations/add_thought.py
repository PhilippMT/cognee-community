"""Add a thought to the thought graph with automatic connection discovery."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.infrastructure.databases.vector import get_vector_engine
from cognee.shared.logging_utils import get_logger

from cognee_community_tasks_thought_graph.models.thought_node import ThoughtNode

from .discover_connections import discover_connections

logger = get_logger(__name__)


async def add_thought(
    content: str,
    title: Optional[str] = None,
    tags: Optional[List[str]] = None,
    context: Optional[str] = None,
    energy_level: Optional[int] = None,
    related_projects: Optional[List[str]] = None,
    importance_score: Optional[int] = None,
    auto_connect: bool = True,
    similarity_threshold: float = 0.7,
) -> ThoughtNode:
    """
    Add a new thought to the thought graph with automatic connection discovery.

    This is the main entry point for quick thought capture - optimized for ADHD workflows
    where ideas need to be captured quickly without breaking flow.

    Args:
        content: The main thought/idea content (required, cannot be empty)
        title: Optional short title for the thought
        tags: Optional list of tags for categorization
        context: Optional context about when/why this thought emerged
        energy_level: Optional energy level when captured (1-10)
        related_projects: Optional list of project names this relates to
        importance_score: Optional importance score (1-10)
        auto_connect: Whether to automatically discover and create connections
        similarity_threshold: Minimum similarity for auto-connections (0.0-1.0)

    Returns:
        The created ThoughtNode with ID assigned

    Raises:
        ValueError: If input validation fails (invalid ranges, empty content, etc.)

    Example:
        >>> thought = await add_thought(
        ...     content="Build a graph database for managing ADHD thoughts",
        ...     tags=["adhd", "productivity", "ideas"],
        ...     importance_score=8,
        ...     auto_connect=True
        ... )
        >>> print(f"Added thought: {thought.id}")
    """
    # Input validation
    if not content or not content.strip():
        raise ValueError("Content cannot be empty")

    if energy_level is not None and not (1 <= energy_level <= 10):
        raise ValueError(f"Energy level must be between 1 and 10, got {energy_level}")

    if importance_score is not None and not (1 <= importance_score <= 10):
        raise ValueError(f"Importance score must be between 1 and 10, got {importance_score}")

    if not (0.0 <= similarity_threshold <= 1.0):
        raise ValueError(f"Similarity threshold must be between 0.0 and 1.0, got {similarity_threshold}")

    # Create thought node
    thought = ThoughtNode(
        id=uuid4(),
        content=content,
        title=title,
        tags=tags or [],
        context=context,
        energy_level=energy_level,
        related_projects=related_projects or [],
        importance_score=importance_score,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    logger.info(f"Adding thought: {thought.title or thought.content[:50]}")

    try:
        # Add node to graph database
        graph_engine = await get_graph_engine()
        await graph_engine.add_node(thought)

        # Index in vector store for semantic search
        try:
            vector_engine = get_vector_engine()
            await vector_engine.create_data_points("ThoughtNode", [thought])
        except Exception as e:
            logger.warning(f"Failed to index thought in vector store: {e}")

        logger.info(f"Successfully added thought node {thought.id}")

        # Auto-discover connections if requested
        if auto_connect:
            logger.info("Auto-discovering connections for new thought")
            try:
                connections = await discover_connections(
                    thought_id=thought.id,
                    similarity_threshold=similarity_threshold,
                    max_connections=10
                )
                logger.info(f"Auto-discovered {len(connections)} connections")
            except Exception as e:
                logger.warning(f"Error in auto-connection discovery: {e}")
                # Don't fail the whole operation if connection discovery fails

        return thought

    except Exception as e:
        logger.error(f"Error adding thought to graph: {e}")
        raise


async def add_thoughts_batch(
    thoughts_data: List[Dict[str, Any]],
    auto_connect: bool = True,
) -> List[ThoughtNode]:
    """
    Add multiple thoughts in a batch operation.

    More efficient than adding one at a time when you have multiple thoughts
    to capture (e.g., from a brainstorming session).

    Args:
        thoughts_data: List of dictionaries with thought data
        auto_connect: Whether to auto-discover connections

    Returns:
        List of created ThoughtNode objects
    """
    thoughts = []

    for data in thoughts_data:
        try:
            thought = await add_thought(
                content=data.get("content", ""),
                title=data.get("title"),
                tags=data.get("tags"),
                context=data.get("context"),
                energy_level=data.get("energy_level"),
                related_projects=data.get("related_projects"),
                importance_score=data.get("importance_score"),
                auto_connect=auto_connect,
            )
            thoughts.append(thought)
        except Exception as e:
            logger.error(f"Error adding thought in batch: {e}")
            # Continue with other thoughts
            continue

    logger.info(f"Successfully added {len(thoughts)}/{len(thoughts_data)} thoughts")

    return thoughts
