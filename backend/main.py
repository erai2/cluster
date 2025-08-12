from __future__ import annotations

from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse
import io
import csv
import time

app = FastAPI(title="HCJ API", version="1.0.0")

# CORS: 프론트(vite dev, streamlit)와 개발 호스트 모두 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Rule(BaseModel):
    id: int = Field(..., description="unique rule id")
    condition: str
    action: str


# 데모용 인메모리 저장
_rules: List[Rule] = [
    Rule(id=1, condition="text contains 'error'", action="label='issue'"),
    Rule(id=2, condition="score > 0.9", action="route='priority'"),
]


@app.get("/health")
def health():
    return {"status": "ok", "ts": int(time.time())}


@app.get("/rules", response_model=List[Rule])
def list_rules():
    return _rules


@app.get("/rules/{rule_id}", response_model=Rule)
def get_rule(rule_id: int):
    for r in _rules:
        if r.id == rule_id:
            return r
    raise HTTPException(status_code=404, detail="Rule not found")


@app.post("/rules", response_model=Rule, status_code=201)
def add_rule(rule: Rule):
    if any(r.id == rule.id for r in _rules):
        raise HTTPException(status_code=409, detail="Duplicate id")
    _rules.append(rule)
    return rule


@app.put("/rules/{rule_id}", response_model=Rule)
def edit_rule(rule_id: int, rule: Rule):
    for i, r in enumerate(_rules):
        if r.id == rule_id:
            _rules[i] = rule
            return rule
    raise HTTPException(status_code=404, detail="Rule not found")


@app.delete("/rules/{rule_id}", status_code=204)
def delete_rule(rule_id: int):
    for i, r in enumerate(_rules):
        if r.id == rule_id:
            _rules.pop(i)
            return
    raise HTTPException(status_code=404, detail="Rule not found")


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    # 데모: 파일 이름/크기만 回
    data = await file.read()
    return {
        "filename": file.filename,
        "size": len(data),
        "content_type": file.content_type,
    }


@app.get("/export")
def export_rules_csv():
    # CSV 스트림으로 내보내기
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["id", "condition", "action"])
    writer.writeheader()
    for r in _rules:
        writer.writerow(r.model_dump())
    buf.seek(0)
    return StreamingResponse(
        io.BytesIO(buf.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="rules.csv"'},
    )
