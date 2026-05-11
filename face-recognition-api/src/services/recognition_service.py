from pathlib import Path
from typing import List
import tempfile
import shutil

from src.models.detector import FaceDetector
from src.models.registry import FaceRegistry
from src.core.exceptions import FaceNotDetectedError, DuplicatePersonError
from src.api.schemas import (
    DetectResponse,
    EnrollResponse,
    IdentifyResponse,
    PersonSummary,
)


class RecognitionService:
    """
    Orquesta del pipeline: detectar -> extraer embedding -> buscar/registrar.
    Inyecta dependencias para facilitar testing y swaps de implementacion.
    """

    def __init__(self, detector: FaceDetector, registry: FaceRegistry):
        self.detector = detector
        self.registry = registry

    async def detect(self, image_path: Path) -> DetectResponse:
        faces = await self.detector.detect(image_path)
        return DetectResponse(
            faces=[
                {
                    "bbox": f["bbox"],
                    "embedding": f["embedding"],
                    "confidence": f["confidence"],
                }
                for f in faces
            ],
            count=len(faces),
        )

    async def enroll(self, image_path: Path, name: str, extra: dict) -> EnrollResponse:
        embedding, _ = await self.detector.get_single_embedding(image_path)
        # Opcional: verificar duplicados antes de agregar
        pid, existing_name, sim = await self.registry.search(embedding, k=1)
        if pid is not None and sim > 0.85:
            raise DuplicatePersonError(
                f"Rostro ya registrado como {existing_name} (sim={sim:.3f})"
            )
        person_id = await self.registry.add(name, embedding, extra)
        return EnrollResponse(
            person_id=person_id,
            name=name,
            message="Persona enrolada correctamente.",
        )

    async def identify(self, image_path: Path) -> List[IdentifyResponse]:
        faces = await self.detector.detect(image_path)
        results: List[IdentifyResponse] = []
        for face in faces:
            emb = face["embedding"]
            pid, pname, sim = await self.registry.search(emb, k=1)
            results.append(
                IdentifyResponse(
                    person_id=pid,
                    name=pname,
                    similarity=round(sim, 4),
                    bbox=face["bbox"],
                    is_match=pid is not None,
                )
            )
        return results

    async def list_persons(self) -> List[PersonSummary]:
        rows = await self.registry.list_persons()
        return [PersonSummary(**r) for r in rows]

    async def delete_person(self, person_id: str) -> None:
        await self.registry.delete(person_id)
