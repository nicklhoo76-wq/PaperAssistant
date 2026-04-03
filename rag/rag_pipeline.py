from rag.pdf_loader import load_pdf, load_pdf_with_pages
from rag.deepseek_llm import DeepSeekLLM
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_classic.schema import Document

# ---------------------------------
# 初始化模型
# ---------------------------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
llm = DeepSeekLLM()

# ---------------------------------
# 构建 RAG
# ---------------------------------
prompt_template = """
你是一个顶级论文分析助手，请基于给定论文片段回答问题。

【上下文说明】
在提供的论文片段中，每个片段都标注了其来源页码（格式：【第X页】）。

【要求】
1. 必须用自己的话总结，不要逐字复制原文
2. 回答必须结构化，不超过300字
3. 在回答中标注绝对真实的引用来源，格式为 [第X页]，对应论文片段中的页码
4. 即使信息不完整，也基于已有内容进行合理推断并总结

【论文片段】
{context}

【问题】
{question}

【回答】
请按以下结构输出：

【核心结论】
- ...

【具体分析】
- ...

【总结】
- ...
"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

def build_rag(pdf_path):
    text = load_pdf(pdf_path)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(text)

    # LangChain FAISS 索引
    pages = load_pdf_with_pages(pdf_path)

    docs = []
    for page_num, text in pages:
        chunks = splitter.split_text(text)

        for i, chunk in enumerate(chunks):
            docs.append(
                Document(
                    page_content=f"【第{page_num}页】{chunk}",
                    metadata={
                        "source": f"第{page_num}页",
                        "page": page_num,
                        "chunk_id": i
                    }
                )
            )
    store = FAISS.from_documents(docs, embeddings)
    print("DEBUG DOC:", docs[0].metadata)

    # RetrievalQA 链
    retriever = store.as_retriever(search_type="mmr", search_kwargs={"k": 6, "fetch_k": 15})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": PROMPT, "verbose": True},
        return_source_documents=True
    )

    return qa_chain

# ---------------------------------
# 查询 RAG
# ---------------------------------
def query_rag(qa_chain, question):
    result = qa_chain.invoke({"query": question})
    answer = result["result"]
    sources = result.get("source_documents", [])
    return answer, sources