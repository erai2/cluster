import streamlit as st
import sqlite3
import pandas as pd
import openai
import json
import tempfile
import os
import numpy as np

from PyPDF2 import PdfReader
import docx
import chardet

# === 설정 ===
DB_FILE = "terms.db"
openai.api_key = st.secrets["OPENAI_API_KEY"]

# === DB 초기화 ===
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            term TEXT,
            definition TEXT,
            explanation TEXT,
            examples TEXT,
            rules TEXT,
            keywords TEXT,
            source_file TEXT,
            embedding BLOB,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# === 파일 텍스트 추출 ===
def extract_text(file):
    ext = file.name.split(".")[-1].lower()
    if ext in ["txt", "md"]:
        raw = file.read()
        try:
            encoding = chardet.detect(raw)["encoding"] or "utf-8"
            return raw.decode(encoding)
        except:
            return raw.decode("utf-8", errors="ignore")

    elif ext == "pdf":
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        reader = PdfReader(tmp_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        os.remove(tmp_path)
        return text

    elif ext in ["docx", "doc"]:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        doc = docx.Document(tmp_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        os.remove(tmp_path)
        return text

    elif ext == "csv":
        df = pd.read_csv(file)
        return "\n".join(df.astype(str).apply(lambda x: " ".join(x), axis=1))

    else:
        st.error("지원하지 않는 파일 형식입니다.")
        return ""

# === AI 분석 ===
def extract_terms(text):
    prompt = f"""
    다음 문서에서 주요 용어, 정의, 설명, 사례, 규칙, 키워드를 JSON 배열로 출력:
    - category: 카테고리
    - term: 용어명
    - definition: 짧은 정의
    - explanation: 긴 설명
    - examples: 사례 배열
    - rules: 규칙 배열
    - keywords: 키워드 배열

    문서:
    {text}
    """
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )
    try:
        return json.loads(resp.choices[0].message.content)
    except:
        st.error("AI 응답 파싱 실패")
        return []

# === 임베딩 생성 ===
def get_embedding(text):
    resp = openai.Embedding.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(resp["data"][0]["embedding"], dtype=np.float32)

# === DB 저장 ===
def save_to_db(data, source_file):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for item in data:
        emb = get_embedding(item.get('definition', '') + " " + item.get('explanation', ''))
        c.execute("""
            INSERT INTO terms (category, term, definition, explanation, examples, rules, keywords, source_file, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.get('category', ''),
            item.get('term', ''),
            item.get('definition', ''),
            item.get('explanation', ''),
            json.dumps(item.get('examples', []), ensure_ascii=False),
            json.dumps(item.get('rules', []), ensure_ascii=False),
            json.dumps(item.get('keywords', []), ensure_ascii=False),
            source_file,
            emb.tobytes()
        ))
    conn.commit()
    conn.close()

# === 의미 기반 검색 ===
def semantic_search(query, top_n=5):
    q_emb = get_embedding(query)
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM terms", conn)
    conn.close()

    if df.empty:
        return pd.DataFrame()

    df["embedding"] = df["embedding"].apply(lambda x: np.frombuffer(x, dtype=np.float32))
    df["score"] = df["embedding"].apply(lambda e: np.dot(q_emb, e) / (np.linalg.norm(q_emb) * np.linalg.norm(e)))
    df = df.sort_values("score", ascending=False).head(top_n)
    return df.drop(columns=["embedding"])

# === UI ===
st.set_page_config(page_title="문서 AI 분석 DB", layout="wide")
st.title("📄 문서 → AI 용어 분석 DB (임베딩 검색 포함)")

init_db()

tab1, tab2, tab3 = st.tabs(["📥 업로드/분석", "🔍 DB 검색/수정", "🤖 의미 기반 검색"])

with tab1:
    uploaded = st.file_uploader("문서 업로드", type=["txt","md","pdf","docx","doc","csv"])
    if uploaded:
        text = extract_text(uploaded)
        if text:
            st.subheader("📌 원본 텍스트 (일부 미리보기)")
            st.text_area("원본", text[:3000], height=200)
            if st.button("AI 분석 실행"):
                terms = extract_terms(text)
                if terms:
                    save_to_db(terms, uploaded.name)
                    st.success(f"{len(terms)} 개의 용어 저장 완료 (파일: {uploaded.name})")
                    st.json(terms)

with tab2:
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM terms", conn)
    conn.close()
    search = st.text_input("키워드 검색")
    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]
    st.dataframe(df, use_container_width=True)

with tab3:
    query = st.text_input("자연어로 검색 (예: '부모성과 관련된 규칙')")
    if query:
        results = semantic_search(query)
        if not results.empty:
            st.dataframe(results, use_container_width=True)
        else:
            st.info("검색 결과가 없습니다.")