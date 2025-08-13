import os
import toml

def load_api_key():
    # 우선 .env 환경변수에서 로드
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key

    # secret.toml에서 로드
    if os.path.exists("secret.toml"):
        data = toml.load("secret.toml")
        if "OPENAI_API_KEY" in data:
            return data["OPENAI_API_KEY"]

    raise ValueError("❌ OPENAI_API_KEY를 환경변수 또는 secret.toml에 설정하세요.")
