from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class GeneratedTestOut(BaseModel):
    id: int
    review_id: int
    name: str
    test_type: str
    code: str
    expected_outcome: Optional[str] = None
    execution_status: str  # PASSED, FAILED, ERROR, TIMEOUT, SKIPPED, REJECTED
    execution_output: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TestExecutionResult(BaseModel):
    test_id: int
    status: str
    output: str
