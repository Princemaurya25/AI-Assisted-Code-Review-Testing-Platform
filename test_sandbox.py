from app.sandbox.python_sandbox import execute_python_test_sandboxed


def test_sandbox_passing_python_test():
    source_code = """
def add(a, b):
    return a + b
"""
    test_code = """
def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
"""
    status, output = execute_python_test_sandboxed(source_code, test_code)
    assert status == "PASSED"


def test_sandbox_failing_assertion():
    source_code = """
def multiply(a, b):
    return a * b
"""
    test_code = """
def test_multiply():
    assert multiply(2, 3) == 999  # Should fail!
"""
    status, output = execute_python_test_sandboxed(source_code, test_code)
    assert status == "FAILED"
    assert "AssertionError" in output


def test_sandbox_execution_timeout():
    source_code = """
import time
def infinite_loop():
    while True:
        time.sleep(0.1)
"""
    test_code = """
def test_infinite():
    infinite_loop()
"""
    status, output = execute_python_test_sandboxed(source_code, test_code)
    assert status == "TIMEOUT"
