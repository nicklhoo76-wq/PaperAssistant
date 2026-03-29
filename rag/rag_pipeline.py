from rag.pdf_loader import load_pdf
from rag.splitter import split_text
from rag.embedding import embed_texts, model
from rag.vector_store import VectorStore

def build_rag(pdf_path):
    text = load_pdf(pdf_path)
    chunks = split_text(text)

    embeddings = embed_texts(chunks)

    store = VectorStore(len(embeddings[0]))
    store.add(embeddings, chunks)

    return store


def query_rag(store, query):
    query_emb = model.encode([query])[0]
    results = store.search(query_emb)

    # 简单拼接作为回答
    answer = "\n\n".join(results)

    return answer