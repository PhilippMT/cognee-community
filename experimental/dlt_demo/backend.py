from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
TEST_DATA_DIR = BASE_DIR / "test_data"
GRAPH_FILE_PATH = BASE_DIR / "graph_visualization.html"
APPROVED_PREVIEW_PATH = TEST_DATA_DIR / "approved_preview.json"
GENERATED_OWL_PATH = TEST_DATA_DIR / "generated_ontology.owl"

TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Ensure local cognee package is importable when run from this demo folder.
REPO_ROOT = BASE_DIR.parents[2]
COGNEE_PACKAGE_ROOT = REPO_ROOT / "cognee"
if str(COGNEE_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(COGNEE_PACKAGE_ROOT))

import cognee  # noqa: E402
from cognee.infrastructure.llm import LLMGateway  # noqa: E402
from cognee.modules.ontology.get_default_ontology_resolver import (  # noqa: E402
    get_ontology_resolver_from_env,
)


class GeneratePreviewRequest(BaseModel):
    ison_file_path: str = Field(..., min_length=1)
    dataset_name: str = Field(default="main_dataset", min_length=1)


class RegeneratePreviewRequest(BaseModel):
    feedback: str = Field(..., min_length=1)


class ApprovePreviewRequest(BaseModel):
    pass


class SearchRequest(BaseModel):
    question: str = Field(..., min_length=1)
    dataset_name: Optional[str] = None


class PreviewEntity(BaseModel):
    key: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    description: str = ""


class PreviewRelationship(BaseModel):
    source_key: str = Field(..., min_length=1)
    relation: str = Field(..., min_length=1)
    target_key: str = Field(..., min_length=1)
    description: str = ""


class OntologyPreview(BaseModel):
    title: str = "Ontology Preview"
    top_entity_key: Optional[str] = None
    entities: list[PreviewEntity] = Field(default_factory=list)
    relationships: list[PreviewRelationship] = Field(default_factory=list)


class WorkflowState:
    def __init__(self) -> None:
        self.dataset_name: Optional[str] = None
        self.ison_file_path: Optional[str] = None
        self.ison_text: Optional[str] = None
        self.preview: Optional[OntologyPreview] = None


state = WorkflowState()

app = FastAPI(title="Cognee ISON Ontology Workflow Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _resolve_local_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path.resolve()


def _read_ison_text(ison_file_path: str) -> str:
    path = _resolve_local_path(ison_file_path)
    if not path.exists():
        raise HTTPException(status_code=400, detail=f".ison file not found: {path}")
    text = path.read_text(encoding="utf-8")

    # Validate JSON-like structure early so the user gets a clear error.
    try:
        payload = json.loads(text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse .ison as JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail=".ison content must be a JSON object.")

    return text


def _build_preview_prompt(feedback: Optional[str], previous_preview: Optional[OntologyPreview]) -> tuple[str, str]:
    system_prompt = (
        "You convert ontology-like JSON into a readable ontology preview. "
        "Return only structured output matching the response schema. "
        "Keep descriptions short and factual. "
        "Do not invent entities or relationships not present in the source."
    )

    previous_block = ""
    if previous_preview is not None:
        previous_block = (
            "\n\nPrevious preview:\n"
            + previous_preview.model_dump_json(indent=2)
        )

    feedback_block = ""
    if feedback:
        feedback_block = f"\n\nUser feedback to address:\n{feedback.strip()}"

    text_input = (
        "Source .ison content:\n"
        + (state.ison_text or "")
        + previous_block
        + feedback_block
        + "\n\nGenerate improved ontology preview."
    )

    return text_input, system_prompt


async def _generate_preview_with_llm(
    *,
    feedback: Optional[str] = None,
    previous_preview: Optional[OntologyPreview] = None,
) -> OntologyPreview:
    text_input, system_prompt = _build_preview_prompt(feedback, previous_preview)

    try:
        preview = await LLMGateway.acreate_structured_output(
            text_input=text_input,
            system_prompt=system_prompt,
            response_model=OntologyPreview,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {exc}") from exc

    if not preview.entities:
        raise HTTPException(status_code=500, detail="Generated preview has no entities.")

    return preview


def _sanitize_xml_id(value: str) -> str:
    filtered = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in value.strip())
    if not filtered:
        filtered = "entity"
    if filtered[0].isdigit():
        filtered = f"n_{filtered}"
    return filtered


def _preview_to_owl(preview: OntologyPreview, destination: Path) -> Path:
    ns = "http://example.org/generated-ison-ontology#"

    ET.register_namespace("", ns)
    ET.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    ET.register_namespace("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    ET.register_namespace("owl", "http://www.w3.org/2002/07/owl#")

    rdf = ET.Element(
        "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF",
        attrib={"{http://www.w3.org/XML/1998/namespace}base": ns[:-1]},
    )

    ontology = ET.SubElement(rdf, "{http://www.w3.org/2002/07/owl#}Ontology")
    ontology.set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", ns[:-1])
    ET.SubElement(ontology, "{http://www.w3.org/2000/01/rdf-schema#}label").text = preview.title

    entity_keys: dict[str, str] = {}
    for entity in preview.entities:
        entity_id = _sanitize_xml_id(entity.key)
        entity_keys[entity.key] = entity_id

        cls = ET.SubElement(rdf, "{http://www.w3.org/2002/07/owl#}Class")
        cls.set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", f"{ns}{entity_id}")
        ET.SubElement(cls, "{http://www.w3.org/2000/01/rdf-schema#}label").text = entity.label
        if entity.description.strip():
            ET.SubElement(cls, "{http://www.w3.org/2000/01/rdf-schema#}comment").text = entity.description.strip()

    for relationship in preview.relationships:
        source_id = entity_keys.get(relationship.source_key)
        target_id = entity_keys.get(relationship.target_key)
        if not source_id or not target_id:
            continue

        rel_id = _sanitize_xml_id(f"{relationship.relation}_{relationship.source_key}_{relationship.target_key}")

        prop = ET.SubElement(rdf, "{http://www.w3.org/2002/07/owl#}ObjectProperty")
        prop.set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", f"{ns}{rel_id}")
        ET.SubElement(prop, "{http://www.w3.org/2000/01/rdf-schema#}label").text = relationship.relation

        domain = ET.SubElement(prop, "{http://www.w3.org/2000/01/rdf-schema#}domain")
        domain.set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource", f"{ns}{source_id}")

        range_el = ET.SubElement(prop, "{http://www.w3.org/2000/01/rdf-schema#}range")
        range_el.set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource", f"{ns}{target_id}")

        if relationship.description.strip():
            ET.SubElement(prop, "{http://www.w3.org/2000/01/rdf-schema#}comment").text = relationship.description.strip()

    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(rdf).write(destination, encoding="utf-8", xml_declaration=True)
    return destination


def _build_ontology_config(owl_path: Path) -> dict[str, Any]:
    resolver = get_ontology_resolver_from_env(
        ontology_resolver="rdflib",
        matching_strategy="fuzzy",
        ontology_file_path=str(owl_path),
    )
    return {"ontology_config": {"ontology_resolver": resolver}}


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/generate-preview")
async def generate_preview(request: GeneratePreviewRequest) -> dict[str, Any]:
    ison_path = _resolve_local_path(request.ison_file_path)
    ison_text = _read_ison_text(str(ison_path))

    try:
        add_result = await cognee.add(str(ison_path), dataset_name=request.dataset_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"cognee.add failed for .ison: {exc}") from exc

    state.dataset_name = request.dataset_name
    state.ison_file_path = str(ison_path)
    state.ison_text = ison_text
    state.preview = await _generate_preview_with_llm(feedback=None, previous_preview=None)

    return {
        "message": "ISON ingested and preview generated.",
        "dataset_name": state.dataset_name,
        "ison_file_path": state.ison_file_path,
        "preview": state.preview.model_dump(),
        "add_result": str(add_result),
    }


@app.post("/api/regenerate-preview")
async def regenerate_preview(request: RegeneratePreviewRequest) -> dict[str, Any]:
    if state.ison_text is None:
        raise HTTPException(status_code=400, detail="No active .ison session. Generate preview first.")

    state.preview = await _generate_preview_with_llm(
        feedback=request.feedback,
        previous_preview=state.preview,
    )

    return {
        "message": "Preview regenerated using feedback.",
        "preview": state.preview.model_dump(),
    }


@app.post("/api/approve-preview")
async def approve_preview(_request: ApprovePreviewRequest) -> dict[str, Any]:
    if state.preview is None or state.dataset_name is None:
        raise HTTPException(status_code=400, detail="No preview to approve. Generate preview first.")

    APPROVED_PREVIEW_PATH.write_text(state.preview.model_dump_json(indent=2), encoding="utf-8")

    try:
        await cognee.add(str(APPROVED_PREVIEW_PATH), dataset_name=state.dataset_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"cognee.add failed for approved preview JSON: {exc}") from exc

    owl_path = _preview_to_owl(state.preview, GENERATED_OWL_PATH)
    config = _build_ontology_config(owl_path)

    try:
        cognify_result = await cognee.cognify(
            datasets=[state.dataset_name],
            config=config,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"cognee.cognify failed: {exc}") from exc

    return {
        "message": "Preview approved. OWL generated and cognify executed.",
        "dataset_name": state.dataset_name,
        "owl_file_path": str(owl_path),
        "approved_preview_path": str(APPROVED_PREVIEW_PATH),
        "cognify_result": str(cognify_result),
    }


@app.post("/api/visualize-graph")
async def visualize_graph() -> dict[str, Any]:
    try:
        result = await cognee.visualize_graph(destination_file_path=str(GRAPH_FILE_PATH))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"visualize_graph failed: {exc}") from exc

    return {
        "message": "Graph visualization generated.",
        "graph_url": "/graph/latest",
        "result": str(result),
    }


@app.post("/api/search")
async def search_graph(request: SearchRequest) -> dict[str, Any]:
    dataset_name = request.dataset_name or state.dataset_name
    datasets = [dataset_name] if dataset_name else None

    try:
        results = await cognee.search(
            query_text=request.question.strip(),
            datasets=datasets,
            top_k=50,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"search failed: {exc}") from exc

    return {
        "message": "Search completed.",
        "question": request.question,
        "dataset_name": dataset_name,
        "answer": str(results),
    }


@app.get("/graph/latest")
async def graph_latest() -> FileResponse:
    if not GRAPH_FILE_PATH.exists():
        raise HTTPException(status_code=404, detail="Graph not generated yet. Click Visualize Graph first.")
    return FileResponse(GRAPH_FILE_PATH, media_type="text/html")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
