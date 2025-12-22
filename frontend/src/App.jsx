import { useEffect, useMemo, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const styles = {
  layout: {
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif",
    padding: "1.5rem",
    maxWidth: "960px",
    margin: "0 auto",
    color: "#0f172a",
  },
  card: {
    border: "1px solid #e2e8f0",
    borderRadius: "12px",
    padding: "1rem",
    marginBottom: "1.25rem",
    background: "#fff",
    boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
  },
  label: {
    display: "block",
    fontWeight: 600,
    marginBottom: "0.35rem",
  },
  helper: {
    color: "#475569",
    marginTop: "0.4rem",
    lineHeight: 1.4,
  },
  statusPill: (isOnline) => ({
    display: "inline-flex",
    alignItems: "center",
    gap: "0.35rem",
    background: isOnline ? "#ecfeff" : "#fff1f2",
    color: isOnline ? "#0e7490" : "#be123c",
    padding: "0.35rem 0.6rem",
    borderRadius: "999px",
    fontWeight: 600,
    fontSize: "0.95rem",
  }),
  uploadButton: {
    padding: "0.65rem 1rem",
    borderRadius: "10px",
    border: "1px solid #cbd5e1",
    background: "#0ea5e9",
    color: "#fff",
    fontWeight: 700,
    cursor: "pointer",
  },
};

function ScatterPlot({ points, regressionLine }) {
  const width = 760;
  const height = 420;
  const margin = { top: 24, right: 24, bottom: 56, left: 64 };

  const allValues = useMemo(() => {
    const allX = [...points, ...(regressionLine || [])].map((p) => p.x);
    const allY = [...points, ...(regressionLine || [])].map((p) => p.y);
    return {
      minX: allX.length ? Math.min(...allX) : 0,
      maxX: allX.length ? Math.max(...allX) : 1,
      minY: allY.length ? Math.min(...allY) : 0,
      maxY: allY.length ? Math.max(...allY) : 1,
    };
  }, [points, regressionLine]);

  const xRange = allValues.maxX - allValues.minX || 1;
  const yRange = allValues.maxY - allValues.minY || 1;

  const scaleX = (value) =>
    margin.left + ((value - allValues.minX) / xRange) * (width - margin.left - margin.right);
  const scaleY = (value) =>
    height - margin.bottom - ((value - allValues.minY) / yRange) * (height - margin.top - margin.bottom);

  const ticks = (min, max, count = 4) => {
    const step = (max - min) / count;
    return new Array(count + 1).fill(null).map((_, idx) => Number((min + idx * step).toFixed(2)));
  };

  return (
    <svg width={width} height={height} role="img" aria-label="Scatter plot of uploaded data with regression line">
      {/* Axes */}
      <line
        x1={margin.left}
        y1={height - margin.bottom}
        x2={width - margin.right}
        y2={height - margin.bottom}
        stroke="#cbd5e1"
      />
      <line
        x1={margin.left}
        y1={margin.top}
        x2={margin.left}
        y2={height - margin.bottom}
        stroke="#cbd5e1"
      />

      {/* Axis labels */}
      <text x={width / 2} y={height - margin.bottom + 40} textAnchor="middle" fontWeight="600" fill="#0f172a">
        x (horizontal)
      </text>
      <text
        x={16}
        y={height / 2}
        textAnchor="middle"
        fontWeight="600"
        fill="#0f172a"
        transform={`rotate(-90 16 ${height / 2})`}
      >
        y (vertical)
      </text>

      {/* Ticks */}
      {ticks(allValues.minX, allValues.maxX).map((tick) => (
        <g key={`x-${tick}`} transform={`translate(${scaleX(tick)}, ${height - margin.bottom})`}>
          <line y2="6" stroke="#94a3b8" />
          <text y="20" textAnchor="middle" fontSize="12" fill="#475569">
            {tick}
          </text>
        </g>
      ))}
      {ticks(allValues.minY, allValues.maxY).map((tick) => (
        <g key={`y-${tick}`} transform={`translate(${margin.left}, ${scaleY(tick)})`}>
          <line x1="-6" x2="0" stroke="#94a3b8" />
          <text x="-12" y="4" textAnchor="end" fontSize="12" fill="#475569">
            {tick}
          </text>
        </g>
      ))}

      {/* Regression line */}
      {regressionLine?.length === 2 && (
        <line
          x1={scaleX(regressionLine[0].x)}
          y1={scaleY(regressionLine[0].y)}
          x2={scaleX(regressionLine[1].x)}
          y2={scaleY(regressionLine[1].y)}
          stroke="#0ea5e9"
          strokeWidth={2.5}
        />
      )}

      {/* Points */}
      {points.map((point, idx) => (
        <circle
          key={`${point.x}-${point.y}-${idx}`}
          cx={scaleX(point.x)}
          cy={scaleY(point.y)}
          r={5}
          fill="#1d4ed8"
          opacity="0.85"
        >
          <title>
            x: {point.x}, y: {point.y}
          </title>
        </circle>
      ))}
    </svg>
  );
}

export default function App() {
  const [apiStatus, setApiStatus] = useState("Loading...");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");
  const [points, setPoints] = useState([]);
  const [modelResult, setModelResult] = useState(null);
  const [datasetInfo, setDatasetInfo] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/`)
      .then((response) => response.json())
      .then((data) => setApiStatus(data.status || "ok"))
      .catch(() => setApiStatus("unable to reach API"));
  }, []);

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError("");
    setUploadSuccess("");
    setModelResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/datasets/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || "Upload failed");
      }

      const body = await response.json();
      const uploadedPoints = [...body.train, ...body.test];
      setPoints(uploadedPoints);
      setDatasetInfo({
        rows: body.rows,
        train: body.train.length,
        test: body.test.length,
      });
      setUploadSuccess(`Uploaded ${body.rows} rows. Train/Test split: ${body.train.length}/${body.test.length}`);

      const modelResponse = await fetch(`${API_BASE_URL}/model`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: uploadedPoints }),
      });

      if (!modelResponse.ok) {
        const errorBody = await modelResponse.json().catch(() => ({}));
        throw new Error(errorBody.detail || "Model training failed");
      }

      const modelBody = await modelResponse.json();
      setModelResult(modelBody);
    } catch (error) {
      setUploadError(error.message || "Something went wrong");
    } finally {
      setIsUploading(false);
    }
  };

  const isApiOnline = apiStatus === "ok";

  return (
    <main style={styles.layout}>
      <header style={{ marginBottom: "1rem" }}>
        <h1 style={{ fontSize: "2.25rem", marginBottom: "0.35rem" }}>CSV Regression Explorer</h1>
        <p style={{ color: "#475569" }}>
          Upload a CSV with <code>x,y</code> columns, visualize the scatter plot, and fetch a regression line from the
          API.
        </p>
      </header>

      <section style={styles.card}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
          <div>
            <div style={styles.label}>API status</div>
            <div style={styles.statusPill(isApiOnline)}>
              <span style={{ width: 10, height: 10, borderRadius: "50%", background: isApiOnline ? "#0ea5e9" : "#fb7185" }} />
              {apiStatus}
            </div>
          </div>
          <div style={{ textAlign: "right", color: "#475569" }}>
            <div>
              Using base URL: <code>{API_BASE_URL}</code>
            </div>
            <small>Docker default: http://api:8000 • Override locally with VITE_API_BASE_URL</small>
          </div>
        </div>
      </section>

      <section style={styles.card}>
        <label style={styles.label} htmlFor="dataset-upload">
          Upload CSV dataset
        </label>
        <input id="dataset-upload" type="file" accept=".csv,text/csv" onChange={handleUpload} disabled={isUploading} />
        <p style={styles.helper}>
          Your file must include a header row of <code>x,y</code> and both columns must contain numeric values. Download
          the{" "}
          <a href="/sample.csv" download>
            sample CSV
          </a>{" "}
          to get started.
        </p>

        {uploadSuccess && <p style={{ color: "#15803d", fontWeight: 600, marginTop: "0.5rem" }}>{uploadSuccess}</p>}
        {uploadError && <p style={{ color: "#b91c1c", fontWeight: 600, marginTop: "0.5rem" }}>{uploadError}</p>}
      </section>

      {datasetInfo && (
        <section style={styles.card}>
          <h2 style={{ marginTop: 0 }}>Dataset summary</h2>
          <ul style={{ color: "#475569", lineHeight: 1.6 }}>
            <li>
              Total rows: <strong>{datasetInfo.rows}</strong>
            </li>
            <li>
              Train/Test rows:{" "}
              <strong>
                {datasetInfo.train} / {datasetInfo.test}
              </strong>
            </li>
          </ul>
        </section>
      )}

      {points.length > 0 && (
        <section style={styles.card}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2 style={{ margin: 0 }}>Scatter plot</h2>
            {modelResult && (
              <div style={{ textAlign: "right", color: "#475569" }}>
                <div>
                  Regression line: <code>y = {modelResult.slope.toFixed(3)}x + {modelResult.intercept.toFixed(3)}</code>
                </div>
                <div>
                  R²: <strong>{modelResult.r_squared.toFixed(3)}</strong>
                </div>
              </div>
            )}
          </div>
          <p style={styles.helper}>x is mapped to the horizontal axis and y is mapped to the vertical axis.</p>
          <ScatterPlot points={points} regressionLine={modelResult?.line} />
        </section>
      )}
    </main>
  );
}
