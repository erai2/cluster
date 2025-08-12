import streamlit as st
import os
import pandas as pd
import json
import openai
import re

from model_utils import extract_cluster_keywords
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

from saju_database import (
    PART_CATEGORIES,
    initialize_db,
    add_basic_theory,
    add_terminology,
    add_case_study,
    search_concept,
    search_terminology,
    search_case_study,
    read_file_content,
    parse_basic_theory_text,
    parse_terminology_text,
    parse_case_study_text,
    get_basic_theory_all,
    get_terminology_all,
    get_case_studies_all,
)

# --- 0. 기본 설정 ---
st.set_page_config(page_title="통합 문서 분석 시스템", layout="wide")
st.title("🧩 통합 문서 분석 시스템")
st.info("문서 기반 Q&A, 요약, 군집 분석과 더불어 텍스트를 구조화하여 시각화용 JSON으로 추출할 수 있습니다.")

# 업로드 디렉토리 설정
UPLOAD_DIR = "./uploaded_docs"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- 사주 전문 지식 DB 초기화 ---
initialize_db()


# ---- 사주 DB 입력 폼에서 사용할 파일 업로드 콜백 ----

def handle_basic_theory_file() -> None:
    file = st.session_state.get("bt_file")
    if not file:
        return
    text = read_file_content(file)
    data = parse_basic_theory_text(text)
    if part := data.get("part"):
        st.session_state.bt_part = part if part in PART_CATEGORIES else st.session_state.bt_part
    if category := data.get("category"):
        part_key = st.session_state.get("bt_part")
        if part_key in PART_CATEGORIES and category in PART_CATEGORIES[part_key]:
            st.session_state.bt_category = category
    st.session_state.bt_concept = data.get("concept", "")
    st.session_state.bt_detail = data.get("detail", "")


def handle_terminology_file() -> None:
    file = st.session_state.get("term_file")
    if not file:
        return
    text = read_file_content(file)
    data = parse_terminology_text(text)
    if part := data.get("part"):
        st.session_state.term_part = part if part in PART_CATEGORIES else st.session_state.term_part
    if category := data.get("category"):
        part_key = st.session_state.get("term_part")
        if part_key in PART_CATEGORIES and category in PART_CATEGORIES[part_key]:
            st.session_state.term_category = category
    st.session_state.term_term = data.get("term", "")
    st.session_state.term_meaning = data.get("meaning", "")


def handle_case_file() -> None:
    file = st.session_state.get("case_file")
    if not file:
        return
    text = read_file_content(file)
    data = parse_case_study_text(text)
    if part := data.get("part"):
        st.session_state.case_part = part if part in PART_CATEGORIES else st.session_state.case_part
    if category := data.get("category"):
        part_key = st.session_state.get("case_part")
        if part_key in PART_CATEGORIES and category in PART_CATEGORIES[part_key]:
            st.session_state.case_category = category
    st.session_state.case_birth = data.get("birth_info", "")
    st.session_state.case_chart = data.get("chart", "")
    st.session_state.case_analysis = data.get("analysis", "")
    st.session_state.case_result = data.get("result", "")

# --- 1. 핵심 로직 함수 ---

# 기존 함수들 (load_documents, build_rag_chain, summarize_text)
@st.cache_data
def load_documents(path_or_directory):
    """디렉토리 또는 단일 파일 경로에서 문서를 로드합니다."""
    docs = []
    paths_to_load = []

    if os.path.isdir(path_or_directory):
        for filename in os.listdir(path_or_directory):
            paths_to_load.append(os.path.join(path_or_directory, filename))
    elif os.path.isfile(path_or_directory):
        paths_to_load.append(path_or_directory)

    for path in paths_to_load:
        filename = os.path.basename(path)
        try:
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(path)
            elif filename.endswith((".docx", ".doc")):
                loader = UnstructuredWordDocumentLoader(path)
            elif filename.endswith((".txt", ".csv")):
                loader = TextLoader(path, encoding="utf-8")
            else:
                continue
            docs.extend(loader.load())
        except Exception as e:
            st.warning(f"'{filename}' 파일 로딩 중 오류 발생: {e}")
    return docs

@st.cache_resource
def build_rag_chain(_docs, openai_api_key):
    """RAG 체인을 빌드합니다."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(_docs)
    if not splits: return None
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        return ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(temperature=0, openai_api_key=openai_api_key),
            retriever=vectorstore.as_retriever(),
            memory=memory
        )
    except Exception as e:
        st.error(f"RAG 체인 빌드 중 오류 발생: {e}")
        return None

@st.cache_data
def summarize_text(text, openai_api_key, model="gpt-3.5-turbo"):
    """AI를 사용하여 문서 내용을 요약합니다."""
    client = ChatOpenAI(temperature=0, openai_api_key=openai_api_key, model_name=model)
    prompt = f"다음 텍스트를 핵심 내용만 간추려 한국어로 명확하게 요약해줘:\n\n{text[:4000]}"
    return client.invoke(prompt).content


def gpt_summary(text_list, openai_api_key):
    """Summarize a list of texts into a representative topic using GPT."""
    openai.api_key = openai_api_key
    joined = "\n".join(f"- {t}" for t in text_list)
    prompt = f"다음 문장들을 요약하여 주제를 한 문장으로 말해줘:\n{joined}\n\n주제:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60,
        temperature=0.7,
    )
    return response.choices[0].message["content"].strip()

# --- JSON 추출을 위한 신규 함수들 ---
@st.cache_data
def parse_text_files_for_json(file_paths):
    """여러 텍스트 파일 내용을 읽고 Part, Section으로 구조화합니다."""
    structured_data = {"parts": []}
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            part_title = os.path.basename(file_path).split('.')[0]
            current_part = {"partTitle": part_title, "sections": []}
            structured_data["parts"].append(current_part)
            
            sections = re.split(r'\n##\s*(.*?)\n', content)
            if len(sections) > 1:
                sections.pop(0)
                for i in range(0, len(sections), 2):
                    section_title = sections[i].strip()
                    section_content = sections[i+1].strip()
                    if section_title:
                        current_part["sections"].append({
                            "sectionTitle": section_title,
                            "content": section_content,
                            "summary": "", "keywords": []
                        })
        except Exception as e:
            st.warning(f"{os.path.basename(file_path)} 파일 처리 중 오류: {e}")
    return structured_data

@st.cache_data
def analyze_structure_with_ai(_structured_data, openai_api_key):
    """구조화된 데이터의 각 섹션을 AI로 분석합니다."""
    if not openai_api_key:
        st.error("OpenAI API 키가 필요합니다.")
        return _structured_data

    client = ChatOpenAI(temperature=0, openai_api_key=openai_api_key, model_name="gpt-3.5-turbo")
    total_sections = sum(len(p.get('sections', [])) for p in _structured_data.get('parts', []))
    progress_bar = st.progress(0, "AI 분석 시작...")
    processed_count = 0

    for part in _structured_data.get('parts', []):
        for section in part.get('sections', []):
            try:
                prompt = f"""
                다음 텍스트를 분석하여 JSON 형식으로 응답해줘.
                1. "summary": 텍스트의 핵심 내용을 한국어로 한 문장으로 요약.
                2. "keywords": 가장 중요한 키워드를 5개까지 한국어 문자열 배열로 추출.
                텍스트: --- {section['content'][:3000]} ---
                JSON 응답:
                """
                response_content = client.invoke(prompt).content
                json_str = response_content[response_content.find('{'):response_content.rfind('}')+1]
                analysis = json.loads(json_str)
                section['summary'] = analysis.get('summary', '요약 실패')
                section['keywords'] = analysis.get('keywords', [])
            except Exception:
                section['summary'] = "AI 분석 오류"
                section['keywords'] = ["오류"]
            processed_count += 1
            progress_bar.progress(processed_count / total_sections, f"분석 중... ({processed_count}/{total_sections})")
    
    progress_bar.empty()
    return _structured_data

# --- 2. Streamlit UI 구성 ---

# 세션 상태 변수 초기화
if 'summary_result' not in st.session_state: st.session_state.summary_result = None
if 'cluster_result_df' not in st.session_state: st.session_state.cluster_result_df = None
if 'structured_data' not in st.session_state: st.session_state.structured_data = None

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    if 'OPENAI_API_KEY' in st.secrets:
        openai_api_key = st.secrets['OPENAI_API_KEY']
        st.success("API Key가 안전하게 로드되었습니다.")
    else:
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        if not openai_api_key: st.warning("OpenAI API 키를 입력해주세요.")

    files = sorted(os.listdir(UPLOAD_DIR))
    if files:
        selected_file_for_delete = st.selectbox("삭제할 파일 선택", options=[""] + files)
        if selected_file_for_delete and st.button("선택한 파일 삭제"):
            os.remove(os.path.join(UPLOAD_DIR, selected_file_for_delete))
            st.success(f"'{selected_file_for_delete}' 삭제 완료!")
            st.rerun()

# 메인 화면 탭
tabs = st.tabs([
    "💬 문서 기반 Q&A (RAG)",
    "✍️ 문서 요약",
    "📊 문서 군집 분석",
    "📜 텍스트 구조화 및 JSON 내보내기",
    "🔮 사주 지식 DB"
])

# --- Tab 1: RAG Q&A ---
with tabs[0]:
    st.subheader("AI에게 문서에 대해 질문하세요")
    if not openai_api_key: st.warning("사이드바에서 OpenAI API 키를 먼저 입력해주세요.")
    elif not files: st.info("질문할 문서를 먼저 업로드해주세요.")
    else:
        if "rag_chain" not in st.session_state or st.button("문서 변경, 체인 재생성"):
            with st.spinner("문서를 분석하여 RAG 체인을 빌드하는 중..."):
                docs = load_documents(UPLOAD_DIR)
                if docs:
                    st.session_state.rag_chain = build_rag_chain(docs, openai_api_key)
                    if st.session_state.rag_chain: st.success("RAG 체인 빌드 완료!")
                    else: st.error("RAG 체인 빌드에 실패했습니다.")
                else: st.error("문서 로딩에 실패했습니다.")
        
        if "messages" not in st.session_state: st.session_state.messages = []
        for message in st.session_state.messages:
            with st.chat_message(message["role"]): st.markdown(message["content"])

        if prompt := st.chat_input("질문을 입력하세요..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("답변 생성 중..."):
                    if "rag_chain" in st.session_state and st.session_state.rag_chain:
                        response = st.session_state.rag_chain({"question": prompt})
                        answer = response['answer']
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else: st.error("RAG 체인이 초기화되지 않았습니다.")

# --- Tab 2: 문서 요약 ---
with tabs[1]:
    st.subheader("선택한 문서를 AI가 요약합니다")
    if not openai_api_key: st.warning("사이드바에서 OpenAI API 키를 먼저 입력해주세요.")
    elif not files: st.info("요약할 문서를 먼저 업로드해주세요.")
    else:
        selected_file = st.selectbox("요약할 파일 선택", options=[""] + files, key="summary_select")
        if selected_file and st.button("선택한 파일 요약하기"):
            with st.spinner(f"'{selected_file}' 파일 요약 중..."):
                docs = load_documents(os.path.join(UPLOAD_DIR, selected_file))
                if docs:
                    st.session_state.summary_result = {"filename": selected_file, "summary": summarize_text(docs[0].page_content, openai_api_key)}
                else:
                    st.error("문서 내용을 읽을 수 없습니다."); st.session_state.summary_result = None
        if st.session_state.summary_result:
            res = st.session_state.summary_result
            st.success(f"'{res['filename']}' 요약 결과:"); st.write(res['summary'])
            st.download_button("요약 결과 다운로드 (.txt)", res['summary'].encode('utf-8'), f"summary_{res['filename']}.txt")

# --- Tab 3: 문서 군집 분석 ---
with tabs[2]:
    st.subheader("업로드된 모든 문서를 내용 기반으로 그룹화합니다")
    if not files or len(files) < 2: st.info("분석하려면 2개 이상의 문서를 업로드해주세요.")
    else:
        if st.button("전체 문서 분석 및 군집화 실행"):
            with st.spinner("모든 문서를 벡터화하고 군집 분석을 수행하는 중..."):
                docs_for_cluster = [d for f in files if (d := load_documents(os.path.join(UPLOAD_DIR, f))) and d[0].page_content.strip()]
                if len(docs_for_cluster) >= 2:
                    texts = [d[0].page_content for d in docs_for_cluster]
                    model = SentenceTransformer("all-MiniLM-L6-v2")
                    embeddings = model.encode(texts)
                    num_clusters = min(len(docs_for_cluster), 4)
                    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto').fit(embeddings)
                    labels = kmeans.labels_
                    cluster_keywords = extract_cluster_keywords(texts, labels)
                    st.session_state.cluster_texts = texts
                    st.session_state.cluster_labels = labels
                    st.session_state.cluster_keywords = cluster_keywords
                    st.session_state.cluster_result_df = pd.DataFrame({
                        "파일명": [os.path.basename(d[0].metadata['source']) for d in docs_for_cluster],
                        "원문": texts,
                        "클러스터": labels,
                    })
                else:
                    st.error("분석 가능한 문서가 2개 미만입니다.")
                    st.session_state.cluster_result_df = None
        if st.session_state.cluster_result_df is not None:
            df = st.session_state.cluster_result_df
            st.success("군집 분석 결과:")
            st.dataframe(df.drop(columns=["원문"]).sort_values(by="클러스터").reset_index(drop=True))
            st.download_button(
                "분석 결과 다운로드 (.csv)",
                df.to_csv(index=False).encode('utf-8-sig'),
                "cluster_analysis.csv",
            )

            st.subheader("🧠 클러스터 요약 및 키워드")
            texts = st.session_state.cluster_texts
            labels = st.session_state.cluster_labels
            cluster_keywords = st.session_state.cluster_keywords
            num_clusters = len(set(labels))
            for i in range(num_clusters):
                cluster_texts = [texts[j] for j in range(len(texts)) if labels[j] == i]
                keywords = cluster_keywords.get(i, [])
                st.markdown(f"### 🔹 클러스터 {i}")
                st.markdown(f"**📌 주요 키워드:** {', '.join(keywords)}")
                if openai_api_key and st.button(f"GPT로 클러스터 {i} 요약", key=f"summary_{i}"):
                    with st.spinner("요약 중..."):
                        summary = gpt_summary(cluster_texts, openai_api_key)
                        st.success(f"✅ 요약: {summary}")
                with st.expander("📄 문장 보기"):
                    for t in cluster_texts:
                        st.write(f"- {t}")

# --- Tab 4: 텍스트 구조화 및 JSON 내보내기 ---
with tabs[3]:
    st.subheader("업로드된 텍스트 파일을 분석하여 시각화용 JSON으로 변환합니다.")
    if not files: st.info("사이드바에서 분석할 텍스트 파일을 먼저 업로드해주세요.")
    else:
        if st.button("텍스트 구조화 및 AI 분석 실행", type="primary"):
            txt_files = [f for f in files if f.endswith(('.txt', '.csv'))]
            if not txt_files:
                st.warning("분석할 .txt 또는 .csv 파일이 없습니다.")
            else:
                file_paths = [os.path.join(UPLOAD_DIR, f) for f in txt_files]
                with st.spinner("파일 내용을 구조화하는 중..."):
                    structured_data = parse_text_files_for_json(file_paths)
                if openai_api_key:
                    analyzed_data = analyze_structure_with_ai(structured_data, openai_api_key)
                    st.session_state.structured_data = analyzed_data
                    st.success("AI 분석 및 구조화 완료!")
                else:
                    st.session_state.structured_data = structured_data
                    st.warning("API 키가 없어 AI 분석을 건너뛰고 구조화만 완료했습니다.")

        if st.session_state.structured_data:
            st.header("📊 분석 결과 미리보기")
            for part in st.session_state.structured_data.get('parts', []):
                with st.expander(f"**Part: {part['partTitle']}**"):
                    for section in part.get('sections', []):
                        st.subheader(section['sectionTitle'])
                        st.markdown(f"**AI 요약:** {section.get('summary', 'N/A')}")
                        st.markdown(f"**AI 키워드:** `{'`, `'.join(section.get('keywords', []))}`")
            
            st.header("💾 JSON 파일로 내보내기")
            final_json = json.dumps(st.session_state.structured_data, indent=2, ensure_ascii=False)
            st.download_button("visualization_data.json 다운로드", final_json, "visualization_data.json", "application/json")

# --- Tab 5: 사주 지식 DB ---
with tabs[4]:
    st.subheader("전문 사주 지식 관리 및 검색")
    st.info("기본 이론, 전문용어, 사례를 추가하고 검색할 수 있습니다.")

    db_tabs = st.tabs(["기본 이론", "전문 용어", "사례 연구"])

    # 기본 이론 입력/검색 UI
    with db_tabs[0]:
        st.markdown("#### 기본 이론 입력")
        with st.form("basic_theory_form"):
            st.file_uploader(
                "문서 업로드",
                type=["txt", "pdf", "docx"],
                key="bt_file",
                on_change=handle_basic_theory_file,
            )
            part = st.selectbox("단원", list(PART_CATEGORIES.keys()), key="bt_part")
            cat = st.selectbox("카테고리", PART_CATEGORIES[part], key="bt_category")
            concept = st.text_input("개념", key="bt_concept")
            detail = st.text_area("상세 설명", key="bt_detail")
            if st.form_submit_button("추가"):
                add_basic_theory(f"{part} > {cat}", concept, detail)
                st.success("등록되었습니다.")
        st.markdown("#### 기본 이론 검색")
        keyword = st.text_input("검색어", key="bt_search")
        if st.button("검색", key="bt_search_btn"):
            result_df = search_concept(keyword)
            st.dataframe(result_df) if not result_df.empty else st.write("검색 결과가 없습니다.")
        st.markdown("#### 등록된 기본 이론")
        st.dataframe(get_basic_theory_all())

    # 전문 용어 입력/검색 UI
    with db_tabs[1]:
        st.markdown("#### 용어 입력")
        with st.form("terminology_form"):
            st.file_uploader(
                "문서 업로드",
                type=["txt", "pdf", "docx"],
                key="term_file",
                on_change=handle_terminology_file,
            )
            part = st.selectbox("단원", list(PART_CATEGORIES.keys()), key="term_part")
            cat = st.selectbox("분류", PART_CATEGORIES[part], key="term_category")
            term = st.text_input("용어", key="term_term")
            meaning = st.text_area("의미", key="term_meaning")
            if st.form_submit_button("추가"):
                add_terminology(term, meaning, f"{part} > {cat}")
                st.success("등록되었습니다.")
        st.markdown("#### 용어 검색")
        keyword = st.text_input("검색어", key="term_search")
        if st.button("검색", key="term_search_btn"):
            result_df = search_terminology(keyword)
            st.dataframe(result_df) if not result_df.empty else st.write("검색 결과가 없습니다.")
        st.markdown("#### 등록된 용어")
        st.dataframe(get_terminology_all())

    # 사례 연구 입력/검색 UI
    with db_tabs[2]:
        st.markdown("#### 사례 입력")
        with st.form("case_form"):
            st.file_uploader(
                "문서 업로드",
                type=["txt", "pdf", "docx"],
                key="case_file",
                on_change=handle_case_file,
            )
            part = st.selectbox("단원", list(PART_CATEGORIES.keys()), key="case_part")
            cat = st.selectbox("분류", PART_CATEGORIES[part], key="case_category")
            birth_info = st.text_input("출생정보", key="case_birth")
            chart = st.text_area("명식", key="case_chart")
            analysis = st.text_area("분석", key="case_analysis")
            result = st.text_area("결과", key="case_result")
            if st.form_submit_button("추가"):
                add_case_study(birth_info, chart, analysis, result, f"{part} > {cat}")
                st.success("등록되었습니다.")
        st.markdown("#### 사례 검색")
        keyword = st.text_input("검색어", key="case_search")
        if st.button("검색", key="case_search_btn"):
            result_df = search_case_study(keyword)
            st.dataframe(result_df) if not result_df.empty else st.write("검색 결과가 없습니다.")
        st.markdown("#### 등록된 사례")
        st.dataframe(get_case_studies_all())
