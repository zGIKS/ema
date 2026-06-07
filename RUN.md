# Run

```bash
nix-shell
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

Endpoints:

- `POST /register`
- `POST /persons/{person_id}/samples`
