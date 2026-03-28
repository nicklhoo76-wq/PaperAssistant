from retrieval.search import search_papers
from report.generator import generate_report, save_markdown
from report.table import generate_comparison_table
from retrieval.download import download_pdf
from extraction.pdf_parser import extract_sections
from extraction.section_extractor import find_relevant_sections
from extraction.extractor import analyze_method, analyze_experiment
import os


query = input("请输入检索关键词: ")
papers = search_papers(query, max_results=3)
    
os.makedirs("pdfs", exist_ok=True)
extracted = []

for i, p in enumerate(papers):
    pdf_path = f"pdfs/paper_{i}.pdf"

    print(f"\n下载: {p['title']}")
    download_pdf(p["pdf_url"], pdf_path)

    sections = extract_sections(pdf_path)
    method_text, exp_text = find_relevant_sections(sections)
    method_info = analyze_method(p["title"], method_text)
    exp_info = analyze_experiment(p["title"], exp_text)

    extracted.append({
        "title": p["title"],
        "method": method_info,
        "experiment": exp_info
    })
    
table = generate_comparison_table(extracted)
nl_report = generate_report(extracted, query)
save_markdown(nl_report, table)