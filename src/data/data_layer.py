import os
from pathlib import Path
from typing import List, Dict

from src.algorithms.recursion_utils import recursive_find_images

class DataLayer:
    def __init__(self, data_root: str = "data", allow_flat_known_people: bool = False):
        self.root = Path(data_root)
        self.known_dir = self.root / "known_people"
        self.unknown_dir = self.root / "unknown"
        self.allow_flat_known_people = allow_flat_known_people
        self.output_dir = Path("output")
        self.models_dir = Path("models")

        self.known_dir.mkdir(parents=True, exist_ok=True)
        self.unknown_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def list_known_people(self) -> List[str]:
        if not self.known_dir.exists():
            return []
        people: set[str] = set()
        # Folder-per-person (recommended)
        for d in self.known_dir.iterdir():
            if d.is_dir():
                people.add(d.name)

        # Flat mode (optional): images directly under known_people/
        if self.allow_flat_known_people:
            for p in self.known_dir.iterdir():
                if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                    people.add(p.stem)

        return sorted(people)

    def list_images_for_person(self, person_name: str) -> List[Path]:
        person_dir = self.known_dir / person_name
        if person_dir.exists() and person_dir.is_dir():
            return recursive_find_images(person_dir)

        if not self.allow_flat_known_people:
            return []

        # Flat mode fallback: match a single file under known_people/
        for ext in (".jpg", ".jpeg", ".png"):
            candidate = self.known_dir / f"{person_name}{ext}"
            if candidate.exists() and candidate.is_file():
                return [candidate]
        return []

    def list_unknown_images(self) -> List[Path]:
        if not self.unknown_dir.exists():
            return []
        return recursive_find_images(self.unknown_dir)

    def get_embedding_storage_path(self) -> Path:
        return self.root / "embeddings.json"
