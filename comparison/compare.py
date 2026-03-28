from utils.llm import ask_llm

def compare_papers(extracted_list):
    """
    比较多篇论文的相似点和差异
    extracted_list: list of JSON strings from extractor
    """
    prompt = f"""
    我有以下几篇论文的关键信息：
    {extracted_list}

    请帮我总结它们的相似点和差异，输出一份对比报告。
    """
    return ask_llm(prompt)