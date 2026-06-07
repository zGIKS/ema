# Face Recognition API (Clean Architecture / DDD-ish)

FastAPI service that supports:

- **Detection**: find a face bounding box in an image
- **Identification**: compute an embedding and match it against enrolled identities
- **Enrollment**: register a new person with one or more reference images

This repo is structured as a bounded context under `src/app/identification/` with shared code in `src/shared/` and strict separation:

- `domain/`: value objects, commands, ports (interfaces)
- `application/`: command handlers (orchestrate the use case)
- `infrastructure/`: AI adapters, persistence adapters, ACL mappers
- `api/`: FastAPI routing + Pydantic schemas (DTOs)

## Quickstart

1. Install deps (recommended: Nix):

```bash
nix-shell
```

To include the InsightFace engine deps in Nix:

```bash
nix-shell --arg withML true
```

Alternatively, with `uv` (non-Nix environments):

```bash
uv sync

# Required: real recognition engine
uv sync --extra ml
```

Then run with:

```bash
uv run uvicorn src.main:app --reload --port 8000
```

2. Run:

```bash
uvicorn src.main:app --reload --port 8000
```

Embeddings persistence (MVP):

- By default, enrolled faces are stored in a local SQLite file at `./data/fr.sqlite3`.
- You can change it with `FR_DB_PATH=/path/to/fr.sqlite3`.

Note: images are not stored; only embeddings are persisted.

3. Try:

- `POST /register` with `person_id` + `file`
- You can also send multiple images using `files` (repeat the form field)
- `POST /identify` with `file`

## Real recognition

This repo includes an optional InsightFace-based engine (real face detection + embeddings).

Run with InsightFace:

```bash
FR_ENGINE=insightface uvicorn src.main:app --reload --port 8000
```

Engine selection:

- `FR_ENGINE=insightface` (default): uses InsightFace only
