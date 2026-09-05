from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.submission import CodeSubmission
from app.models.review import CodeReview
from app.models.recommendation import Recommendation
from app.schemas.review import ReviewOut, ReviewDetailOut, ComplexityMetricsOut, RecommendationOut, RecommendationAction
from app.services.code_service import get_submission_by_id
from app.services.review_service import execute_full_code_review
from app.analyzers.complexity_analyzer import run_static_analysis

router = APIRouter(prefix="/reviews", tags=["Code Reviews"])


@router.post("/{code_id}", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def trigger_code_review(
    code_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submission = get_submission_by_id(db, current_user.id, code_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Code submission not found.")

    review = execute_full_code_review(db, submission)
    return review


@router.get("/history", response_model=List[ReviewOut])
def get_review_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    language: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(CodeReview).join(CodeSubmission).filter(CodeSubmission.user_id == current_user.id)
    if language:
        query = query.filter(CodeSubmission.language == language)
    return query.order_by(CodeReview.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{review_id}", response_model=ReviewDetailOut)
def get_review_details(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(CodeReview).join(CodeSubmission).filter(
        CodeReview.id == review_id,
        CodeSubmission.user_id == current_user.id
    ).first()

    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

    # Calculate static complexity metrics for display
    submission = review.submission
    static_res = run_static_analysis(submission.code, submission.language)

    complexity_out = ComplexityMetricsOut(
        cyclomatic_complexity=static_res.metrics.cyclomatic_complexity,
        function_count=static_res.metrics.function_count,
        max_function_length=static_res.metrics.max_function_length,
        max_nesting_depth=static_res.metrics.max_nesting_depth,
        estimated_time_complexity=static_res.metrics.estimated_time_complexity,
        estimated_space_complexity=static_res.metrics.estimated_space_complexity,
        maintainability_rating=static_res.metrics.maintainability_rating
    )

    return ReviewDetailOut(
        id=review.id,
        submission_id=review.submission_id,
        overall_score=review.overall_score,
        quality_score=review.quality_score,
        security_score=review.security_score,
        performance_score=review.performance_score,
        maintainability_score=review.maintainability_score,
        testing_score=review.testing_score,
        summary=review.summary,
        status=review.status,
        created_at=review.created_at,
        language=submission.language,
        title=submission.title,
        code=submission.code,
        context_description=submission.context_description,
        complexity_metrics=complexity_out,
        findings=review.findings,
        generated_tests=review.generated_tests,
        recommendations=review.recommendations
    )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(CodeReview).join(CodeSubmission).filter(
        CodeReview.id == review_id,
        CodeSubmission.user_id == current_user.id
    ).first()

    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

    db.delete(review)
    db.commit()
    return None


@router.post("/recommendations/{recommendation_id}/action", response_model=RecommendationOut)
def update_recommendation_status(
    recommendation_id: int,
    action_in: RecommendationAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = db.query(Recommendation).join(CodeReview).join(CodeSubmission).filter(
        Recommendation.id == recommendation_id,
        CodeSubmission.user_id == current_user.id
    ).first()

    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found.")

    act = action_in.action.upper()
    if act in ["ACCEPT", "ACCEPTED"]:
        rec.status = "ACCEPTED"
    elif act in ["REJECT", "REJECTED"]:
        rec.status = "REJECTED"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Action must be ACCEPT or REJECT.")

    db.commit()
    db.refresh(rec)
    return rec
