import numpy as np
from insightface.app import FaceAnalysis
from pathlib import Path

class FeatureExtractionLayer:
    def __init__(self, model_name: str = "buffalo_l", model_root: str = "models", det_size: tuple = (640, 640)):
        self.app = FaceAnalysis(name=model_name, root=model_root)
        self.app.prepare(ctx_id=-1, det_size=det_size)

    @staticmethod
    def l2_normalize(vec: np.ndarray, eps: float = 1e-12) -> np.ndarray:
        vec = np.asarray(vec, dtype=np.float32)
        denom = float(np.linalg.norm(vec))
        if denom < eps:
            return vec
        return vec / denom

    def detect(self, rgb_image: np.ndarray):
        return self.app.get(rgb_image)

    def extract_primary(self, rgb_image: np.ndarray) -> tuple:
        """
        Returns (embedding, face_obj) or (None, None) if no face detected.
        embedding: np.ndarray with shape (512,)
        face_obj: insightface.dataobj face (has bbox, kps, etc.)
        """
        faces = self.detect(rgb_image)
        if not faces:
            return None, None

        def area(face):
            x1, y1, x2, y2 = face.bbox
            return (x2 - x1) * (y2 - y1)

        main_face = max(faces, key=area)
        embedding = main_face.embedding
        if embedding is None:
            return None, None
        emb = self.l2_normalize(np.array(embedding, dtype=np.float32))
        return emb, main_face

    def extract_all(self, rgb_image: np.ndarray, min_det_score: float = 0.0) -> list:
        """
        Returns list of (embedding, face_obj) for all detected faces.
        Filters by face.det_score when available.
        """
        faces = self.detect(rgb_image)
        results = []
        for face in faces:
            det_score = float(getattr(face, "det_score", 1.0))
            if det_score < min_det_score:
                continue
            embedding = getattr(face, "embedding", None)
            if embedding is None:
                continue
            emb = self.l2_normalize(np.array(embedding, dtype=np.float32))
            results.append((emb, face))
        return results
