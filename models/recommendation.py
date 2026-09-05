from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("code_reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # Readability, Performance, Security, Maintainability, Architecture
    title = Column(String(255), nullable=False)
    problem = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    original_code = Column(Text, nullable=False)
    suggested_code = Column(Text, nullable=False)
    start_line = Column(Integer, nullable=True)
    end_line = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, ACCEPTED, REJECTED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    review = relationship("CodeReview", back_populates="recommendations")
