# Debian Slim 기반 Node.js 20 이미지 사용
FROM node:20-slim

WORKDIR /app

# 필수 OS 패키지 설치 (빌드 툴 포함, 필요 시)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3 \
    git \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치
COPY frontend/package.json frontend/package-lock.json* ./

# npm 캐시 정리 후 설치 (optional deps 문제 방지)
RUN npm cache clean --force && npm install

# 소스 복사
COPY frontend/ ./

EXPOSE 5173

# Vite dev 서버 실행
CMD ["npm", "run", "dev", "--", "--host"]
