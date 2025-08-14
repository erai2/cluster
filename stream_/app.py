import os
from pathlib import Path
import streamlit as st
from parser import parse_file
from normalization.hanja_norm import normalize_hanja
from condition_filter import filter_sentences
from gpt_extractor_v2 import extract_rules

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("환경변수 OPENAI_API_KEY가 설정되지 않았습니다.")
    st.stop()

st.title("📚 규칙 추출기")

uploaded_file = st.file_uploader("분석할 파일을 업로드하세요", type=["txt", "docx", "pdf"])

if uploaded_file is not None:
    input_path = Path("input") / uploaded_file.name
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("파일 처리 중...")
    text = parse_file(input_path)
    text = normalize_hanja(text)
    candidate_sents = filter_sentences(text.split("\n"))
    rules = extract_rules(candidate_sents, OPENAI_API_KEY)

    st.success("추출 완료!")
    st.json(rules)

    output_path = Path("output") / f"{input_path.stem}_rules.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(rules))
    st.download_button("📥 결과 다운로드", data=str(rules), file_name=f"{input_path.stem}_rules.json")
