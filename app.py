import streamlit as st
from retrieval.search import safe_search, add_noise
from retrieval.download import download_pdf
from extraction.extractor import extract_summary, save_cache
from comparison.compare import compare_papers
from streamlit_pdf_viewer import pdf_viewer
from rag.rag_pipeline import build_rag, query_rag
import os, re
import fitz

st.set_page_config(page_title="PaperAssistant", layout="wide")

st.markdown("""
<style>
/* 缩小 sidebar 宽度 */
section[data-testid="stSidebar"] {
    width: 220px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# 辅助函数：PDF页面高亮
# ---------------------------------
def highlight_pdf_page(pdf_path, page_num, chunk_content):
    """
    生成PDF某一页的预览，并高亮指定内容
    """
    try:
        pdf_doc = fitz.open(pdf_path)
        page = pdf_doc[page_num - 1]

        # 从chunk_content中提取实际内容
        text_to_highlight = chunk_content
        if text_to_highlight.startswith(f"【第{page_num}页】"):
            text_to_highlight = text_to_highlight[len(f"【第{page_num}页】"):]

        # 搜索并高亮文本 - 搜索较长的文本以实现完整高亮
        search_text = text_to_highlight[:400] if len(text_to_highlight) > 400 else text_to_highlight
        text_instances = page.search_for(search_text)

        for inst in text_instances:
            try:
                page.draw_rect(inst, color=(1, 1, 0), fill=(1, 1, 0), fill_opacity=0.3)
            except:
                pass

        # 将页面转换为图像
        pix = page.get_pixmap(matrix=fitz.Matrix(12, 12))  # 缩放
        img_data = pix.tobytes("png")

        pdf_doc.close()
        return img_data
    except Exception as e:
        print(f"高亮失败: {e}")
        return None

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

if "highlight_page" not in st.session_state:
    st.session_state.highlight_page = None

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "current_answer" not in st.session_state:
    st.session_state.current_answer = None

if "current_sources" not in st.session_state:
    st.session_state.current_sources = None

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

                # 补一个 assistant
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

        # 防止重复执行
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

        # 如果有高亮页面，显示高亮后的页面
        if st.session_state.highlight_page and st.session_state.current_sources:
            # 找到该页的文档内容
            page_to_docs = {}
            for doc in st.session_state.current_sources:
                page = doc.metadata.get("page")
                if page is not None:
                    page = int(page)
                if page not in page_to_docs:
                    page_to_docs[page] = []
                page_to_docs[page].append(doc)

            if st.session_state.highlight_page in page_to_docs:
                docs = page_to_docs[st.session_state.highlight_page]
                # 获取第一个doc的内容来高亮
                chunk_content = docs[0].page_content
                img_data = highlight_pdf_page(st.session_state.selected_pdf, st.session_state.highlight_page, chunk_content)

                col_reset, col_empty = st.columns([1, 4])
                with col_reset:
                    if st.button("返回完整预览"):
                        st.session_state.highlight_page = None
                        st.rerun()

                if img_data:
                    st.image(img_data, width=700)
                else:
                    pdf_viewer(st.session_state.selected_pdf, width=700, height=1000)
            else:
                pdf_viewer(st.session_state.selected_pdf, width=700, height=1000)
        else:
            # 显示完整PDF
            pdf_viewer(st.session_state.selected_pdf, width=700, height=1000)

        # 构建 RAG
        if st.session_state.rag_store is None:
            with st.spinner("正在构建论文索引..."):
                st.session_state.rag_store = build_rag(st.session_state.selected_pdf)

        st.success("RAG已就绪，可以提问")
        question = st.text_input("问这篇论文的问题")

        # 如果问题改变，执行新查询
        if question and question != st.session_state.current_question and st.session_state.rag_store:
            with st.spinner("正在回答..."):
                answer, sources = query_rag(st.session_state.rag_store, question)
            st.session_state.current_question = question
            st.session_state.current_answer = answer
            st.session_state.current_sources = sources
            st.session_state.highlight_page = None  # 重置高亮

        # 如果有缓存的结果，直接显示
        if st.session_state.current_answer and st.session_state.current_question:
            answer = st.session_state.current_answer
            sources = st.session_state.current_sources

            st.markdown("### 回答")
            st.write(answer)

            # 从回答中按顺序提取所有引用的页码
            cited_pages = []
            cited_pages_set = set()
            for match in re.finditer(r"\[第(\d+)页\]", answer):
                page = int(match.group(1))
                if page not in cited_pages_set:
                    cited_pages.append(page)
                    cited_pages_set.add(page)

            print(f"DEBUG:参考来源：{sources}")
            print(f"DEBUG:回答中引用的页码：{cited_pages}")
            with st.expander("参考来源"):
                if sources:
                    # 创建页码到doc的映射
                    page_to_docs = {}
                    for doc in sources:
                        page = doc.metadata.get("page")
                        # 统一转换为整数
                        if page is not None:
                            page = int(page)
                        if page not in page_to_docs:
                            page_to_docs[page] = []
                        page_to_docs[page].append(doc)

                    print(f"DEBUG:sources中的页码：{list(page_to_docs.keys())}")

                    # 按回答中的引用顺序显示
                    for page in cited_pages:
                        if page in page_to_docs:
                            is_highlighted = st.session_state.highlight_page == page

                            if st.button(f"第{page}页", key=f"page_{page}", disabled=is_highlighted):
                                st.session_state.highlight_page = page
                                st.rerun()

                            for i, doc in enumerate(page_to_docs[page]):
                                # 移除 doc.page_content 中的页码标记
                                content = doc.page_content
                                if content.startswith(f"【第{page}页】"):
                                    content = content[len(f"【第{page}页】"):]

                                st.write(content[:400] + "...")
                        else:
                            st.markdown(f"**第{page}页**")
                            st.write("(参考内容未在检索结果中)")
                else:
                    st.write("暂无参考来源")


    else:
        st.info("点击左侧论文查看 PDF")