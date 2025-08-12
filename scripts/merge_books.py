import argparse
import os
import re
from glob import glob

TOC_HEADER = "# 목차\n\n"

def collect_files(indir: str):
    # Book1~6 + pdf_* 순으로 정렬
    books = sorted(glob(os.path.join(indir, "Book[1-9]*.md")))
    pdfs  = sorted(glob(os.path.join(indir, "pdf_*.md")))
    return books + pdfs

def make_toc(md: str):
    # H1/H2만 목차로 (###는 생략)
    lines = md.splitlines()
    toc = [TOC_HEADER]
    for ln in lines:
        if ln.startswith("# "):
            title = ln[2:].strip()
            anchor = "#" + re.sub(r"[^\w\- ]", "", title).strip().lower().replace(" ", "-")
            toc.append(f"- [{title}]({anchor})")
        elif ln.startswith("## "):
            title = ln[3:].strip()
            anchor = "#" + re.sub(r"[^\w\- ]", "", title).strip().lower().replace(" ", "-")
            toc.append(f"  - [{title}]({anchor})")
    return "\n".join(toc) + "\n\n---\n\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    files = collect_files(args.indir)
    buff = []
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        buff.append(f"# {name}\n")
        with open(f, "r", encoding="utf-8") as fh:
            buff.append(fh.read().strip())
        buff.append("\n\n---\n")

    merged = "\n".join(buff).strip()
    toc = make_toc(merged)
    final = toc + merged

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as out:
        out.write(final)

    print(f"📚 병합 완료 → {args.output}")

if __name__ == "__main__":
    main()
