import streamlit as st
from retrieval.search import search_papers
from extraction.extractor import extract_summary
from comparison.compare import compare_papers
from streamlit_pdf_viewer import pdf_viewer
import requests
import os

st.set_page_config(page_title="Paper Agent Pro", layout="wide")

# ----------------------------
# 初始化
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "cache" not in st.session_state:
    st.session_state.cache = {}

if "selected_pdf" not in st.session_state:
    st.session_state.selected_pdf = None

os.makedirs("pdfs", exist_ok=True)

# ----------------------------
# 三栏布局
# ----------------------------
col_main, col_pdf = st.columns([2, 2])

# ============================
# 左侧：对话历史
# ============================
with st.sidebar:
    st.title("历史对话")
    for i, msg in enumerate(st.session_state.messages):
        role = "你" if msg["role"] == "user" else "助手"
        st.markdown(f"{i+1}. **{role}**: {msg['content'][:50]}{'...' if len(msg['content'])>50 else ''}")

    st.header("设置")
    max_papers = st.slider("检索论文数量", min_value=1, max_value=5, value=3)
    if st.button("清空历史"):
        st.session_state.messages = []
        st.session_state.cache = {}
        st.session_state.pdfs = {}
        st.experimental_rerun()

# ============================
# 中间：主分析
# ============================
with col_main:
    st.title("Research Agent")

    query = st.chat_input("输入研究问题...")

    if query:
        st.session_state.messages.append({"role": "user", "content": query})

        with st.spinner("正在分析论文..."):

            if query in st.session_state.cache:
                report, papers, extracted = st.session_state.cache[query]
            else:
                papers = search_papers(query, max_results=max_papers)

                extracted = []
                for p in papers:
                    info = extract_summary(p)
                    extracted.append(info)

                report = compare_papers(extracted)

                st.session_state.cache[query] = (report, papers, extracted)

        st.markdown("## 分析结果")
        st.markdown(report)

        st.session_state.messages.append({
            "role": "assistant",
            "content": report
        })

        # 论文列表
        with st.expander("查看论文"):
            for i, p in enumerate(papers):
                st.markdown(f"### {p['title']}")

                if st.button(f"查看PDF {i}", key=f"pdf_btn_{i}"):
                    pdf_url = p["pdf_url"]

                    file_path = f"pdfs/paper_{i}.pdf"

                    # 下载 PDF
                    if not os.path.exists(file_path):
                        r = requests.get(pdf_url)
                        with open(file_path, "wb") as f:
                            f.write(r.content)

                    st.session_state.selected_pdf = file_path

        # 提取信息
        with st.expander("提取信息"):
            for e in extracted:
                st.code(e)

# ============================
# 右侧：PDF 预览
# ============================
with col_pdf:
    st.header("PDF 预览")

    if st.session_state.selected_pdf:
        pdf_viewer(st.session_state.selected_pdf)

    else:
        st.info("点击左侧论文查看 PDF")