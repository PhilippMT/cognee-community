"""Unit tests for thought graph algorithms.

These test the pure graph algorithm functions which operate on simple
node/edge tuple lists and require only networkx (no database or LLM).
"""

from uuid import uuid4

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_nodes(n: int):
    """Create *n* node tuples with deterministic UUIDs."""
    ids = [str(uuid4()) for _ in range(n)]
    nodes = [
        (nid, {"content": f"thought_{i}", "tags": [f"tag_{i % 3}"]})
        for i, nid in enumerate(ids)
    ]
    return nodes, ids


def _make_edges(ids, connections):
    """Build edge tuples from a list of (src_idx, tgt_idx, strength) triples."""
    return [
        (ids[src], ids[tgt], "relates_to", {"strength": strength})
        for src, tgt, strength in connections
    ]


# ---------------------------------------------------------------------------
# PageRank
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pagerank_empty():
    from cognee_community_tasks_thought_graph.algorithms.pagerank import calculate_pagerank

    result = await calculate_pagerank([], [])
    assert result == {}


@pytest.mark.asyncio
async def test_pagerank_no_edges():
    from cognee_community_tasks_thought_graph.algorithms.pagerank import calculate_pagerank

    nodes, ids = _make_nodes(3)
    result = await calculate_pagerank(nodes, [])
    assert len(result) == 3
    for score in result.values():
        assert abs(score - 1.0 / 3) < 1e-6


@pytest.mark.asyncio
async def test_pagerank_with_edges():
    from cognee_community_tasks_thought_graph.algorithms.pagerank import (
        calculate_pagerank,
        get_top_pagerank_thoughts,
    )

    nodes, ids = _make_nodes(4)
    # Node 0 is the "hub" that everyone points to
    edges = _make_edges(ids, [(1, 0, 0.9), (2, 0, 0.8), (3, 0, 0.7)])
    scores = await calculate_pagerank(nodes, edges)
    assert len(scores) == 4

    top = await get_top_pagerank_thoughts(scores, top_k=1)
    assert len(top) == 1
    # The hub node should have the highest score
    from uuid import UUID

    assert top[0][0] == UUID(ids[0])


# ---------------------------------------------------------------------------
# Centrality
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_centrality_empty():
    from cognee_community_tasks_thought_graph.algorithms.centrality import calculate_centrality

    assert await calculate_centrality([], []) == {}


@pytest.mark.asyncio
async def test_centrality_degree():
    from cognee_community_tasks_thought_graph.algorithms.centrality import calculate_centrality

    nodes, ids = _make_nodes(3)
    edges = _make_edges(ids, [(0, 1, 1.0), (0, 2, 1.0)])
    scores = await calculate_centrality(nodes, edges, centrality_type="degree")
    assert len(scores) == 3


@pytest.mark.asyncio
async def test_bridge_thoughts():
    from cognee_community_tasks_thought_graph.algorithms.centrality import find_bridge_thoughts

    nodes, ids = _make_nodes(5)
    # Node 2 bridges two clusters: 0-1 and 3-4
    edges = _make_edges(ids, [(0, 1, 1.0), (1, 2, 1.0), (2, 3, 1.0), (3, 4, 1.0)])
    bridges = await find_bridge_thoughts(nodes, edges, threshold=0.1)
    assert len(bridges) > 0


# ---------------------------------------------------------------------------
# Community Detection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_community_detection_empty():
    from cognee_community_tasks_thought_graph.algorithms.community_detection import (
        detect_communities,
    )

    assert await detect_communities([], []) == {}


@pytest.mark.asyncio
async def test_community_detection_no_edges():
    from cognee_community_tasks_thought_graph.algorithms.community_detection import (
        detect_communities,
    )

    nodes, ids = _make_nodes(3)
    result = await detect_communities(nodes, [])
    # Each node should be its own community
    assert len(result) == 3
    assert len(set(result.values())) == 3


@pytest.mark.asyncio
async def test_community_detection_greedy():
    from cognee_community_tasks_thought_graph.algorithms.community_detection import (
        detect_communities,
        get_community_summary,
    )

    nodes, ids = _make_nodes(4)
    edges = _make_edges(ids, [(0, 1, 1.0), (2, 3, 1.0)])
    communities = await detect_communities(nodes, edges, algorithm="greedy")
    assert len(communities) == 4

    summary = await get_community_summary(nodes, communities)
    assert len(summary) > 0
    for _cid, info in summary.items():
        assert "size" in info
        assert "top_tags" in info


@pytest.mark.asyncio
async def test_community_detection_louvain():
    from cognee_community_tasks_thought_graph.algorithms.community_detection import (
        detect_communities,
    )

    nodes, ids = _make_nodes(4)
    edges = _make_edges(ids, [(0, 1, 1.0), (2, 3, 1.0)])
    communities = await detect_communities(nodes, edges, algorithm="louvain")
    assert len(communities) == 4


@pytest.mark.asyncio
async def test_community_detection_label_propagation():
    from cognee_community_tasks_thought_graph.algorithms.community_detection import (
        detect_communities,
    )

    nodes, ids = _make_nodes(4)
    edges = _make_edges(ids, [(0, 1, 1.0), (2, 3, 1.0)])
    communities = await detect_communities(nodes, edges, algorithm="label_propagation")
    assert len(communities) == 4


# ---------------------------------------------------------------------------
# Shortest Path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_shortest_path_empty():
    from cognee_community_tasks_thought_graph.algorithms.shortest_path import find_shortest_paths

    result = await find_shortest_paths([], [], uuid4())
    assert result == {}


@pytest.mark.asyncio
async def test_shortest_path_simple():
    from uuid import UUID

    from cognee_community_tasks_thought_graph.algorithms.shortest_path import find_shortest_paths

    nodes, ids = _make_nodes(3)
    edges = _make_edges(ids, [(0, 1, 1.0), (1, 2, 1.0)])
    paths = await find_shortest_paths(nodes, edges, UUID(ids[0]), UUID(ids[2]))
    assert UUID(ids[2]) in paths
    assert len(paths[UUID(ids[2])]) == 3  # 0 -> 1 -> 2


@pytest.mark.asyncio
async def test_connection_chains():
    from cognee_community_tasks_thought_graph.algorithms.shortest_path import find_connection_chains

    nodes, ids = _make_nodes(4)
    edges = _make_edges(ids, [(0, 1, 1.0), (1, 2, 1.0), (2, 3, 1.0)])
    chains = await find_connection_chains(nodes, edges, min_length=2, max_length=4)
    assert len(chains) > 0


# ---------------------------------------------------------------------------
# Transitive Connections
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_transitive_connections_empty():
    from cognee_community_tasks_thought_graph.algorithms.transitive_connections import (
        find_transitive_connections,
    )

    result = await find_transitive_connections([], [])
    assert result == []


@pytest.mark.asyncio
async def test_transitive_connections_finds_indirect():

    from cognee_community_tasks_thought_graph.algorithms.transitive_connections import (
        find_transitive_connections,
    )

    nodes, ids = _make_nodes(3)
    # 0 -> 1 -> 2 but no direct 0 -> 2
    edges = _make_edges(ids, [(0, 1, 0.8), (1, 2, 0.9)])
    result = await find_transitive_connections(nodes, edges, max_hops=2)
    # Should find 0 <-> 2 as transitive
    assert len(result) > 0
    sources_and_targets = {(str(r[0]), str(r[1])) for r in result}
    assert (ids[0], ids[2]) in sources_and_targets or (ids[2], ids[0]) in sources_and_targets


@pytest.mark.asyncio
async def test_suggest_missing_links():
    from cognee_community_tasks_thought_graph.algorithms.transitive_connections import (
        suggest_missing_links,
    )

    nodes, ids = _make_nodes(3)
    edges = _make_edges(ids, [(0, 1, 0.8), (1, 2, 0.9)])
    suggestions = await suggest_missing_links(nodes, edges, top_k=5)
    assert len(suggestions) > 0
    assert "source_id" in suggestions[0]
    assert "reason" in suggestions[0]


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

def test_thought_node_creation():
    from cognee_community_tasks_thought_graph.models import ThoughtNode

    node = ThoughtNode(content="Test thought", tags=["test"])
    assert node.content == "Test thought"
    assert node.tags == ["test"]
    assert node.id is not None
    d = node.to_dict()
    assert d["content"] == "Test thought"


def test_connection_creation():
    from cognee_community_tasks_thought_graph.models import Connection

    conn = Connection(source_id=uuid4(), target_id=uuid4(), strength=0.8)
    assert conn.strength == 0.8
    assert conn.relationship_type == "relates_to"
    d = conn.to_dict()
    assert d["strength"] == 0.8


def test_surprise_score_creation():
    from cognee_community_tasks_thought_graph.models import SurpriseScore

    score = SurpriseScore(
        source_id=uuid4(),
        target_id=uuid4(),
        overall_score=0.75,
        semantic_distance=0.8,
    )
    assert score.overall_score == 0.75
    d = score.to_dict()
    assert d["overall_score"] == 0.75
