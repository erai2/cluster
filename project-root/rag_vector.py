import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from docx import Document
import fitz  # PyMuPDF

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_FILE = "faiss_index.bin"
META_FILE = "doc_chunks.pkl"
CHUNK_SIZE = 500

model = SentenceTransformer(EMBEDDING_MODEL)

def chunk_text(text, size=CHUNK_SIZE):
    return [text[i:i+size] for i in range(0, len(text), size)]

def read_pdf(path):
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def read_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def get_documents(doc_dir):
    contents = []
    for filename in os.listdir(doc_dir):
        path = os.path.join(doc_dir, filename)
        if filename.lower().endswith(".txt"):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                contents.append((filename, f.read()))
        elif filename.lower().endswith(".pdf"):
            contents.append((filename, read_pdf(path)))
        elif filename.lower().endswith(".docx"):
            contents.append((filename, read_docx(path)))
    return contents

def build_faiss_index(doc_dir):
    docs = get_documents(doc_dir)
    chunks, metadatas = [], []

    for fname, content in docs:
        for chunk in chunk_text(content):
            chunks.append(chunk)
            metadatas.append({"file": fname, "text": chunk})

    embeddings = model.encode(chunks, show_progress_bar=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

    with open(META_FILE, "wb") as f:
        pickle.dump(metadatas, f)

    faiss.write_index(index, INDEX_FILE)

def get_answer_from_documents(question: str, doc_dir: str) -> str:
    if not os.path.exists(INDEX_FILE) or not os.path.exists(META_FILE):
        build_faiss_index(doc_dir)

    index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, "rb") as f:
        metadatas = pickle.load(f)

    q_embedding = model.encode([question])
    D, I = index.search(np.array(q_embedding), k=3)

    answers = []
    for idx in I[0]:
        if idx < len(metadatas):
            answers.append(f"[{metadatas[idx]['file']}] {metadatas[idx]['text']}")

    return "\n\n".join(answers) if answers else "📄 관련 문서에서 답변을 찾을 수 없습니다."
