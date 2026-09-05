from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token


def register_user(db: Session, user_in: UserCreate) -> User:
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered."
        )
    
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        password_hash=hashed_pwd,
        full_name=user_in.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, credentials: UserLogin) -> Optional[User]:
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        return None
    if not verify_password(credentials.password, user.password_hash):
        return None
    return user
