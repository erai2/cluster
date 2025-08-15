import streamlit as st
import sqlite3
import openai
import json
import time
from pathlib import Path
import pandas as pd
import os

# 환경설정
DB_FILE = "terms.db"
openai.api_key = st.secrets["OPENAI_API_KEY"]

# DB 초기화
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS terms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        term TEXT,
        definition TEXT,
        explanation TEXT,
        examples TEXT,
        rules TEXT,
        keywords TEXT,
        source_file TEXT
    )''')
    conn.commit()
    conn.close()

# 텍스트 추출 (txt, md, pdf, docx)
def extract_text(file):
    suffix = Path(file.name).suffix.lower()
    if suffix in [".txt", ".md"]:
        return file.read().decode("utf-8", errors="ignore")
    elif suffix == ".pdf":
        from pdfminer.high_level import extract_text
        tmp_path = Path("uploads") / f"{int(time.time())}.pdf"
        tmp_path.parent.mkdir(exist_ok=True)
        with open(tmp_path, "wb") as f:
            f.write(file.read())
        return extract_text(str(tmp_path))
    elif suffix in [".docx"]:
        import docx
        tmp_path = Path("uploads") / f"{int(time.time())}.docx"
        tmp_path.parent.mkdir(exist_ok=True)
        with open(tmp_path, "wb") as f:
            f.write(file.read())
        doc = docx.Document(str(tmp_path))
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        st.error(f"지원하지 않는 파일 형식: {suffix}")
        return ""

# AI 구조화
def extract_terms(text, filename):
    prompt = f"""
    아래 문서에서 주요 용어, 정의, 설명, 사례, 규칙, 키워드를 다음 JSON 배열 구조로 출력하세요.
    단, 원문을 최대한 보존하고 누락 없이 추출하세요.

    JSON 형식:
    [
      {{
        "category": "...",
        "term": "...",
        "definition": "...",
        "explanation": "...",
        "examples": ["..."],
        "rules": ["..."],
        "keywords": ["..."],
        "source_file": "{filename}"
      }}
    ]

    문서:
    {text}
    """
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return json.loads(resp.choices[0].message.content)

# DB 저장
def save_to_db(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for item in data:
        c.execute('''INSERT INTO terms (category, term, definition, explanation, examples, rules, keywords, source_file)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (item.get('category'), item.get('term'), item.get('definition'),
                   item.get('explanation'), json.dumps(item.get('examples', []), ensure_ascii=False),
                   json.dumps(item.get('rules', []), ensure_ascii=False),
                   json.dumps(item.get('keywords', []), ensure_ascii=False),
                   item.get('source_file')))
    conn.commit()
    conn.close()

# UI
st.set_page_config(page_title="문서 → 용어 DB", layout="wide")
st.title("📚 문서 업로드 → AI 구조화 → DB 저장")

init_db()

uploaded = st.file_uploader("문서 업로드", type=["txt", "md", "pdf", "docx"])
if uploaded:
    with st.spinner("텍스트 추출 중..."):
        text = extract_text(uploaded)
    if text:
        with st.spinner("AI로 용어 구조화 중..."):
            terms = extract_terms(text, uploaded.name)
        save_to_db(terms)
        st.success(f"{len(terms)}개의 용어가 DB에 저장되었습니다.")

st.subheader("📂 DB 저장 내용")
conn = sqlite3.connect(DB_FILE)
df = pd.read_sql("SELECT * FROM terms", conn)
conn.close()
st.dataframe(df, use_container_width=True)