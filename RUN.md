# Run

```bash
# deps (Nix)
nix-shell
# or: nix-shell --arg withML true

# install python deps with uv
uv sync
# required (real recognition): uv sync --extra ml

# run API
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080

# engine is InsightFace by default

# persistence (default): ./data/fr.sqlite3
# override: FR_DB_PATH=./data/fr.sqlite3
```
