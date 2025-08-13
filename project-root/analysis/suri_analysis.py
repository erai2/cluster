from openai import OpenAI
from .config import load_api_key
from .db_utils import save_json, load_json
from .prompts import SURI_ANALYSIS_PROMPT
import time
import os

DATA_FILE = "data/suri_analysis.json"

client = OpenAI(api_key=load_api_key())

def analyze_suri(data):
    prompt = SURI_ANALYSIS_PROMPT.format(data=data)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    result = response.choices[0].message.content.strip()

    # 저장
    record = {
        "id": int(time.time()),
        "input": data,
        "output": result
    }
    existing = load_json(DATA_FILE, default=[])
    existing.append(record)
    save_json(DATA_FILE, existing)

    return result
