import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import faiss
import asyncio
from datetime import datetime

from src.core.config import settings
from src.core.exceptions import PersonNotFoundError


class FaceRegistry:
    """
    Registro de identidades usando FAISS para busqueda por similitud.
    FAISS IndexFlatIP con vectores L2-normalizados equivale a cosine similarity.
    """

    def __init__(self) -> None:
        self._index: Optional[faiss.IndexFlatIP] = None
        self._metadata: Dict[int, dict] = {}
        self._id_to_index: Dict[str, int] = {}
        self._lock = asyncio.Lock()
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        settings.faiss_index_path.parent.mkdir(parents=True, exist_ok=True)

    async def _load(self) -> None:
        if self._index is not None:
            return
        async with self._lock:
            if self._index is not None:
                return
            if settings.faiss_index_path.exists():
                self._index = faiss.read_index(str(settings.faiss_index_path))
                with open(settings.faiss_metadata_path, "r") as f:
                    raw = json.load(f)
                self._metadata = {int(k): v for k, v in raw.get("metadata", {}).items()}
                self._id_to_index = raw.get("id_to_index", {})
            else:
                self._index = faiss.IndexFlatIP(settings.embedding_dim)
                self._metadata = {}
                self._id_to_index = {}

    async def add(self, name: str, embedding: List[float], extra: Optional[dict] = None) -> str:
        await self._load()
        person_id = str(uuid.uuid4())
        vec = np.array([embedding], dtype=np.float32)
        async with self._lock:
            idx = self._index.ntotal
            self._index.add(vec)
            self._metadata[idx] = {
                "person_id": person_id,
                "name": name,
                "enrolled_at": datetime.utcnow().isoformat(),
                "metadata": extra or {},
            }
            self._id_to_index[person_id] = idx
            self._persist()
        return person_id

    async def search(self, embedding: List[float], k: int = 1) -> Tuple[Optional[str], Optional[str], float]:
        await self._load()
        vec = np.array([embedding], dtype=np.float32)
        distances, indices = self._index.search(vec, k)
        if indices[0][0] == -1:
            return None, None, 0.0
        best_idx = int(indices[0][0])
        best_dist = float(distances[0][0])
        if best_dist < settings.faiss_threshold:
            return None, None, best_dist
        meta = self._metadata.get(best_idx, {})
        return meta.get("person_id"), meta.get("name"), best_dist

    async def list_persons(self) -> List[dict]:
        await self._load()
        return [
            {
                "person_id": m["person_id"],
                "name": m["name"],
                "enrolled_at": m.get("enrolled_at"),
            }
            for m in self._metadata.values()
        ]

    async def delete(self, person_id: str) -> None:
        await self._load()
        if person_id not in self._id_to_index:
            raise PersonNotFoundError(f"Persona {person_id} no encontrada.")
        # FAISS no soporta borrado eficiente sin reconstruccion.
        # Para produccion con alta concurrencia se recomienda usar IDMap + remove_ids.
        async with self._lock:
            keep_indices = [
                i for i, m in self._metadata.items()
                if m["person_id"] != person_id
            ]
            if not keep_indices:
                self._index = faiss.IndexFlatIP(settings.embedding_dim)
                self._metadata = {}
                self._id_to_index = {}
            else:
                new_index = faiss.IndexFlatIP(settings.embedding_dim)
                vecs = self._index.reconstruct_n(0, self._index.ntotal)
                vecs = vecs[keep_indices]
                new_index.add(vecs)
                new_meta = {}
                new_map = {}
                for new_idx, old_idx in enumerate(keep_indices):
                    new_meta[new_idx] = self._metadata[old_idx]
                    new_map[self._metadata[old_idx]["person_id"]] = new_idx
                self._index = new_index
                self._metadata = new_meta
                self._id_to_index = new_map
            self._persist()

    def _persist(self) -> None:
        if self._index is not None:
            faiss.write_index(self._index, str(settings.faiss_index_path))
        with open(settings.faiss_metadata_path, "w") as f:
            json.dump(
                {
                    "metadata": {str(k): v for k, v in self._metadata.items()},
                    "id_to_index": self._id_to_index,
                },
                f,
                indent=2,
            )
