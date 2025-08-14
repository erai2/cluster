import os
import sys
from pathlib import Path
from parser import parse_file
from normalization.hanja_norm import normalize_hanja
from condition_filter import filter_sentences
from gpt_extractor_v2 import extract_rules

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    sys.exit("[ERROR] OPENAI_API_KEY 환경변수를 설정하세요.")

def run_pipeline(input_path: Path, output_dir: Path):
    output_dir.mkdir(exist_ok=True, parents=True)
    text = parse_file(input_path)
    text = normalize_hanja(text)
    sentences = text.split("\n")
    candidate_sents = filter_sentences(sentences)
    rules = extract_rules(candidate_sents, OPENAI_API_KEY)

    (output_dir / f"{input_path.stem}_rules.json").write_text(str(rules), encoding="utf-8")
    print(f"[DONE] Saved: {output_dir}/{input_path.stem}_rules.json")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python -m rule_extractor_advanced.main <input-file>")
    input_file = Path(sys.argv[1])
    run_pipeline(input_file, Path(__file__).parent / "output")
