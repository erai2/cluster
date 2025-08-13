import json
from pathlib import Path


def load_json(path: Path):
    path = Path(path)
    if path.exists():
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    return []


def save_json(path: Path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
