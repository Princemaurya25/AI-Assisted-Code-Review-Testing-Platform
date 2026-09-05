from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.submission import CodeSubmissionCreate, CodeSubmissionOut, LanguageDetectOut
from app.services.code_service import create_submission, get_user_submissions, get_submission_by_id
from app.analyzers.language_detector import detect_language

router = APIRouter(prefix="/code", tags=["Code Submissions"])


@router.post("/submit", response_model=CodeSubmissionOut, status_code=status.HTTP_201_CREATED)
def submit_code(
    sub_in: CodeSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_submission(db, current_user.id, sub_in)


@router.post("/upload", response_model=CodeSubmissionOut, status_code=status.HTTP_201_CREATED)
async def upload_code_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    context_description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content_bytes = await file.read()
    try:
        code_str = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content must be UTF-8 encoded plain text."
        )

    filename = file.filename or "submitted_code"
    file_title = title or filename

    sub_in = CodeSubmissionCreate(
        title=file_title,
        language=language or filename.split(".")[-1],
        code=code_str,
        context_description=context_description
    )
    return create_submission(db, current_user.id, sub_in)


@router.post("/detect-language", response_model=LanguageDetectOut)
def detect_code_language(payload: dict):
    code = payload.get("code", "")
    filename = payload.get("filename", "")
    detected_lang, confidence, supported = detect_language(code, filename)
    return {
        "detected_language": detected_lang,
        "confidence": confidence,
        "supported": supported
    }


@router.get("", response_model=List[CodeSubmissionOut])
def list_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    language: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_submissions(db, current_user.id, skip=skip, limit=limit, language=language)


@router.get("/{submission_id}", response_model=CodeSubmissionOut)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = get_submission_by_id(db, current_user.id, submission_id)
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")
    return sub
