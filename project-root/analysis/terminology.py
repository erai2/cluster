from .db_utils import load_json, save_json
import time

DATA_FILE = "data/terms.json"

def add_term(category, term, definition, example=""):
    terms = load_json(DATA_FILE, default=[])
    new_term = {
        "id": int(time.time()),
        "category": category,
        "term": term,
        "definition": definition,
        "example": example
    }
    terms.append(new_term)
    save_json(DATA_FILE, terms)
    return new_term

def search_terms(keyword):
    terms = load_json(DATA_FILE, default=[])
    return [t for t in terms if keyword.lower() in t["term"].lower()]
