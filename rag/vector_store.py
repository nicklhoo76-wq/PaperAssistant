import faiss
import numpy as np

class VectorStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embeddings, texts):
        self.index.add(np.array(embeddings))
        self.texts.extend(texts)

    def search(self, query_embedding, top_k=3):
        D, I = self.index.search(np.array([query_embedding]), top_k)
        return [self.texts[i] for i in I[0]]