# 현재 활성 모델 및 벡터DB 상태 관리
import os
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma

class ModelManager:
    def __init__(self):
        self.current_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        self.embedding_db = None

    def load_model(self, model_name: str):
        """LLM 교체"""
        self.current_model = model_name
        return ChatOpenAI(model=model_name, temperature=0)

    def load_vector_db(self, persist_dir: str):
        """벡터 DB 로드"""
        self.embedding_db = Chroma(persist_directory=persist_dir)
        return self.embedding_db

    def get_status(self) -> Dict:
        return {
            "current_model": self.current_model,
            "embedding_loaded": self.embedding_db is not None
        }

# 싱글톤 인스턴스
model_manager = ModelManager()
