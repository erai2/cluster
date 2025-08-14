# -*- coding: utf-8 -*-
import os, json, argparse
from typing import Iterable, List
from .parser import load_text_any, yield_sentences
from .condition_filter import filter_stream
from .gpt_extractor_v2 import extract_rule_advanced

def batched(iterable: Iterable[str], n: int) -> Iterable[List[str]]:
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= n:
            yield batch
            batch = []
    if batch: yield batch

def run_pipeline(
    input_path="input/Book1.docx",
    output_path="output/rules_output.json",
    batch_size:int=10,
    max_records:int=None,
    checkpoint_path="intermediate/checkpoint.jsonl",
    resume:bool=True
):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)

    text = load_text_any(input_path)
    sent_stream = filter_stream(yield_sentences(text))

    processed = 0
    results = []
    seen = set()

    if resume and os.path.exists(checkpoint_path):
        with open(checkpoint_path, "r", encoding="utf-8") as ck:
            for line in ck:
                try:
                    rec = json.loads(line)
                    results.append(rec)
                    seen.add(rec.get("source_sent", ""))
                except Exception:
                    pass
        processed = len(results)

    for batch in batched(sent_stream, batch_size):
        out_batch = []
        for s in batch:
            if max_records is not None and processed >= max_records: break
            if s in seen: continue
            try:
                extracted = extract_rule_advanced(s, source=input_path)
                obj = json.loads(extracted)
                obj["id"] = processed + 1
                obj["source_sent"] = s
                out_batch.append(obj)
                processed += 1
            except Exception as e:
                print(f"[ERROR] {processed+1}: {e}")
        if out_batch:
            with open(checkpoint_path, "a", encoding="utf-8") as ck:
                for r in out_batch:
                    ck.write(json.dumps(r, ensure_ascii=False) + "\n")
            results.extend(out_batch)
        if max_records is not None and processed >= max_records: break

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ {len(results)}개 규칙 저장 완료 → {output_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="input/Book1.docx")
    ap.add_argument("--output", default="output/rules_output.json")
    ap.add_argument("--batch-size", type=int, default=10)
    ap.add_argument("--max-records", type=int, default=None)
    ap.add_argument("--checkpoint", default="intermediate/checkpoint.jsonl")
    ap.add_argument("--no-resume", action="store_true")
    args = ap.parse_args()
    run_pipeline(
        input_path=args.input,
        output_path=args.output,
        batch_size=args.batch_size,
        max_records=args.max_records,
        checkpoint_path=args.checkpoint,
        resume=not args.no_resume
    )
