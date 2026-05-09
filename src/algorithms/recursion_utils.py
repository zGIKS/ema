from __future__ import annotations

from pathlib import Path


def recursive_find_images(root: Path, suffixes: set[str] | None = None) -> list[Path]:
    """
    ## 5. Recursive Function

    Recorre recursivamente un árbol de carpetas y devuelve archivos de imagen.

    Ejemplo de recurrencia conceptual:
      f(dir) = imágenes_en(dir) + sum_{subdir in dir} f(subdir)

    En este repo se usa para listar imágenes aunque existan subcarpetas dentro de
    `known_people/<persona>/...` o `unknown/...`.
    """

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

