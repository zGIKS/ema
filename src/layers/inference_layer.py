import numpy as np
from typing import Dict, List, Tuple

class InferenceLayer:
    def __init__(self, metric: str = "cosine"):
        self.metric = metric

    def _similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        if self.metric == "cosine":
            dot = np.dot(a, b)
            norm = np.linalg.norm(a) * np.linalg.norm(b)
            return float(dot / norm) if norm > 0 else 0.0
        elif self.metric == "euclidean":
            dist = np.linalg.norm(a - b)
            return float(1 / (1 + dist))
        else:
            raise ValueError(f"Unsupported metric: {self.metric}")

    def compare(self, new_embedding: np.ndarray, stored_embeddings: Dict) -> List[Tuple[str, float]]:
        """
        stored_embeddings supported formats:
          - v1: {"dante": [emb1, emb2], "maria": [emb3]}
          - v2: {"people": {"dante": {"embeddings":[...], "prototype": [...]}, ...}}
        Returns list sorted by descending similarity: [("dante", 0.92), ...]
        """
        if "people" in stored_embeddings and isinstance(stored_embeddings["people"], dict):
            people = stored_embeddings["people"]
        else:
            people = stored_embeddings

        results = []
        for name, payload in people.items():
            if isinstance(payload, dict):
                embeddings_list = payload.get("embeddings", [])
                prototype = payload.get("prototype", None)
            else:
                embeddings_list = payload
                prototype = None

            best_sim = -1.0
            if prototype is not None:
                sim = self._similarity(new_embedding, prototype)
                if sim > best_sim:
                    best_sim = sim
            for emb in embeddings_list:
                sim = self._similarity(new_embedding, emb)
                if sim > best_sim:
                    best_sim = sim
            results.append((name, best_sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results
