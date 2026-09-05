from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class GeneratedTest(Base):
    __tablename__ = "generated_tests"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("code_reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    test_type = Column(String(50), nullable=False, default="normal")  # normal, boundary, edge, invalid, exception
    code = Column(Text, nullable=False)
    expected_outcome = Column(Text, nullable=True)
    execution_status = Column(String(50), nullable=False, default="SKIPPED")  # PASSED, FAILED, ERROR, TIMEOUT, SKIPPED, REJECTED
    execution_output = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    review = relationship("CodeReview", back_populates="generated_tests")
