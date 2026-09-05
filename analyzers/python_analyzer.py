import ast
from typing import List, Tuple
from app.analyzers.base import StaticAnalysisResult, ComplexityMetrics, AnalysisFinding
from app.analyzers.security_analyzer import scan_security_issues


class PythonASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1
        self.function_count = 0
        self.max_func_length = 0
        self.max_nesting_depth = 0
        self.findings: List[AnalysisFinding] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.function_count += 1
        func_length = (node.end_lineno - node.lineno + 1) if hasattr(node, 'end_lineno') and node.end_lineno else 10
        if func_length > self.max_func_length:
            self.max_func_length = func_length

        if func_length > 40:
            self.findings.append(AnalysisFinding(
                category="maintainability",
                severity="medium",
                title=f"Long Function '{node.name}' ({func_length} lines)",
                description=f"Function '{node.name}' spans {func_length} lines. Long functions are harder to test and maintain.",
                recommendation="Break down into smaller helper functions (single responsibility principle).",
                line_number=node.lineno,
                code_snippet=f"def {node.name}(...):",
                confidence=1.0,
                source_type="RULE_BASED",
                validation_status="VALIDATED"
            ))

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)  # type: ignore

    def visit_If(self, node: ast.If):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.complexity += 1
        # Check for bare except or silent pass
        if node.type is None:
            self.findings.append(AnalysisFinding(
                category="bug",
                severity="high",
                title="Bare 'except:' Clause",
                description="Catching all exceptions without specifying exception type masks unexpected errors including KeyboardInterrupt.",
                recommendation="Specify explicit exception types e.g., 'except Exception as e:'",
                line_number=node.lineno,
                code_snippet="except:",
                confidence=1.0,
                source_type="RULE_BASED",
                validation_status="VALIDATED"
            ))

        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.findings.append(AnalysisFinding(
                category="bug",
                severity="medium",
                title="Empty Exception Handler (Swallowed Error)",
                description="Exception is silently ignored with 'pass'. This can mask critical bugs.",
                recommendation="Log the exception or re-raise it instead of swallowing it silently.",
                line_number=node.lineno,
                code_snippet="except: pass",
                confidence=1.0,
                source_type="RULE_BASED",
                validation_status="VALIDATED"
            ))
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


def calculate_max_nesting(code: str) -> int:
    lines = code.splitlines()
    max_depth = 0
    current_depth = 0
    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(stripped)
        depth = indent // 4
        if depth > max_depth:
            max_depth = depth
    return max_depth


def analyze_python_code(code: str) -> StaticAnalysisResult:
    findings: List[AnalysisFinding] = []
    
    # Run Security Rules
    security_findings = scan_security_issues(code, "Python")
    findings.extend(security_findings)

    # Check Syntax
    try:
        tree = ast.parse(code)
        syntax_valid = True
        syntax_error = None
    except SyntaxError as err:
        syntax_valid = False
        syntax_error = f"SyntaxError on line {err.lineno}: {err.msg}"
        findings.append(AnalysisFinding(
            category="bug",
            severity="critical",
            title="Python Syntax Error",
            description=f"File contains invalid Python syntax: {err.msg}",
            recommendation="Fix Python syntax error before proceeding.",
            line_number=err.lineno or 1,
            code_snippet=err.text.strip() if err.text else "",
            confidence=1.0,
            source_type="RULE_BASED",
            validation_status="VALIDATED"
        ))
        return StaticAnalysisResult(
            language="Python",
            syntax_valid=False,
            syntax_error=syntax_error,
            metrics=ComplexityMetrics(
                cyclomatic_complexity=1,
                function_count=0,
                max_function_length=0,
                max_nesting_depth=calculate_max_nesting(code),
                estimated_time_complexity="Unknown",
                estimated_space_complexity="Unknown",
                maintainability_rating="Low"
            ),
            findings=findings
        )

    visitor = PythonASTVisitor()
    visitor.visit(tree)
    findings.extend(visitor.findings)

    nesting_depth = calculate_max_nesting(code)
    if nesting_depth > 4:
        findings.append(AnalysisFinding(
            category="readability",
            severity="medium",
            title=f"Deep Code Nesting (Level {nesting_depth})",
            description=f"Deeply nested code structures (depth {nesting_depth}) impair readability and increase cognitive load.",
            recommendation="Use guard clauses and early returns to flatten nested blocks.",
            line_number=1,
            confidence=0.9,
            source_type="RULE_BASED",
            validation_status="VALIDATED"
        ))

    # Calculate complexity metrics
    cc = visitor.complexity
    if cc > 15:
        rating = "Low"
    elif cc > 8:
        rating = "Medium"
    else:
        rating = "High"

    # Time/Space Complexity Estimation based on loops
    loop_count = code.count(" for ") + code.count(" while ")
    if loop_count == 0:
        time_comp = "O(1)"
        space_comp = "O(1)"
    elif loop_count == 1:
        time_comp = "O(n)"
        space_comp = "O(1)"
    elif nesting_depth >= 2 and loop_count >= 2:
        time_comp = "O(n²)"
        space_comp = "O(n)"
    else:
        time_comp = "O(n)"
        space_comp = "O(1)"

    metrics = ComplexityMetrics(
        cyclomatic_complexity=cc,
        function_count=visitor.function_count,
        max_function_length=visitor.max_func_length,
        max_nesting_depth=nesting_depth,
        estimated_time_complexity=time_comp,
        estimated_space_complexity=space_comp,
        maintainability_rating=rating
    )

    return StaticAnalysisResult(
        language="Python",
        syntax_valid=True,
        syntax_error=None,
        metrics=metrics,
        findings=findings
    )
