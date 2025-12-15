# app/providers/embeddings/local_embeddings.py
from sentence_transformers import SentenceTransformer

class LocalEmbeddings:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Se descarga una vez, luego es local
        self.model = SentenceTransformer(model_name)
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        return 384  # dimensión de all-MiniLM-L6-v2