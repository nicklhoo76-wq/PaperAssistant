# Paper Research Agent

A ChatGPT-style research assistant for automatic paper retrieval, analysis, and comparison.

---

## Features

* **Paper Retrieval**
  Automatically search and fetch papers from arXiv based on user queries.

* **LLM-based Information Extraction**
  Extract key components from papers:

  * Research problem
  * Method
  * Dataset
  * Results

* **Paper Comparison**
  Compare multiple papers and generate structured insights.

* **Chat-style Interface**
  Interactive UI built with Streamlit.

* **PDF Viewer**
  Download and preview paper PDFs directly inside the app.

---

## Demo

Run the app locally:

```bash
streamlit run app.py
```

Then open:

```
http://localhost:8501
```

---

## Project Structure

```
paper-agent/
│
├── app.py                  # Streamlit UI
│
├── retrieval/
│   ├── search.py           # arXiv search
│   └── download.py         # PDF download
│
├── extraction/
│   ├── extractor.py        # LLM-based extraction
│   ├── pdf_parser.py       # PDF parsing
│   └── section_extractor.py# section detection
│
├── comparison/
│   └── compare.py          # paper comparison logic
│
├── pdfs/                   # downloaded PDFs (ignored)
└── README.md
```

---

## Installation

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install streamlit arxiv pymupdf requests
```

---

## Usage

1. Enter a research topic (e.g., *Graph Neural Networks*)
2. The agent will:

   * Retrieve relevant papers
   * Extract key information
   * Generate a comparison report
3. Click a paper to preview its PDF

---

## Tech Stack

* **Frontend/UI**: Streamlit
* **Paper Source**: arXiv API
* **PDF Parsing**: PyMuPDF
* **LLM Integration**: (e.g., DeepSeek / OpenAI)

---

## Known Issues

* arXiv API may return **429 (rate limit)**
* LLM output may be unstable without proper prompting
* PDF parsing currently reads limited pages

---

## Future Work

* [ ] RAG-based paper QA (grounded answers with citations)
* [ ] Multi-agent architecture (planner / reviewer)
* [ ] Better PDF understanding (figure & table parsing)
* [ ] Deployment (Streamlit Cloud / Docker)

---

## Highlights

* End-to-end AI agent pipeline
* Real-world integration (API + PDF + LLM)
* Interactive product-style UI

---

## License

MIT License
