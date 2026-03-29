import streamlit as st
import requests
import time


def rate_limit():
    if "last_request_time" not in st.session_state:
        st.session_state.last_request_time = 0

    now = time.time()

    # 限制：5秒一次
    if now - st.session_state.last_request_time < 5:
        wait_time = 5 - (now - st.session_state.last_request_time)
        st.warning(f"请求过快，请等待 {wait_time:.1f} 秒")
        return False

    st.session_state.last_request_time = now
    return True

def safe_search(query, max_results):
    print("DEBUG: 查询关键词:", query)

    # cache命中
    if query in st.session_state.cache:
        print("DEBUG: 缓存命中")
        return st.session_state.cache[query]

    last_call_time = getattr(st.session_state, "last_api_call", 0)
    if time.time() - last_call_time < 1:  # 1秒间隔
        time.sleep(1)
    st.session_state.last_api_call = time.time()
    
    # 限流
    if not rate_limit():
        return []

    papers = search_papers(query, max_results)
    print("DEBUG: API返回papers数量:", len(papers))

    if papers:
        st.session_state.cache[query] = papers
    else:
        papers = [{
            "title": "Fallback Paper",
            "summary": "No data (API limited)",
            "pdf_url": "",
            "url": "#"
        }]

    st.session_state.cache[query] = papers
    return papers

@st.cache_data(ttl=600)
def cached_search(query, max_results):
    return search_papers(query, max_results)

def search_papers(query, max_results=3):
    time.sleep(3)
    url = "https://api.semanticscholar.org/graph/v1/paper/search"

    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,authors,year,abstract,url,openAccessPdf"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        print("API返回:", data)

        papers = []

        for paper in data.get("data", []):
            papers.append({
                "title": paper.get("title", "No title"),
                "authors": ", ".join([a["name"] for a in paper.get("authors", [])]),
                "year": paper.get("year", "Unknown"),
                "summary": paper.get("abstract") or "No abstract",
                "url": paper.get("url"),
                "pdf_url": (
                    paper.get("openAccessPdf", {}).get("url")
                    if paper.get("openAccessPdf") else None
                )
            })

        return papers

    except Exception as e:
        print("搜索失败:", e)
        return []