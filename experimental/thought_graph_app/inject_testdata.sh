#!/usr/bin/env bash
# Inject test data into the Thought Graph API
set -xeuo pipefail

BASE_URL="${1:-http://localhost:8000}"

post() {
  echo ">>> $1"
  curl -s -X POST "$BASE_URL$1" \
    -H "Content-Type: application/json" \
    -d "$2" | python3 -m json.tool
  echo
}

get() {
  echo ">>> $1"
  curl -s "$BASE_URL$1" | python3 -m json.tool
  echo
}

echo "=== Health Check ==="
get /health

echo "=== Adding thoughts (batch) ==="
post /thoughts/batch '{
  "thoughts": [
    {
      "content": "Graph databases could model how ADHD brains actually link ideas — not linearly but through associative jumps across domains",
      "title": "Graph DBs for ADHD thinking",
      "tags": ["adhd", "graph-databases", "neuroscience"],
      "context": "Reading about Neo4j while procrastinating on taxes",
      "energy_level": 8,
      "importance_score": 9,
      "related_projects": ["thought-graph"],
      "auto_connect": false
    },
    {
      "content": "Working memory bottleneck is the core ADHD issue — what if we externalize the buffer into a knowledge graph that persists context?",
      "title": "Externalized working memory",
      "tags": ["adhd", "working-memory", "knowledge-graph"],
      "context": "Forgot what I was doing mid-task again",
      "energy_level": 6,
      "importance_score": 8,
      "related_projects": ["thought-graph", "cognee"],
      "auto_connect": false
    },
    {
      "content": "Spaced repetition + graph traversal = remembering connections not just facts. Each revisit strengthens edge weights naturally",
      "title": "Spaced repetition on graphs",
      "tags": ["spaced-repetition", "learning", "graph-algorithms"],
      "context": "Anki session reminded me of PageRank",
      "energy_level": 7,
      "importance_score": 7,
      "related_projects": ["thought-graph"],
      "auto_connect": false
    },
    {
      "content": "Surprise connections between distant thoughts might be the ADHD superpower — divergent thinking as a graph property",
      "title": "Divergent thinking as graph metric",
      "tags": ["adhd", "creativity", "graph-algorithms", "neuroscience"],
      "context": "Shower thought after reading about community detection",
      "energy_level": 9,
      "importance_score": 8,
      "auto_connect": false
    },
    {
      "content": "LLMs can infer implicit relationships between thoughts that pure embedding similarity misses — use as a connection discovery oracle",
      "title": "LLM-powered connection discovery",
      "tags": ["llm", "knowledge-graph", "semantic-search"],
      "context": "Testing cognee pipelines",
      "energy_level": 5,
      "importance_score": 7,
      "related_projects": ["cognee", "thought-graph"],
      "auto_connect": false
    },
    {
      "content": "Edge weight decay models forgetting — connections you dont revisit fade, mimicking how memory actually works in ADHD brains",
      "title": "Edge decay as forgetting model",
      "tags": ["graph-algorithms", "memory", "adhd", "neuroscience"],
      "context": "Realized I forgot about a project I was excited about last month",
      "energy_level": 4,
      "importance_score": 6,
      "related_projects": ["thought-graph"],
      "auto_connect": false
    },
    {
      "content": "Community detection on thought graphs reveals thematic clusters you didnt know you had — like finding hidden projects in your braindump",
      "title": "Hidden project discovery",
      "tags": ["community-detection", "graph-algorithms", "productivity"],
      "context": "Ran Louvain on my notes and found 3 proto-projects",
      "energy_level": 7,
      "importance_score": 8,
      "related_projects": ["thought-graph"],
      "auto_connect": false
    },
    {
      "content": "FastAPI + graph database + LLM = personal second brain API. Capture thoughts via REST, let the system find the patterns",
      "title": "Second brain as API",
      "tags": ["fastapi", "architecture", "llm", "knowledge-graph"],
      "context": "Designing the thought graph app architecture",
      "energy_level": 8,
      "importance_score": 9,
      "related_projects": ["thought-graph", "cognee"],
      "auto_connect": false
    }
  ]
}'

echo "=== Adding single thought ==="
post /thoughts '{
  "content": "Hyperfocus sessions produce the best graph clusters — high energy thoughts are more densely connected. Track energy as metadata.",
  "title": "Energy level as graph signal",
  "tags": ["adhd", "hyperfocus", "metadata", "graph-algorithms"],
  "context": "3am coding session, extremely locked in",
  "energy_level": 10,
  "importance_score": 7,
  "related_projects": ["thought-graph"],
  "auto_connect": true,
  "similarity_threshold": 0.5
}'

echo "=== Enriching graph ==="
post /enrich '{
  "compute_pagerank": true,
  "compute_centrality": true,
  "detect_communities": true,
  "find_transitive": true,
  "auto_add_transitive_links": true,
  "transitive_strength_threshold": 0.3
}'

echo "=== Getting communities ==="
get "/communities?algorithm=greedy&include_summary=true"

echo "=== Finding surprise connections ==="
get "/connections/surprise?min_surprise_score=0.3&max_results=10"

echo "=== Running memify ==="
post /memify '{
  "enable_web_enrichment": false,
  "enable_project_matching": true,
  "enable_edge_decay": true,
  "enable_potential_connections": true,
  "decay_rate": 0.05,
  "min_edge_weight": 0.1,
  "project_patterns": {
    "thought-graph": ["graph", "thought", "adhd", "brain"],
    "cognee": ["cognee", "pipeline", "knowledge-graph", "llm"]
  }
}'

echo "=== Done! ==="
