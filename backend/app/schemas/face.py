from pydantic import BaseModel
from datetime import datetime

class FaceRegistrationRequest(BaseModel):
    student_id: int | None = None
    images: list[str]  # list of base64 encoded images

class FaceRegistrationResponse(BaseModel):
    success: bool
    message: str
    num_samples: int = 0
    quality_score: float = 0.0

class FaceRegistrationStatus(BaseModel):
    student_id: int
    is_registered: bool
    num_samples: int = 0
    quality_score: float = 0.0
    registered_at: datetime | None = None
