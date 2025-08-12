#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RAW_DIR="$ROOT_DIR/data/raw"
OUT_DIR="$ROOT_DIR/data/processed"

mkdir -p "$OUT_DIR"

echo "▶ DOCX 처리..."
for f in "$RAW_DIR"/Book*.docx; do
  [ -f "$f" ] || continue
  python "$ROOT_DIR/scripts/process_docx.py" --input "$f" --outdir "$OUT_DIR"
done

echo "▶ PDF 처리..."
for f in "$RAW_DIR"/*.pdf; do
  [ -f "$f" ] || continue
  python "$ROOT_DIR/scripts/process_pdf.py" --input "$f" --outdir "$OUT_DIR"
done

echo "▶ 병합/목차 생성..."
python "$ROOT_DIR/scripts/merge_books.py" --indir "$OUT_DIR" --output "$OUT_DIR/merged_books.md"

echo "✅ 완료: $OUT_DIR/merged_books.md"
