import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import openai
from dotenv import load_dotenv
import uuid
import faiss
import numpy as np

load_dotenv()
openai.api_key = os.getenv(
    "API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOC_STORE = {}
EMB_STORE = None
ID_TO_DOCID = []


def get_embedding(text):
    resp = openai.Embedding.create(model="text-embedding-3-small", input=text)
    return np.array(resp["data"][0]["embedding"], dtype=np.float32)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        # Read bytes
        contents = await file.read()
        # Decode safely to string
        text_str = contents.decode("utf-8", errors="ignore")

        doc_id = str(uuid.uuid4())
        DOC_STORE[doc_id] = text_str

        # Generate embedding
        emb = get_embedding(text_str)
        global EMB_STORE, ID_TO_DOCID
        if EMB_STORE is None:
            d = emb.shape[0]
            EMB_STORE = faiss.IndexFlatL2(d)
        EMB_STORE.add(np.expand_dims(emb, axis=0))
        ID_TO_DOCID.append(doc_id)
        return {"doc_id": doc_id, "message": "uploaded"}

    except Exception as e:
        return {"error": str(e)}


@app.post("/ask")
async def ask(doc_id: str = Form(...), question: str = Form(...)):
    if EMB_STORE is None:
        return {"answer": "No documents uploaded yet."}
    q_emb = get_embedding(question)
    D, I = EMB_STORE.search(np.expand_dims(q_emb, axis=0), k=1)
    nearest_doc_id = ID_TO_DOCID[int(I[0][0])]
    context = DOC_STORE[nearest_doc_id]
    prompt = f"Document:\n{context}\n\nQuestion: {question}\nAnswer based only on this document."
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return {"answer": resp["choices"][0]["message"]["content"]}
