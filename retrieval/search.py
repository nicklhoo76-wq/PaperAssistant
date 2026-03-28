import arxiv
import time
import streamlit as st

@st.cache_data(ttl=600)
def cached_search(query):
    return search_papers(query)

def search_papers(query, max_results=3, retries=3):
    for i in range(retries):
        try:
            time.sleep(2)
            print(f"尝试第{i+1}次搜索...")

            search = arxiv.Search(
                query=query,
                max_results=max_results
            )

            results = list(search.results())

            papers = []
            for result in results:
                papers.append({
                    "title": result.title,
                    "authors": result.authors,
                    "summary": result.summary,
                    "pdf_url": result.pdf_url,
                    "url": result.entry_id
                })

            if papers:
                return papers

        except Exception as e:
            print("错误:", e)
            time.sleep(3)

    # fallback（关键）
    print("使用 fallback 数据")
    return [
        {
            "title": "Fallback Paper: Transformer Overview",
            "summary": "Mock summary",
            "pdf_url": "",
            "url": "#"
        }
    ]