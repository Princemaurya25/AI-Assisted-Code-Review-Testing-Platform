from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.submission import CodeSubmission
from app.models.review import CodeReview
from app.models.test_case import GeneratedTest
from app.schemas.test import GeneratedTestOut, TestExecutionResult
from app.sandbox.runner import run_sandboxed_test

router = APIRouter(prefix="/tests", tags=["Test Cases & Execution"])


@router.get("/reviews/{review_id}/tests", response_model=List[GeneratedTestOut])
def get_review_tests(
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

    return review.generated_tests


@router.post("/{test_id}/execute", response_model=TestExecutionResult)
def execute_single_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    test_model = db.query(GeneratedTest).join(CodeReview).join(CodeSubmission).filter(
        GeneratedTest.id == test_id,
        CodeSubmission.user_id == current_user.id
    ).first()

    if not test_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated test not found.")

    submission = test_model.review.submission
    exec_status, exec_output = run_sandboxed_test(submission.code, test_model.code, submission.language)

    test_model.execution_status = exec_status
    test_model.execution_output = exec_output
    db.commit()

    return TestExecutionResult(
        test_id=test_model.id,
        status=exec_status,
        output=exec_output
    )
