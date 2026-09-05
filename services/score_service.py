from typing import List, Dict, Any
from app.analyzers.base import StaticAnalysisResult, AnalysisFinding


def calculate_review_scores(
    static_result: StaticAnalysisResult,
    validated_findings: List[AnalysisFinding],
    has_generated_tests: bool = False
) -> Dict[str, float]:
    """
    Calculates transparent, deterministic scores (0.0 to 100.0) based on static metrics
    and validated findings.

    Formula:
    Base Score = 100.0
    Deductions per category:
      - Critical finding: -15.0
      - High finding: -8.0
      - Medium finding: -4.0
      - Low finding: -2.0
      - Info finding: -0.5
    """
    # Category score buckets starting at 100.0
    category_scores = {
        "quality": 100.0,
        "security": 100.0,
        "performance": 100.0,
        "maintainability": 100.0,
        "testing": 90.0 if has_generated_tests else 70.0
    }

    severity_penalties = {
        "critical": 15.0,
        "high": 8.0,
        "medium": 4.0,
        "low": 2.0,
        "info": 0.5
    }

    # Process validated findings (ignore rejected findings!)
    for f in validated_findings:
        if f.validation_status == "REJECTED":
            continue

        penalty = severity_penalties.get(f.severity.lower(), 2.0)
        cat = f.category.lower()

        if cat == "security":
            category_scores["security"] -= penalty
        elif cat == "performance":
            category_scores["performance"] -= penalty
        elif cat in ["maintainability", "readability"]:
            category_scores["maintainability"] -= penalty
        elif cat in ["bug", "best_practices"]:
            category_scores["quality"] -= penalty

    # Complexity penalties
    cc = static_result.metrics.cyclomatic_complexity
    if cc > 15:
        category_scores["maintainability"] -= 15.0
        category_scores["quality"] -= 10.0
    elif cc > 8:
        category_scores["maintainability"] -= 8.0

    if static_result.metrics.max_nesting_depth > 4:
        category_scores["maintainability"] -= 5.0

    if not static_result.syntax_valid:
        category_scores["quality"] -= 40.0

    # Clamp scores between 0.0 and 100.0
    for k in category_scores:
        category_scores[k] = round(max(0.0, min(100.0, category_scores[k])), 1)

    # Weighted Overall Score Calculation
    overall = (
        category_scores["quality"] * 0.30 +
        category_scores["security"] * 0.25 +
        category_scores["performance"] * 0.20 +
        category_scores["maintainability"] * 0.15 +
        category_scores["testing"] * 0.10
    )

    category_scores["overall"] = round(overall, 1)
    return category_scores
