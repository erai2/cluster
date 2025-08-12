#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -q -r requirements.txt

chmod +x scripts/refactor_apply.sh
./scripts/refactor_apply.sh

echo "▶ 서버 기동..."
uvicorn suri.main:app --reload
