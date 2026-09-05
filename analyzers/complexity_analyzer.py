from app.analyzers.base import StaticAnalysisResult
from app.analyzers.python_analyzer import analyze_python_code
from app.analyzers.js_ts_analyzer import analyze_js_ts_code
from app.analyzers.java_analyzer import analyze_java_code
from app.analyzers.cpp_analyzer import analyze_cpp_code


def run_static_analysis(code: str, language: str) -> StaticAnalysisResult:
    lang_upper = language.strip().lower()
    
    if lang_upper == "python":
        return analyze_python_code(code)
    elif lang_upper in ["javascript", "js"]:
        return analyze_js_ts_code(code, "JavaScript")
    elif lang_upper in ["typescript", "ts"]:
        return analyze_js_ts_code(code, "TypeScript")
    elif lang_upper == "java":
        return analyze_java_code(code)
    elif lang_upper in ["c++", "cpp", "cplusplus"]:
        return analyze_cpp_code(code)
    else:
        # Fallback default analyzer
        return analyze_python_code(code)
