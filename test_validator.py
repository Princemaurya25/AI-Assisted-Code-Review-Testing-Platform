from app.schemas.ai import AIFindingSchema
from app.analyzers.base import AnalysisFinding
from app.validators.finding_validator import validate_ai_finding, validate_and_deduplicate_findings


def test_validator_line_out_of_bounds_rejection():
    code = "x = 10\ny = 20\n"
    ai_finding = AIFindingSchema(
        category="security",
        severity="high",
        line=999,  # Out of bounds!
        title="Fake Vulnerability",
        description="Hallucinated issue",
        recommendation="Fix it"
    )
    status, notes = validate_ai_finding(ai_finding, code, "Python", [])
    assert status == "REJECTED"
    assert "out of bounds" in notes


def test_validator_snippet_mismatch_rejection():
    code = "def foo():\n    return 42\n"
    ai_finding = AIFindingSchema(
        category="bug",
        severity="medium",
        line=2,
        title="Variable Error",
        description="Non-existent snippet",
        recommendation="Fix",
        code_snippet="non_existent_variable_name_xyz = 100"
    )
    status, notes = validate_ai_finding(ai_finding, code, "Python", [])
    assert status == "REJECTED"
    assert "not found" in notes


def test_validator_sql_injection_plausibility_rejection():
    code = "def calculate_factorial(n):\n    if n <= 1:\n        return 1\n    return n * calculate_factorial(n-1)\n"
    ai_finding = AIFindingSchema(
        category="security",
        severity="critical",
        line=2,
        title="SQL Injection Vulnerability",
        description="Vulnerable SQL query",
        recommendation="Use bindings",
        code_snippet="if n <= 1:"
    )
    status, notes = validate_ai_finding(ai_finding, code, "Python", [])
    assert status == "REJECTED"
    assert "no database or SQL query patterns exist" in notes


def test_validator_static_correlation_validated():
    code = "eval('1 + 1')\n"
    static_finding = AnalysisFinding(
        category="security",
        severity="critical",
        title="Use of Dangerous 'eval()' Function",
        description="eval is dangerous",
        recommendation="Avoid eval",
        line_number=1,
        source_type="RULE_BASED",
        validation_status="VALIDATED"
    )
    ai_finding = AIFindingSchema(
        category="security",
        severity="critical",
        line=1,
        title="Dangerous eval call",
        description="eval permits arbitrary execution",
        recommendation="Remove eval",
        code_snippet="eval('1 + 1')"
    )
    status, notes = validate_ai_finding(ai_finding, code, "Python", [static_finding])
    assert status == "VALIDATED"
    assert "Independently validated by static analysis" in notes
