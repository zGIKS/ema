import numpy as np


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def sample_similarity_pairs(embeddings_store: dict, max_pairs: int = 2000,
                            seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)

    if "people" in embeddings_store and isinstance(embeddings_store["people"], dict):
        people = embeddings_store["people"]
        per_person = {name: payload.get("embeddings", [])
                      for name, payload in people.items() if isinstance(payload, dict)}
    else:
        per_person = embeddings_store

    names = [n for n in per_person.keys() if per_person[n]]
    if len(names) < 2:
        return np.array([], dtype=np.float32), np.array([], dtype=np.float32)

    pos: list[float] = []
    neg: list[float] = []

    for name in names:
        embs = per_person[name]
        if len(embs) < 2:
            continue
        for _ in range(min(max_pairs // max(1, len(names)), 20)):
            i, j = rng.choice(len(embs), size=2, replace=False)
            pos.append(cosine_similarity(embs[i], embs[j]))

    for _ in range(max_pairs):
        a, b = rng.choice(names, size=2, replace=False)
        ea = per_person[a][rng.integers(0, len(per_person[a]))]
        eb = per_person[b][rng.integers(0, len(per_person[b]))]
        neg.append(cosine_similarity(ea, eb))

    return np.asarray(pos, dtype=np.float32), np.asarray(neg, dtype=np.float32)