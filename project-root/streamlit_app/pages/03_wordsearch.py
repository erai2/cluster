import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
import streamlit as st
import pandas as pd
from analysis.terminology import load_terms, save_terms, search_term

st.title("📚 명리 용어 사전")

keyword = st.text_input("용어 검색")
if st.button("검색"):
    results = search_term(keyword)
    if results:
        st.dataframe(pd.DataFrame(results))
    else:
        st.info("검색 결과가 없습니다.")

st.markdown("---\n### 용어 등록")
term = st.text_input("용어")
meaning = st.text_input("의미")
if st.button("추가"):
    terms = load_terms()
    terms.append({"Term": term, "Meaning": meaning})
    save_terms(terms)
    st.success("저장되었습니다.")
    st.dataframe(pd.DataFrame(terms))
