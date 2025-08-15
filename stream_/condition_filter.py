# -*- coding: utf-8 -*-
from typing import Iterable

KEYWORDS = ["면","경우","허투","보면","없으면","되면","강하면","약하면",
            "제압","穿","破","沖","合","墓","庫"]

def filter_stream(sent_iter: Iterable[str]) -> Iterable[str]:
    for s in sent_iter:
        if any(k in s for k in KEYWORDS):
            yield s
