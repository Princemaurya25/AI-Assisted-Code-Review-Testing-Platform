from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.submission import CodeSubmission
from app.models.review import CodeReview
from app.models.finding import Finding
from app.models.test_case import GeneratedTest
from app.schemas.review import DashboardStatsOut, ReviewOut

router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])


@router.get("/stats", response_model=DashboardStatsOut)
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total Reviews for current user
    reviews_query = db.query(CodeReview).join(CodeSubmission).filter(CodeSubmission.user_id == current_user.id)
    total_reviews = reviews_query.count()

    if total_reviews == 0:
        return DashboardStatsOut(
            total_reviews=0,
            average_score=0.0,
            security_issues_count=0,
            critical_findings_count=0,
            test_success_rate=100.0,
            language_breakdown={},
            recent_reviews=[]
        )

    # Average Score
    avg_score_res = db.query(func.avg(CodeReview.overall_score)).join(CodeSubmission).filter(
        CodeSubmission.user_id == current_user.id
    ).scalar()
    avg_score = round(float(avg_score_res or 0.0), 1)

    # Security Issues Count
    security_count = db.query(Finding).join(CodeReview).join(CodeSubmission).filter(
        CodeSubmission.user_id == current_user.id,
        Finding.category == "security"
    ).count()

    # Critical Findings Count
    critical_count = db.query(Finding).join(CodeReview).join(CodeSubmission).filter(
        CodeSubmission.user_id == current_user.id,
        Finding.severity == "critical"
    ).count()

    # Test Success Rate
    total_tests = db.query(GeneratedTest).join(CodeReview).join(CodeSubmission).filter(
        CodeSubmission.user_id == current_user.id
    ).count()

    passed_tests = db.query(GeneratedTest).join(CodeReview).join(CodeSubmission).filter(
        CodeSubmission.user_id == current_user.id,
        GeneratedTest.execution_status == "PASSED"
    ).count()

    test_pass_rate = round((passed_tests / total_tests * 100.0), 1) if total_tests > 0 else 100.0

    # Language Breakdown
    lang_counts = db.query(CodeSubmission.language, func.count(CodeSubmission.id)).filter(
        CodeSubmission.user_id == current_user.id
    ).group_by(CodeSubmission.language).all()

    lang_breakdown = {lang: count for lang, count in lang_counts}

    # Recent Reviews (top 5)
    recent_reviews = reviews_query.order_by(CodeReview.created_at.desc()).limit(5).all()

    return DashboardStatsOut(
        total_reviews=total_reviews,
        average_score=avg_score,
        security_issues_count=security_count,
        critical_findings_count=critical_count,
        test_success_rate=test_pass_rate,
        language_breakdown=lang_breakdown,
        recent_reviews=recent_reviews
    )
