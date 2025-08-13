import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
import streamlit as st
from analysis.suri_analysis import load_analysis
from analysis.terminology import load_terms
# 필요시: from analysis.basic_theory import load_theory
# 필요시: from analysis.case_studies import load_cases
import pandas as pd

# ------ 1. 데이터 로딩 ------
suri_data = load_analysis()         # 구조 해석 데이터 (리스트)
terms_data = load_terms()           # 명리 용어 데이터 (리스트)
# theory_data = load_theory()      # 이론 데이터 (옵션)
# cases_data = load_cases()        # 사례 데이터 (옵션)

# ------ 2. UI : 연관검색 입력 ------
st.title("🔎 수암명리 구조해석 & 용어/이론/사례 연관검색")
st.markdown("""
명식·주제·분석·키워드로 구조 해석 DB를 검색하고,  
자동으로 **연관 명리용어/이론/사례**까지 통합 표출합니다.
""")

search_kw = st.text_input("검색어(명식·주제·분석·용어·주요 단어 등)", "")
search_btn = st.button("연관자료 통합검색")

# ------ 3. 구조 해석 DB 검색 ------
if search_btn and search_kw:
    # 1차: 구조 해석 DB 검색
    def item_match(item, kw):
        return any(kw in str(item.get(f, "")) for f in
                   ["명식_천간", "명식_지지", "주제", "구조_표", "천간_분석", "지지_분석", "합충_분석", "현실_응용"])

    suri_hits = [item for item in suri_data if item_match(item, search_kw)]
    st.markdown(f"### 🌀 구조 해석 결과 ({len(suri_hits)}건)")
    if suri_hits:
        for i, item in enumerate(suri_hits):
            st.markdown(f"---\n#### {i+1}. [명식] {item['명식_천간']} / {item['명식_지지']}")
            st.markdown(f"- **주제:** {item['주제']}")
            st.markdown(f"- **[1. 구조 표]**\n{item['구조_표']}")
            st.markdown(f"- **[2. 천간]**\n{item['천간_분석']}")
            st.markdown(f"- **[3. 지지]**\n{item['지지_분석']}")
            st.markdown(f"- **[4. 합충]**\n{item['합충_분석']}")
            st.markdown(f"- **[5. 현실응용]**\n{item['현실_응용']}")
    else:
        st.info("구조 해석 데이터에서 결과 없음.")

    # 2차: 연관키워드 추출 (명식 글자/주제/분석 단어)
    rel_keywords = set()
    for item in suri_hits:
        rel_keywords.update(item["명식_천간"].split())
        rel_keywords.update(item["명식_지지"].split())
        rel_keywords.update(item["주제"].split())
        rel_keywords.update(item["천간_분석"].split())
        rel_keywords.update(item["지지_분석"].split())
        rel_keywords.update(item["합충_분석"].split())
        rel_keywords.update(item["현실_응용"].split())

    # 3차: 명리 용어 연관 검색
    def term_match(term):
        return any(k in term["Term"] or k in term.get("Meaning", "") for k in rel_keywords)
    term_hits = [t for t in terms_data if term_match(t)]

    st.markdown("### 📚 연관 명리 용어")
    if term_hits:
        st.dataframe(pd.DataFrame(term_hits))
    else:
        st.info("연관 용어 결과 없음.")

    # 4차: (선택) 연관 이론/사례
    # if 'theory_data' in locals():
    #     theory_hits = [t for t in theory_data if any(k in t["Concept"] or k in t["Category"] or k in t["Detail"] for k in rel_keywords)]
    #     st.markdown("### 📖 연관 이론")
    #     if theory_hits:
    #         st.dataframe(pd.DataFrame(theory_hits))
    #     else:
    #         st.info("연관 이론 없음.")

    # if 'cases_data' in locals():
    #     case_hits = [c for c in cases_data if any(k in c["Analysis"] or k in c["Result"] for k in rel_keywords)]
    #     st.markdown("### 🔬 연관 실전 사례")
    #     if case_hits:
    #         st.dataframe(pd.DataFrame(case_hits))
    #     else:
    #         st.info("연관 사례 없음.")

    # 5차: (선택) 전체 통합 테이블로 한 번에 출력 (필요시)
else:
    st.info("검색어를 입력 후 [연관자료 통합검색] 버튼을 눌러주세요.")

st.caption("구조 해석/명리 용어/이론/사례 연관 결과를 통합 제공")
