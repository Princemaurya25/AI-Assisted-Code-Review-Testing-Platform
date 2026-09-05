from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class FindingOut(BaseModel):
    id: int
    review_id: int
    category: str
    severity: str
    title: str
    description: str
    recommendation: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    confidence: float
    source_type: str  # RULE_BASED, AI_SUGGESTED
    validation_status: str  # VALIDATED, PARTIALLY_VALIDATED, REJECTED, AI_SUGGESTED
    validation_notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FindingValidateUpdate(BaseModel):
    validation_status: str  # VALIDATED, PARTIALLY_VALIDATED, REJECTED, AI_SUGGESTED
    validation_notes: Optional[str] = None
