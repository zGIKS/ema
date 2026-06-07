# Run

```bash
uv sync --extra ml
export FR_ENGINE=insightface
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080
```
