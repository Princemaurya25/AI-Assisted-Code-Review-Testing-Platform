from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CodeSubmissionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    language: Optional[str] = None  # auto-detected if not provided
    code: str = Field(..., min_length=1)
    context_description: Optional[str] = None


class CodeSubmissionOut(BaseModel):
    id: int
    user_id: int
    title: str
    language: str
    code: str
    context_description: Optional[str] = None
    file_size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LanguageDetectOut(BaseModel):
    detected_language: str
    confidence: float
    supported: bool
