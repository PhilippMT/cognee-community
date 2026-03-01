"""Match thoughts to projects and repositories."""

import re
from typing import Any, Dict, List, Optional
from uuid import UUID

from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.shared.logging_utils import get_logger

logger = get_logger(__name__)


async def match_to_projects(
    thought_id: Optional[UUID] = None,
    auto_detect: bool = True,
    project_patterns: Optional[Dict[str, List[str]]] = None
) -> Dict[str, Any]:
    """
    Match thoughts to projects and repositories.

    Analyzes thought content and tags to identify which projects or repositories
    they relate to. Can auto-detect project names or use provided patterns.

    Args:
        thought_id: ID of specific thought to match (None = match all)
        auto_detect: Automatically detect project names in content
        project_patterns: Dictionary of project_name -> [keywords/patterns]

    Returns:
        Dictionary with matching results:
        - thoughts_matched: Number of thoughts matched
        - projects_found: Set of project names found
        - matches: List of (thought_id, project_name, confidence) tuples

    Example:
        >>> results = await match_to_projects(
        ...     auto_detect=True,
        ...     project_patterns={
        ...         "cognee": ["cognee", "knowledge graph", "memory"],
        ...         "backend-api": ["api", "backend", "server"]
        ...     }
        ... )
        >>> print(f"Matched {results['thoughts_matched']} thoughts to projects")
    """
    logger.info("Matching thoughts to projects")

    try:
        graph_engine = await get_graph_engine()

        # Get thoughts to process
        if thought_id:
            node_data = await graph_engine.get_node(str(thought_id))
            if not node_data:
                logger.warning(f"Thought {thought_id} not found")
                return {
                    "thoughts_matched": 0,
                    "projects_found": set(),
                    "matches": []
                }
            nodes = [(str(thought_id), node_data)]
        else:
            # Get all ThoughtNode nodes
            all_nodes, _ = await graph_engine.get_graph_data()
            nodes = [(nid, props) for nid, props in all_nodes
                    if props.get("__class__") == "ThoughtNode" or "content" in props]

        # Default project patterns
        if project_patterns is None:
            project_patterns = {}

        # Common project detection patterns
        common_patterns = {
            "github_repo": r"github\.com/[\w-]+/[\w-]+",
            "gitlab_repo": r"gitlab\.com/[\w-]+/[\w-]+",
            "project_mention": r"(?:project|repo|repository):\s*(\w+)",
        }

        matches = []
        projects_found = set()

        for node_id, node_data in nodes:
            content = node_data.get("content", "").lower()
            tags = [t.lower() for t in node_data.get("tags", [])]
            related_projects = node_data.get("related_projects", [])

            # Add existing related_projects
            for project in related_projects:
                projects_found.add(project)
                matches.append((UUID(node_id), project, 1.0))

            # Check project patterns
            for project_name, keywords in project_patterns.items():
                confidence = 0.0

                # Check keywords in content
                for keyword in keywords:
                    if keyword.lower() in content:
                        confidence += 0.3
                    if keyword.lower() in tags:
                        confidence += 0.5

                if confidence > 0.0:
                    confidence = min(confidence, 1.0)
                    projects_found.add(project_name)
                    matches.append((UUID(node_id), project_name, confidence))

            # Auto-detect repository URLs
            if auto_detect:
                for _pattern_name, pattern in common_patterns.items():
                    repo_matches = re.findall(pattern, content)
                    for repo in repo_matches:
                        projects_found.add(repo)
                        matches.append((UUID(node_id), repo, 0.9))

        logger.info(f"Matched {len(matches)} thoughts to {len(projects_found)} projects")

        return {
            "thoughts_matched": len(set(m[0] for m in matches)),
            "projects_found": projects_found,
            "matches": matches
        }

    except Exception as e:
        logger.error(f"Error matching thoughts to projects: {e}")
        return {
            "thoughts_matched": 0,
            "projects_found": set(),
            "matches": []
        }


async def create_project_connections(
    matches: List[tuple],
    min_confidence: float = 0.5
) -> int:
    """
    Create graph connections between thoughts and projects.

    Takes match results and creates explicit "related_to_project" edges
    in the graph with confidence as the edge weight.

    Args:
        matches: List of (thought_id, project_name, confidence) tuples
        min_confidence: Minimum confidence to create connection

    Returns:
        Number of connections created
    """
    logger.info(f"Creating project connections from {len(matches)} matches")

    try:
        graph_engine = await get_graph_engine()
        connections_created = 0

        # Group by thought
        thought_projects: Dict[UUID, List[tuple]] = {}
        for thought_id, project_name, confidence in matches:
            if confidence >= min_confidence:
                if thought_id not in thought_projects:
                    thought_projects[thought_id] = []
                thought_projects[thought_id].append((project_name, confidence))

        # Update thought nodes with project information
        for thought_id, projects in thought_projects.items():
            node_data = await graph_engine.get_node(str(thought_id))
            if node_data:
                # Update related_projects field
                existing_projects = set(node_data.get("related_projects", []))
                new_projects = {p[0] for p in projects}
                all_projects = list(existing_projects | new_projects)

                updated_data = {**node_data, "related_projects": all_projects}

                # Persist the update by re-adding the node
                await graph_engine.delete_node(str(thought_id))
                await graph_engine.add_nodes([(str(thought_id), updated_data)])

                connections_created += len(new_projects - existing_projects)

        logger.info(f"Created {connections_created} project connections")

        return connections_created

    except Exception as e:
        logger.error(f"Error creating project connections: {e}")
        return 0


async def find_project_clusters(
    min_shared_projects: int = 1
) -> Dict[str, List[UUID]]:
    """
    Find clusters of thoughts that share project associations.

    Groups thoughts by their project connections to identify themes
    and related work across the thought graph.

    Args:
        min_shared_projects: Minimum shared projects for clustering

    Returns:
        Dictionary mapping project names to lists of thought IDs
    """
    logger.info("Finding project-based thought clusters")

    try:
        graph_engine = await get_graph_engine()
        all_nodes, _ = await graph_engine.get_graph_data()

        # Group thoughts by project
        project_thoughts: Dict[str, List[UUID]] = {}

        for node_id, node_data in all_nodes:
            if node_data.get("__class__") == "ThoughtNode" or "related_projects" in node_data:
                projects = node_data.get("related_projects", [])

                for project in projects:
                    if project not in project_thoughts:
                        project_thoughts[project] = []
                    project_thoughts[project].append(UUID(node_id))

        # Filter by minimum cluster size
        clusters = {
            project: thoughts
            for project, thoughts in project_thoughts.items()
            if len(thoughts) >= min_shared_projects
        }

        logger.info(f"Found {len(clusters)} project clusters")

        return clusters

    except Exception as e:
        logger.error(f"Error finding project clusters: {e}")
        return {}
