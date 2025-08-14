# -*- coding: utf-8 -*-
import re
from typing import Iterable, List

KEYWORDS = ["면","허투","보면","경우","없으면","되면","강하면","약하면",
            "제압","穿","破","沖","合","墓","庫"]

def extract_condition_candidates(text: str) -> List[str]:
    text = re.sub(r'\n+', ' ', text)
    parts = re.split(r'(?<=[다요음함\.!\?])\s+', text)
    return [s.strip() for s in parts if any(k in s for k in KEYWORDS)]

def filter_stream(sent_iter: Iterable[str]) -> Iterable[str]:
    for s in sent_iter:
        if any(k in s for k in KEYWORDS):
            yield s
