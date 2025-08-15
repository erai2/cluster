import streamlit as st
import psycopg2
import pandas as pd
import json
import openai
from datetime import datetime

# =========================
# 환경 설정 (Secrets)
# =========================
openai.api_key = st.secrets["OPENAI_API_KEY"]

DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "dbname": st.secrets["DB_NAME"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASS"],
    "port": st.secrets["DB_PORT"]
}

# =========================
# DB 연결 함수
# =========================
def get_conn():
    return psycopg2.connect(**DB_CONFIG)

# =========================
# DB 초기화
# =========================
def init_db():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS original_docs (
            id SERIAL PRIMARY KEY,
            filename TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS structured_terms (
            id SERIAL PRIMARY KEY,
            category TEXT,
            term TEXT,
            definition TEXT,
            explanation TEXT,
            examples JSONB,
            rules JSONB,
            keywords JSONB,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

# =========================
# DB 저장 함수
# =========================
def save_original(filename, content):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO original_docs (filename, content) VALUES (%s, %s)",
            (filename, content)
        )
        conn.commit()

def save_structured(data, source_file):
    with get_conn() as conn, conn.cursor() as cur:
        for item in data:
            cur.execute("""
                INSERT INTO structured_terms
                (category, term, definition, explanation, examples, rules, keywords, source_file)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                item.get('category'), item.get('term'), item.get('definition'),
                item.get('explanation'),
                json.dumps(item.get('examples', []), ensure_ascii=False),
                json.dumps(item.get('rules', []), ensure_ascii=False),
                json.dumps(item.get('keywords', []), ensure_ascii=False),
                source_file
            ))
        conn.commit()

# =========================
# AI 구조화 함수
# =========================
def ai_extract_terms(text):
    prompt = f"""
    다음 문서에서 주요 용어, 정의, 설명, 사례, 규칙, 키워드를 JSON 배열로 출력:
    {text}
    """
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return json.loads(resp.choices[0].message.content)

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="문서 AI 구조화 & PostgreSQL", layout="wide")
st.title("📄 문서 AI 구조화 & PostgreSQL 저장기")

# 초기화
init_db()

tab1, tab2 = st.tabs(["1️⃣ 업로드 & 저장", "2️⃣ DB 조회/수정/삭제"])

# -------------------------
# 1️⃣ 업로드 & 저장
# -------------------------
with tab1:
    uploaded = st.file_uploader("문서 업로드", type=["txt", "md", "pdf", "docx"])
    if uploaded:
        raw_text = uploaded.read().decode("utf-8", errors="ignore")
        st.subheader("📌 추출된 원문 (미리보기)")
        st.text_area("원문", raw_text[:2000], height=300)

        if st.button("AI 구조화 & DB 저장"):
            # 1. 원문 저장
            save_original(uploaded.name, raw_text)

            # 2. AI 구조화
            with st.spinner("AI가 문서를 분석 중입니다..."):
                structured_data = ai_extract_terms(raw_text)

            # 3. 구조화 데이터 저장
            save_structured(structured_data, uploaded.name)

            st.success(f"✅ {len(structured_data)} 개 항목 저장 완료!")

# -------------------------
# 2️⃣ DB 조회/수정/삭제
# -------------------------
with tab2:
    st.subheader("📂 원문 목록")
    orig_df = pd.read_sql("SELECT * FROM original_docs ORDER BY id DESC", get_conn())
    st.dataframe(orig_df, use_container_width=True)

    st.subheader("📂 구조화 데이터")
    df = pd.read_sql("SELECT * FROM structured_terms ORDER BY id DESC", get_conn())
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if st.button("💾 수정 저장"):
        with get_conn() as conn, conn.cursor() as cur:
            for _, row in edited_df.iterrows():
                cur.execute("""
                    UPDATE structured_terms
                    SET category=%s, term=%s, definition=%s, explanation=%s
                    WHERE id=%s
                """, (row['category'], row['term'], row['definition'], row['explanation'], row['id']))
        st.success("수정 완료!")

    del_id = st.number_input("삭제할 ID", step=1)
    if st.button("🗑 삭제"):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM structured_terms WHERE id=%s", (del_id,))
        st.warning(f"{del_id}번 삭제 완료")
