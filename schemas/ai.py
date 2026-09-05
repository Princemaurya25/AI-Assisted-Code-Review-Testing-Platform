from typing import List, Optional
from pydantic import BaseModel, Field


class AIFindingSchema(BaseModel):
    category: str = Field(..., description="security, bug, performance, maintainability, readability, best_practices")
    severity: str = Field(..., description="critical, high, medium, low, info")
    line: Optional[int] = Field(None, description="1-indexed line number in source code")
    title: str = Field(..., description="Short finding summary title")
    description: str = Field(..., description="Detailed explanation of the issue")
    recommendation: str = Field(..., description="How to fix or resolve")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    code_snippet: Optional[str] = Field(None, description="Exact code snippet referenced")


class AIRecommendationSchema(BaseModel):
    category: str = Field(..., description="Readability, Performance, Security, Maintainability, Architecture")
    title: str
    problem: str
    reason: str
    original_code: str
    suggested_code: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None


class AITestCaseSchema(BaseModel):
    name: str
    test_type: str = Field(..., description="normal, boundary, edge, invalid, exception")
    code: str
    expected_outcome: Optional[str] = None


class AIReviewSchema(BaseModel):
    summary: str
    findings: List[AIFindingSchema] = []
    recommendations: List[AIRecommendationSchema] = []


class AITestSuiteSchema(BaseModel):
    tests: List[AITestCaseSchema] = []
