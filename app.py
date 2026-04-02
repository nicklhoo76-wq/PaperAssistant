import streamlit as st
from retrieval.search import safe_search, add_noise
from retrieval.download import download_pdf
from extraction.extractor import extract_summary, save_cache
from comparison.compare import compare_papers
from streamlit_pdf_viewer import pdf_viewer
from rag.rag_pipeline import build_rag, query_rag
import os

st.set_page_config(page_title="PaperAssistant", layout="wide")

st.markdown("""
<style>
/* 缩小 sidebar 宽度 */
section[data-testid="stSidebar"] {
    width: 220px !important;
}
</style>
""", unsafe_allow_html=True)

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

if "rag_store" not in st.session_state:
    st.session_state.rag_store = None

if "rag_pdf" not in st.session_state:
    st.session_state.rag_pdf = None

os.makedirs("pdfs", exist_ok=True)

# ----------------------------
# 三栏布局
# ----------------------------
col_main, col_pdf = st.columns([1, 1.5])

# ============================
# 左侧：对话历史
# ============================
with st.sidebar:
    st.title("导航栏")
    st.header("设置")
    max_papers = st.slider("检索论文数量", min_value=2, max_value=6, value=4)

    if st.button("清空缓存"):
        st.session_state.cache = {}
        st.session_state.selected_pdf = None
        st.rerun()

    if st.button("清空历史"):
        st.session_state.messages = []
        st.session_state.cache = {}
        st.session_state.current_query = None
        st.session_state.running = False
        st.rerun()

    st.header("历史对话")
    count = 0
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            count += 1
            st.markdown(f"{count}. **你**: {msg['content'][:50]}...")
        else:
            st.markdown(f"   **助手**: {msg['content'][:50]}...")

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

        # 如果有缓存，直接用
        if query in st.session_state.cache:
            data = st.session_state.cache.get(query)

            if not data:
                st.warning("缓存不存在")
                st.stop()

            if not isinstance(data, tuple) or len(data) != 3:
                st.warning("缓存损坏，正在重置，请点击导航栏：清空缓存")
                del st.session_state.cache[query]
                st.stop()

            report, papers, extracted = data

        else:
            # =========================
            # Step 1: 搜索
            # =========================
            with st.spinner("正在检索论文..."):
                query_with_noise = add_noise(query)
                papers = safe_search(query_with_noise, max_results=max_papers)

            print("DEBUG: 返回论文列表:", papers)

            if not papers or all(p['title'] == "Fallback Paper" for p in papers):

                error_msg = "当前请求过多，未获取到论文，请更换关键词或稍后重试重试"

                # 补一个 assistant（关键）
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

                st.warning(error_msg)

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
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": report
                    })

                    # 缓存结果
                    save_cache(query, report, papers, extracted)

                except Exception as e:
                    report = f"对比失败: {e}"

        # 关键：防止重复执行
        st.session_state.running = False
    
    # =========================
    # 展示层
    # =========================
    if st.session_state.current_query in st.session_state.cache:

        query = st.session_state.current_query
        report, papers, extracted = st.session_state.cache[query]

        # 显示对话
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            st.markdown(report)

        # =========================
        # 论文列表
        # =========================
        st.subheader("论文列表")

        for i, p in enumerate(papers):

            st.markdown(f"### {p['title']}")

            pdf_url = p.get("pdf_url")

            if not pdf_url:
                st.info("该论文没有开放PDF")
                continue

            if st.button(f"查看PDF {i}", key=f"pdf_{st.session_state.current_query}_{i}"):

                #st.write("按钮触发成功")

                file_path = download_pdf(pdf_url, f"paper_{st.session_state.current_query}_{i}.pdf")

                if file_path:
                    st.session_state.selected_pdf = file_path
                    st.session_state.rag_store = None
                    st.session_state.rag_pdf = file_path

                    st.rerun()
                else:
                    st.warning("PDF下载失败")

        # 提取信息
        with st.expander("提取信息"):
            for e in extracted:
             st.code(e)

# ============================
# 右侧：PDF 预览
# ============================
with col_pdf:
    st.header("PDF 预览")
    if st.session_state.selected_pdf and os.path.exists(st.session_state.selected_pdf):
        print("PDF路径:", st.session_state.selected_pdf)
        print("文件存在:", os.path.exists(st.session_state.selected_pdf) if st.session_state.selected_pdf else "None")
        pdf_viewer(st.session_state.selected_pdf, width=700, height=1000)

        # 构建 RAG
        if st.session_state.rag_store is None:
            with st.spinner("正在构建论文索引..."):
                st.session_state.rag_store = build_rag(st.session_state.selected_pdf)

        st.success("RAG已就绪，可以提问")
        question = st.text_input("问这篇论文的问题")

        if question and st.session_state.rag_store:

            with st.spinner("正在回答..."):
                answer, sources = query_rag(st.session_state.rag_store, question)

            st.markdown("### 回答")
            st.write(answer)
            print(f"DEBUG:参考来源：{sources}")

            with st.expander("参考来源"):
                if sources:
                    for i, doc in enumerate(sources):
                        source = doc.metadata.get("source", "unknown")
                        st.markdown(f"**片段 {i+1} - 来源: {source}**")
                        st.write(doc.page_content[:300])
                else:
                    st.write("暂无参考来源")

    else:
        st.info("点击左侧论文查看 PDF")