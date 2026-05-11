from pydantic import BaseModel, Field
from typing import List, Optional


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    score: float


class FaceDetection(BaseModel):
    bbox: BoundingBox
    embedding: Optional[List[float]] = None
    confidence: float


class DetectResponse(BaseModel):
    faces: List[FaceDetection]
    count: int


class EnrollRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    metadata: Optional[dict] = Field(default_factory=dict)


class EnrollResponse(BaseModel):
    person_id: str
    name: str
    message: str


class IdentifyResponse(BaseModel):
    person_id: Optional[str]
    name: Optional[str]
    similarity: float
    bbox: BoundingBox
    is_match: bool


class PersonSummary(BaseModel):
    person_id: str
    name: str
    enrolled_at: Optional[str] = None
