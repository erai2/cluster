import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
import streamlit as st
import pandas as pd
from analysis.suri_analysis import load_analysis, save_analysis

st.title("📚 구조 해석 검색 및 수정")

db = load_analysis()

keyword = st.text_input("키워드 검색", key="kw_page2")
field_sel = st.selectbox(
    "검색 필드",
    ["전체", "명식_천간", "명식_지지", "주제", "천간_분석", "지지_분석", "합충_분석", "현실_응용"],
)
search_btn = st.button("🔍 검색")

if search_btn:
    results = []
    for idx, item in enumerate(db):
        target = " ".join(map(str, item.values())) if field_sel == "전체" else item.get(field_sel, "")
        if keyword and keyword in target:
            results.append((idx, item))
    if results:
        st.info(f"{len(results)}건 검색됨 (클릭시 편집)")
        for idx, item in results:
            st.markdown(f"---\n#### {idx+1}. [명식: {item['명식_천간']} / {item['명식_지지']}] | {item['주제']}")
            st.markdown(f"- **[1. 구조표]**\n{item['구조_표']}")
            st.markdown(f"- **[2. 천간]**\n{item['천간_분석']}")
            st.markdown(f"- **[3. 지지]**\n{item['지지_분석']}")
            st.markdown(f"- **[4. 합충]**\n{item['합충_분석']}")
            st.markdown(f"- **[5. 현실응용]**\n{item['현실_응용']}")
            if st.button("이 해석 불러와 편집", key=f"edit_{idx}"):
                st.session_state.edit_idx = idx
                st.session_state.in1_page1 = item["명식_천간"]
                st.session_state.in2_page1 = item["명식_지지"]
                st.session_state.in3_page1 = item["주제"]
                st.session_state.f1_page1 = item["구조_표"]
                st.session_state.f2_page1 = item["천간_분석"]
                st.session_state.f3_page1 = item["지지_분석"]
                st.session_state.f4_page1 = item["합충_분석"]
                st.session_state.f5_page1 = item["현실_응용"]
                st.session_state.f6_page1 = item["프롬프트"]
                st.success("입력 페이지에 데이터가 불러와졌습니다.")
    else:
        st.info("검색 결과가 없습니다.")

st.markdown("---\n#### 전체 구조 해석 데이터")
df = pd.DataFrame(db)
if not df.empty:
    st.dataframe(df)
