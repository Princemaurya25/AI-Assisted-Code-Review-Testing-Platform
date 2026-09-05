from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("code_submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_score = Column(Float, nullable=False, default=0.0)
    quality_score = Column(Float, nullable=False, default=0.0)
    security_score = Column(Float, nullable=False, default=0.0)
    performance_score = Column(Float, nullable=False, default=0.0)
    maintainability_score = Column(Float, nullable=False, default=0.0)
    testing_score = Column(Float, nullable=False, default=0.0)
    summary = Column(Text, nullable=False, default="")
    status = Column(String(50), nullable=False, default="COMPLETED")  # COMPLETED, IN_PROGRESS, FAILED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    submission = relationship("CodeSubmission", back_populates="reviews")
    findings = relationship("Finding", back_populates="review", cascade="all, delete-orphan")
    generated_tests = relationship("GeneratedTest", back_populates="review", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="review", cascade="all, delete-orphan")
