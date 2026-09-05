import re
from typing import Tuple

SUPPORTED_LANGUAGES = ["Python", "JavaScript", "TypeScript", "Java", "C++"]


def detect_language(code: str, filename_or_ext: str = "") -> Tuple[str, float, bool]:
    """
    Detects programming language from file extension or code syntax.
    Returns (language_name, confidence, is_supported).
    """
    if filename_or_ext:
        ext = filename_or_ext.lower().split(".")[-1]
        ext_map = {
            "py": "Python",
            "js": "JavaScript",
            "jsx": "JavaScript",
            "ts": "TypeScript",
            "tsx": "TypeScript",
            "java": "Java",
            "cpp": "C++",
            "cxx": "C++",
            "cc": "C++",
            "hpp": "C++",
            "h": "C++"
        }
        if ext in ext_map:
            return ext_map[ext], 0.95, True

    code_sample = code[:3000]

    # Python heuristics
    if re.search(r'def\s+\w+\s*\(.*?\):', code_sample) or re.search(r'import\s+\w+|from\s+\w+\s+import', code_sample):
        if ":" in code_sample and ("elif " in code_sample or "self." in code_sample or "__name__" in code_sample):
            return "Python", 0.9, True

    # C++ heuristics
    if re.search(r'#include\s+<.*?>', code_sample) or "std::" in code_sample or "cout <<" in code_sample:
        return "C++", 0.95, True

    # Java heuristics
    if re.search(r'public\s+class\s+\w+', code_sample) or re.search(r'public\s+static\s+void\s+main', code_sample) or "System.out.println" in code_sample:
        return "Java", 0.95, True

    # TypeScript heuristics
    if re.search(r':\s*(string|number|boolean|any|void)\b', code_sample) or re.search(r'interface\s+\w+\s*\{', code_sample) or re.search(r'type\s+\w+\s*=', code_sample):
        return "TypeScript", 0.9, True

    # JavaScript heuristics
    if re.search(r'const\s+\w+\s*=|let\s+\w+\s*=|var\s+\w+\s*=', code_sample) or re.search(r'function\s+\w+\s*\(', code_sample) or "console.log" in code_sample:
        return "JavaScript", 0.85, True

    # Default fallback to Python with lower confidence if unknown
    return "Python", 0.5, True
