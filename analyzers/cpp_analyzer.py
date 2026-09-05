import re
from typing import List
from app.analyzers.base import StaticAnalysisResult, ComplexityMetrics, AnalysisFinding
from app.analyzers.security_analyzer import scan_security_issues


def analyze_cpp_code(code: str) -> StaticAnalysisResult:
    findings: List[AnalysisFinding] = []

    # Security rules
    findings.extend(scan_security_issues(code, "C++"))

    # Unsafe C functions check
    lines = code.splitlines()
    unsafe_c_funcs = [
        (r'\bgets\s*\(', "Use of Extremely Unsafe function 'gets()'", "gets() causes severe buffer overflows and has been removed from modern C++ standards.", "critical"),
        (r'\bstrcpy\s*\(', "Use of Unsafe Function 'strcpy()'", "strcpy() does not perform bounds checking, leading to buffer overflows. Use std::string or strncpy_s.", "high"),
        (r'\bstrcat\s*\(', "Use of Unsafe Function 'strcat()'", "strcat() can overflow buffers. Use std::string operator+= or strncat_s.", "high"),
        (r'\bsprintf\s*\(', "Use of Unsafe Function 'sprintf()'", "sprintf() is vulnerable to buffer overflows. Use snprintf() or std::ostringstream.", "medium"),
    ]

    for idx, line in enumerate(lines, start=1):
        for pattern, title, desc, severity in unsafe_c_funcs:
            if re.search(pattern, line):
                findings.append(AnalysisFinding(
                    category="security",
                    severity=severity,
                    title=title,
                    description=desc,
                    recommendation="Replace with safe C++ Standard Library equivalents.",
                    line_number=idx,
                    code_snippet=line.strip(),
                    confidence=1.0,
                    source_type="RULE_BASED",
                    validation_status="VALIDATED"
                ))

        # Check raw pointers vs smart pointers
        if re.search(r'\bnew\s+\w+', line) and "std::make_shared" not in line and "std::make_unique" not in line:
            findings.append(AnalysisFinding(
                category="maintainability",
                severity="medium",
                title="Raw 'new' Allocation",
                description="Manual memory management using 'new' increases risk of memory leaks and double-free errors.",
                recommendation="Prefer smart pointers like std::unique_ptr or std::shared_ptr (RAII).",
                line_number=idx,
                code_snippet=line.strip(),
                confidence=0.85,
                source_type="RULE_BASED",
                validation_status="VALIDATED"
            ))

    # Cyclomatic Complexity
    decision_tokens = [r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b', r'\bcatch\b', r'&&', r'\|\|', r'\bcase\b', r'\?']
    complexity = 1
    for token in decision_tokens:
        complexity += len(re.findall(token, code))

    function_count = len(re.findall(r'(\w+[\s\*&]+)+\w+\s*\([^)]*\)\s*\{', code))

    max_nesting = 0
    curr_nesting = 0
    for line in lines:
        curr_nesting += line.count('{') - line.count('}')
        if curr_nesting > max_nesting:
            max_nesting = curr_nesting

    rating = "High" if complexity < 8 else ("Medium" if complexity < 15 else "Low")
    time_comp = "O(n²)" if max_nesting >= 2 and ("for" in code or "while" in code) else ("O(n)" if "for" in code or "while" in code else "O(1)")

    return StaticAnalysisResult(
        language="C++",
        syntax_valid=True,
        syntax_error=None,
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
