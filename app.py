import streamlit as st
from retrieval.search import safe_search
from extraction.extractor import extract_summary
from comparison.compare import compare_papers
from streamlit_pdf_viewer import pdf_viewer
import requests
import os


st.set_page_config(page_title="PaperAssistant", layout="wide")

# ----------------------------
# 初始化
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "cache" not in st.session_state:
    st.session_state.cache = {}

if "current_query" not in st.session_state:
    st.session_state.current_query = None

if "running" not in st.session_state:
    st.session_state.running = False

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
    max_papers = st.slider("检索论文数量", min_value=2, max_value=6, value=4)
    if st.button("清空历史"):
        st.session_state.messages = []
        st.session_state.cache = {}
        st.session_state.current_query = None
        st.session_state.running = False
        st.rerun()

# ============================
# 中间：主分析
# ============================
with col_main:
    st.title("PaperAssistant")

    query = st.chat_input("输入研究问题...")

    if query:
        st.session_state.current_query = query
        st.session_state.running = True
        st.session_state.messages.append({"role": "user", "content": query})
        st.rerun()

    if st.session_state.running and st.session_state.current_query:

        query = st.session_state.current_query

        with st.chat_message("assistant"):

            # 如果有缓存，直接用
            if query in st.session_state.cache:
                report, papers, extracted = st.session_state.cache[query]
                st.markdown(report)

            else:
                # =========================
                # Step 1: 搜索
                # =========================
                with st.spinner("正在检索论文..."):
                    papers = safe_search(query, max_results=max_papers)

                print("DEBUG: 返回论文列表:", papers)

                if not papers or all(p['title'] == "Fallback Paper" for p in papers):
                    st.warning("API 没有返回真实论文")
                    st.session_state.running = False
                    st.stop()

                # =========================
                # Step 2: 提取
                # =========================
                extracted = []

                with st.spinner("正在提取信息..."):
                    for p in papers:
                        try:
                            info = extract_summary(p)

                            # fallback（关键）
                            if not info:
                                info = f"""
                                {{
                                  "title": "{p['title']}",
                                  "method": "N/A",
                                  "dataset": "N/A",
                                  "result": "{(p.get('summary') or '')[:100]}"
                                }}
                                """
                            extracted.append(info)

                        except Exception as e:
                            print("提取错误:", e)
                            extracted.append(f"""
                                {{
                                  "title": "{p['title']}",
                                  "method": "ERROR",
                                  "dataset": "N/A",
                                  "result": "Extraction failed"
                                }}
                            """)

                # =========================
                # Step 3: 对比
                # =========================
                with st.spinner("正在生成对比报告..."):
                    try:
                        report = compare_papers(extracted)
                    except Exception as e:
                        report = f"对比失败: {e}"

                # 缓存结果
                st.session_state.cache[query] = (report, papers, extracted)

                # 输出结果
                st.markdown(report)

            # =========================
            # 展示细节（折叠）
            # =========================

            # 论文列表
            with st.expander("查看论文"):
                for i, p in enumerate(papers):
                    st.markdown(f"### {p['title']}")

                    if st.button(f"查看PDF {i}", key=f"pdf_btn_{i}"):
                        st.session_state.selected_pdf = file_path
                        pdf_url = p["pdf_url"]

                        file_path = f"pdfs/paper_{i}.pdf"

                        # 下载 PDF
                        if not os.path.exists(file_path):
                            r = requests.get(pdf_url, timeout=10)
                            with open(file_path, "wb") as f:
                                f.write(r.content)

            # 提取信息
            with st.expander("提取信息"):
                for e in extracted:
                    st.code(e)

        # 保存 assistant 回复
        st.session_state.messages.append({
            "role": "assistant",
            "content": report
        })

        # 关键：防止重复执行
        st.session_state.running = False

# ============================
# 右侧：PDF 预览
# ============================
with col_pdf:
    st.header("PDF 预览")
    if st.session_state.selected_pdf:
        pdf_viewer(st.session_state.selected_pdf)

    else:
        st.info("点击左侧论文查看 PDF")