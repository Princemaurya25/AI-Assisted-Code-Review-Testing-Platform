from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("code_reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # security, bug, performance, maintainability, readability, best_practices
    severity = Column(String(50), nullable=False, index=True)  # critical, high, medium, low, info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    line_number = Column(Integer, nullable=True)
    code_snippet = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False, default=1.0)
    source_type = Column(String(50), nullable=False, default="RULE_BASED")  # RULE_BASED, AI_SUGGESTED
    validation_status = Column(String(50), nullable=False, default="VALIDATED")  # VALIDATED, PARTIALLY_VALIDATED, REJECTED, AI_SUGGESTED
    validation_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    review = relationship("CodeReview", back_populates="findings")
