import json
import numpy as np
from pathlib import Path
from typing import Dict, List


class StorageLayer:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path

    @staticmethod
    def _l2_normalize(vec: np.ndarray, eps: float = 1e-12) -> np.ndarray:
        vec = np.asarray(vec, dtype=np.float32)
        denom = float(np.linalg.norm(vec))
        if denom < eps:
            return vec
        return vec / denom

    def save(self, embeddings: Dict[str, List[np.ndarray]]):
        people = {}
        for name, emb_list in embeddings.items():
            emb_list = [self._l2_normalize(e) for e in emb_list if e is not None]
            if not emb_list:
                continue
            mean = np.mean(np.stack(emb_list, axis=0), axis=0)
            prototype = self._l2_normalize(mean)
            people[name] = {
                "embeddings": [emb.tolist() for emb in emb_list],
                "prototype": prototype.tolist(),
            }

        serializable = {"version": 2, "people": people}
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2)

    def load(self) -> Dict:
        if not self.storage_path.exists():
            return {}
        with open(self.storage_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and "people" in data and isinstance(data["people"], dict):
            people = {}
            for name, payload in data["people"].items():
                embeddings = [np.array(v, dtype=np.float32) for v in payload.get("embeddings", [])]
                proto = payload.get("prototype", None)
                prototype = np.array(proto, dtype=np.float32) if proto is not None else None
                people[name] = {"embeddings": embeddings, "prototype": prototype}
            return {"version": int(data.get("version", 2)), "people": people}

        if isinstance(data, dict):
            return {name: [np.array(v, dtype=np.float32) for v in vectors] for name, vectors in data.items()}
        return {}


from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class QPolicyOnDisk:
    q_table: list[list[float]]
    bin_edges: list[float]
    actions: list[float]


class PolicyStore:
    def __init__(self, path: Path):
        self.path = path

    def save_q_policy(self, policy: QPolicyOnDisk) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(policy), indent=2), encoding="utf-8")

    def load_q_policy(self) -> QPolicyOnDisk | None:
        if not self.path.exists():
            return None
        obj = json.loads(self.path.read_text("utf-8"))
        return QPolicyOnDisk(
            q_table=obj["q_table"],
            bin_edges=obj["bin_edges"],
            actions=obj["actions"],
        )