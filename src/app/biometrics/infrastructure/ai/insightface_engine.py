from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import NotFoundError, ValidationError
from src.app.biometrics.domain.model.results import FaceExtractionResult
from src.app.biometrics.domain.model.valueobjects import BoundingBox, FaceEmbedding
from src.app.biometrics.domain.services import FaceEmbeddingExtractionQueryService


@dataclass(frozen=True, slots=True)
class _FacePick:
    embedding: tuple[float, ...]
    bbox: tuple[float, float, float, float]


class InsightFaceRecognitionEngine(FaceEmbeddingExtractionQueryService):
    """
    Real face detection + embedding extractor using InsightFace.

    Requires optional deps:
      - insightface
      - onnxruntime
      - opencv-python-headless
    """

    def __init__(
        self,
        model_name: str = "buffalo_l",
        det_size: tuple[int, int] = (640, 640),
    ) -> None:
        try:
            import cv2  # type: ignore
            from insightface.app import FaceAnalysis  # type: ignore
        except Exception as e:  # pragma: no cover
            raise ValidationError(
                "InsightFace engine requires insightface + onnxruntime + opencv-python-headless"
            ) from e

        self._cv2 = cv2
        self._app = FaceAnalysis(name=model_name, providers=["CPUExecutionProvider"])
        self._app.prepare(ctx_id=0, det_size=tuple(int(x) for x in det_size))

    async def handle_extract_embedding(self, image_bytes: bytes) -> FaceExtractionResult:
        if not image_bytes:
            raise ValidationError("image_bytes cannot be empty")

        img = self._decode(image_bytes)
        faces = self._app.get(img)
        if not faces:
            raise NotFoundError("No face detected")

        pick = self._pick_face(faces)
        emb = self._normalize(pick.embedding)

        x1, y1, x2, y2 = (int(v) for v in pick.bbox)
        w = max(1, x2 - x1)
        h = max(1, y2 - y1)
        box = BoundingBox(x=max(0, x1), y=max(0, y1), w=w, h=h)
        return FaceExtractionResult(
            embedding=FaceEmbedding(tuple(float(x) for x in emb)),
            box=box,
        )

    def _decode(self, image_bytes: bytes):
        import numpy as np  # local import to keep module load lightweight

        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = self._cv2.imdecode(arr, self._cv2.IMREAD_COLOR)
        if img is None:
            raise ValidationError("Invalid image bytes")
        return img

    @staticmethod
    def _pick_face(faces: list[object]) -> _FacePick:
        """
        Pick the largest face by bbox area.
        """

        best: _FacePick | None = None
        for f in faces:
            emb = getattr(f, "embedding", None)
            bbox = getattr(f, "bbox", None)
            if emb is None or bbox is None:
                continue
            bb = tuple(float(v) for v in bbox)
            if len(bb) < 4:
                continue
            area = float(max(0.0, (bb[2] - bb[0])) * max(0.0, (bb[3] - bb[1])))
            candidate = _FacePick(embedding=tuple(float(v) for v in emb), bbox=bb[:4])
            if best is None:
                best = candidate
                best_area = area
            else:
                if area > best_area:
                    best = candidate
                    best_area = area
        if best is None:
            raise NotFoundError("No usable face detected")
        return best

    @staticmethod
    def _normalize(values: tuple[float, ...]) -> tuple[float, ...]:
        import math

        vec = tuple(float(v) for v in values)
        norm = math.sqrt(sum(v * v for v in vec))
        if norm <= 1e-6:
            return vec
        return tuple(v / norm for v in vec)
