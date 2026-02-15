"""
Monkey-patch cognee's KuzuAdapter to fix Neo4j-specific Cypher syntax.

cognee 0.5.2's KuzuAdapter uses MERGE ... ON CREATE SET, ON MATCH SET,
+= map updates, and timestamp() — none of which Kuzu supports.
This module patches the affected methods with Kuzu-compatible equivalents.

Import this module before any graph operations to apply the fix.
"""

import json
from datetime import datetime, timezone

from cognee.infrastructure.databases.graph.kuzu.adapter import KuzuAdapter
from cognee.shared.logging_utils import get_logger

logger = get_logger(__name__)

# Save reference to the adapter's JSONEncoder
_JSONEncoder = None
for _name in dir(KuzuAdapter):
    pass
# Get JSONEncoder from the adapter module
import cognee.infrastructure.databases.graph.kuzu.adapter as _adapter_module
_JSONEncoder = getattr(_adapter_module, "JSONEncoder", None)


def _patched_edge_query_and_params(self, from_node, to_node, relationship_name, properties):
    """Kuzu-compatible edge query builder."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    query = """
        MATCH (from:Node), (to:Node)
        WHERE from.id = $from_id AND to.id = $to_id
        MERGE (from)-[r:EDGE {
            relationship_name: $relationship_name
        }]->(to)
        SET r.created_at = cast($created_at, 'TIMESTAMP'),
            r.updated_at = cast($updated_at, 'TIMESTAMP'),
            r.properties = $properties
    """
    params = {
        "from_id": from_node,
        "to_id": to_node,
        "relationship_name": relationship_name,
        "created_at": now,
        "updated_at": now,
        "properties": json.dumps(properties, cls=_JSONEncoder),
    }
    return query, params


async def _patched_add_node(self, node):
    """Kuzu-compatible single node add."""
    try:
        if isinstance(node, tuple):
            node_id, props = node
            properties = dict(props) if isinstance(props, dict) else {"id": str(node_id)}
            properties.setdefault("id", str(node_id))
        elif isinstance(node, dict):
            properties = dict(node)
        elif hasattr(node, "model_dump"):
            properties = node.model_dump()
        else:
            properties = vars(node)

        core_properties = {
            "id": str(properties.pop("id", "")),
            "name": str(properties.pop("name", "")),
            "type": str(properties.pop("type", "")),
        }
        core_properties["properties"] = json.dumps(properties, cls=_JSONEncoder)

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
        params = {}
        set_clauses = []
        for key, value in core_properties.items():
            if value is not None:
                param_name = f"param_{key}"
                params[param_name] = value
                if key != "id":
                    set_clauses.append(f"n.{key} = ${param_name}")
        set_clauses.extend(["n.created_at = cast($created_at, 'TIMESTAMP')", "n.updated_at = cast($updated_at, 'TIMESTAMP')"])
        params.update({"param_id": core_properties["id"], "created_at": now, "updated_at": now})

        merge_query = f"""
        MERGE (n:Node {{id: $param_id}})
        SET {", ".join(set_clauses)}
        """
        await self.query(merge_query, params)
    except Exception as e:
        logger.error(f"Failed to add node: {e}")
        raise


async def _patched_add_nodes(self, nodes):
    """Kuzu-compatible batch node add — adds one at a time to avoid UNWIND+MERGE issues."""
    if not nodes:
        return
    for node in nodes:
        await _patched_add_node(self, node)


async def _patched_add_edges(self, edges):
    """Kuzu-compatible batch edge add."""
    if not edges:
        return
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
        for from_node, to_node, relationship_name, properties in edges:
            query = """
            MATCH (from:Node), (to:Node)
            WHERE from.id = $from_id AND to.id = $to_id
            MERGE (from)-[r:EDGE {
                relationship_name: $relationship_name
            }]->(to)
            SET r.created_at = cast($created_at, 'TIMESTAMP'),
                r.updated_at = cast($updated_at, 'TIMESTAMP'),
                r.properties = $properties
            """
            params = {
                "from_id": from_node,
                "to_id": to_node,
                "relationship_name": relationship_name,
                "created_at": now,
                "updated_at": now,
                "properties": json.dumps(properties, cls=_JSONEncoder),
            }
            await self.query(query, params)
    except Exception as e:
        logger.error(f"Failed to add edges in batch: {e}")
        raise


# Apply patches
KuzuAdapter._edge_query_and_params = _patched_edge_query_and_params
KuzuAdapter.add_node = _patched_add_node
KuzuAdapter.add_nodes = _patched_add_nodes
KuzuAdapter.add_edges = _patched_add_edges

logger.info("Applied Kuzu adapter patches for cognee 0.5.2 compatibility")
