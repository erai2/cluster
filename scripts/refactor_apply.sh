#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "🚀 리팩토링 시작"

# 0) 타겟 초기화
rm -rf suri
mkdir -p suri/{api,core,models,services}

# 1) 소스 후보 → suri 로 병합 (있는 것만)
for SRC in app src backend fucc ; do
  if [ -d "$SRC" ]; then
    echo "📦 병합: $SRC → suri/"
    # 최상위 api/ core/ models/ services/ 는 보존 병합
    [ -d "$SRC/api" ]      && rsync -a "$SRC/api/"      "suri/api/"      || true
    [ -d "$SRC/routers" ]  && rsync -a "$SRC/routers/"  "suri/api/"      || true
    [ -d "$SRC/routes" ]   && rsync -a "$SRC/routes/"   "suri/api/"      || true
    [ -d "$SRC/core" ]     && rsync -a "$SRC/core/"     "suri/core/"     || true
    [ -d "$SRC/models" ]   && rsync -a "$SRC/models/"   "suri/models/"   || true
    [ -d "$SRC/services" ] && rsync -a "$SRC/services/" "suri/services/" || true

    # api 외 루트 파이썬 파일들도 복사(충돌 나면 마지막 것이 우선)
    find "$SRC" -maxdepth 1 -type f -name "*.py" -exec rsync -a {} suri/ \; || true
  fi
done

# 2) __init__.py 보정
touch suri/__init__.py
touch suri/api/__init__.py
touch suri/core/__init__.py
touch suri/models/__init__.py
touch suri/services/__init__.py

# 3) 라우터 자동 탐색 → main.py 생성
python3 scripts/generate_main.py

# 4) 캐시 제거
find suri -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "✅ 완료: suri/main.py 생성됨"
echo "👉 실행: uvicorn suri.main:app --reload"
