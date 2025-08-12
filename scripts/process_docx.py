import argparse
import os
from docx import Document
from utils_text import transform_lines

def docx_to_lines(path: str):
    doc = Document(path)
    lines = []
    for p in doc.paragraphs:
        t = (p.text or "").replace("\u3000", " ").strip()
        if t:
            lines.append(t)
        else:
            lines.append("")  # 빈 줄 유지
    return lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    infile = args.input
    base = os.path.splitext(os.path.basename(infile))[0]
    outfile = os.path.join(args.outdir, f"{base}.md")

    lines = docx_to_lines(infile)
    md = transform_lines(lines)

    os.makedirs(args.outdir, exist_ok=True)
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"✅ DOCX → MD: {outfile}")

if __name__ == "__main__":
    main()
