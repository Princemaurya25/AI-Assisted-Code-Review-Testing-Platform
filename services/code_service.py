from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.submission import CodeSubmission
from app.schemas.submission import CodeSubmissionCreate
from app.analyzers.language_detector import detect_language


def create_submission(db: Session, user_id: int, sub_in: CodeSubmissionCreate) -> CodeSubmission:
    # Size check (max 500 KB)
    code_size = len(sub_in.code.encode('utf-8'))
    if code_size > 500 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source code file size exceeds maximum limit of 500 KB."
        )

    # Detect language if not explicitly provided
    detected_lang, confidence, supported = detect_language(sub_in.code, sub_in.language or "")
    
    submission = CodeSubmission(
        user_id=user_id,
        title=sub_in.title,
        language=detected_lang,
        code=sub_in.code,
        context_description=sub_in.context_description,
        file_size=code_size
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def get_user_submissions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    language: Optional[str] = None
) -> List[CodeSubmission]:
    query = db.query(CodeSubmission).filter(CodeSubmission.user_id == user_id)
    if language:
        query = query.filter(CodeSubmission.language == language)
    return query.order_by(CodeSubmission.created_at.desc()).offset(skip).limit(limit).all()


def get_submission_by_id(db: Session, user_id: int, submission_id: int) -> Optional[CodeSubmission]:
    return db.query(CodeSubmission).filter(
        CodeSubmission.id == submission_id,
        CodeSubmission.user_id == user_id
    ).first()
