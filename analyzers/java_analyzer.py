import re
from typing import List
from app.analyzers.base import StaticAnalysisResult, ComplexityMetrics, AnalysisFinding
from app.analyzers.security_analyzer import scan_security_issues


def analyze_java_code(code: str) -> StaticAnalysisResult:
    findings: List[AnalysisFinding] = []

    # Security rules
    findings.extend(scan_security_issues(code, "Java"))

    # Basic Syntax (Class declaration check)
    syntax_valid = True
    syntax_error = None
    if "class " not in code and "interface " not in code and "enum " not in code:
        syntax_valid = False
        syntax_error = "Missing class or interface definition in Java code."
        findings.append(AnalysisFinding(
            category="bug",
            severity="high",
            title="Missing Java Class Structure",
            description="Java code must define at least one class, interface, or record.",
            recommendation="Wrap methods inside a valid public class declaration.",
            line_number=1,
            confidence=0.9,
            source_type="RULE_BASED",
            validation_status="VALIDATED"
        ))

    # Cyclomatic Complexity
    decision_tokens = [r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b', r'\bcatch\b', r'&&', r'\|\|', r'\bcase\b', r'\?']
    complexity = 1
    for token in decision_tokens:
        complexity += len(re.findall(token, code))

    # Methods count
    methods = re.findall(r'(public|protected|private|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*(\{ throws|\{)', code)
    function_count = len(methods)

    lines = code.splitlines()
    for idx, line in enumerate(lines, start=1):
        if re.search(r'catch\s*\([^)]+\)\s*\{\s*\}', line):
            findings.append(AnalysisFinding(
                category="bug",
                severity="high",
                title="Empty Java Catch Block",
                description="Swallowing exceptions in an empty catch block prevents failure visibility.",
                recommendation="Log exception details or rethrow as a domain exception.",
                line_number=idx,
                code_snippet=line.strip(),
                confidence=1.0,
                source_type="RULE_BASED",
                validation_status="VALIDATED"
            ))

        if "System.out.print" in line:
            findings.append(AnalysisFinding(
                category="best_practices",
                severity="info",
                title="Direct System.out Printing",
                description="Avoid using System.out.println for production logging.",
                recommendation="Use a structured logging framework like SLF4J / Logback.",
                line_number=idx,
                code_snippet=line.strip(),
                confidence=0.8,
                source_type="RULE_BASED",
                validation_status="VALIDATED"
            ))

    max_nesting = 0
    curr_nesting = 0
    for line in lines:
        curr_nesting += line.count('{') - line.count('}')
        if curr_nesting > max_nesting:
            max_nesting = curr_nesting

    rating = "High" if complexity < 8 else ("Medium" if complexity < 15 else "Low")
    time_comp = "O(n²)" if max_nesting >= 2 and ("for" in code or "while" in code) else ("O(n)" if "for" in code or "while" in code else "O(1)")

    return StaticAnalysisResult(
        language="Java",
        syntax_valid=syntax_valid,
        syntax_error=syntax_error,
        metrics=ComplexityMetrics(
            cyclomatic_complexity=complexity,
            function_count=function_count,
            max_function_length=len(lines),
            max_nesting_depth=max_nesting,
            estimated_time_complexity=time_comp,
            estimated_space_complexity="O(1)",
            maintainability_rating=rating
        ),
        findings=findings
    )
