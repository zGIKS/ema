# Face Recognition API - Arquitectura Limpia

API de reconocimiento facial de alta precision con arquitectura modular, async y escalable.

## Modelos de IA

| Capa | Modelo | Arquitectura | Precision |
|------|--------|--------------|-----------|
| **Deteccion** | SCRFD-10GF (InsightFace `buffalo_l`) | CNN + Anchor-free | SOTA en WIDERFACE |
| **Embeddings** | ArcFace ResNet100 @ WebFace600K | ResNet-100 + Additive Angular Margin | 99.8%+ LFW, top NIST FRVT |
| **Busqueda** | FAISS IndexFlatIP | Producto interno (coseno) | Exacta, millones de IDs |

## Arquitectura del Software

```
src/
├── core/
│   ├── config.py          # Pydantic-Settings (12-factor)
│   └── exceptions.py      # Excepciones de dominio
├── models/
│   ├── detector.py        # InsightFace wrapper (lazy init, thread-safe)
│   └── registry.py        # FAISS + metadata (async-safe)
├── services/
│   └── recognition_service.py  # Orquesta detector + registry
├── api/
│   ├── schemas.py         # Pydantic v2 (validacion + documentacion)
│   └── routes.py          # FastAPI routers + DI
└── main.py                # Entrypoint Uvicorn
```

### Principios aplicados
- **Inyeccion de dependencias**: `RecognitionService` recibe `FaceDetector` y `FaceRegistry` por constructor. Facil de mockear en tests.
- **Async everywhere**: La carga del modelo ONNX y FAISS se hace en `run_in_executor` para no bloquear el event loop.
- **Lazy initialization**: `FaceDetector` no carga el modelo hasta el primer request.
- **Locking**: Tanto el detector como el registry usan `asyncio.Lock` para evitar condiciones de carrera.

## Endpoints

### `POST /api/v1/detect`
Detecta rostros y devuelve bounding boxes + embeddings.

### `POST /api/v1/enroll`
Registra una persona nueva a partir de una foto.

### `POST /api/v1/identify`
Identifica todos los rostros en una imagen contra la base de datos.

### `GET /api/v1/persons`
Lista las personas registradas.

### `DELETE /api/v1/persons/{person_id}`
Elimina una persona del registro.

## Instalacion

```bash
cd face-recognition-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar

```bash
python -m src.main
```

La primera vez descarga automaticamente el modelo `buffalo_l` (~400MB).

## Docker

```bash
docker build -t face-recognition-api .
docker run -p 8000:8000 -v $(pwd)/data:/app/data face-recognition-api
```

## Escalabilidad
- **Vertical**: Usa `onnxruntime-gpu` para inferencia en GPU.
- **Horizontal**: El estado (FAISS + metadata) vive en disco; puedes montar el volumen compartido o migrar a **Milvus** / **Pinecone** sin tocar la logica de negocio (mismo interface).
- **Async**: Uvicorn maneja miles de requests concurrentes mientras los modelos corren en thread pool.

## Tests

```bash
pytest tests/
```
