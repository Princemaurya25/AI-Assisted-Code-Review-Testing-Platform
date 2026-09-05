import re
from typing import List, Tuple, Dict
from app.schemas.ai import AIFindingSchema
from app.analyzers.base import AnalysisFinding


VALID_CATEGORIES = {"security", "bug", "performance", "maintainability", "readability", "best_practices"}
VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}


def validate_ai_finding(
    ai_finding: AIFindingSchema,
    code: str,
    language: str,
    static_findings: List[AnalysisFinding]
) -> Tuple[str, str]:
    """
    Validates a single AI-generated finding against source code truth and deterministic static analysis.
    Returns (validation_status, validation_notes).

    Statuses:
    - VALIDATED: Verified line, code snippet exists, and cross-confirmed by static analyzer.
    - PARTIALLY_VALIDATED: Valid line and snippet match, plausible issue, no static rule conflict.
    - AI_SUGGESTED: Plausible AI suggestion with valid line, but unverified by static analyzer.
    - REJECTED: Invalid line number, hallucinated snippet, or false vulnerability claim.
    """
    notes = []
    lines = code.splitlines()
    total_lines = len(lines)

    # 1. Validate Category & Severity values
    if ai_finding.category.lower() not in VALID_CATEGORIES:
        return "REJECTED", f"Rejected: Unknown category '{ai_finding.category}'."
    if ai_finding.severity.lower() not in VALID_SEVERITIES:
        return "REJECTED", f"Rejected: Unknown severity '{ai_finding.severity}'."

    # 2. Validate Line Number Bounds
    target_line = ai_finding.line
    if target_line is not None:
        if target_line < 1 or target_line > total_lines:
            return "REJECTED", f"Rejected: Line number {target_line} out of bounds (Source has {total_lines} lines)."
        notes.append(f"Line {target_line} exists in source code.")

    # 3. Check Code Snippet Truth / Existence
    snippet_matched = False
    if ai_finding.code_snippet and target_line:
        actual_line = lines[target_line - 1].strip()
        cleaned_snippet = ai_finding.code_snippet.strip()

        # Check exact or substring match at or around target_line (+/- 2 lines)
        search_range = range(max(0, target_line - 3), min(total_lines, target_line + 2))
        for l_idx in search_range:
            if cleaned_snippet in lines[l_idx] or lines[l_idx].strip() in cleaned_snippet:
                snippet_matched = True
                break

        if not snippet_matched:
            return "REJECTED", f"Rejected: Referenced code snippet '{cleaned_snippet[:30]}...' not found near line {target_line}."
        notes.append("Referenced code snippet verified in source code.")

    # 4. Check Vulnerability Plausibility (e.g. SQL Injection claim)
    code_lower = code.lower()
    title_lower = ai_finding.title.lower()
    desc_lower = ai_finding.description.lower()

    if "sql injection" in title_lower or "sql injection" in desc_lower:
        sql_keywords = ["select", "insert", "update", "delete", "from", "where", "db", "query", "sql"]
        has_sql_ctx = any(kw in code_lower for kw in sql_keywords)
        if not has_sql_ctx:
            return "REJECTED", "Rejected: SQL Injection claimed, but no database or SQL query patterns exist in code."

    if "xss" in title_lower or "cross-site scripting" in desc_lower:
        web_keywords = ["html", "innerhtml", "dom", "response", "render", "jsx", "tsx", "component", "script"]
        has_web_ctx = any(kw in code_lower for kw in web_keywords)
        if not has_web_ctx:
            return "REJECTED", "Rejected: XSS claimed, but code lacks HTML/DOM/web context."

    # 5. Cross-reference with Deterministic Static Analysis Findings
    static_correlation = False
    if target_line:
        for sf in static_findings:
            if sf.line_number == target_line and sf.category.lower() == ai_finding.category.lower():
                static_correlation = True
                break

    if static_correlation:
        notes.append("Independently validated by static analysis rule engine.")
        return "VALIDATED", " | ".join(notes)

    if snippet_matched:
        notes.append("Line number and code snippet matched. AI suggestion accepted.")
        return "PARTIALLY_VALIDATED", " | ".join(notes)

    if target_line:
        notes.append("Valid line number. AI suggestion recorded for developer review.")
        return "AI_SUGGESTED", " | ".join(notes)

    return "AI_SUGGESTED", "General AI suggestion recorded."


def validate_and_deduplicate_findings(
    ai_findings: List[AIFindingSchema],
    code: str,
    language: str,
    static_findings: List[AnalysisFinding]
) -> List[AnalysisFinding]:
    """
    Processes both static analysis findings and AI findings, runs validation on AI findings,
    and returns a unified list of de-duplicated AnalysisFinding entries.
    """
    final_findings: List[AnalysisFinding] = list(static_findings)  # Static findings start as VALIDATED
    
    seen_keys = set()
    for sf in static_findings:
        key = (sf.category.lower(), sf.line_number, sf.title.lower())
        seen_keys.add(key)

    for ai_f in ai_findings:
        status, notes = validate_ai_finding(ai_f, code, language, static_findings)

        # De-duplication key
        dedup_key = (ai_f.category.lower(), ai_f.line, ai_f.title.lower())
        if dedup_key in seen_keys:
            continue
        seen_keys.add(dedup_key)

        converted_finding = AnalysisFinding(
            category=ai_f.category.lower(),
            severity=ai_f.severity.lower(),
            title=f"[AI] {ai_f.title}" if status != "VALIDATED" else ai_f.title,
            description=ai_f.description,
            recommendation=ai_f.recommendation,
            line_number=ai_f.line,
            code_snippet=ai_f.code_snippet,
            confidence=ai_f.confidence,
            source_type="AI_SUGGESTED",
            validation_status=status,
            validation_notes=notes
        )
        final_findings.append(converted_finding)

    return final_findings
