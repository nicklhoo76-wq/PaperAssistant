from rag.pdf_loader import load_pdf
from rag.deepseek_llm import DeepSeekLLM
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate

# ---------------------------------
# 初始化模型
# ---------------------------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
#llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
llm = DeepSeekLLM()

# ---------------------------------
# 构建 RAG
# ---------------------------------
prompt_template = """
你是一个顶级论文分析助手，请基于给定论文片段回答问题。

【要求】
1. 必须用自己的话总结，不要逐字复制原文
2. 回答必须结构化，不超过300字
3. 即使信息不完整，也请基于已有内容进行合理推断并总结

【论文标题】
{title}

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
    input_variables=["title", "context", "question"]
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
    store = FAISS.from_texts(chunks, embeddings)

    # RetrievalQA 链
    retriever = store.as_retriever(search_type="mmr", search_kwargs={"k": 6, "fetch_k": 15})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="map_rerank",
        chain_type_kwargs={"prompt": PROMPT, "verbose": True},
        return_source_documents=True
    )

    return qa_chain

# ---------------------------------
# 查询 RAG
# ---------------------------------
def query_rag(qa_chain, question):
    result = qa_chain({"query": question})
    answer = result["result"]
    sources = result.get("source_documents", [])
    return answer, sources