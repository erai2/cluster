from pathlib import Path
from typing import List

from .db_utils import load_json, save_json

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "terminology.json"


def load_terms() -> List[dict]:
    return load_json(DB_PATH)


def save_terms(data: List[dict]):
    save_json(DB_PATH, data)


def search_term(keyword: str) -> List[dict]:
    terms = load_terms()
    return [t for t in terms if keyword in t.get("Term", "") or keyword in t.get("Meaning", "")]
