# ISON Ontology Demo (React + Python)

This demo implements the workflow:

1. Ingest only `.ison` via `cognee.add()`.
2. Generate a readable JSON ontology preview from `.ison` using `LLMGateway`.
3. User reviews preview:
   - `No` -> user feedback -> regenerate preview via LLM.
   - `Yes` -> approve preview.
4. On approval:
   - Save approved preview JSON.
   - Generate `.owl` from approved preview.
   - Run `cognee.cognify(...)` using generated OWL through ontology config.
5. Visualize graph.
6. Search graph.

## Run

```bash
cd <project_root>/cognee-community/experimental/dlt_demo
pip install -r requirements.txt
uvicorn backend:app --reload --port 8010
```

Open:

- http://127.0.0.1:8010

## Notes

- Required: valid LLM and Cognee environment setup (`LLM_API_KEY` etc.). Check the [cognee repo](https://github.com/topoteretes/cognee) for more details.
- Example `.ison` path in UI defaults to `test_data/taxonomy.ison`.
- Generated artifacts:
  - `test_data/approved_preview.json`
  - `test_data/generated_ontology.owl`
- `.owl` is not ingested via `add()`; it is used only in `cognify` ontology config.
