import { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function App() {
  const [apiStatus, setApiStatus] = useState("Loading...");

  useEffect(() => {
    fetch(`${API_BASE_URL}/`)
      .then((response) => response.json())
      .then((data) => setApiStatus(data.status || "ok"))
      .catch(() => setApiStatus("unable to reach API"));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", padding: "1.5rem" }}>
      <h1>Vite + React</h1>
      <p>
        API Base URL: <strong>{API_BASE_URL}</strong>
      </p>
      <p>
        API Status: <strong>{apiStatus}</strong>
      </p>
      <p>Update the FastAPI service in the <code>api</code> folder and the React app in <code>frontend</code>.</p>
    </main>
  );
}
