# -*- coding: utf-8 -*-
from typing import Iterable
import re
from .normalization.hanja_norm import normalize_for_index
try:
    from docx import Document
except Exception:
    Document = None

def extract_text_from_docx(path: str) -> str:
    if Document is None:
        raise RuntimeError("python-docx가 필요합니다. pip install python-docx")
    doc = Document(path)
    raw = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return normalize_for_index(raw)

def extract_text_from_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    return normalize_for_index(raw)

def load_text_any(path: str) -> str:
    p = path.lower()
    if p.endswith(".docx"):
        return extract_text_from_docx(path)
    elif p.endswith(".txt"):
        return extract_text_from_txt(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")

_SENT_SPLIT = re.compile(r'(?<=[다요음함\.!\?])\s+')

def yield_sentences(text: str) -> Iterable[str]:
    text = re.sub(r'\n+', ' ', text)
    for s in _SENT_SPLIT.split(text):
        s = s.strip()
        if len(s) >= 2:
            yield s
