import re
import sqlite3
from pathlib import Path
from typing import IO

import pandas as pd
from pypdf import PdfReader
try:  # python-docx may not be installed
    from docx import Document
except Exception:  # pragma: no cover - optional dependency
    Document = None

# 사주 전문 지식 DB의 Part/카테고리 정의
PART_CATEGORIES = {
    "Part 1. 상법(象法)": ["궁위의 상", "십신의 상", "기타 중요 개념"],
    "Part 2. 象의 응용 - 실전 예문": ["관인상생", "정재/편재 차이", "여명 재성 해석"],
    "Part 3. 合法": ["천간합/지지합", "인동 응기"],
}

DB_PATH = Path(__file__).with_name("saju.db")


def _get_conn() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def initialize_db() -> None:
    """Create tables and insert sample data if the database is empty."""
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS basic_theory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            concept TEXT,
            detail TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS terminology (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT,
            meaning TEXT,
            category TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS case_studies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            birth_info TEXT,
            chart TEXT,
            analysis TEXT,
            result TEXT
        )
        """
    )

    cur.execute("SELECT COUNT(*) FROM basic_theory")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO basic_theory (category, concept, detail) VALUES (?, ?, ?)",
            (
                "Part 1. 상법(象法) > 궁위의 상",
                "궁위의 상",
                "궁위는 명식에서 육친의 위치에 따라 드러나는 상징을 해석하는 기초 개념이다.",
            ),
        )

    cur.execute("SELECT COUNT(*) FROM terminology")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO terminology (term, meaning, category) VALUES (?, ?, ?)",
            (
                "십신",
                "천간과 지지의 관계를 열 가지로 분류한 명리학 용어",
                "기초",
            ),
        )

    cur.execute("SELECT COUNT(*) FROM case_studies")
    if cur.fetchone()[0] == 0:
        cur.execute(
            """
            INSERT INTO case_studies (category, birth_info, chart, analysis, result)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "Part 2. 象의 응용 - 실전 예문 > 관인상생",
                "1990-01-01 12:00",
                "갑오년 병자월 정축일 경인시",
                "관인상생 구조로 학업운이 왕성",
                "국가고시 합격",
            ),
        )

    conn.commit()
    conn.close()

def add_basic_theory(category: str, concept: str, detail: str) -> None:
    """Insert a basic theory record into the database."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO basic_theory (category, concept, detail) VALUES (?, ?, ?)",
        (category, concept, detail),
    )
    conn.commit()
    conn.close()

def add_terminology(term: str, meaning: str, category: str) -> None:
    """Insert a terminology record into the database."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO terminology (term, meaning, category) VALUES (?, ?, ?)",
        (term, meaning, category),
    )
    conn.commit()
    conn.close()

def add_case_study(
    birth_info: str,
    chart: str,
    analysis: str,
    result: str,
    category: str,
) -> None:
    """Insert a case study record into the database."""
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO case_studies (category, birth_info, chart, analysis, result)
        VALUES (?, ?, ?, ?, ?)
        """,
        (category, birth_info, chart, analysis, result),
    )
    conn.commit()
    conn.close()

def search_concept(keyword: str) -> pd.DataFrame:
    """Search the basic theory table for a keyword."""
    like = f"%{keyword}%"
    conn = _get_conn()
    df = pd.read_sql_query(
        "SELECT category, concept, detail FROM basic_theory WHERE category LIKE ? OR concept LIKE ? OR detail LIKE ?",
        conn,
        params=(like, like, like),
    )
    conn.close()
    return df


def search_terminology(keyword: str) -> pd.DataFrame:
    """Search the terminology table for a keyword."""
    like = f"%{keyword}%"
    conn = _get_conn()
    df = pd.read_sql_query(
        "SELECT term, meaning, category FROM terminology WHERE term LIKE ? OR meaning LIKE ? OR category LIKE ?",
        conn,
        params=(like, like, like),
    )
    conn.close()
    return df


def search_case_study(keyword: str) -> pd.DataFrame:
    """Search the case studies table for a keyword."""
    like = f"%{keyword}%"
    conn = _get_conn()
    df = pd.read_sql_query(
        """
        SELECT category, birth_info, chart, analysis, result
        FROM case_studies
        WHERE category LIKE ? OR birth_info LIKE ? OR chart LIKE ? OR analysis LIKE ? OR result LIKE ?
        """,
        conn,
        params=(like, like, like, like, like),
    )
    conn.close()
    return df


def get_basic_theory_all() -> pd.DataFrame:
    conn = _get_conn()
    df = pd.read_sql_query("SELECT category, concept, detail FROM basic_theory", conn)
    conn.close()
    return df


def get_terminology_all() -> pd.DataFrame:
    conn = _get_conn()
    df = pd.read_sql_query("SELECT term, meaning, category FROM terminology", conn)
    conn.close()
    return df


def get_case_studies_all() -> pd.DataFrame:
    conn = _get_conn()
    df = pd.read_sql_query(
        "SELECT category, birth_info, chart, analysis, result FROM case_studies",
        conn,
    )
    conn.close()
    return df


# ---- 파일 업로드 및 자동 필드 추출 유틸리티 ----

def read_file_content(file: IO[bytes]) -> str:
    """업로드된 다양한 문서 형식에서 텍스트를 추출합니다."""
    name = getattr(file, "name", "")
    ext = name.split(".")[-1].lower()
    if ext in {"txt", "csv", "md"}:
        content = file.read().decode("utf-8", errors="ignore")
    elif ext == "pdf":
        reader = PdfReader(file)
        content = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif ext == "docx":
        if Document is None:
            raise ValueError("docx 처리를 위해 python-docx가 필요합니다.")
        document = Document(file)
        content = "\n".join(p.text for p in document.paragraphs)
    else:
        raise ValueError("지원하지 않는 파일 형식입니다.")
    file.seek(0)  # 이후 다른 처리를 위해 파일 포인터를 초기화
    return content


def _extract_fields(text: str, mapping: dict[str, list[str]]) -> dict[str, str]:
    """텍스트에서 주어진 키 매핑에 따라 값을 추출합니다."""
    result: dict[str, str] = {}
    for field, keys in mapping.items():
        for key in keys:
            pattern = re.compile(rf"{key}\s*[:：]\s*(.*)")
            match = pattern.search(text)
            if match:
                result[field] = match.group(1).strip()
                break
    return result


def parse_basic_theory_text(text: str) -> dict[str, str]:
    mapping = {
        "part": ["part", "단원"],
        "category": ["category", "카테고리", "분류"],
        "concept": ["concept", "개념"],
        "detail": ["detail", "상세", "설명"],
    }
    return _extract_fields(text, mapping)


def parse_terminology_text(text: str) -> dict[str, str]:
    mapping = {
        "part": ["part", "단원"],
        "category": ["category", "분류"],
        "term": ["term", "용어"],
        "meaning": ["meaning", "의미"],
    }
    return _extract_fields(text, mapping)


def parse_case_study_text(text: str) -> dict[str, str]:
    mapping = {
        "part": ["part", "단원"],
        "category": ["category", "분류"],
        "birth_info": ["birth_info", "출생정보"],
        "chart": ["chart", "명식"],
        "analysis": ["analysis", "분석"],
        "result": ["result", "결과"],
    }
    return _extract_fields(text, mapping)

