import argparse
import os
from pypdf import PdfReader
from utils_text import transform_lines

def pdf_to_lines(path: str):
    reader = PdfReader(path)
    lines = []
    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").replace("\u3000", " ")
        # 페이지 경계 시 H2 헤더 삽입 (선택)
        if i == 0:
            lines.append(f"")
        else:
            lines.append(f"")  # 빈 줄로만 구분, 필요시 "## p.{i+1}" 등 추가 가능
        # 줄 단위로 분리
        for ln in text.splitlines():
            # PDF 추출 특성상 하이픈 분리/붙음 이슈가 있으면 여기에 보정 규칙 추가
            lines.append(ln)
    return lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    infile = args.input
    base = os.path.splitext(os.path.basename(infile))[0]
    outfile = os.path.join(args.outdir, f"pdf_{base}.md")

    lines = pdf_to_lines(infile)
    md = transform_lines(lines)

    os.makedirs(args.outdir, exist_ok=True)
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"✅ PDF → MD: {outfile}")

if __name__ == "__main__":
    main()
