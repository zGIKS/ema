from __future__ import annotations

from pathlib import Path


def load_dotenv(path: str | Path = ".env", override: bool = False) -> bool:
    """
    Minimal .env loader (sin dependencias).

    - Lee KEY=VALUE (sin export).
    - Ignora líneas vacías y comentarios (# ...).
    - Soporta valores con comillas simples o dobles.
    - Si override=False, no pisa variables ya definidas en el entorno.
    """
    import os

    p = Path(path)
    if not p.exists():
        return False

    for raw_line in p.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if (len(value) >= 2) and ((value[0] == value[-1]) and value[0] in {"'", '"'}):
            value = value[1:-1]

        if not override and key in os.environ:
            continue
        os.environ[key] = value

    return True

