"""Discover connections between thoughts using semantic similarity and LLM inference."""

from typing import List
from uuid import UUID

from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.infrastructure.databases.vector import get_vector_engine
from cognee.infrastructure.llm.LLMGateway import LLMGateway
from cognee.shared.logging_utils import get_logger
from pydantic import BaseModel, Field

from cognee_community_tasks_thought_graph.models.connection import Connection

logger = get_logger(__name__)


class _LLMConnectionCandidate(BaseModel):
    """A single connection discovered by the LLM."""

    candidate_index: int = Field(description="1-based index of the candidate thought")
    relationship: str = Field(description="Type of relationship (e.g. inspires, contradicts)")
    explanation: str = Field(description="Why these thoughts are related")


class _LLMConnectionResult(BaseModel):
    """Structured LLM output for connection discovery."""

    connections: List[_LLMConnectionCandidate] = Field(
        default_factory=list,
        description="List of discovered connections",
    )


async def discover_connections(
    thought_id: UUID,
    similarity_threshold: float = 0.7,
    max_connections: int = 10,
    use_llm: bool = True,
) -> List[Connection]:
    """
    Discover connections between a thought and other thoughts in the graph.

    Uses multiple methods to find connections:
    1. Semantic similarity (vector embeddings)
    2. Tag overlap
    3. LLM inference for non-obvious connections

    Args:
        thought_id: ID of the thought to find connections for
        similarity_threshold: Minimum similarity score (0.0-1.0)
        max_connections: Maximum number of connections to return
        use_llm: Whether to use LLM for discovering non-obvious connections

    Returns:
        List of Connection objects representing discovered relationships
    """
    logger.info(f"Discovering connections for thought {thought_id}")

    try:
        graph_engine = await get_graph_engine()
        vector_engine = get_vector_engine()

        # Get the source thought
        source_node_data = await graph_engine.get_node(str(thought_id))
        if not source_node_data:
            logger.warning(f"Source thought {thought_id} not found")
            return []

        # Method 1: Semantic similarity search
        connections = []

        try:
            # Search for similar thoughts using vector similarity
            similar_results = await vector_engine.search(
                collection_name="ThoughtNode",
                query_text=source_node_data.get("content", ""),
                limit=max_connections * 2  # Get more candidates for filtering
            )

            for result in similar_results:
                result_id = UUID(result.get("id"))
                if result_id == thought_id:
                    continue  # Skip self

                similarity_score = result.get("score", 0.0)

                if similarity_score >= similarity_threshold:
                    connection = Connection(
                        source_id=thought_id,
                        target_id=result_id,
                        relationship_type="semantically_related",
                        strength=similarity_score,
                        discovery_method="semantic_similarity",
                        explanation=f"Similar content (similarity: {similarity_score:.2f})"
                    )
                    connections.append(connection)

        except Exception as e:
            logger.warning(f"Error in semantic similarity search: {e}")

        # Method 2: Tag-based connections
        source_tags = set(source_node_data.get("tags", []))
        if source_tags:
            try:
                # Query all nodes and check for tag overlap
                all_nodes, _ = await graph_engine.get_graph_data()

                for node_id, node_data in all_nodes:
                    target_id = UUID(node_id)
                    if target_id == thought_id:
                        continue

                    target_tags = set(node_data.get("tags", []))
                    if target_tags:
                        overlap = source_tags & target_tags
                        if overlap:
                            overlap_ratio = len(overlap) / len(source_tags | target_tags)

                            if overlap_ratio >= 0.3:  # At least 30% tag overlap
                                connection = Connection(
                                    source_id=thought_id,
                                    target_id=target_id,
                                    relationship_type="shares_tags",
                                    strength=overlap_ratio,
                                    discovery_method="tag_overlap",
                                    explanation=f"Shared tags: {', '.join(overlap)}"
                                )
                                connections.append(connection)

            except Exception as e:
                logger.warning(f"Error in tag-based connection discovery: {e}")

        # Method 3: LLM-based inference for non-obvious connections
        if use_llm and len(connections) < max_connections:
            try:
                # Get a few candidate thoughts
                candidates = []
                all_nodes, _ = await graph_engine.get_graph_data()
                for node_id, node_data in all_nodes[:20]:
                    if UUID(node_id) != thought_id:
                        candidates.append({
                            "id": node_id,
                            "content": node_data.get("content", ""),
                            "title": node_data.get("title"),
                        })

                if candidates:
                    cand_list = candidates[:10]
                    numbered = "\n".join(
                        f"{i+1}. {c['title'] or c['content'][:100]}"
                        for i, c in enumerate(cand_list)
                    )

                    system_prompt = (
                        "You are a thought-connection analyst. Given a source thought "
                        "and numbered candidate thoughts, identify non-obvious but "
                        "meaningful connections. Return ONLY connections you are "
                        "confident about."
                    )
                    text_input = (
                        f"Source Thought: {source_node_data.get('content', '')}\n\n"
                        f"Candidates:\n{numbered}\n\n"
                        "Identify connections between the source thought and the "
                        "candidates. For each, provide the candidate index, "
                        "relationship type, and a short explanation."
                    )

                    llm_result = await LLMGateway.acreate_structured_output(
                        text_input=text_input,
                        system_prompt=system_prompt,
                        response_model=_LLMConnectionResult,
                    )

                    for llm_conn in llm_result.connections:
                        idx = llm_conn.candidate_index - 1
                        if 0 <= idx < len(cand_list):
                            target_id = UUID(cand_list[idx]["id"])
                            connection = Connection(
                                source_id=thought_id,
                                target_id=target_id,
                                relationship_type=llm_conn.relationship,
                                strength=0.6,
                                discovery_method="llm_inferred",
                                explanation=llm_conn.explanation,
                            )
                            connections.append(connection)

                    logger.info(
                        f"LLM discovered {len(llm_result.connections)} connections"
                    )

            except Exception as e:
                logger.warning(f"Error in LLM-based connection discovery: {e}")

        # Deduplicate and sort by strength
        seen_pairs = set()
        unique_connections = []

        for conn in connections:
            pair = (conn.source_id, conn.target_id)
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                unique_connections.append(conn)

        unique_connections.sort(key=lambda c: c.strength, reverse=True)
        result = unique_connections[:max_connections]

        # Add connections to graph
        edges = [(str(c.source_id), str(c.target_id), c.relationship_type, c.to_dict())
                 for c in result]
        if edges:
            await graph_engine.add_edges(edges)

        logger.info(f"Discovered {len(result)} connections for thought {thought_id}")

        return result

    except Exception as e:
        logger.error(f"Error discovering connections: {e}")
        return []
