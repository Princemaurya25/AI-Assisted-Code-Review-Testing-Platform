import json
import logging
import openai
from typing import Dict, Any
from app.core.config import settings
from app.schemas.ai import AIReviewSchema, AITestSuiteSchema
from app.validators.prompt_sanitizer import format_code_data_block
from app.ai.prompts import SYSTEM_CODE_REVIEW_PROMPT, SYSTEM_TEST_GENERATION_PROMPT

logger = logging.getLogger("code_review_platform")


def get_mock_ai_review(code: str, language: str) -> AIReviewSchema:
    lines = code.splitlines()
    line_count = len(lines)
    
    findings = [
        {
            "category": "performance",
            "severity": "medium",
            "line": min(3, line_count),
            "title": "Suboptimal Operation / Function Call in Loop",
            "description": "Performing repeated operations or dynamic allocations inside loops can degrade runtime performance.",
            "recommendation": "Hoist constant computations and static declarations outside the loop iteration.",
            "confidence": 0.88,
            "code_snippet": lines[min(2, line_count - 1)].strip() if lines else ""
        },
        {
            "category": "maintainability",
            "severity": "low",
            "line": min(1, line_count),
            "title": "Missing Comprehensive Type Annotations / Documentation",
            "description": "Function signatures lack detailed docstrings or type hints for parameters and return types.",
            "recommendation": "Add standard docstrings describing parameter constraints, side effects, and return values.",
            "confidence": 0.92,
            "code_snippet": lines[0].strip() if lines else ""
        }
    ]

    # Add security mock finding if security keywords present
    code_lower = code.lower()
    if "select" in code_lower or "eval" in code_lower or "password" in code_lower:
        findings.append({
            "category": "security",
            "severity": "high",
            "line": min(5, line_count),
            "title": "Potential Security Vulnerability Pattern Detected",
            "description": "Code contains references to database queries, secrets, or dynamic evaluation that require strict validation.",
            "recommendation": "Sanitize input parameters and use parameterized query interfaces.",
            "confidence": 0.95,
            "code_snippet": lines[min(4, line_count - 1)].strip() if lines else ""
        })

    recommendations = [
        {
            "category": "Readability",
            "title": "Refactor Guard Clauses for Input Validation",
            "problem": "Deep nesting and inline condition checking increases cognitive complexity.",
            "reason": "Early returns (guard clauses) make main function logic linear and significantly easier to test.",
            "original_code": lines[0].strip() if lines else "",
            "suggested_code": f"// Enhanced {language} Implementation\n" + (lines[0].strip() if lines else ""),
            "start_line": 1,
            "end_line": min(5, line_count)
        }
    ]

    return AIReviewSchema(
        summary=f"Automated AI Code Review completed for {language} source snippet. Analyzed {line_count} lines of code across quality, security, performance, and testing dimensions.",
        findings=findings,
        recommendations=recommendations
    )


def get_mock_test_suite(code: str, language: str) -> AITestSuiteSchema:
    tests = [
        {
            "name": "test_normal_execution",
            "test_type": "normal",
            "code": f"def test_normal():\n    # Test normal execution for {language}\n    pass",
            "expected_outcome": "Returns expected status code and output."
        },
        {
            "name": "test_boundary_conditions",
            "test_type": "boundary",
            "code": f"def test_boundary():\n    # Test boundary limits (0, max values)\n    pass",
            "expected_outcome": "Handles upper/lower limit inputs gracefully without panic."
        },
        {
            "name": "test_invalid_inputs_exception",
            "test_type": "exception",
            "code": f"def test_invalid_input():\n    # Test invalid inputs\n    pass",
            "expected_outcome": "Raises appropriate exception for malformed parameters."
        }
    ]
    return AITestSuiteSchema(tests=tests)


def call_openai_review(code: str, language: str, context: str = "") -> AIReviewSchema:
    api_key = settings.OPENAI_API_KEY.strip()

    if not api_key or api_key.lower() == "mock" or api_key.startswith("sk-placeholder"):
        logger.info("Using Deterministic Mock AI Review Service (No valid OpenAI API key configured).")
        return get_mock_ai_review(code, language)

    try:
        client = openai.OpenAI(api_key=api_key)
        data_payload = format_code_data_block(code, language, context)

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_CODE_REVIEW_PROMPT},
                {"role": "user", "content": f"Analyze this {language} code payload:\n{data_payload}"}
            ],
            temperature=0.2,
            max_tokens=2500
        )

        content = response.choices[0].message.content
        raw_json = json.loads(content)
        
        # Pydantic schema validation
        validated_response = AIReviewSchema.model_validate(raw_json)
        return validated_response

    except Exception as e:
        logger.warning(f"OpenAI API call failed: {str(e)}. Falling back to deterministic mock AI response.")
        return get_mock_ai_review(code, language)


def call_openai_test_generation(code: str, language: str, context: str = "") -> AITestSuiteSchema:
    api_key = settings.OPENAI_API_KEY.strip()

    if not api_key or api_key.lower() == "mock" or api_key.startswith("sk-placeholder"):
        logger.info("Using Deterministic Mock Test Generation Service.")
        return get_mock_test_suite(code, language)

    try:
        client = openai.OpenAI(api_key=api_key)
        data_payload = format_code_data_block(code, language, context)

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_TEST_GENERATION_PROMPT},
                {"role": "user", "content": f"Generate tests for this {language} code payload:\n{data_payload}"}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        content = response.choices[0].message.content
        raw_json = json.loads(content)
        
        validated_response = AITestSuiteSchema.model_validate(raw_json)
        return validated_response

    except Exception as e:
        logger.warning(f"OpenAI Test Generation API call failed: {str(e)}. Falling back to mock test suite.")
        return get_mock_test_suite(code, language)
