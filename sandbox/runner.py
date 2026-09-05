import ast
from typing import Tuple
from app.sandbox.python_sandbox import execute_python_test_sandboxed


def validate_test_syntax(test_code: str, language: str) -> Tuple[bool, str]:
    """
    Validates test code syntax before executing.
    """
    lang_lower = language.lower()
    if lang_lower == "python":
        try:
            ast.parse(test_code)
            return True, ""
        except SyntaxError as err:
            return False, f"Test Syntax Error on line {err.lineno}: {err.msg}"
    
    # Simple brace matching check for non-python languages
    if test_code.count('{') != test_code.count('}'):
        return False, "Unbalanced braces in generated test code."
    
    return True, ""


def run_sandboxed_test(source_code: str, test_code: str, language: str) -> Tuple[str, str]:
    """
    Orchestrates sandboxed execution based on programming language.
    """
    syntax_ok, error_msg = validate_test_syntax(test_code, language)
    if not syntax_ok:
        return "REJECTED", f"Test Code Validation Failed: {error_msg}"

    lang_lower = language.lower()
    if lang_lower == "python":
        return execute_python_test_sandboxed(source_code, test_code)
    else:
        # Non-python languages static test structure validation
        return "SKIPPED", f"Test structure validated for {language}. Sandboxed execution available for Python execution engine."
