import os
import psycopg2
from psycopg2.extras import Json

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # 원문 보관함
    cur.execute("""
    CREATE TABLE IF NOT EXISTS original_docs (
        id SERIAL PRIMARY KEY,
        filename TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 구조화 데이터
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
    conn.close()
