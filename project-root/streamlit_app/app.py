import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
#!/usr/bin/env python
import os, io, time
from typing import Optional, List, Any, Dict
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import psycopg2.extras
import os, streamlit as st

# DB_URL 우선순위: Streamlit Secrets > 환경변수 > (옵션) 하드코딩 기본값
DB_URL = (
    st.secrets.get("DB_URL")
    or os.environ.get("DB_URL")
    or None  # 필요하면 "postgresql://user:pass@host:5432/dbname" 기본값을 넣어도 됩니다
)
if not DB_URL:
    st.error("⚠️ DB_URL이 설정되어 있지 않습니다. Secrets 또는 환경변수에 DB_URL을 넣어주세요.")
    st.stop()
@st.cache_resource(show_spinner=False)
def get_conn():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    return conn

def run_query(sql: str, params: tuple | list | None = None) -> list[dict]:
    conn = get_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params or [])
        if cur.description:
            return [dict(r) for r in cur.fetchall()]
        return []

def run_exec(sql: str, params: tuple | list | None = None) -> int:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(sql, params or [])
    conn.commit()
    return cur.rowcount

# ──────────────────────────────────────────────────────────────────────────────
# DDL(최소 테이블): passages, chunk_edits  ※ 이미 있으면 IF NOT EXISTS로 스킵
# ──────────────────────────────────────────────────────────────────────────────
def ensure_schema():
    run_exec("""
        CREATE TABLE IF NOT EXISTS passages (
          pid     SERIAL PRIMARY KEY,
          doc_id  TEXT,
          loc     TEXT,
          kind    TEXT,
          text    TEXT
        );
    """)
    run_exec("""
        CREATE TABLE IF NOT EXISTS chunk_edits (
          pid         INTEGER PRIMARY KEY,         -- passages.pid 사용
          label       TEXT,
          score       REAL,
          edited_text TEXT,
          updated_at  TIMESTAMP DEFAULT NOW()
        );
    """)
ensure_schema()

st.set_page_config(page_title="Databox — DB Direct", layout="wide")
st.title("📦 Databox — Streamlit(DB 직접 연결)")

# ──────────────────────────────────────────────────────────────────────────────
# 업로드 → 간단 인제스트(청크 분할) → passages에 삽입
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("📤 문서 업로드 & Ingest(직접 DB)")
with st.form("upload"):
    files = st.file_uploader("텍스트/ZIP 가능 (PDF/DOCX는 파서 미포함 데모)", type=None, accept_multiple_files=True)
    doc_prefix = st.text_input("doc_id prefix", value="doc")
    max_len = st.number_input("청크 길이(max_len)", min_value=100, value=1200, step=100)
    submitted = st.form_submit_button("업로드 후 인제스트")

def iter_txt_chunks(name: str, data: bytes, max_len: int):
    # 간단 텍스트 추출(데모): txt/md만 처리. ZIP/기타는 스킵 또는 확장 필요
    text = None
    low = name.lower()
    if low.endswith(".txt") or low.endswith(".md"):
        try:
            text = data.decode("utf-8", errors="ignore")
        except Exception:
            pass
    # TODO: pdf/docx 파서는 별도 라이브러리 추가 후 구현
    if not text:
        return
    for i in range(0, len(text), max_len):
        yield text[i:i+max_len]

if submitted:
    if not files:
        st.warning("파일을 선택하세요.")
    else:
        inserted = 0
        with st.spinner("DB 저장 중..."):
            for idx, f in enumerate(files, start=1):
                doc_id = f"{doc_prefix}-{idx}"
                if f.name.lower().endswith(".zip"):
                    st.info(f"ZIP은 이 데모에서 자동 해제하지 않습니다. 개별 txt/md 업로드를 권장합니다.")
                    continue
                for j, chunk in enumerate(iter_txt_chunks(f.name, f.getvalue(), int(max_len)), start=1):
                    run_exec(
                        "INSERT INTO passages (doc_id, loc, kind, text) VALUES (%s,%s,%s,%s)",
                        (doc_id, f"{j}", "text", chunk)
                    )
                    inserted += 1
        st.success(f"Inserted chunks: {inserted}")

# ──────────────────────────────────────────────────────────────────────────────
# DB 요약
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("📊 DB 요약")
counts = {}
for t in ["passages", "chunk_edits"]:
    try:
        r = run_query(f"SELECT COUNT(*) AS c FROM {t};")
        counts[t] = r[0]["c"] if r else 0
    except Exception:
        pass
df_counts = pd.DataFrame([{"table": k, "count": v} for k, v in counts.items()])
if len(df_counts):
    st.dataframe(df_counts, use_container_width=True)
    try:
        fig = px.bar(df_counts, x="table", y="count", title="테이블별 행 수")
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.info("plotly 미설치 시 표로만 표시됩니다.")

# ──────────────────────────────────────────────────────────────────────────────
# 라벨 분포(편집본 기준)
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("🏷️ 라벨 분포")
label_rows = run_query("""
    SELECT label, COUNT(*) AS cnt
    FROM chunk_edits
    WHERE label IS NOT NULL AND label <> ''
    GROUP BY label ORDER BY cnt DESC LIMIT 200;
""")
if label_rows:
    dfl = pd.DataFrame(label_rows)
    st.bar_chart(dfl.set_index("label"))
    st.dataframe(dfl, use_container_width=True, height=260)
else:
    st.info("라벨 편집 데이터가 없습니다. 아래에서 라벨을 추가/수정해 보세요.")

# ──────────────────────────────────────────────────────────────────────────────
# 청크 조회 + 편집(라벨/점수/텍스트) → chunk_edits UPSERT
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("✍️ 청크 정교화 (편집 후 저장)")
with st.form("qform"):
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    with c1:
        q = st.text_input("검색어(q, ILIKE 본문)", value="")
    with c2:
        sel_label = st.text_input("라벨 필터(정확히 일치)", value="")
    with c3:
        limit = st.number_input("limit", min_value=10, max_value=1000, value=200, step=50)
    with c4:
        offset = st.number_input("offset", min_value=0, value=0, step=100)
    do_load = st.form_submit_button("불러오기")

if do_load:
    where = []
    params: list[Any] = []
    if q:
        where.append("p.text ILIKE %s")
        params.append(f"%{q}%")
    if sel_label:
        where.append("ce.label = %s")
        params.append(sel_label)
    where_sql = "WHERE " + " AND ".join(where) if where else ""
    rows = run_query(f"""
        SELECT p.pid, p.doc_id, p.loc, p.kind,
               COALESCE(ce.edited_text, p.text) AS text,
               ce.label, ce.score
        FROM passages p
        LEFT JOIN chunk_edits ce ON ce.pid = p.pid
        {where_sql}
        ORDER BY p.pid ASC
        OFFSET %s LIMIT %s;
    """, params + [int(offset), int(limit)])

    if not rows:
        st.info("검색 결과가 없습니다.")
    else:
        df = pd.DataFrame(rows)
        # 편집 컬럼 보장
        for col in ["label", "score", "edited_text"]:
            if col not in df.columns:
                df[col] = None
        st.caption("표에서 라벨/점수/텍스트를 수정한 다음 저장을 누르세요.")
        edited = st.data_editor(
            df[["pid","doc_id","loc","kind","text","label","score"]],
            num_rows="fixed", use_container_width=True, height=420
        )
        # edited_text는 별도 편집창(간단)
        with st.expander("선택한 pid의 edited_text 편집"):
            sel_pid = st.number_input("pid", min_value=0, value=int(edited.iloc[0]["pid"]) if len(edited) else 0)
            cur_text_row = next((r for r in rows if r["pid"] == sel_pid), None)
            cur_text = (cur_text_row or {}).get("text", "")
            new_text = st.text_area("edited_text", value=cur_text, height=200)
        if st.button("저장(업서트)"):
            payload = []
            # edited DataFrame → 라벨/점수 업데이트
            for _, r in edited.iterrows():
                payload.append({
                    "pid": int(r["pid"]),
                    "label": (None if pd.isna(r.get("label")) else r.get("label")),
                    "score": (None if pd.isna(r.get("score")) else float(r.get("score"))),
                    "edited_text": None
                })
            # edited_text 반영 (선택 pid에 한해)
            if sel_pid:
                for it in payload:
                    if it["pid"] == int(sel_pid):
                        it["edited_text"] = new_text
                        break
                else:
                    payload.append({"pid": int(sel_pid), "label": None, "score": None, "edited_text": new_text})

            # UPSERT 실행
            updated = 0
            for it in payload:
                run_exec("""
                    INSERT INTO chunk_edits (pid, label, score, edited_text, updated_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (pid) DO UPDATE
                    SET label = EXCLUDED.label,
                        score = EXCLUDED.score,
                        edited_text = EXCLUDED.edited_text,
                        updated_at = NOW();
                """, (it["pid"], it["label"], it["score"], it["edited_text"]))
                updated += 1
            st.success(f"업데이트 {updated}건 완료")

st.caption(f"DB_URL host: {DB_URL.split('@')[-1] if '@' in DB_URL else '(hidden)'}")

