# -*- coding: utf-8 -*-
"""
Hanja normalization utilities:
- canon_hanja: fold compatibility/variant forms (禄, 祿 -> 祿)
- annotate_readings: attach [hangul] reading to key Hanja for indexing (e.g., 祿[록])
- normalize_for_index: convenience pipeline
"""
import json, re, unicodedata
from pathlib import Path

_RES = Path(__file__).resolve().parents[1] / "resources"

def _load(name):
    with open(_RES / name, "r", encoding="utf-8") as f:
        return json.load(f)

VAR = _load("hanja_variant_map.json")   # variant -> canonical hanja
READ = _load("hanja_reading_map.json")  # hanja -> [readings]

def canon_hanja(text: str) -> str:
    if not text: return text
    t = unicodedata.normalize("NFKC", text)
    # greedy phrase replace first (longest keys first), then char replace
    keys = sorted(VAR.keys(), key=len, reverse=True)
    for k in keys:
        t = t.replace(k, VAR[k])
    return t

def annotate_readings(text: str) -> str:
    if not text: return text
    def repl(ch):
        if ch in READ:
            rd = READ[ch][0]
            return f"{ch}[{rd}]"
        return ch
    return "".join(repl(c) for c in text)

def normalize_for_index(text: str) -> str:
    t = canon_hanja(text)
    # spacing & ideographic space
    t = re.sub(r"\u3000", " ", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\s*\n\s*", "\n", t)
    # annotate selected hanja with readings for better search recall
    t = annotate_readings(t)
    return t
