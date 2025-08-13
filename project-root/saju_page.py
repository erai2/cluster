import streamlit as st
from saju_analyzer import SuamSaJuAnalyzer

# Keep a single analyzer instance across reruns
if 'saju_analyzer' not in st.session_state:
    st.session_state.saju_analyzer = SuamSaJuAnalyzer()

analyzer = st.session_state.saju_analyzer

st.title("Suri DB 관리")

# -- 사주 분석 --
st.header("사주 분석")
saju_text = st.text_input("사주 입력 (예: 갑인 병오 정미 무신)")
if st.button("분석하기") and saju_text:
    result = analyzer.analyze_saju(saju_text)
    st.json(result)

# -- 이론/용어 검색 --
st.header("이론/용어 검색")
keyword = st.text_input("키워드", key="search")
if st.button("검색") and keyword:
    rows = analyzer.search_concept(keyword)
    if rows:
        for row in rows:
            st.write(row)
    else:
        st.info("검색 결과가 없습니다.")

# -- 기본 이론 추가 --
st.header("기본 이론 추가")
col1, col2 = st.columns(2)
with col1:
    bt_category = st.text_input("카테고리", key="bt_cat")
    bt_concept = st.text_input("개념", key="bt_concept")
with col2:
    bt_description = st.text_area("설명", key="bt_desc")
if st.button("이론 추가") and bt_category and bt_concept:
    analyzer.add_basic_theory(bt_category, bt_concept, bt_description)
    st.success("이론이 추가되었습니다.")

# -- 용어 추가 --
st.header("용어 추가")
col1, col2 = st.columns(2)
with col1:
    term = st.text_input("용어", key="term")
    meaning = st.text_area("의미", key="meaning")
with col2:
    term_category = st.text_input("분류", key="term_cat")
if st.button("용어 추가") and term:
    analyzer.add_terminology(term, meaning, term_category)
    st.success("용어가 추가되었습니다.")
