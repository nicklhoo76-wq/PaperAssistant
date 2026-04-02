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

* **PDF Viewer**
  Download and preview paper PDFs directly inside the app.

* **RAG-based paper QA**
  Answer paper questions using LLM with LangChain.

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
│   ├── deepseek_llm.py     # LLM wrapper
│   ├── pdf_loader.py       # PDF loading
│   └── rag_pipeline.py     # main pipeline
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
pip install streamlit arxiv pymupdf requests faiss-cpu sentence-transformers angchain langchain-community langchain-openai langchain-text-splitters
```

Then, set your LLM API key to use it for report generation permanently：

```bash
setx LLM_API_KEY your_api_key
```
but temporarily:

```bash
set LLM_API_KEY=your_api_key
```

(e.g., if you use openai, LLM_API_KEY is OPENAI_API_KEY)

**notice**: we use deepseek here for RAG QA, but if you want to use gpt, please change Line 16 in rag\rag_pipeline into just like this without other requirements:

```Python
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
```


## Usage

1. Enter a research topic (e.g., *Graph Neural Networks*)
2. The agent will:

   * Retrieve relevant papers
   * Extract key information
   * Generate a comparison report
3. Click a paper below to preview its PDF
4. Question on the paper below


## Tech Stack

* **Frontend/UI**: Streamlit
* **Paper Source**: multiple source (arXiv API, Semantic Scholar)
* **PDF Parsing**: PyMuPDF
* **LLM Integration**: (e.g., DeepSeek / OpenAI)
* **RAG QA**: LangChain


## Known Issues

* source_documents in paper QA can't be generated
* LLM output may be unstable without proper prompting
* paper API may return 429 (rate limit) so retrying it after a few minutes is suggested


## Future Work

* [ ] RAG-based paper QA (**better** grounded answers with citations)
* [ ] Multi-agent architecture (planner / reviewer)
* [ ] Better PDF understanding (figure & table parsing)
* [ ] Deployment (Streamlit Cloud / Docker)


## Highlights

* End-to-end AI agent pipeline
* Real-world integration (API + PDF + LLM)
* Interactive product-style UI


## License

MIT License