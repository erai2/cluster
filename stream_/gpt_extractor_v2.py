# -*- coding: utf-8 -*-
"""
This is a placeholder extractor that returns a deterministic JSON structure.
Replace `extract_rule_advanced` with your model call if needed.
"""
import json

def extract_rule_advanced(sentence: str, source: str = "") -> str:
    # Minimal heuristic: split by '면' or '경우' as IF/THEN marker
    if "면" in sentence:
        parts = sentence.split("면", 1)
        cond = parts[0].strip()
        then = parts[1].strip()
    elif "경우" in sentence:
        parts = sentence.split("경우", 1)
        cond = parts[0].strip()
        then = parts[1].strip()
    else:
        cond = sentence.strip()
        then = ""
    obj = {
        "if": cond,
        "then": then,
        "source": source,
        "confidence": 0.6 if then else 0.3
    }
    return json.dumps(obj, ensure_ascii=False)
