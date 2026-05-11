import asyncio
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from PIL import Image
import insightface
from insightface.app import FaceAnalysis

from src.core.config import settings
from src.core.exceptions import FaceNotDetectedError


class FaceDetector:
    """
    Wrapper sobre InsightFace con deteccion SCRFD + embedding ArcFace.
    ArcFace ResNet100 entrenado en WebFace600K es SOTA en precision (NIST FRVT).
    """

    def __init__(self) -> None:
        self._app: Optional[FaceAnalysis] = None
        self._lock = asyncio.Lock()

    async def _get_app(self) -> FaceAnalysis:
        if self._app is None:
            async with self._lock:
                if self._app is None:
                    loop = asyncio.get_event_loop()
                    self._app = await loop.run_in_executor(None, self._sync_init)
        return self._app

    def _sync_init(self) -> FaceAnalysis:
        app = FaceAnalysis(
            name=settings.insightface_model,
            root=".",
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        app.prepare(ctx_id=settings.insightface_ctx_id, det_size=settings.det_size)
        return app

    async def detect(self, image_path: Path) -> List[dict]:
        app = await self._get_app()
        img = Image.open(image_path).convert("RGB")
        img_np = np.array(img)

        loop = asyncio.get_event_loop()
        faces = await loop.run_in_executor(None, lambda: app.get(img_np))

        if not faces:
            raise FaceNotDetectedError("No se detecto ningun rostro en la imagen.")

        results = []
        for face in faces:
            bbox = face.bbox.astype(float).tolist()
            embedding = face.embedding.tolist() if face.embedding is not None else None
            if embedding is not None:
                embedding = (np.array(embedding) / np.linalg.norm(embedding)).tolist()
            results.append(
                {
                    "bbox": {
                        "x1": bbox[0],
                        "y1": bbox[1],
                        "x2": bbox[2],
                        "y2": bbox[3],
                        "score": float(face.det_score),
                    },
                    "embedding": embedding,
                    "confidence": float(face.det_score),
                }
            )
        return results

    async def get_single_embedding(self, image_path: Path) -> Tuple[List[float], dict]:
        faces = await self.detect(image_path)
        best = max(
            faces,
            key=lambda f: (f["bbox"]["x2"] - f["bbox"]["x1"])
            * (f["bbox"]["y2"] - f["bbox"]["y1"]),
        )
        return best["embedding"], best["bbox"]
