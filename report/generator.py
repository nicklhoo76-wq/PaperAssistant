from utils.llm import ask_llm

def generate_report(extracted_list, query):
    """
    根据提取的论文信息生成自然语言总结报告
    """
    prompt = f"""
    我有以下论文的关键信息：
    {extracted_list}

    请帮我生成一份面向科研人员的报告：
    - 介绍检索主题: {query}
    - 总结每篇论文的研究问题、方法、数据集、主要结果
    - 对比论文的相似点和差异
    - 给出简短结论和推荐

    请用自然语言输出。
    """
    return ask_llm(prompt)

def save_markdown(report, table, filename="report.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
        for row in table:
            f.write("\t".join(row))