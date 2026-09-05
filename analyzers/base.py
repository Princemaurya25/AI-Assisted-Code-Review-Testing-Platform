from typing import List, Optional
from pydantic import BaseModel


class AnalysisFinding(BaseModel):
    category: str  # security, bug, performance, maintainability, readability, best_practices
    severity: str  # critical, high, medium, low, info
    title: str
    description: str
    recommendation: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    confidence: float = 1.0
    source_type: str = "RULE_BASED"
    validation_status: str = "VALIDATED"
    validation_notes: Optional[str] = None


class ComplexityMetrics(BaseModel):
    cyclomatic_complexity: int = 1
    function_count: int = 0
    max_function_length: int = 0
    max_nesting_depth: int = 0
    estimated_time_complexity: str = "O(1)"
    estimated_space_complexity: str = "O(1)"
    maintainability_rating: str = "High"


class StaticAnalysisResult(BaseModel):
    language: str
    syntax_valid: bool
    syntax_error: Optional[str] = None
    metrics: ComplexityMetrics
    findings: List[AnalysisFinding] = []
