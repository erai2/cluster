# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Iterable
import re

from normalization.hanja_norm import normalize_for_index

def _read_txt(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def _read_docx(p: Path) -> str:
    try:
        from docx import Document
    except Exception as e:
        raise RuntimeError("python-docx 미설치: pip install python-docx") from e
    doc = Document(str(p))
    return "\n".join(par.text for par in doc.paragraphs)

def _read_pdf(p: Path) -> str:
    try:
        from pdfminer.high_level import extract_text
    except Exception as e:
        raise RuntimeError("pdfminer.six 미설치: pip install pdfminer.six") from e
    return extract_text(str(p))

def parse_file(path_like) -> str:
    p = Path(path_like)
    ext = p.suffix.lower()
    if ext == ".txt":
        raw = _read_txt(p)
    elif ext == ".docx":
        raw = _read_docx(p)
    elif ext == ".pdf":
        raw = _read_pdf(p)
    else:
        raise ValueError(f"지원하지 않는 형식: {ext}")
    return normalize_for_index(raw)

# 문장 스트림 (여기 한 곳에서만 제공)
_SENT_SPLIT = re.compile(r'(?<=[다요음함\.!\?])\s+')
def yield_sentences(text: str) -> Iterable[str]:
    text = re.sub(r'\n+', ' ', text)
    for s in _SENT_SPLIT.split(text):
        s = s.strip()
        if len(s) > 1:
            yield s
