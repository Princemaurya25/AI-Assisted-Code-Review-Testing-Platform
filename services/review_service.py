import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.submission import CodeSubmission
from app.models.review import CodeReview
from app.models.finding import Finding
from app.models.test_case import GeneratedTest
from app.models.recommendation import Recommendation

from app.analyzers.complexity_analyzer import run_static_analysis
from app.ai.client import call_openai_review, call_openai_test_generation
from app.validators.finding_validator import validate_and_deduplicate_findings
from app.sandbox.runner import run_sandboxed_test
from app.services.score_service import calculate_review_scores

logger = logging.getLogger("code_review_platform")


def execute_full_code_review(db: Session, submission: CodeSubmission) -> CodeReview:
    logger.info(f"Executing Code Review Pipeline for Submission ID #{submission.id} ({submission.language})")

    # 1. Deterministic Static Code Analysis
    static_res = run_static_analysis(submission.code, submission.language)

    # 2. Structured AI Code Review
    ai_review = call_openai_review(submission.code, submission.language, submission.context_description or "")

    # 3. AI Output Validation Layer (Core Validation Engine)
    validated_findings = validate_and_deduplicate_findings(
        ai_review.findings,
        submission.code,
        submission.language,
        static_res.findings
    )

    # 4. AI Test Case Generation
    ai_test_suite = call_openai_test_generation(submission.code, submission.language, submission.context_description or "")

    # 5. Sandboxed Test Execution & Validation
    generated_test_models = []
    for t_schema in ai_test_suite.tests:
        exec_status, exec_output = run_sandboxed_test(submission.code, t_schema.code, submission.language)
        gen_test = GeneratedTest(
            name=t_schema.name,
            test_type=t_schema.test_type,
            code=t_schema.code,
            expected_outcome=t_schema.expected_outcome,
            execution_status=exec_status,
            execution_output=exec_output
        )
        generated_test_models.append(gen_test)

    # 6. Score Service Engine
    scores = calculate_review_scores(
        static_res,
        validated_findings,
        has_generated_tests=len(generated_test_models) > 0
    )

    # 7. Persist to Database
    review = CodeReview(
        submission_id=submission.id,
        overall_score=scores["overall"],
        quality_score=scores["quality"],
        security_score=scores["security"],
        performance_score=scores["performance"],
        maintainability_score=scores["maintainability"],
        testing_score=scores["testing"],
        summary=ai_review.summary,
        status="COMPLETED"
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Add Findings
    for f in validated_findings:
        db_f = Finding(
            review_id=review.id,
            category=f.category,
            severity=f.severity,
            title=f.title,
            description=f.description,
            recommendation=f.recommendation,
            line_number=f.line_number,
            code_snippet=f.code_snippet,
            confidence=f.confidence,
            source_type=f.source_type,
            validation_status=f.validation_status,
            validation_notes=f.validation_notes
        )
        db.add(db_f)

    # Add Generated Tests
    for gt in generated_test_models:
        gt.review_id = review.id
        db.add(gt)

    # Add Recommendations
    for rec in ai_review.recommendations:
        db_rec = Recommendation(
            review_id=review.id,
            category=rec.category,
            title=rec.title,
            problem=rec.problem,
            reason=rec.reason,
            original_code=rec.original_code,
            suggested_code=rec.suggested_code,
            start_line=rec.start_line,
            end_line=rec.end_line,
            status="PENDING"
        )
        db.add(db_rec)

    db.commit()
    db.refresh(review)

    logger.info(f"Code Review #{review.id} completed successfully. Score: {review.overall_score}/100")
    return review
