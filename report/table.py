def generate_comparison_table(extracted_list):
    """
    将提取结果整理成表格
    """
    headers = ["论文标题", "研究问题", "方法", "数据集", "主要结果"]
    table = [headers]
    
    import json
    for paper_info in extracted_list:
        info = json.loads(paper_info)
        table.append([
            info.get("title", "N/A"),
            info.get("研究问题", "N/A"),
            info.get("方法", "N/A"),
            info.get("数据集", "N/A"),
            info.get("主要结果", "N/A"),
        ])
    return table