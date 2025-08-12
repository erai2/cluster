"""FastAPI 이미지 업로드 엔드포인트 테스트"""

from pathlib import Path
import sys
from fastapi.testclient import TestClient

# 프로젝트 루트를 PYTHONPATH에 추가
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from backend.main import app

client = TestClient(app)


def test_upload_image(tmp_path):
    """샘플 이미지를 업로드하고 응답을 확인합니다."""
    img_path = tmp_path / "sample.png"
    img_path.write_bytes(b"fake image data")

    with img_path.open("rb") as f:
        response = client.post(
            "/upload-image",
            files={"file": ("sample.png", f, "image/png")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sample.png"
