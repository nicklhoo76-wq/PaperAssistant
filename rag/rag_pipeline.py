from rag.pdf_loader import load_pdf
from rag.deepseek_llm import DeepSeekLLM
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
def build_rag(pdf_path):
    text = load_pdf(pdf_path)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks = splitter.split_text(text)

    # LangChain FAISS 索引
    store = FAISS.from_texts(chunks, embeddings)

    # RetrievalQA 链
    retriever = store.as_retriever(search_type="mmr", search_kwargs={"k": 4})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False
    )

    return qa_chain


# ---------------------------------
# 查询 RAG
# ---------------------------------
def query_rag(qa_chain, question):
    # qa_chain 直接返回回答
    answer = qa_chain.run(question)
    return answer