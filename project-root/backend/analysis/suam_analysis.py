import re
from pathlib import Path
from typing import Tuple, List

from .db_utils import load_json, save_json

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "suri_analysis.json"


def load_analysis() -> List[dict]:
    """Load stored analysis entries."""
    return load_json(DB_PATH)


def save_analysis(data: List[dict]):
    """Persist analysis entries."""
    save_json(DB_PATH, data)
    llm = ChatOpenAI(openai_api_key=api_key, temperature=0.2, model="gpt-3.5-turbo")
    response = llm.invoke(prompt)
    text = response.content
    parts = re.split(r"\n?[\d\.]+[\)\.] ", text)
    if len(parts) < 6:
        table = tiangan_desc = dizhi_desc = hapchung_desc = reality = ""
    else:
        _, table, tiangan_desc, dizhi_desc, hapchung_desc, reality = parts[:6]
    return [table.strip(), tiangan_desc.strip(), dizhi_desc.strip(), hapchung_desc.strip(), reality.strip()], prompt
