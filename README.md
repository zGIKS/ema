# Face Recognition API

Minimal FastAPI service for face enrollment and identification.

Structure:

- `src/app/identity/` for registration and DNI validation
- `src/app/biometrics/` for face matching and identification
- `src/app/shared/` for shared app code

## Run

```bash
nix-shell
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

`.env` is loaded automatically.

Required `.env` keys:

- `FR_ENGINE=insightface`
- `FR_DECOLECTA_API_KEY=...`
- `FR_DECOLECTA_BASE_URL=https://api.decolecta.com`
- `FR_CLOUDINARY_API_KEY=...`
- `FR_CLOUDINARY_API_SECRET=...`
- `FR_CLOUDINARY_CLOUD_NAME=...`
- `FR_DB_URL=mongodb://admin:admin@localhost:27017`
- `FR_DB_NAME=ema`
## Notes

- InsightFace is required.
- Images are stored in Cloudinary and only embeddings are persisted in MongoDB.
- `POST /api/v1/identity/register` creates a person once using DNI + one image.
- `GET /api/v1/biometrics/identify` is the biometric read path.
- `GET /api/v1/identity/persons` is the identity read path.
- `POST /api/v1/identity/persons/{person_id}/samples` adds more photos.
