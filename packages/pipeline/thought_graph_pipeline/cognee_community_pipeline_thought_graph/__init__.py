"""
ADHD Thought Graph Pipeline for Cognee.

Orchestrates the full thought graph workflow: ingest thoughts, discover
connections, enrich with graph algorithms, and surface surprise insights.
"""

from .thought_graph_pipeline import run_thought_graph_pipeline

__all__ = ["run_thought_graph_pipeline"]
