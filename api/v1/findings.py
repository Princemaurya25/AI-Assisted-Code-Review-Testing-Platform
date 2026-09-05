from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.submission import CodeSubmission
from app.models.review import CodeReview
from app.models.finding import Finding
from app.schemas.finding import FindingOut, FindingValidateUpdate

router = APIRouter(prefix="/findings", tags=["Findings & Validation"])


@router.get("/reviews/{review_id}/findings", response_model=List[FindingOut])
def get_review_findings(
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

    return review.findings


@router.post("/{finding_id}/validate", response_model=FindingOut)
def validate_finding_manual(
    finding_id: int,
    val_in: FindingValidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    finding = db.query(Finding).join(CodeReview).join(CodeSubmission).filter(
        Finding.id == finding_id,
        CodeSubmission.user_id == current_user.id
    ).first()

    if not finding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found.")

    finding.validation_status = val_in.validation_status
    if val_in.validation_notes:
        finding.validation_notes = val_in.validation_notes

    db.commit()
    db.refresh(finding)
    return finding
