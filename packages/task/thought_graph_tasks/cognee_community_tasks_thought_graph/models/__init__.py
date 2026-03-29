"""
Thought Graph Data Models.

Provides the core data structures for representing thoughts, connections,
and surprise scores in the ADHD-optimized thought graph system.

Classes:
    ThoughtNode: A single thought/idea node extending cognee's DataPoint.
    Connection: A relationship between two thoughts with strength and metadata.
    SurpriseScore: Quantifies how unexpected a connection is across multiple dimensions.
"""

from .connection import Connection
from .surprise_score import SurpriseScore
from .thought_node import ThoughtNode

__all__ = ["ThoughtNode", "Connection", "SurpriseScore"]
