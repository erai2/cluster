import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
import streamlit as st
import pandas as pd
from analysis.suri_analysis import load_analysis, save_analysis, llm_auto_analysis
from analysis.config import load_api_key

st.title("🌀 구조 해석 입력 및 자동 분석")

db = load_analysis()
col1, col2 = st.columns([2,1])
with col1:
    tiangan = st.text_input("천간", key="in1_page1")
    dizhi = st.text_input("지지", key="in2_page1")
    
table_summary = st.text_area("1. 구조 표 요약", height=60, key="f1_page1")
tiangan_analysis = st.text_area("2. 천간 분석", height=80, key="f2_page1")
dizhi_analysis = st.text_area("3. 지지 분석", height=80, key="f3_page1")
hapchung_analysis = st.text_area("4. 합/충/형/파 분석", height=80, key="f4_page1")
reality_application = st.text_area("5. 현실 응용/해석", height=100, key="f5_page1")
prompt_field = st.text_area("프롬프트(질문 내용)", height=100, key="f6_page1")

if auto_btn and api_key and tiangan and dizhi and topic:
    with st.spinner("LLM 구조 해석 중..."):
        st.session_state.f1_page1, st.session_state.f2_page1, st.session_state.f3_page1, st.session_state.f4_page1, st.session_state.f5_page1 = fields
        st.session_state.f6_page1 = prompt_used
        st.success("자동 구조 해석이 완료되었습니다. 내용 수정 후 저장 가능!")

if st.button("💾 구조 해석 저장"):
    entry = {
        "명식_천간": tiangan,
        "명식_지지": dizhi,
        "주제": topic,
        "구조_표": st.session_state.get("f1_page1", ""),
        "천간_분석": st.session_state.get("f2_page1", ""),
        "지지_분석": st.session_state.get("f3_page1", ""),
        "합충_분석": st.session_state.get("f4_page1", ""),
        "현실_응용": st.session_state.get("f5_page1", ""),
        "프롬프트": st.session_state.get("f6_page1", ""),
    }
    db.append(entry)
    save_analysis(db)
    st.success("구조 해석이 저장되었습니다.")

