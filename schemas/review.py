from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.finding import FindingOut
from app.schemas.test import GeneratedTestOut


class RecommendationOut(BaseModel):
    id: int
    review_id: int
    category: str
    title: str
    problem: str
    reason: str
    original_code: str
    suggested_code: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    status: str  # PENDING, ACCEPTED, REJECTED
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationAction(BaseModel):
    action: str  # ACCEPT, REJECT


class ComplexityMetricsOut(BaseModel):
    cyclomatic_complexity: int
    function_count: int
    max_function_length: int
    max_nesting_depth: int
    estimated_time_complexity: str
    estimated_space_complexity: str
    maintainability_rating: str  # High, Medium, Low


class ReviewOut(BaseModel):
    id: int
    submission_id: int
    overall_score: float
    quality_score: float
    security_score: float
    performance_score: float
    maintainability_score: float
    testing_score: float
    summary: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewDetailOut(ReviewOut):
    language: str
    title: str
    code: str
    context_description: Optional[str] = None
    complexity_metrics: Optional[ComplexityMetricsOut] = None
    findings: List[FindingOut] = []
    generated_tests: List[GeneratedTestOut] = []
    recommendations: List[RecommendationOut] = []


class DashboardStatsOut(BaseModel):
    total_reviews: int
    average_score: float
    security_issues_count: int
    critical_findings_count: int
    test_success_rate: float
    language_breakdown: dict
    recent_reviews: List[ReviewOut] = []
