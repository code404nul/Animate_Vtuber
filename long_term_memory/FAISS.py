import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from long_term_memory.memory_manager import get_index, get_label

model = SentenceTransformer('BAAI/bge-large-en-v1.5')  # Tu peux le changer ici

class SemanticSearchEngine:
    def __init__(self):
        self.index = None
        self.text_map = {}
        self.dimension = None
        self.add_texts()

    def vectorize(self, text: str) -> np.ndarray:
        vec = model.encode(text, convert_to_numpy=True)
        vec = vec / np.linalg.norm(vec) if np.linalg.norm(vec) > 0 else vec
        return vec.astype(np.float32)
    
    def get_text(self):
        texts = []
        for index in range(1, get_index() + 1):
            text = get_label(index, "output")
            if text:
                texts.append(text)
        return texts

    def add_texts(self) -> None:
        texts = self.get_text()
        vectors = [self.vectorize(text) for text in texts]

        if self.index is None:
            self.dimension = vectors[0].shape[0]
            self.index = faiss.IndexFlatIP(self.dimension)

        vectors_np = np.stack(vectors)
        self.index.add(vectors_np)

        start_idx = len(self.text_map)
        self.text_map.update({i + start_idx: text for i, text in enumerate(texts)})

    def search(self, query: str, seuil: float = 0.5) -> list[tuple[str, float]]:
        query_vector = self.vectorize(query).reshape(1, -1)
        top_k = len(self.text_map)  # on cherche par rapport à tous les éléments indexés
        scores, indices = self.index.search(query_vector, top_k)

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if score >= seuil and idx in self.text_map:
                results.append((self.text_map[idx], float(score)))
        return results


    def pretty_print_results(self, query: str, results: list[tuple[str, float]]) -> None:
        print(f"\nQuery: {query}")
        for match, score in results:
            print(f"→ Match: {match} (similarity = {score:.4f})")
