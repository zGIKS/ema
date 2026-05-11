# Face Recognition API (Clean Architecture / DDD-ish)

FastAPI service that supports:

- **Detection**: find a face bounding box in an image
- **Identification**: compute an embedding and match it against enrolled identities
- **Enrollment**: register a new person with one or more reference images

This repo is structured as a bounded context under `src/contexts/identification/` with strict separation:

- `domain/`: value objects, commands, ports (interfaces)
- `application/`: command handlers (orchestrate the use case)
- `infrastructure/`: AI adapters, persistence adapters, ACL mappers
- `api/`: FastAPI routing + Pydantic schemas (DTOs)

## Quickstart

1. Install deps:

```bash
cd face-recognition-api
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. Run:

```bash
uvicorn src.main:app --reload --port 8000
```

3. Try:

- `POST /register` with `person_id` + `file`
- `POST /identify` with `file`

Note: the current AI implementation is a **stub** (deterministic pseudo-embedding) so the architecture is runnable without heavyweight ML dependencies.

