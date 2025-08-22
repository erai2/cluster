import re, json, os
import pandas as pd

def parse_cases(text: str):
    """
    텍스트에서 <사례>, 규칙, 조건/결과 패턴을 자동 추출
    """
    results = []

    # 1) <사례> 블록 추출
    case_blocks = re.findall(r"<사례.*?>.*?(?=<사례|\Z)", text, flags=re.DOTALL)
    for i, block in enumerate(case_blocks, 1):
        results.append({
            "id": f"case_{i}",
            "type": "사례",
            "content": block.strip()
        })

    # 2) 조건 → 결과 규칙 추출 (예: "OO하면 → XX된다")
    rules = re.findall(r"(.+?)\s*→\s*(.+)", text)
    for i, (cond, res) in enumerate(rules, 1):
        results.append({
            "id": f"rule_{i}",
            "type": "규칙",
            "condition": cond.strip(),
            "result": res.strip()
        })

    return results

def save_cases(results, out_dir="data/processed", fname="cases.json"):
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, fname)
    csv_path = os.path.join(out_dir, fname.replace(".json", ".csv"))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    df = pd.DataFrame(results)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    return json_path, csv_path