import os
from pathlib import Path
from typing import List, Dict

from src.algorithms.recursion_utils import recursive_find_images

class DataLayer:
    def __init__(self, data_root: str = "data"):
        self.root = Path(data_root)
        self.known_dir = self.root / "known_people"
        self.unknown_dir = self.root / "unknown"
        self.output_dir = Path("output")
        self.models_dir = Path("models")

        self.known_dir.mkdir(parents=True, exist_ok=True)
        self.unknown_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def list_known_people(self) -> List[str]:
        if not self.known_dir.exists():
            return []
        return [d.name for d in self.known_dir.iterdir() if d.is_dir()]

    def list_images_for_person(self, person_name: str) -> List[Path]:
        person_dir = self.known_dir / person_name
        if not person_dir.exists():
            return []
        return recursive_find_images(person_dir)

    def list_unknown_images(self) -> List[Path]:
        if not self.unknown_dir.exists():
            return []
        return recursive_find_images(self.unknown_dir)

    def get_embedding_storage_path(self) -> Path:
        return self.root / "embeddings.json"
