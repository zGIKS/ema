# Face Recognition API

Minimal FastAPI service for face enrollment and identification.

Structure:

- `src/app/identification/` for the bounded context
- `src/app/shared/` for shared app code

## Run

```bash
nix-shell
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

## Notes

- InsightFace is required.
- Images are not stored.
- Only embeddings are persisted in SQLite.
