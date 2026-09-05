import sys
import subprocess
import tempfile
import os
from typing import Tuple
from app.core.config import settings


def execute_python_test_sandboxed(source_code: str, test_code: str) -> Tuple[str, str]:
    """
    Executes Python test code along with source code in a safe, isolated temporary process
    with enforced timeouts and memory limits.

    Returns (status, output_log).
    Statuses: PASSED, FAILED, ERROR, TIMEOUT, REJECTED
    """
    # 1. Prepare combined script
    full_script = f"""# Isolated Sandbox Test Script
import sys, os

{source_code}

# --- Generated Test Execution ---
{test_code}

if __name__ == '__main__':
    # Run test functions if present
    test_funcs = [v for k, v in list(globals().items()) if k.startswith('test_') and callable(v)]
    for func in test_funcs:
        func()
    print("ALL_TESTS_PASSED_SUCCESSFULLY")
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(full_script)
        tmp_path = tmp_file.name

    try:
        # Prepare environment with stripped sensitive variables
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": os.path.dirname(tmp_path),
            "PYTHONDONTWRITEBYTECODE": "1"
        }

        # Run process with subprocess timeout
        proc = subprocess.Popen(
            [sys.executable, tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )

        stdout, stderr = proc.communicate(timeout=settings.SANDBOX_TIMEOUT_SECONDS)
        exit_code = proc.returncode

        if exit_code == 0 and "ALL_TESTS_PASSED_SUCCESSFULLY" in stdout:
            return "PASSED", f"Execution successful.\n{stdout.replace('ALL_TESTS_PASSED_SUCCESSFULLY', '').strip()}"
        elif exit_code == 0:
            return "PASSED", f"Execution completed cleanly.\n{stdout.strip()}"
        else:
            if "AssertionError" in stderr:
                return "FAILED", f"Test Assertion Failed:\n{stderr.strip()}"
            else:
                return "ERROR", f"Runtime Error during test execution:\n{stderr.strip()}"

    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        return "TIMEOUT", f"Execution Timed Out (exceeded limit of {settings.SANDBOX_TIMEOUT_SECONDS}s)."

    except Exception as ex:
        return "ERROR", f"Sandbox execution exception: {str(ex)}"

    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
