import re
from typing import List
from app.analyzers.base import StaticAnalysisResult, ComplexityMetrics, AnalysisFinding
from app.analyzers.security_analyzer import scan_security_issues


def analyze_js_ts_code(code: str, language: str = "JavaScript") -> StaticAnalysisResult:
    findings: List[AnalysisFinding] = []

    # Run security scanner
    findings.extend(scan_security_issues(code, language))

    # Basic Syntax Check (Brace/Paren Matching)
    stack = []
    syntax_valid = True
    syntax_error = None
    line_no = 1
    
    for idx, char in enumerate(code):
        if char == '\n':
            line_no += 1
        if char in "({[":
            stack.append((char, line_no))
        elif char in ")}]" :
            if not stack:
                syntax_valid = False
                syntax_error = f"Unmatched closing '{char}' at line {line_no}"
                break
            top, _ = stack.pop()
            if (char == ')' and top != '(') or (char == '}' and top != '{') or (char == ']' and top != '['):
                syntax_valid = False
                syntax_error = f"Mismatched bracket '{top}' and '{char}' at line {line_no}"
                break

    if syntax_valid and stack:
        syntax_valid = False
        top, top_line = stack[-1]
        syntax_error = f"Unclosed '{top}' opening at line {top_line}"

    if not syntax_valid:
        findings.append(AnalysisFinding(
            category="bug",
            severity="critical",
            title=f"{language} Syntax Error",
            description=syntax_error or "Syntax check failed.",
            recommendation="Fix bracket/syntax errors in source code.",
            line_number=top_line if stack else line_no,
            confidence=1.0,
            source_type="RULE_BASED",
            validation_status="VALIDATED"
        ))

    # Cyclomatic Complexity calculation
    decision_tokens = [r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b', r'\bcatch\b', r'&&', r'\|\|', r'\bcase\b', r'\?']
    complexity = 1
    for token in decision_tokens:
        matches = re.findall(token, code)
        complexity += len(matches)

    # Function count and length
    funcs = re.findall(r'(function\s+\w*|\w+\s*=\s*\([^)]*\)\s*=>|\b\w+\s*\([^)]*\)\s*\{)', code)
    function_count = len(funcs)

    # Code quality / smell rules
    lines = code.splitlines()
    for idx, line in enumerate(lines, start=1):
        if re.search(r'\bvar\s+\w+', line):
            findings.append(AnalysisFinding(
                category="best_practices",
                severity="low",
                title="Use of 'var' Keyword",
                description="The 'var' keyword has function scope and can lead to hoisting issues.",
                recommendation="Replace 'var' with 'const' or 'let'.",
                line_number=idx,
                code_snippet=line.strip(),
                confidence=1.0,
                source_type="RULE_BASED",
                validation_status="VALIDATED"
            ))

        if re.search(r'[^=!]=[=][^=]', line) and "===" not in line and "!==" not in line and "==" in line:
            findings.append(AnalysisFinding(
                category="bug",
                severity="low",
                title="Loose Equality Operator (==)",
                description="Loose equality (==) performs type coercion, leading to edge case bugs.",
                recommendation="Use strict equality operator (===).",
                line_number=idx,
                code_snippet=line.strip(),
                confidence=0.9,
                source_type="RULE_BASED",
                validation_status="VALIDATED"
            ))

    # Nesting depth
    max_nesting = 0
    curr_nesting = 0
    for line in lines:
        curr_nesting += line.count('{') - line.count('}')
        if curr_nesting > max_nesting:
            max_nesting = curr_nesting

    rating = "High" if complexity < 8 else ("Medium" if complexity < 15 else "Low")
    time_comp = "O(n²)" if max_nesting >= 2 and ("for" in code or "while" in code) else ("O(n)" if "for" in code or "while" in code else "O(1)")

    return StaticAnalysisResult(
        language=language,
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
