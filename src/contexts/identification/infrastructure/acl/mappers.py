from __future__ import annotations

import numpy as np

from src.contexts.identification.domain.model.valueobjects import FaceEmbedding


def numpy_embedding_to_vo(arr: np.ndarray) -> FaceEmbedding:
    """
    Anti-corruption layer mapper:
    converts model/infra artifacts (numpy arrays) to domain value objects.
    """

    flat = np.asarray(arr, dtype=np.float32).reshape(-1)
    return FaceEmbedding(tuple(float(x) for x in flat.tolist()))

