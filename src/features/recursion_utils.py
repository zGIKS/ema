from __future__ import annotations
from pathlib import Path


def recursive_find_images(root: Path, suffixes: set[str] | None = None) -> list[Path]:
    if suffixes is None:
        suffixes = {".jpg", ".jpeg", ".png"}

    results: list[Path] = []
    for p in root.iterdir():
        if p.is_dir():
            results.extend(recursive_find_images(p, suffixes=suffixes))
        else:
            if p.suffix.lower() in suffixes:
                results.append(p)
    return sorted(results)