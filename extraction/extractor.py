from utils.llm import ask_llm
import streamlit as st

def extract_summary(paper):
    """
    让 LLM 提取论文的关键信息
    paper: dict, 包含 title, summary
    """
    prompt = f"""
    请帮我从以下论文摘要提取关键信息：
    论文标题: {paper['title']}
    摘要: {paper['summary']}
    请提取: 研究问题、方法、数据集、主要结果
    用 JSON 格式返回
    """
    result = ask_llm(prompt)
    return result

def extract_from_fulltext(title, text):
    prompt = f"""
You are a research assistant.

Paper title: {title}

Paper content:
{text[:3000]}

Extract:
- research problem
- method
- dataset
- key results
- limitations

Return JSON.
"""
    return ask_llm(prompt)


def analyze_method(title, method_text):
    prompt = f"""
You are a research expert.

Paper: {title}

Method section:
{method_text[:3000]}

Explain:
- core idea
- model architecture
- innovation

Be concise.
"""
    return ask_llm(prompt)

def analyze_experiment(title, exp_text):
    prompt = f"""
Paper: {title}

Experiment section:
{exp_text[:3000]}

Extract:
- dataset
- metrics
- performance
- comparison results
"""
    return ask_llm(prompt)

def save_cache(query, report, papers, extracted):
    st.session_state.cache[query] = (report, papers, extracted)