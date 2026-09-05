import re
from typing import List
from app.analyzers.base import AnalysisFinding


def scan_security_issues(code: str, language: str) -> List[AnalysisFinding]:
    findings: List[AnalysisFinding] = []
    lines = code.splitlines()

    # 1. Hardcoded Secrets & API Keys
    secret_patterns = [
        (r'(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token|password|passwd|access[_-]?token)\s*=\s*["\'][A-Za-z0-9_\-]{8,}["\']',
         "Hardcoded Secret / API Key",
         "Hardcoded credentials pose a severe security risk. Store secrets in environment variables or a secret manager.",
         "critical"),
        (r'-----BEGIN (RSA|PRIVATE|EC) KEY-----',
         "Embedded Private Key",
         "Private keys must never be committed to source code.",
         "critical")
    ]

    # 2. SQL Injection Patterns
    sql_patterns = [
        (r'(?i)(SELECT|INSERT|UPDATE|DELETE)\s+.*?\+\s*\w+',
         "Potential SQL Injection (String Concatenation)",
         "SQL queries constructed using string concatenation are vulnerable to SQL Injection. Use parameterized queries.",
         "high"),
        (r'(?i)f["\'].*?(SELECT|INSERT|UPDATE|DELETE)\s+.*?\{.*?\}',
         "Potential SQL Injection (f-string interpolation)",
         "SQL queries built with string interpolation can lead to SQL Injection. Use parameterized query bindings.",
         "high"),
        (r'(?i)raw\(\s*["\'].*?\%\s*\w+',
         "Potential SQL Injection (Raw Query)",
         "Avoid unescaped raw SQL execution. Always bind parameters.",
         "high")
    ]

    # 3. Code Injection / Dangerous Execution
    eval_patterns = [
        (r'\beval\s*\(', "Use of Dangerous 'eval()' Function",
         "eval() executes untrusted string code directly. Replace with safe parsing logic.", "critical"),
        (r'\bexec\s*\(', "Use of Dangerous 'exec()' Function",
         "exec() allows arbitrary code execution. Refactor to static functions.", "critical"),
        (r'\bRuntime\.getRuntime\(\)\.exec\s*\(', "Command Injection Vulnerability (Java exec)",
         "Executing system commands dynamically can allow Command Injection. Sanitize input strictly.", "high"),
        (r'\bsystem\s*\(\s*["\']?', "System Command Execution",
         "system() passes command strings directly to the shell. Validate inputs or use safe process APIs.", "high"),
        (r'\bpopen\s*\(', "Process Spawn via popen()",
         "Ensure arguments passed to popen are strictly sanitized to prevent shell injection.", "medium")
    ]

    # 4. Insecure Deserialization
    deserialize_patterns = [
        (r'\bpickle\.loads\s*\(', "Insecure Deserialization (pickle)",
         "pickle.loads() can execute arbitrary code on untrusted data. Use safer formats like JSON.", "high"),
        (r'\byaml\.unsafe_load\s*\(', "Insecure YAML Loading",
         "yaml.unsafe_load() permits arbitrary code execution. Use yaml.safe_load().", "high"),
        (r'\bObjectInputStream\s*\(', "Java Insecure Deserialization",
         "Java ObjectInputStream on untrusted data can lead to Remote Code Execution.", "high")
    ]

    # 5. Path Traversal
    path_patterns = [
        (r'\.\./|\.\.\\', "Potential Path Traversal Relative Path",
         "Detected directory traversal sequence (../). Validate and sanitize file paths using safe absolute path functions.", "medium")
    ]

    # 6. Weak Cryptography
    crypto_patterns = [
        (r'\b(md5|sha1)\b(?!\.py)', "Use of Weak Hashing Algorithm",
         "MD5 and SHA-1 are cryptographically broken. Upgrade to SHA-256 or bcrypt/argon2 for passwords.", "medium")
    ]

    all_patterns = secret_patterns + sql_patterns + eval_patterns + deserialize_patterns + path_patterns + crypto_patterns

    for line_idx, line in enumerate(lines, start=1):
        # Skip pure comment lines
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
            continue

        for pattern, title, desc, severity in all_patterns:
            if re.search(pattern, line):
                findings.append(AnalysisFinding(
                    category="security",
                    severity=severity,
                    title=f"Potential Security Issue: {title}",
                    description=desc,
                    recommendation=f"Review line {line_idx} and eliminate unsafe patterns.",
                    line_number=line_idx,
                    code_snippet=line.strip(),
                    confidence=0.9,
                    source_type="RULE_BASED",
                    validation_status="VALIDATED",
                    validation_notes="Confirmed by deterministic static security rule engine."
                ))

    return findings
