import { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [docId, setDocId] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const upload = async () => {
    if (!file) return alert("Choose a file");
    const form = new FormData();
    form.append("file", file);
    const res = await axios.post("http://localhost:8000/upload", form);
    setDocId(res.data.doc_id);
    alert("Uploaded successfully!");
  };

  const ask = async () => {
    if (!docId) return alert("Upload a document first");
    const form = new FormData();
    form.append("doc_id", docId);
    form.append("question", question);
    // Example
    const res = await axios.post("http://127.0.0.1:8000/ask", form);
    setAnswer(res.data.answer);
  };

  return (
    <div style={{ padding: 24 }}>
      <h1>SmartDoc Assistant 🧠</h1>

      <div>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={upload}>Upload</button>
      </div>

      <div style={{ marginTop: 20 }}>
        <input
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button onClick={ask}>Ask</button>
      </div>

      <div style={{ marginTop: 20 }}>
        <h3>Answer:</h3>
        <p>{answer}</p>
      </div>
    </div>
  );
}

export default App;
