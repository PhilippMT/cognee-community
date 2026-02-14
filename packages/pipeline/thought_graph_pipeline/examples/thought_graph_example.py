"""
ADHD Thought Graph Pipeline Example.

Demonstrates the full workflow:
1. Capture scattered thoughts from a brainstorming session
2. Auto-discover connections between them
3. Enrich with graph algorithms (PageRank, communities, etc.)
4. Surface surprise connections for creative insights

Run:
    python examples/thought_graph_example.py
"""

import asyncio
import os

import cognee
from cognee.shared.logging_utils import setup_logging, INFO
from cognee_community_pipeline_thought_graph import run_thought_graph_pipeline
from cognee_community_tasks_thought_graph.operations.get_thought_communities import get_thought_communities


async def main():
    print("=" * 70)
    print("ADHD Thought Graph Pipeline Example")
    print("=" * 70)

    os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"

    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)

    # Simulate a brainstorming session with scattered ADHD thoughts
    thoughts_data = [
        {
            "content": "Build a knowledge graph for managing scattered thoughts",
            "title": "Knowledge Graph System",
            "tags": ["project", "ai", "productivity"],
            "importance_score": 9,
            "energy_level": 8,
        },
        {
            "content": "ADHD brains think in non-linear, associative patterns",
            "title": "ADHD Brain Patterns",
            "tags": ["adhd", "neuroscience", "learning"],
            "importance_score": 8,
        },
        {
            "content": "Need a quick-capture tool for ideas that suddenly appear",
            "title": "Quick Capture Tool",
            "tags": ["productivity", "adhd", "tools"],
            "importance_score": 7,
        },
        {
            "content": "Graph databases represent non-hierarchical relationships",
            "title": "Graph Database Benefits",
            "tags": ["database", "technology", "graphs"],
            "importance_score": 6,
        },
        {
            "content": "PageRank could identify the most important thoughts",
            "title": "Using PageRank",
            "tags": ["algorithms", "ai", "graphs"],
            "importance_score": 6,
        },
        {
            "content": "Community detection reveals thematic clusters in ideas",
            "title": "Community Detection",
            "tags": ["algorithms", "ai", "organization"],
            "importance_score": 6,
        },
        {
            "content": "Best ideas come from unexpected connections between topics",
            "title": "Serendipitous Discovery",
            "tags": ["creativity", "learning", "innovation"],
            "importance_score": 8,
        },
        {
            "content": "Working memory issues make it hard to hold multiple ideas",
            "title": "Working Memory Challenges",
            "tags": ["adhd", "neuroscience", "challenges"],
            "importance_score": 7,
        },
        {
            "content": "External brain systems compensate for ADHD limitations",
            "title": "External Brain Concept",
            "tags": ["adhd", "productivity", "tools"],
            "importance_score": 9,
        },
        {
            "content": "Obsidian and Roam use bidirectional links but could be smarter",
            "title": "PKM Tool Inspiration",
            "tags": ["tools", "productivity", "notes"],
            "importance_score": 7,
        },
    ]

    print(f"\nCapturing {len(thoughts_data)} thoughts...\n")

    # Run the pipeline
    run_status = None
    async for status in run_thought_graph_pipeline(thoughts_data):
        run_status = status

    print(f"Pipeline complete: {run_status}\n")

    # Show communities
    communities = await get_thought_communities(include_summary=True)
    print(f"Detected {communities['total_communities']} thematic communities:")
    for cid, summary in communities.get("summaries", {}).items():
        tags = ", ".join(summary.get("top_tags", []))
        print(f"  {cid}: {summary['size']} thoughts — topics: {tags}")

    print("\nDone! Your thought graph is enriched and ready to explore.")


if __name__ == "__main__":
    setup_logging(log_level=INFO)
    asyncio.run(main())
