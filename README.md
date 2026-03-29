# PaperAssistant

A ChatGPT-style research assistant agent for automatic paper retrieval, analysis, and comparison.

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

* **PDF Viewer(not completed yet)**
  Download and preview paper PDFs directly inside the app.

## Demo

Run the app locally:

```bash
streamlit run app.py
```

Then open:

```
http://localhost:8501
```

## Project Structure

```
paper-agent/
│
├── app.py                  # Streamlit UI
│
├── retrieval/
│   ├── search.py           # paper search
│   └── download.py         # PDF download
│
├── rag/
│   ├── embedding.py        # text embedding
│   ├── pdf_loader.py       # PDF loading
│   ├── rag_pipeline.py     # main pipeline
│   ├── splitter.py         # text splitting
│   └── vector_store.py     # vector stored
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


## Installation

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install streamlit arxiv pymupdf requests faiss-cpu sentence-transformers
```


## Usage

1. Enter a research topic (e.g., *Graph Neural Networks*)
2. The agent will:

   * Retrieve relevant papers
   * Extract key information
   * Generate a comparison report
3. Click a paper below to preview its PDF


## Tech Stack

* **Frontend/UI**: Streamlit
* **Paper Source**: arXiv API
* **PDF Parsing**: PyMuPDF
* **LLM Integration**: (e.g., DeepSeek / OpenAI)


## Known Issues

* paper API may return **429 (rate limit)** (retrying it after a few minutes is suggested)
* LLM output may be unstable without proper prompting
* PDF viewing button no responds


## Future Work

* [ ] RAG-based paper QA (grounded answers with citations & no api requests)
* [ ] Multi-agent architecture (planner / reviewer)
* [ ] Better PDF understanding (figure & table parsing)
* [ ] Deployment (Streamlit Cloud / Docker)


## Highlights

* End-to-end AI agent pipeline
* Real-world integration (API + PDF + LLM)
* Interactive product-style UI


## License

MIT License