const { useState } = React;

function App() {
  const [isonFilePath, setIsonFilePath] = useState("test_data/taxonomy.ison");
  const [datasetName, setDatasetName] = useState("main_dataset");

  const [preview, setPreview] = useState(null);
  const [feedback, setFeedback] = useState("");
  const [showFeedback, setShowFeedback] = useState(false);

  const [status, setStatus] = useState("Idle");
  const [busy, setBusy] = useState(false);

  const [graphUrl, setGraphUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [searchAnswer, setSearchAnswer] = useState("");

  async function callApi(path, body) {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Request failed");
    }
    return data;
  }

  async function generatePreview() {
    setBusy(true);
    setStatus("Ingesting .ison and generating JSON preview via LLM...");
    setPreview(null);
    setFeedback("");
    setShowFeedback(false);
    try {
      const data = await callApi("/api/generate-preview", {
        ison_file_path: isonFilePath,
        dataset_name: datasetName,
      });
      setPreview(data.preview || null);
      setStatus(data.message);
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function regeneratePreview() {
    if (!feedback.trim()) {
      setStatus("Please provide feedback first.");
      return;
    }

    setBusy(true);
    setStatus("Regenerating preview using your feedback...");
    try {
      const data = await callApi("/api/regenerate-preview", {
        feedback,
      });
      setPreview(data.preview || null);
      setFeedback("");
      setShowFeedback(false);
      setStatus(data.message);
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function approvePreview() {
    setBusy(true);
    setStatus("Ingesting approved JSON, generating OWL, and running cognify...");
    try {
      const data = await callApi("/api/approve-preview", {});
      setStatus(data.message);
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function visualizeGraph() {
    setBusy(true);
    setStatus("Generating graph visualization...");
    try {
      const data = await callApi("/api/visualize-graph", {});
      setGraphUrl(data.graph_url);
      setStatus(data.message);
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function runSearch() {
    if (!question.trim()) {
      setStatus("Please enter a question first.");
      return;
    }

    setBusy(true);
    setStatus("Searching the generated graph...");
    setSearchAnswer("");
    try {
      const data = await callApi("/api/search", {
        question,
        dataset_name: datasetName || null,
      });
      setSearchAnswer(data.answer || "No answer.");
      setStatus(data.message);
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="wrap">
      <div className="card">
        <h1>Cognee ISON Ontology Demo</h1>
        <p className="muted">
          Ingest .ison, generate readable preview with LLM, iterate with feedback, then ingest approved JSON and run cognify with generated OWL.
        </p>
      </div>

      <div className="card">
        <h3>1) Ingest .ison + Generate Preview</h3>
        <div className="grid">
          <label>
            .ison file path
            <input
              value={isonFilePath}
              onChange={(e) => setIsonFilePath(e.target.value)}
              placeholder="test_data/taxonomy.ison"
            />
          </label>

          <label>
            Dataset name
            <input
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              placeholder="main_dataset"
            />
          </label>
        </div>

        <div className="row" style={{ marginTop: 12 }}>
          <button disabled={busy} onClick={generatePreview}>
            Generate Preview
          </button>
        </div>
      </div>

      <div className="card">
        <h3>2) Review Preview</h3>
        <p className="muted">If preview looks correct, click Yes. If not, click No and provide feedback for regeneration.</p>

        {preview ? <pre>{JSON.stringify(preview, null, 2)}</pre> : <p className="muted">No preview yet.</p>}

        <div className="row" style={{ marginTop: 8 }}>
          <button className="no" disabled={busy || !preview} onClick={() => setShowFeedback(true)}>
            No
          </button>
          <button className="yes" disabled={busy || !preview} onClick={approvePreview}>
            Yes
          </button>
        </div>

        {showFeedback ? (
          <div className="grid" style={{ marginTop: 10 }}>
            <label>
              What is wrong with this preview?
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Example: rename entity labels, adjust top entity, fix relation directions."
              />
            </label>
            <div className="row">
              <button disabled={busy} onClick={regeneratePreview}>
                Regenerate With Feedback
              </button>
            </div>
          </div>
        ) : null}
      </div>

      <div className="card">
        <h3>3) Graph Visualization</h3>
        <div className="row">
          <button className="ghost" disabled={busy} onClick={visualizeGraph}>
            Visualize Graph
          </button>
        </div>
        {graphUrl ? (
          <div style={{ marginTop: 12 }}>
            <p>
              Open graph in new tab: <a href={graphUrl} target="_blank" rel="noreferrer">{graphUrl}</a>
            </p>
            <iframe className="graph-frame" title="Graph Visualization" src={graphUrl} />
          </div>
        ) : null}
      </div>

      <div className="card">
        <h3>4) Search Graph</h3>
        <p className="muted">Ask a question about the generated graph.</p>
        <div className="grid" style={{ marginTop: 10 }}>
          <label>
            Question
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What entities are most connected?"
            />
          </label>
        </div>
        <div className="row" style={{ marginTop: 10 }}>
          <button disabled={busy} onClick={runSearch}>
            Search
          </button>
        </div>
        {searchAnswer ? (
          <div style={{ marginTop: 10 }}>
            <pre>{searchAnswer}</pre>
          </div>
        ) : null}
      </div>

      <div className="card">
        <div className="status">Status: {status}</div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
