"""
ADHD Thought Graph Tasks for Cognee.

This package provides models, algorithms, and operations for managing
interconnected ideas and thoughts with a focus on discovering hidden
connections, transitive relationships, and surprising associations
that are especially valuable for ADHD thought patterns.

Subpackages:
    models: Data models (ThoughtNode, Connection, SurpriseScore)
    algorithms: Graph algorithms (PageRank, centrality, community detection, etc.)
    operations: High-level operations (add thoughts, discover connections, enrich, etc.)
"""

from .models import ThoughtNode, Connection, SurpriseScore

__all__ = ["ThoughtNode", "Connection", "SurpriseScore"]
