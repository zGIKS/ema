import os
from pathlib import Path
from typing import List, Dict

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
        return sorted([p for p in person_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}])

    def list_unknown_images(self) -> List[Path]:
        if not self.unknown_dir.exists():
            return []
        return sorted([p for p in self.unknown_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}])

    def get_embedding_storage_path(self) -> Path:
        return self.root / "embeddings.json"
